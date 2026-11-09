from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List


class MacroRunner:
    def __init__(self, device_driver: Any):
        self.device_driver = device_driver
        self._task: asyncio.Task | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self, macro: Dict[str, Any]) -> None:
        if self.running:
            raise RuntimeError("Una macro è già in esecuzione")
        self.validate(macro)
        self._task = asyncio.create_task(self.run(macro))

    def validate(self, macro: Dict[str, Any]) -> None:
        for step in macro.get("steps", []):
            step_type = step.get("type", "color")
            if step_type not in {"color", "sleep", "flash"}:
                raise ValueError(f"Tipo di blocco macro non supportato: {step_type}")
            self._duration(step)
            if step_type == "color":
                color = step.get("color")
                if color is None and "r" in step:
                    color = "#{:02x}{:02x}{:02x}".format(
                        *(max(0, min(255, int(step.get(channel, 0)))) for channel in ("r", "g", "b"))
                    )
                    step["color"] = color
                self._validate_color(color or "#0000ff")
            elif step_type == "flash":
                self._validate_color(step.get("from_color", "#ffffff"))
                self._validate_color(step.get("to_color", "#0000ff"))
                try:
                    interval = float(step.get("interval", 0.5))
                except (TypeError, ValueError) as exc:
                    raise ValueError("Intervallo flash non valido") from exc
                if not 0.1 <= interval <= 10:
                    raise ValueError("L'intervallo flash deve essere compreso tra 0,1 e 10 secondi")

    async def run(self, macro: Dict[str, Any]) -> None:
        for step in macro.get("steps", []):
            step_type = step.get("type", "color")
            if step_type == "sleep":
                await asyncio.sleep(self._duration(step))
            elif step_type == "flash":
                await self._flash(step)
            elif step_type == "color":
                self._set_color(step.get("color", "#0000ff"))
                await asyncio.sleep(self._duration(step))
            else:
                raise ValueError(f"Tipo di blocco macro non supportato: {step_type}")

    @staticmethod
    def _duration(step: Dict[str, Any]) -> float:
        try:
            duration = float(step.get("duration", step.get("delay_ms", 1000) / 1000))
        except (TypeError, ValueError) as exc:
            raise ValueError("Durata macro non valida") from exc
        if not 0.1 <= duration <= 3600:
            raise ValueError("La durata deve essere compresa tra 0,1 e 3600 secondi")
        return duration

    def _set_color(self, color: str) -> None:
        self._validate_color(color)
        if self.device_driver is not None:
            self.device_driver.set_color(*(int(color[offset:offset + 2], 16) for offset in (1, 3, 5)))

    @staticmethod
    def _validate_color(color: str) -> None:
        if not isinstance(color, str) or re.fullmatch(r"#[0-9a-fA-F]{6}", color) is None:
            raise ValueError(f"Colore non valido: {color}")

    async def _flash(self, step: Dict[str, Any]) -> None:
        duration = self._duration(step)
        try:
            interval = float(step.get("interval", 0.5))
        except (TypeError, ValueError) as exc:
            raise ValueError("Intervallo flash non valido") from exc
        if not 0.1 <= interval <= 10:
            raise ValueError("L'intervallo flash deve essere compreso tra 0,1 e 10 secondi")
        start = asyncio.get_running_loop().time()
        end = start + duration
        colors = (step.get("from_color", "#ffffff"), step.get("to_color", "#0000ff"))
        index = 0
        while asyncio.get_running_loop().time() < end:
            self._set_color(colors[index % 2])
            index += 1
            await asyncio.sleep(min(interval, max(0, end - asyncio.get_running_loop().time())))

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
