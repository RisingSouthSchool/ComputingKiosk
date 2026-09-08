#!/usr/bin/env python3
"""Serve the game hub, persist anonymous game votes, and run Python console
projects as live terminal sessions over WebSocket + pty."""

import asyncio
import fcntl
import json
import os
import pty
import re
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

try:
    from websockets.asyncio.server import serve as ws_serve
    from websockets.exceptions import ConnectionClosed
except ImportError:
    ws_serve = None
    ConnectionClosed = Exception

ROOT = Path(__file__).resolve().parent
VOTES_FILE = ROOT / "votes.json"
VOTES_LOCK = threading.Lock()
SLUG_PATTERN = re.compile(r"^[a-z0-9_-]+$")

PYTHON_PROJECTS_DIR = ROOT / "python_projects"
PYTHON_MANIFEST = ROOT / "pythonProjects.json"
SESSION_TIMEOUT_SECONDS = 10 * 60
PTY_PATH_PATTERN = re.compile(r"^/py/([a-z0-9_-]+)$")
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
        if path == "/api/pty-port":
            self.send_json({"port": PTY_PORT})
            return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/vote":
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


def load_python_project(slug):
    """Look up a slug in pythonProjects.json. Returns (project_dir, entry_path)
    or (None, None) if the slug is unknown or its entry file is missing."""
    try:
        manifest = json.loads(PYTHON_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if not isinstance(manifest, list):
        return None, None
    for entry in manifest:
        if isinstance(entry, dict) and entry.get("slug") == slug:
            entry_file = entry.get("entryFile")
            if not isinstance(entry_file, str) or not entry_file:
                return None, None
            project_dir = (PYTHON_PROJECTS_DIR / slug).resolve()
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

    def __init__(self, websocket, project_dir, entry_path):
        self.websocket = websocket
        self.project_dir = project_dir
        self.entry_path = entry_path
        self.loop = asyncio.get_running_loop()
        self.master_fd = None
        self.process = None
        self.finished = asyncio.Event()
        self._finish_once = False

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

    def _spawn(self):
        master_fd, slave_fd = pty.openpty()
        set_winsize(slave_fd)
        try:
            env = dict(os.environ, TERM="xterm-256color", PYTHONUNBUFFERED="1")
            self.process = subprocess.Popen(
                [sys.executable, self.entry_path.name],
                cwd=str(self.entry_path.parent),
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
            await self._finish("crash", f"exited with code {returncode}")

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
    match = PTY_PATH_PATTERN.fullmatch(path)
    if not match:
        await websocket.close(1008, "unknown session path")
        return
    slug = match.group(1)
    project_dir, entry_path = load_python_project(slug)
    if project_dir is None:
        try:
            await websocket.send(json.dumps({
                "type": "ended", "reason": "spawn_error",
                "detail": f"no runnable project found for \"{slug}\"",
            }))
        except ConnectionClosed:
            pass
        await websocket.close(1008, "unknown project")
        return
    await PtySession(websocket, project_dir, entry_path).run()


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
