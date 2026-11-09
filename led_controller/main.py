from __future__ import annotations

import argparse
import threading
import time
from pathlib import Path

from led_controller.api.routes import create_app


def run_web(simulate: bool = False, host: str = "0.0.0.0", port: int = 8000) -> None:
    try:
        import uvicorn
    except Exception as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("uvicorn is required for the web target. Install requirements.txt first.") from exc

    uvicorn.run(create_app(simulate=simulate), host=host, port=port, log_level="info")


def run_gui(simulate: bool = False) -> None:
    try:
        import webview
    except Exception as exc:  # pragma: no cover - dependency guard
        print("pywebview not installed; switching to web mode instead.")
        run_web(simulate=simulate)
        return

    try:
        import uvicorn
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("uvicorn is required for GUI mode as it serves the shared frontend.") from exc

    config = uvicorn.Config(create_app(simulate=simulate), host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)

    webview.create_window(
        "LED Strip Controller",
        "http://127.0.0.1:8000",
        width=1024,
        height=768,
        resizable=True,
    )
    webview.start()


def main() -> None:
    parser = argparse.ArgumentParser(description="LightAssist BLE LED controller")
    parser.add_argument("--web", action="store_true", help="Start the FastAPI web app")
    parser.add_argument("--gui", action="store_true", help="Start the native desktop GUI")
    parser.add_argument("--simulate", action="store_true", help="Use simulator devices instead of real BLE hardware")
    args = parser.parse_args()

    if args.gui:
        run_gui(simulate=args.simulate)
    else:
        run_web(simulate=args.simulate)


if __name__ == "__main__":
    main()
