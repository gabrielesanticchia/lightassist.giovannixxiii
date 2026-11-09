from __future__ import annotations

import datetime as dt
from typing import Dict, List


class TriggerScheduler:
    def __init__(self):
        self.triggers: List[Dict[str, object]] = []

    def add(self, *, name: str, hour: int, minute: int, action: str) -> None:
        self.triggers.append({"name": name, "hour": hour, "minute": minute, "action": action})

    def due(self, now: dt.datetime | None = None) -> List[Dict[str, object]]:
        current = now or dt.datetime.now()
        return [trigger for trigger in self.triggers if trigger["hour"] == current.hour and trigger["minute"] == current.minute]
