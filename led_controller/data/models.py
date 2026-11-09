from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    from pydantic import BaseModel, ConfigDict, Field

    class ModelBase(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

except Exception:  # pragma: no cover - fallback for minimal environments
    class ModelBase:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def to_dict(self) -> Dict[str, Any]:
            return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

    def Field(default: Any = None, **kwargs: Any) -> Any:  # type: ignore[misc]
        return default


class DeviceInfo(ModelBase):
    mac: str = Field(default="")
    name: str = Field(default="Unknown")
    protocol: str = Field(default="unknown")
    rssi: int = Field(default=-80)
    connected: bool = Field(default=False)


class Scene(ModelBase):
    id: str = Field(default="")
    name: str = Field(default="Scene")
    r: int = Field(default=255)
    g: int = Field(default=0)
    b: int = Field(default=0)
    brightness: int = Field(default=100)
    speed: int = Field(default=50)
    effect: int = Field(default=0)
    color_temp: int = Field(default=0)


class MacroStep(ModelBase):
    id: str = Field(default="")
    name: str = Field(default="Step")
    delay_ms: int = Field(default=1000)
    r: int = Field(default=255)
    g: int = Field(default=0)
    b: int = Field(default=0)
    brightness: int = Field(default=100)
    effect: int = Field(default=0)


class Macro(ModelBase):
    id: str = Field(default="")
    name: str = Field(default="Macro")
    steps: List[MacroStep] = Field(default_factory=list)
    loop: bool = Field(default=False)


class DeviceState(ModelBase):
    address: str = Field(default="")
    name: str = Field(default="")
    protocol: str = Field(default="unknown")
    connected: bool = Field(default=False)
    power: bool = Field(default=False)
    color: Dict[str, int] = Field(default_factory=lambda: {"r": 255, "g": 255, "b": 255})
    brightness: int = Field(default=100)
    speed: int = Field(default=50)
    effect: int = Field(default=0)
    color_temp: int = Field(default=0)
    music_sync: bool = Field(default=False)


@dataclass
class StoredData:
    devices: List[DeviceInfo] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    macros: List[Macro] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "devices": [asdict(device) for device in self.devices],
            "scenes": [asdict(scene) for scene in self.scenes],
            "macros": [asdict(macro) for macro in self.macros],
        }
