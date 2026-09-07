#!/usr/bin/env python3
"""Serve the game hub and persist anonymous game votes."""

import json
import os
import re
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
VOTES_FILE = ROOT / "votes.json"
VOTES_LOCK = threading.Lock()
SLUG_PATTERN = re.compile(r"^[a-z0-9_-]+$")


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
        if urlsplit(self.path).path == "/api/votes":
            with VOTES_LOCK:
                self.send_json(read_votes())
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    handler = partial(HubRequestHandler, directory=str(ROOT))
    with HubServer(("127.0.0.1", args.port), handler) as server:
        print(f"Serving the game hub at http://127.0.0.1:{args.port}")
        server.serve_forever()
