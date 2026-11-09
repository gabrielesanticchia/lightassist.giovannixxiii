from __future__ import annotations

from .base import LedProtocol


class TrionesProtocol(LedProtocol):
    aliases = ("TRIONES", "QHM")
    effect_names = [f"Effect {i}" for i in range(16)]

    def _checksum(self, payload: bytes) -> int:
        return 0x00 if not payload else __import__("functools").reduce(lambda acc, value: acc ^ value, payload, 0)

    def power(self, enabled: bool) -> bytes:
        payload = bytes([0x56, 0x01, 0x01 if enabled else 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        return payload + bytes([self._checksum(payload)])

    def rgb(self, r: int, g: int, b: int) -> bytes:
        payload = bytes([0x56, 0x02, r, g, b, 0x00, 0x00, 0x00])
        return payload + bytes([self._checksum(payload)])

    def brightness(self, value: int) -> bytes:
        value = max(0, min(100, value))
        payload = bytes([0x56, 0x03, value, 0x00, 0x00, 0x00, 0x00, 0x00])
        return payload + bytes([self._checksum(payload)])

    def effect(self, code: int) -> bytes:
        payload = bytes([0x56, 0x04, code, 0x00, 0x00, 0x00, 0x00, 0x00])
        return payload + bytes([self._checksum(payload)])
