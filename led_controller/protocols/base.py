from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List


class LedProtocol(ABC):
    aliases: Iterable[str] = ()
    effect_names: List[str] = []

    @classmethod
    def matches(cls, name: str) -> bool:
        token = (name or "").upper()
        return any(alias.upper() in token or token in alias.upper() for alias in cls.aliases)

    @classmethod
    def supported_names(cls) -> List[str]:
        return list(cls.aliases)

    @abstractmethod
    def power(self, enabled: bool) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def rgb(self, r: int, g: int, b: int) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def brightness(self, value: int) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def effect(self, code: int) -> bytes:
        raise NotImplementedError


def detect_protocol(name: str) -> str:
    from .elk_bledom import ElkBledomProtocol
    from .ledblue import LedBlueProtocol
    from .melk import MelkProtocol
    from .sp import SPProtocol
    from .triones import TrionesProtocol

    for protocol in (ElkBledomProtocol, MelkProtocol, TrionesProtocol, SPProtocol, LedBlueProtocol):
        if protocol.matches(name):
            return protocol.__name__
    return "unknown"
