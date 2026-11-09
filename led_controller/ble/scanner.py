from __future__ import annotations

from typing import Any, Dict, List

from led_controller.ble.simulator import create_simulated_devices


class BleScanner:
    def __init__(self, simulate: bool = False):
        self.simulate = simulate

    def scan(self) -> List[Dict[str, Any]]:
        if self.simulate:
            return create_simulated_devices()
        return []


def scan_devices(simulate: bool = False) -> List[Dict[str, Any]]:
    return BleScanner(simulate=simulate).scan()
