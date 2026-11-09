from __future__ import annotations

from typing import Any, Dict

try:  # pragma: no cover - optional dependency
    import numpy as np
except Exception:  # pragma: no cover
    np = None


class MusicSyncEngine:
    def __init__(self) -> None:
        self.enabled = False

    def enable(self, enabled: bool) -> Dict[str, Any]:
        self.enabled = bool(enabled)
        return {"music_sync": self.enabled}

    def compute_color(self, data: Any) -> Dict[str, Any]:
        if np is not None:
            arr = np.asarray(data, dtype=float)
            if arr.size == 0:
                return {"r": 0, "g": 0, "b": 0}
            value = float(arr.mean())
            return {"r": int(max(0, min(255, value * 1.5))), "g": int(max(0, min(255, value * 3))), "b": int(max(0, min(255, value * 2)))}
        return {"r": 255, "g": 128, "b": 64}
