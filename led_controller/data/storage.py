from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import DeviceInfo, Macro, Scene

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "store.json"


def _ensure_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"devices": [], "scenes": [], "macros": []}, indent=2), encoding="utf-8")


def load_store() -> Dict[str, List[Any]]:
    _ensure_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {"devices": [], "scenes": [], "macros": []}
    return {
        "devices": data.get("devices", []),
        "scenes": data.get("scenes", []),
        "macros": data.get("macros", []),
    }


def save_store(store: Dict[str, List[Any]]) -> None:
    _ensure_file()
    DATA_FILE.write_text(json.dumps(store, indent=2), encoding="utf-8")


def read_devices() -> List[DeviceInfo]:
    devices = load_store().get("devices", [])
    return [DeviceInfo(**device) for device in devices]


def write_devices(devices: List[DeviceInfo]) -> None:
    store = load_store()
    store["devices"] = [item.to_dict() if hasattr(item, "to_dict") else item for item in devices]
    save_store(store)


def read_scenes() -> List[Scene]:
    scenes = load_store().get("scenes", [])
    return [Scene(**scene) for scene in scenes]


def write_scenes(scenes: List[Scene]) -> None:
    store = load_store()
    store["scenes"] = [item.to_dict() if hasattr(item, "to_dict") else item for item in scenes]
    save_store(store)


def read_macros() -> List[Macro]:
    macros = load_store().get("macros", [])
    return [Macro(**macro) for macro in macros]


def write_macros(macros: List[Macro]) -> None:
    store = load_store()
    store["macros"] = [item.to_dict() if hasattr(item, "to_dict") else item for item in macros]
    save_store(store)
