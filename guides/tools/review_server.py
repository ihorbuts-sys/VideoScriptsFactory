"""Serves guides/ on 127.0.0.1 (default 8770) like `python3 -m http.server`, and stores review decisions.

GET  /api/decisions/<name>  -> the saved JSON object (or {})
POST /api/decisions/<name>  -> body {"key": {...}}; merged into guides/review/decisions/<name>.json

Run: python3 -I guides/tools/review_server.py [--port 8770]
"""
import argparse
import json
import re
import threading
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "guides"
DECISIONS = ROOT / "review" / "decisions"
LOCK = threading.Lock()
NAME = re.compile(r"^/api/decisions/([a-z0-9_-]{1,60})$")


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _file(self):
        m = NAME.match(self.path.split("?")[0])
        return DECISIONS / f"{m.group(1)}.json" if m else None

    def do_GET(self):
        path = self._file()
        if path is None:
            return super().do_GET()
        self._json(200, json.loads(path.read_text()) if path.exists() else {})

    def do_POST(self):
        path = self._file()
        if path is None:
            return self._json(404, {"error": "unknown path"})
        try:
            update = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            assert isinstance(update, dict)
        except (ValueError, AssertionError):
            return self._json(400, {"error": "body must be a JSON object"})
        with LOCK:
            DECISIONS.mkdir(parents=True, exist_ok=True)
            saved = json.loads(path.read_text()) if path.exists() else {}
            stamp = datetime.now().isoformat(timespec="seconds")
            for key, value in update.items():
                saved[key] = {**value, "savedAt": stamp}
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
            tmp.replace(path)
        self._json(200, {"saved": list(update), "at": stamp})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8770)
    port = ap.parse_args().port
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT)))
    print(f"serving {ROOT} on http://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
