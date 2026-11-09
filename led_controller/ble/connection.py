from __future__ import annotations

from typing import Any, Dict, List, Optional

from led_controller.ble.simulator import FakeLedDevice, create_simulated_devices
from led_controller.data.storage import read_devices, write_devices
from led_controller.data.models import DeviceInfo
from led_controller.protocols.base import detect_protocol


class LedConnectionManager:
    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.connected_device: Optional[FakeLedDevice] = None
        self.devices = [DeviceInfo(**device) for device in read_devices()] or [
            DeviceInfo(**entry) for entry in create_simulated_devices()
        ]

    def scan(self) -> List[Dict[str, Any]]:
        if self.simulate:
            results = create_simulated_devices()
        else:
            results = []
        if results:
            self.devices = [DeviceInfo(**entry) for entry in results]
            write_devices(self.devices)
        return results

    def connect(self, mac: str, name: str) -> Dict[str, Any]:
        if not mac and not name:
            raise ValueError("A BLE device address or name is required")
        if self.simulate:
            device = FakeLedDevice(mac=mac or "AA:BB:CC:DD:EE:FF", name=name or "ELK-BLEDOM", protocol=detect_protocol(name or "ELK-BLEDOM"))
            device.connected = True
            self.connected_device = device
            status = device.info
            status["connected"] = True
            return status
        self.connected_device = FakeLedDevice(mac=mac or "AA:BB:CC:DD:EE:FF", name=name or "ELK-BLEDOM", protocol=detect_protocol(name or "ELK-BLEDOM"), connected=True)
        return self.connected_device.info

    def disconnect(self) -> Dict[str, Any]:
        if self.connected_device is not None:
            self.connected_device.connected = False
            state = self.connected_device.info.copy()
            state["connected"] = False
            self.connected_device = None
            return state
        return {"connected": False, "name": "", "mac": ""}

    def set_power(self, enabled: bool) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        self.connected_device.power = bool(enabled)
        return self.connected_device.info

    def set_color(self, r: int, g: int, b: int) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        self.connected_device.rgb = {"r": int(r), "g": int(g), "b": int(b)}
        return self.connected_device.info

    def set_brightness(self, value: int) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        self.connected_device.brightness = max(0, min(100, int(value)))
        return self.connected_device.info

    def set_speed(self, value: int) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        return {"speed": max(0, min(100, int(value))) }

    def set_effect(self, code: int) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        self.connected_device.effect = int(code)
        return self.connected_device.info

    def set_color_temp(self, value: int) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        self.connected_device.color_temp = int(value)
        return self.connected_device.info

    def set_music_sync(self, enabled: bool) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        self.connected_device.music_sync = bool(enabled)
        return self.connected_device.info

    def get_state(self) -> Dict[str, Any]:
        if self.connected_device is None:
            return {"connected": False, "name": "", "protocol": "unknown", "power": False, "color": {"r": 0, "g": 0, "b": 0}, "brightness": 0, "speed": 0, "music_sync": False}
        return self.connected_device.info

    def send_raw_frame(self, hex_payload: str) -> Dict[str, Any]:
        if self.connected_device is None:
            raise RuntimeError("No device connected")
        frame = bytes.fromhex(hex_payload.replace(" ", "").replace("0x", "")) if hex_payload else b""
        self.connected_device.last_frame = frame
        return {"frame": frame.hex(), "ok": True}
