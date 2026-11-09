from __future__ import annotations

from .elk_bledom import ElkBledomProtocol


class SPProtocol(ElkBledomProtocol):
    aliases = ("SP105E", "SP110E", "SP611E", "SP621E", "SP")
    effect_names = [f"SP {i}" for i in range(22)]

    def rgb(self, r: int, g: int, b: int) -> bytes:
        return super().rgb(r, g, b)

    def power(self, enabled: bool) -> bytes:
        return super().power(enabled)

    def brightness(self, value: int) -> bytes:
        return super().brightness(value)

    def effect(self, code: int) -> bytes:
        return super().effect(code)
