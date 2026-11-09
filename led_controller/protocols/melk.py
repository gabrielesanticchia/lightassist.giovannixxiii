from __future__ import annotations

from .base import LedProtocol


class MelkProtocol(LedProtocol):
    aliases = ("MELK", "MELK-OA10", "MELK-OC10", "MELK-OF10", "MELK-OG10", "MELK-OA21")
    effect_names = [f"MELK {i}" for i in range(16)]

    def power(self, enabled: bool) -> bytes:
        return bytes([0x7E, 0x07, 0x83, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEF]) if enabled else bytes([0x7E, 0x04, 0x04, 0xF0, 0x00, 0x01, 0xFF, 0x00, 0xEF])

    def rgb(self, r: int, g: int, b: int) -> bytes:
        return bytes([0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF])

    def brightness(self, value: int) -> bytes:
        value = max(0, min(100, value))
        return bytes([0x7E, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xEF])

    def effect(self, code: int) -> bytes:
        return bytes([0x7E, 0x00, 0x03, code % 256, 0x03, 0x00, 0x00, 0x00, 0xEF])
