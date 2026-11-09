from __future__ import annotations

import asyncio
from typing import Any, Dict, List


class MacroRunner:
    def __init__(self, device_driver: Any):
        self.device_driver = device_driver
        self._task: asyncio.Task | None = None

    async def run(self, macro: Dict[str, Any]) -> None:
        steps = macro.get("steps", [])

        async def runner() -> None:
            for step in steps:
                if self.device_driver is not None:
                    if "r" in step:
                        self.device_driver.set_color(step.get("r", 0), step.get("g", 0), step.get("b", 0))
                    if "brightness" in step:
                        self.device_driver.set_brightness(step.get("brightness", 100))
                    if "effect" in step:
                        self.device_driver.set_effect(step.get("effect", 0))
                await asyncio.sleep(max(0.1, (step.get("delay_ms", 1000) / 1000.0)))

        self._task = asyncio.create_task(runner())
        await self._task

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None
