import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

spec = importlib.util.spec_from_file_location("fv_server", Path(__file__).parents[1]/"server.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProtocolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = module.make_server(Path(self.tmp.name)/"server.sqlite", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def request(self, path, body=None):
        request = self.url+path
        if body is not None:
            request = Request(request, json.dumps(body).encode(), {"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=2) as response:
                return response.read().decode()
        except HTTPError as error:
            error.read()
            error.close()
            raise

    def test_retry_dedup_and_metrics(self):
        cmd = {"id": "demo-1", "column": 1}
        self.request("/enqueue", cmd)
        self.request("/enqueue", cmd)
        self.assertEqual(self.request("/next"), "vend demo-1 1")
        self.assertEqual(self.request("/next"), "vend demo-1 1")
        event = dict(cmd, status="ACCEPTED")
        self.assertEqual(self.request("/events", event), "demo-1:ACCEPTED")
        self.assertEqual(self.request("/next"), "")
        event["status"] = "DONE"
        self.request("/events", event)
        self.request("/events", event)
        metrics = json.loads(self.request("/metrics"))
        self.assertEqual(metrics["issued_unique"], 1)
        self.assertEqual(metrics["received_unique"], 1)
        self.assertEqual(metrics["success_unique"], 1)
        self.assertEqual(metrics["commands"][0]["deliveries"], 2)

    def test_conflicting_id(self):
        self.request("/enqueue", {"id": "x", "column": 1})
        with self.assertRaises(HTTPError) as exc:
            self.request("/enqueue", {"id": "x", "column": 2})
        self.assertEqual(exc.exception.code, 400)

    def test_unknown_and_regressing_results(self):
        with self.assertRaises(HTTPError):
            self.request("/events", {"id": "unknown", "column": 1, "status": "DONE"})
        self.request("/enqueue", {"id": "x", "column": 1})
        self.request("/events", {"id": "x", "column": 1, "status": "INTERRUPTED"})
        with self.assertRaises(HTTPError):
            self.request("/events", {"id": "x", "column": 1, "status": "DONE"})

    def test_failure_is_not_success_and_persists(self):
        self.request("/enqueue", {"id": "x", "column": 2})
        self.request("/events", {"id": "x", "column": 2, "status": "FAILED"})
        store = module.Store(Path(self.tmp.name)/"server.sqlite")
        self.assertEqual(store.metrics()["terminal_unique"], 1)
        self.assertEqual(store.metrics()["success_unique"], 0)
        self.assertEqual(store.next_command(), "")

    def test_invalid_commands(self):
        for body in ({"id": "bad id", "column": 1}, {"id": "x", "column": True},
                     {"id": "x", "column": 0}, {"id": "a"*25, "column": 1}, []):
            with self.assertRaises(HTTPError):
                self.request("/enqueue", body)

    def test_no_samples_is_not_100_percent(self):
        metrics = json.loads(self.request("/metrics"))
        self.assertIsNone(metrics["received_fraction"])
        self.assertIsNone(metrics["success_fraction"])


if __name__ == "__main__":
    unittest.main()
