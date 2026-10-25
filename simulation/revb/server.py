"""Single-device local simulation server. No real-machine control or authentication."""
import argparse
import json
import math
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

ID = re.compile(r"[A-Za-z0-9_-]{1,24}\Z")
STATES = {"ACCEPTED", "DONE", "FAILED", "INTERRUPTED"}


class Store:
    def __init__(self, path):
        self.path = str(path)
        self.lock = threading.Lock()
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS commands (
                id TEXT PRIMARY KEY, column_no INTEGER NOT NULL,
                created REAL NOT NULL, received REAL, finished REAL, state TEXT,
                deliveries INTEGER NOT NULL DEFAULT 0)""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        try:
            with db:
                yield db
        finally:
            db.close()

    def enqueue(self, data):
        name, col = data.get("id"), data.get("column")
        if not isinstance(name, str) or not ID.fullmatch(name) or type(col) is not int or col not in (1, 2):
            raise ValueError("Expected id [A-Za-z0-9_-]{1,24} and integer column 1 or 2")
        with self.lock, self.connect() as db:
            found = db.execute("SELECT column_no FROM commands WHERE id=?", (name,)).fetchone()
            if found and found[0] != col:
                raise ValueError("ID_CONFLICT")
            db.execute("INSERT OR IGNORE INTO commands(id,column_no,created) VALUES(?,?,?)",
                       (name, col, time.time()))
        return {"id": name, "queued": not bool(found)}

    def next_command(self):
        with self.lock, self.connect() as db:
            row = db.execute("SELECT id,column_no FROM commands WHERE state IS NULL ORDER BY created,id LIMIT 1").fetchone()
            if not row:
                return ""
            db.execute("UPDATE commands SET deliveries=deliveries+1 WHERE id=?", (row[0],))
            return f"vend {row[0]} {row[1]}"

    def event(self, data):
        name, col, state = data.get("id"), data.get("column"), data.get("status")
        if not isinstance(name, str) or not ID.fullmatch(name) or type(col) is not int or state not in STATES:
            raise ValueError("Invalid event")
        with self.lock, self.connect() as db:
            row = db.execute("SELECT column_no,state FROM commands WHERE id=?", (name,)).fetchone()
            if not row or row[0] != col:
                raise ValueError("Unknown command or column mismatch")
            now = time.time()
            # Duplicate events are acknowledged; terminal outcomes never regress or change.
            if row[1] in (None, "ACCEPTED"):
                db.execute("""UPDATE commands SET received=COALESCE(received,?), state=?,
                    finished=CASE WHEN ?='ACCEPTED' THEN finished ELSE COALESCE(finished,?) END
                    WHERE id=?""", (now, state, state, now, name))
            elif row[1] != state:
                raise ValueError("Terminal result conflict")
        return f"{name}:{state}"

    def metrics(self):
        with self.lock, self.connect() as db:
            rows = db.execute("SELECT id,column_no,created,received,finished,state,deliveries FROM commands ORDER BY created,id").fetchall()
        sent = len(rows)
        received = sum(r[3] is not None for r in rows)
        terminal = sum(r[4] is not None for r in rows)
        done = sum(r[5] == "DONE" for r in rows)
        delays = sorted((r[3]-r[2])*1000 for r in rows if r[3] is not None)
        return {
            "scope": "local functional test; not RF packet delivery or production SLA",
            "issued_unique": sent, "received_unique": received, "terminal_unique": terminal,
            "success_unique": done,
            "received_fraction": received/sent if sent else None,
            "success_fraction": done/sent if sent else None,
            "server_observed_ack_p95_ms": delays[max(0, math.ceil(.95*len(delays))-1)] if delays else None,
            "commands": [dict(zip(("id", "column", "created", "received", "finished", "status", "deliveries"), r)) for r in rows],
        }


def make_server(path, host="127.0.0.1", port=8765):
    store = Store(path)

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, value, is_json=False):
            data = (json.dumps(value) if is_json else value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json" if is_json else "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/next":
                self.respond(200, store.next_command())
            elif self.path in ("/", "/metrics"):
                self.respond(200, store.metrics(), True)
            else:
                self.respond(404, "Not found")

        def do_POST(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1024:
                    raise ValueError("Invalid body size")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Expected JSON object")
                if self.path == "/enqueue":
                    self.respond(200, store.enqueue(body), True)
                elif self.path == "/events":
                    self.respond(200, store.event(body))
                else:
                    self.respond(404, "Not found")
            except (ValueError, TypeError) as exc:
                self.respond(400, str(exc))

        def log_message(self, *_args):
            pass

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("serve", "vend", "status"))
    parser.add_argument("id", nargs="?")
    parser.add_argument("column", nargs="?", type=int)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=Path(__file__).parent/".local"/"server.sqlite")
    args = parser.parse_args()
    if args.action == "serve":
        args.db.parent.mkdir(parents=True, exist_ok=True)
        server = make_server(args.db, port=args.port)
        print(f"Simulation server: http://127.0.0.1:{args.port} (single device, loopback only)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    else:
        base = f"http://127.0.0.1:{args.port}"
        request = base+"/metrics"
        if args.action == "vend":
            if args.id is None or args.column is None:
                parser.error("vend requires id and column")
            request = Request(base+"/enqueue", json.dumps({"id": args.id, "column": args.column}).encode(),
                              {"Content-Type": "application/json"})
        with urlopen(request, timeout=5) as response:
            print(response.read().decode())


if __name__ == "__main__":
    main()
