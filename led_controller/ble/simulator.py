from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from led_controller.protocols.base import detect_protocol


@dataclass
class FakeLedDevice:
    mac: str
    name: str
    protocol: str
    rssi: int = -60
    connected: bool = False
    power: bool = False
    rgb: Dict[str, int] = field(default_factory=lambda: {"r": 255, "g": 255, "b": 255})
    brightness: int = 100
    effect: int = 0
    color_temp: int = 0
    music_sync: bool = False

    @classmethod
    def from_scan(cls, index: int = 0, name: str = "ELK-BLEDOM") -> "FakeLedDevice":
        device_name = name or "ELK-BLEDOM"
        return cls(
            mac=f"AA:BB:CC:DD:EE:{index:02X}",
            name=device_name,
            protocol=detect_protocol(device_name),
            rssi=-60 - index,
        )

    def send_frame(self, frame: bytes) -> bytes:
        self.last_frame = frame
        return frame

    @property
    def info(self) -> Dict[str, object]:
        return {
            "mac": self.mac,
            "name": self.name,
            "protocol": self.protocol,
            "rssi": self.rssi,
            "connected": self.connected,
            "power": self.power,
            "color": self.rgb,
            "brightness": self.brightness,
            "effect": self.effect,
            "music_sync": self.music_sync,
        }


def create_simulated_devices() -> List[Dict[str, object]]:
    sample_names = [
        "ELK-BLEDOM",
        "MELK-OA10",
        "Triones-123",
        "SP105E",
        "LEDBLUE-01",
    ]
    return [FakeLedDevice.from_scan(index=idx, name=name).info for idx, name in enumerate(sample_names)]
