import asyncio
import unittest

from led_controller.engine.macro_runner import MacroRunner


class RecordingDriver:
    def __init__(self):
        self.colors = []

    def set_color(self, r, g, b):
        self.colors.append((r, g, b))


class MacroRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_runs_color_sleep_and_flash_blocks(self):
        driver = RecordingDriver()
        runner = MacroRunner(driver)
        await runner.run({
            "steps": [
                {"type": "color", "color": "#0000ff", "duration": 0.1},
                {"type": "sleep", "duration": 0.1},
                {
                    "type": "flash",
                    "from_color": "#ffffff",
                    "to_color": "#0000ff",
                    "duration": 0.2,
                    "interval": 0.1,
                },
            ],
        })

        self.assertEqual(driver.colors[0], (0, 0, 255))
        self.assertIn((255, 255, 255), driver.colors)
        self.assertIn((0, 0, 255), driver.colors)

    async def test_rejects_invalid_colors_and_durations(self):
        runner = MacroRunner(RecordingDriver())
        with self.assertRaises(ValueError):
            runner.validate({"steps": [{"type": "color", "color": "blue", "duration": 1}]})
        with self.assertRaises(ValueError):
            runner.validate({"steps": [{"type": "sleep", "duration": 0}]})

    async def test_stop_cancels_running_macro(self):
        runner = MacroRunner(RecordingDriver())
        runner.start({"steps": [{"type": "sleep", "duration": 10}]})
        self.assertTrue(runner.running)
        await runner.stop()
        self.assertFalse(runner.running)


if __name__ == "__main__":
    unittest.main()
