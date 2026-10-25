import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).parents[1]
ROOT = HERE.parents[1]


class DiagramTest(unittest.TestCase):
    def setUp(self):
        self.diagram = json.loads((HERE/"diagram.json").read_text(encoding="utf-8"))
        self.edges = {frozenset(row[:2]) for row in self.diagram["connections"]}

    def wired(self, a, b):
        self.assertIn(frozenset((a, b)), self.edges)

    def test_all_endpoints_and_unique_ids(self):
        ids = [p["id"] for p in self.diagram["parts"]]
        self.assertEqual(len(ids), len(set(ids)))
        for row in self.diagram["connections"]:
            for endpoint in row[:2]:
                self.assertIn(endpoint.split(":")[0], ids+["$serialMonitor"])

    def test_fixed_gpio_map_and_external_rx_pullups(self):
        header = (ROOT/"docs/revb/FV-CTRL_RevB-pins.h").read_text()
        expected = dict(re.findall(r"constexpr int (\w+) = (\d+);", header))
        names = ("SERVO_1_TOP", "SERVO_1_BOTTOM", "SERVO_2_TOP", "SERVO_2_BOTTOM")
        values = []
        for i, name in enumerate(names, 1):
            pin = expected[name]
            values.append(pin)
            self.wired(f"esp:{pin}", f"pwm{i}:1")
            self.wired(f"pwm{i}:2", f"servo{i}:PWM")
            self.wired(f"servo{i}:PWM", f"pd{i}:1")
        sketch = (HERE/"sketch.ino").read_text()
        self.assertIn("ServoPins[4]={"+",".join(values)+"}", sketch)
        for i, name in enumerate(("IR_RX_1", "IR_RX_2"), 1):
            self.wired(f"ir{i}series:2", "esp:"+expected[name])
            self.wired(f"ir{i}pull:2", "esp:3V3")
        self.assertIn("RxPins[2]={34,35}", sketch)
        self.assertIn("LimitPins[4]={25,26,27,32}", sketch)
        self.wired("esp:"+expected["IR_TX"], "logic:D4")

    def test_initial_sensor_controls_and_firmware_paths(self):
        parts = {p["id"]: p for p in self.diagram["parts"]}
        for i in (1, 2):
            self.assertEqual(parts[f"ir{i}"]["attrs"]["value"], "")
            self.wired(f"ir{i}:1", "esp:GND.1")
            self.wired(f"ir{i}:3", "esp:3V3")
        for i in range(1, 5):
            self.wired(f"limit{i}:2", f"esp:{[25,26,27,32][i-1]}")
        import tomllib
        config = tomllib.loads((HERE/"wokwi.toml").read_text())
        self.assertEqual(config["wokwi"]["firmware"], ".pio/build/esp32dev/firmware.bin")


if __name__ == "__main__":
    unittest.main()
