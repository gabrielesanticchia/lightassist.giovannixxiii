from __future__ import annotations

from .base import LedProtocol


class ElkBledomProtocol(LedProtocol):
    aliases = (
        "ELK-BLEDOM",
        "ELK-BLEDOB",
        "ELK-BLEDDM",
        "ELK-BLE",
        "ELK-BTC",
        "ELK-BULB",
        "ELK-BULB2",
        "ELK-LAMPL",
        "LEDBLE",
        "LEDBLUE",
        "JACKYLED",
        "XROCKER",
        "DMRRBA-007",
        "Realky",
        "LED-DMX",
        "Colorful-Light",
    )
    effect_names = [f"Effect {i}" for i in range(22)]

    def power(self, enabled: bool) -> bytes:
        return bytes([0x7E, 0x00, 0x04, 0xF0 if enabled else 0x00, 0x00, 0x01, 0xFF, 0x00, 0xEF])

    def rgb(self, r: int, g: int, b: int) -> bytes:
        return bytes([0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF])

    def brightness(self, value: int) -> bytes:
        value = max(0, min(100, value))
        return bytes([0x7E, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xEF])

    def effect(self, code: int) -> bytes:
        code = max(0x87, min(0x9C, code))
        return bytes([0x7E, 0x00, 0x03, code, 0x03, 0x00, 0x00, 0x00, 0xEF])
