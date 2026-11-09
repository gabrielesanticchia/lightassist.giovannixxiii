from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from led_controller.ble.connection import LedConnectionManager
from led_controller.data.models import DeviceInfo, Macro, MacroStep, Scene
from led_controller.data.storage import read_macros, read_scenes, write_macros, write_scenes
from led_controller.engine.macro_runner import MacroRunner
from led_controller.engine.music_sync import MusicSyncEngine

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def create_app(simulate: bool = False) -> FastAPI:
    app = FastAPI(title="LED Strip Controller")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    connection = LedConnectionManager(simulate=simulate)
    macro_runner = MacroRunner(connection)
    music_engine = MusicSyncEngine()

    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/api/devices")
    async def list_devices() -> List[Dict[str, Any]]:
        devices = connection.devices if connection.devices else connection.scan()
        return [device.to_dict() if hasattr(device, "to_dict") else device for device in devices]

    @app.post("/api/scan")
    async def scan() -> List[Dict[str, Any]]:
        return connection.scan()

    @app.post("/api/connect")
    async def connect(payload: Dict[str, Any]) -> Dict[str, Any]:
        mac = payload.get("mac", "")
        name = payload.get("name", "")
        try:
            return connection.connect(mac, name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/disconnect")
    async def disconnect() -> Dict[str, Any]:
        return connection.disconnect()

    @app.post("/api/power")
    async def power(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_power(bool(payload.get("on", payload.get("state", False))))

    @app.post("/api/color")
    async def color(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_color(payload.get("r", 0), payload.get("g", 0), payload.get("b", 0))

    @app.post("/api/brightness")
    async def brightness(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_brightness(payload.get("value", 100))

    @app.post("/api/speed")
    async def speed(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_speed(payload.get("value", 50))

    @app.post("/api/effect")
    async def effect(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_effect(payload.get("value", 0))

    @app.post("/api/color_temp")
    async def color_temp(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_color_temp(payload.get("value", 0))

    @app.post("/api/music_sync")
    async def music_sync(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.set_music_sync(bool(payload.get("enabled", payload.get("on", False))))

    @app.get("/api/state")
    async def state() -> Dict[str, Any]:
        return connection.get_state()

    @app.get("/api/scenes")
    async def get_scenes() -> List[Dict[str, Any]]:
        return [scene.to_dict() if hasattr(scene, "to_dict") else scene for scene in read_scenes()]

    @app.post("/api/scenes")
    async def create_scene(payload: Dict[str, Any]) -> Dict[str, Any]:
        scenes = read_scenes()
        scene = Scene(**payload)
        scenes.append(scene)
        write_scenes(scenes)
        return scene.to_dict()

    @app.delete("/api/scenes/{scene_id}")
    async def delete_scene(scene_id: str) -> Dict[str, str]:
        scenes = read_scenes()
        filtered = [scene for scene in scenes if scene.id != scene_id]
        write_scenes(filtered)
        return {"status": "deleted", "id": scene_id}

    @app.post("/api/scenes/{scene_id}/apply")
    async def apply_scene(scene_id: str) -> Dict[str, Any]:
        scenes = read_scenes()
        for scene in scenes:
            if scene.id == scene_id:
                connection.set_color(scene.r, scene.g, scene.b)
                connection.set_brightness(scene.brightness)
                connection.set_speed(scene.speed)
                connection.set_effect(scene.effect)
                connection.set_color_temp(scene.color_temp)
                return scene.to_dict()
        raise HTTPException(status_code=404, detail="Scene not found")

    @app.get("/api/macros")
    async def get_macros() -> List[Dict[str, Any]]:
        return [macro.to_dict() if hasattr(macro, "to_dict") else macro for macro in read_macros()]

    @app.post("/api/macros")
    async def create_macro(payload: Dict[str, Any]) -> Dict[str, Any]:
        macros = read_macros()
        macro = Macro(**payload)
        macros.append(macro)
        write_macros(macros)
        return macro.to_dict()

    @app.delete("/api/macros/{macro_id}")
    async def delete_macro(macro_id: str) -> Dict[str, str]:
        macros = read_macros()
        filtered = [macro for macro in macros if macro.id != macro_id]
        write_macros(filtered)
        return {"status": "deleted", "id": macro_id}

    @app.post("/api/macros/{macro_id}/play")
    async def play_macro(macro_id: str) -> Dict[str, Any]:
        macros = read_macros()
        for macro in macros:
            if macro.id == macro_id:
                await macro_runner.run(macro.to_dict())
                return {"status": "playing", "id": macro_id}
        raise HTTPException(status_code=404, detail="Macro not found")

    @app.post("/api/macros/{macro_id}/stop")
    async def stop_macro(macro_id: str) -> Dict[str, Any]:
        await macro_runner.stop()
        return {"status": "stopped", "id": macro_id}

    @app.get("/api/macros/{macro_id}/status")
    async def macro_status(macro_id: str) -> Dict[str, Any]:
        return {"status": "idle", "id": macro_id}

    @app.post("/api/raw")
    async def raw(payload: Dict[str, Any]) -> Dict[str, Any]:
        return connection.send_raw_frame(payload.get("hex", ""))

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        while True:
            await websocket.send_json(connection.get_state())
            await websocket.receive_text()

    return app


app = create_app()
