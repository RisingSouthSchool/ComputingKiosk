#!/usr/bin/env python3
"""Serve the game hub, persist anonymous game votes, and run Python console
projects as live terminal sessions over WebSocket + pty."""

import asyncio
import fcntl
import json
import os
import pty
import re
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

def _import_websockets():
    from websockets.asyncio.server import serve
    from websockets.exceptions import ConnectionClosed as closed
    return serve, closed


try:
    ws_serve, ConnectionClosed = _import_websockets()
except ImportError:
    # Not installed for this Python (or too old). Fall back to the copy bundled
    # in vendor/py so the Python console works with no pip install.
    for _name in [name for name in sys.modules if name == "websockets" or name.startswith("websockets.")]:
        del sys.modules[_name]
    sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor" / "py"))
    try:
        ws_serve, ConnectionClosed = _import_websockets()
    except ImportError:
        ws_serve = None
        ConnectionClosed = Exception

ROOT = Path(__file__).resolve().parent
VOTES_FILE = ROOT / "votes.json"
VOTES_LOCK = threading.Lock()
SLUG_PATTERN = re.compile(r"^[a-z0-9_-]+$")

PYTHON_PROJECTS_DIR = ROOT / "python_projects"
PYTHON_MANIFEST = ROOT / "pythonProjects.json"
# Year 11 database projects run through the same terminal as the Python
# projects, but on a throwaway copy of their folder (see PtySession) so a
# student's .db file is never changed by someone using the kiosk.
DB_PROJECTS_DIR = ROOT / "db_projects"
DB_MANIFEST = ROOT / "databaseProjects.json"
SESSION_TIMEOUT_SECONDS = 10 * 60
PTY_PATH_PATTERN = re.compile(r"^/(py|db)/([a-z0-9_-]+)$")
PTY_PORT = None  # set in main(); exposed to the client via /api/pty-port


def read_votes():
    try:
        with VOTES_FILE.open(encoding="utf-8") as file:
            votes = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    if not isinstance(votes, dict):
        return {}
    return {slug: count for slug, count in votes.items() if isinstance(slug, str) and isinstance(count, int) and count >= 0}


_VERSION_CACHE = {"at": 0.0, "value": None}


def read_version():
    """Short git hash, commit count and commit date of the hub's checkout, or
    None when this folder isn't a git clone (or git isn't installed)."""
    import time
    now = time.monotonic()
    if now - _VERSION_CACHE["at"] < 5:
        return _VERSION_CACHE["value"]

    def git(*args):
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                              timeout=3, check=True).stdout.strip()

    value = None
    try:
        short, date = git("log", "-1", "--format=%h|%cd", "--date=format:%-d %b %H:%M").split("|", 1)
        count = None
        if git("rev-parse", "--is-shallow-repository") == "false":
            count = int(git("rev-list", "--count", "HEAD"))
        value = {"hash": short, "count": count, "date": date}
    except (OSError, ValueError, subprocess.SubprocessError):
        value = None
    _VERSION_CACHE.update(at=now, value=value)
    return value


def write_votes(votes):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=ROOT, prefix="votes.", suffix=".tmp", delete=False) as file:
            temporary_path = Path(file.name)
            json.dump(votes, file, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, VOTES_FILE)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


SYNC_SCRIPT = ROOT / "sync_from_repo.sh"
UPDATE_LOCK = threading.Lock()


def run_update():
    """Run sync_from_repo.sh and turn its RESULT line into a small dict:
    status is current | updated | updated-restart | offline | busy | error."""
    if not UPDATE_LOCK.acquire(blocking=False):
        return {"status": "busy"}
    try:
        if not SYNC_SCRIPT.is_file():
            return {"status": "error", "detail": "sync_from_repo.sh is missing from this folder."}
        env = dict(os.environ, KIOSK_NO_RESTART="1", PYTHON=sys.executable)
        try:
            done = subprocess.run(["bash", str(SYNC_SCRIPT)], cwd=str(ROOT), env=env,
                                  capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return {"status": "error", "detail": "The update took too long."}
        except OSError as error:
            return {"status": "error", "detail": str(error)}
        status, detail = "error", (done.stderr.strip().splitlines() or ["No result from the update script."])[-1]
        for line in done.stdout.splitlines():
            if line.startswith("RESULT:"):
                status, _, detail = line[len("RESULT:"):].strip().partition(":")
                status, detail = status.strip(), detail.strip()
        print(f"[update] {status} {detail}".rstrip(), file=sys.stderr)
        _VERSION_CACHE["at"] = 0.0
        return {"status": status, "detail": detail, "version": read_version()}
    finally:
        UPDATE_LOCK.release()


def restart_server():
    """Replace this process with a fresh one so new server code takes effect.
    The PID stays the same, so launch_kiosk.command keeps waiting on it."""
    sys.stderr.flush()
    sys.stdout.flush()
    os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])


class HubRequestHandler(SimpleHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/votes":
            with VOTES_LOCK:
                self.send_json(read_votes())
            return
        if path == "/api/version":
            self.send_json({"version": read_version()})
            return
        if path == "/api/pty-port":
            self.send_json({"port": PTY_PORT})
            return
        super().do_GET()

    def local_origin(self):
        """True for same-machine requests: no Origin header (curl) or a localhost one."""
        origin = self.headers.get("Origin")
        return not origin or urlsplit(origin).hostname in ("127.0.0.1", "localhost")

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/api/update":
            if not self.local_origin():
                self.send_json({"status": "error", "detail": "Forbidden"}, 403)
                return
            outcome = run_update()
            self.send_json(outcome)
            if outcome.get("status") == "updated-restart":
                threading.Timer(1.0, restart_server).start()
            return
        if path != "/api/vote":
            self.send_error(404)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length))
            slug = payload.get("slug") if isinstance(payload, dict) else None
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "invalid JSON"}, 400)
            return
        if not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug):
            self.send_json({"error": "invalid slug"}, 400)
            return
        with VOTES_LOCK:
            votes = read_votes()
            votes[slug] = votes.get(slug, 0) + 1
            write_votes(votes)
            self.send_json({"slug": slug, "count": votes[slug]})

    def log_message(self, format, *args):
        super().log_message(format, *args)


class HubServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def load_python_project(slug, kind="py"):
    """Look up a slug in pythonProjects.json (kind "py") or databaseProjects.json
    (kind "db"). Returns (project_dir, entry_path) or (None, None) if the slug is
    unknown or its entry file is missing."""
    manifest_path, projects_dir = (DB_MANIFEST, DB_PROJECTS_DIR) if kind == "db" else (PYTHON_MANIFEST, PYTHON_PROJECTS_DIR)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if not isinstance(manifest, list):
        return None, None
    for entry in manifest:
        if isinstance(entry, dict) and entry.get("slug") == slug:
            entry_file = entry.get("entryFile")
            if not isinstance(entry_file, str) or not entry_file:
                return None, None
            project_dir = (projects_dir / slug).resolve()
            entry_path = (project_dir / entry_file).resolve()
            if project_dir not in entry_path.parents:
                return None, None  # entryFile escapes its own project folder
            if not entry_path.is_file():
                return None, None
            return project_dir, entry_path
    return None, None


def set_winsize(fd, rows=24, cols=80):
    try:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    except OSError:
        pass


class PtySession:
    """One student's live terminal program, run inside a pty and bridged to a
    single WebSocket connection. Every way the process can end -- clean exit,
    exception, crash, kill, timeout, or a spawn failure -- funnels through
    `_finish()` so the browser always gets exactly one "ended" signal."""

    def __init__(self, websocket, project_dir, entry_path, scratch=False):
        self.websocket = websocket
        self.project_dir = project_dir
        self.entry_path = entry_path
        self.scratch = scratch  # run on a temporary copy of project_dir
        self.scratch_dir = None
        self.loop = asyncio.get_running_loop()
        self.master_fd = None
        self.process = None
        self.finished = asyncio.Event()
        self._finish_once = False
        self.tail = b""  # last bit of program output, used to explain a crash

    async def run(self):
        try:
            self._spawn()
        except Exception as error:  # noqa: BLE001 - a broken submission must never take the server down
            await self._finish("spawn_error", str(error))
            return

        timeout_task = asyncio.create_task(asyncio.sleep(SESSION_TIMEOUT_SECONDS))
        input_task = asyncio.create_task(self._pump_input())
        finished_task = asyncio.create_task(self.finished.wait())
        try:
            self.loop.add_reader(self.master_fd, self._on_output_ready)
            threading.Thread(target=self._wait_for_exit, daemon=True).start()

            done, pending = await asyncio.wait(
                {timeout_task, input_task, finished_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            if finished_task in done:
                pass  # process already ended and reported itself; nothing more to do
            elif timeout_task in done:
                minutes = SESSION_TIMEOUT_SECONDS // 60
                await self._finish("timeout", f"{minutes}-minute session limit reached")
            elif input_task in done:
                await self._finish("disconnected", "browser closed the connection")
        except Exception as error:  # noqa: BLE001 - any unexpected fault still reports "ended" once
            await self._finish("error", str(error))
        finally:
            for task in (timeout_task, input_task, finished_task):
                task.cancel()
            self._cleanup_process()
            self._cleanup_fd()
            self._cleanup_scratch()

    def _spawn(self):
        run_path = self.entry_path
        if self.scratch:
            self.scratch_dir = Path(tempfile.mkdtemp(prefix="kiosk-db-"))
            run_root = self.scratch_dir / "project"
            shutil.copytree(self.project_dir, run_root)
            run_path = run_root / self.entry_path.relative_to(self.project_dir)
        master_fd, slave_fd = pty.openpty()
        set_winsize(slave_fd)
        try:
            env = dict(os.environ, TERM="xterm-256color", PYTHONUNBUFFERED="1")
            self.process = subprocess.Popen(
                [sys.executable, run_path.name],
                cwd=str(run_path.parent),
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                env=env,
                preexec_fn=os.setsid,
                close_fds=True,
            )
        finally:
            os.close(slave_fd)
        self.master_fd = master_fd
        os.set_blocking(self.master_fd, False)

    def _on_output_ready(self):
        try:
            data = os.read(self.master_fd, 65536)
        except OSError:
            data = b""
        if data:
            self.tail = (self.tail + data)[-4000:]
            asyncio.create_task(self._safe_send_bytes(data))
        else:
            # EOF/EIO: the child closed its end of the pty. The exit-wait
            # thread will report the precise reason shortly; nothing to read
            # from here on.
            try:
                self.loop.remove_reader(self.master_fd)
            except (OSError, ValueError):
                pass

    async def _safe_send_bytes(self, data):
        try:
            await self.websocket.send(data)
        except ConnectionClosed:
            pass

    def _wait_for_exit(self):
        returncode = self.process.wait()
        self.loop.call_soon_threadsafe(
            lambda: asyncio.create_task(self._report_exit(returncode))
        )

    async def _report_exit(self, returncode):
        if returncode == 0:
            await self._finish("exit", "program finished")
        else:
            reason = self._last_output_line()
            await self._finish("crash", f"exited with code {returncode}" + (f": {reason}" if reason else ""))

    def _last_output_line(self):
        """Last non-empty line the program printed, minus terminal escape codes.
        For a crash this is normally the Python error message."""
        text = self.tail.decode("utf-8", errors="replace")
        text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[()][0-9A-Za-z]|\x1b[=>]|\x1b\][^\x07]*\x07", "", text)
        lines = [line.strip() for line in text.replace("\r", "\n").split("\n") if line.strip()]
        return lines[-1][:160] if lines else ""

    async def _pump_input(self):
        try:
            async for message in self.websocket:
                self._handle_message(message)
        except ConnectionClosed:
            pass

    def _handle_message(self, message):
        if isinstance(message, (bytes, bytearray)):
            self._write_input(bytes(message))
            return
        try:
            payload = json.loads(message)
        except ValueError:
            self._write_input(message.encode("utf-8", errors="replace"))
            return
        if not isinstance(payload, dict):
            return
        if payload.get("type") == "input" and isinstance(payload.get("data"), str):
            self._write_input(payload["data"].encode("utf-8", errors="replace"))
        elif payload.get("type") == "resize":
            rows, cols = payload.get("rows"), payload.get("cols")
            if isinstance(rows, int) and isinstance(cols, int) and self.master_fd is not None:
                set_winsize(self.master_fd, rows, cols)

    def _write_input(self, data):
        if self.master_fd is None:
            return
        try:
            os.write(self.master_fd, data)
        except OSError:
            pass

    async def _finish(self, reason, detail):
        if self._finish_once:
            return
        self._finish_once = True
        print(f"[python-console] {self.entry_path} ending: reason={reason} detail={detail!r}", file=sys.stderr)
        try:
            await self.websocket.send(json.dumps({"type": "ended", "reason": reason, "detail": detail}))
        except ConnectionClosed:
            pass
        self.finished.set()

    def _cleanup_process(self):
        if self.process is None or self.process.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass

    def _cleanup_scratch(self):
        if self.scratch_dir is not None:
            shutil.rmtree(self.scratch_dir, ignore_errors=True)
            self.scratch_dir = None

    def _cleanup_fd(self):
        if self.master_fd is None:
            return
        try:
            self.loop.remove_reader(self.master_fd)
        except (OSError, ValueError):
            pass
        try:
            os.close(self.master_fd)
        except OSError:
            pass
        self.master_fd = None


async def pty_connection_handler(websocket):
    path = urlsplit(websocket.request.path).path
    print(f"[python-console] connection opened for path {path!r}", file=sys.stderr)
    match = PTY_PATH_PATTERN.fullmatch(path)
    if not match:
        print(f"[python-console] rejecting {path!r}: does not match /py/<slug> or /db/<slug>", file=sys.stderr)
        await websocket.close(1008, "unknown session path")
        return
    kind, slug = match.group(1), match.group(2)
    project_dir, entry_path = load_python_project(slug, kind)
    if project_dir is None:
        print(f"[python-console] no runnable project for slug {slug!r} "
              f"(check {"databaseProjects.json and db_projects" if kind == "db" else "pythonProjects.json and python_projects"}/{slug}/)", file=sys.stderr)
        try:
            await websocket.send(json.dumps({
                "type": "ended", "reason": "spawn_error",
                "detail": f"no runnable project found for \"{slug}\"",
            }))
        except ConnectionClosed:
            pass
        await websocket.close(1008, "unknown project")
        return
    print(f"[python-console] starting session for {slug!r} -> {entry_path}", file=sys.stderr)
    try:
        await PtySession(websocket, project_dir, entry_path, scratch=(kind == "db")).run()
    except Exception as error:  # noqa: BLE001 - a bug here must never take the server down or hang the browser
        print(f"[python-console] session for {slug!r} raised: {error!r}", file=sys.stderr)
        try:
            await websocket.send(json.dumps({"type": "ended", "reason": "error", "detail": str(error)}))
        except ConnectionClosed:
            pass
    print(f"[python-console] connection closed for {slug!r}", file=sys.stderr)


async def run_pty_server(host, port):
    async with ws_serve(pty_connection_handler, host, port, max_size=None):
        await asyncio.get_running_loop().create_future()  # run forever


def start_pty_server(host, port):
    if ws_serve is None:
        print(
            "NOTE: the 'websockets' package is not installed, so Python console "
            "projects will not run. This needs one internet-connected install:\n"
            "    python3 -m pip install websockets\n"
            "(Games still work fine without it.)",
            file=sys.stderr,
        )
        return
    PYTHON_PROJECTS_DIR.mkdir(exist_ok=True)
    print(f"[python-console] sys.executable = {sys.executable}", file=sys.stderr)

    def runner():
        try:
            asyncio.run(run_pty_server(host, port))
        except OSError as error:
            print(f"Could not start the Python console server: {error}", file=sys.stderr)

    threading.Thread(target=runner, daemon=True).start()
    print(f"Serving Python console sessions at ws://{host}:{port}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--pty-port", type=int, default=8766)
    args = parser.parse_args()
    PTY_PORT = args.pty_port
    start_pty_server("127.0.0.1", args.pty_port)
    handler = partial(HubRequestHandler, directory=str(ROOT))
    with HubServer(("127.0.0.1", args.port), handler) as server:
        print(f"Serving the game hub at http://127.0.0.1:{args.port}")
        server.serve_forever()
