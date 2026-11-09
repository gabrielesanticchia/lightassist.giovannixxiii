from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


@dataclass(frozen=True)
class MacroCommand:
    command: str
    args: tuple[str, ...]
    line: int


def parse_macro_text(text: str) -> List[MacroCommand]:
    commands: List[MacroCommand] = []
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        pieces = line.split()
        if not pieces:
            continue
        commands.append(MacroCommand(command=pieces[0].upper(), args=tuple(pieces[1:]), line=line_no))
    return commands


def _as_int(value: str, *, default: int = 0) -> int:
    try:
        return int(value)
    except ValueError:
        return default


def compile_macro(text: str) -> List[Dict[str, Any]]:
    pipeline: List[Dict[str, Any]] = []
    commands = parse_macro_text(text)
    for command in commands:
        name = command.command
        args = command.args
        if name in {"POWER"}:
            value = (args[0].upper() if args else "ON") == "ON"
            pipeline.append({"type": "power", "value": value})
        elif name in {"COLOR", "RGB"}:
            if len(args) >= 3:
                pipeline.append({
                    "type": "color",
                    "r": _as_int(args[0], default=0),
                    "g": _as_int(args[1], default=0),
                    "b": _as_int(args[2], default=0),
                })
        elif name in {"BRIGHTNESS", "BRI"}:
            pipeline.append({"type": "brightness", "value": min(100, max(0, _as_int(args[0], default=100)))})
        elif name in {"SPEED"}:
            pipeline.append({"type": "speed", "value": min(100, max(0, _as_int(args[0], default=50)))})
        elif name in {"EFFECT"}:
            pipeline.append({"type": "effect", "value": _as_int(args[0], default=0)})
        elif name in {"WAIT", "DELAY"}:
            pipeline.append({"type": "wait", "delay_ms": max(0, _as_int(args[0], default=1000))})
        elif name in {"LOOP"}:
            pipeline.append({"type": "loop", "count": max(1, _as_int(args[0], default=1))})
        elif name in {"END"}:
            pipeline.append({"type": "end"})
        elif name in {"SCENE"}:
            pipeline.append({"type": "scene", "name": " ".join(args) if args else "scene"})
    return pipeline


def load_macro_file(path: str | Path) -> List[Dict[str, Any]]:
    macro_path = Path(path)
    return compile_macro(macro_path.read_text(encoding="utf-8"))


def load_macro_files(folder: str | Path) -> Dict[str, List[Dict[str, Any]]]:
    macro_dir = Path(folder)
    result: Dict[str, List[Dict[str, Any]]] = {}
    if not macro_dir.exists():
        return result
    for macro_file in sorted(macro_dir.glob("*.macro")):
        result[macro_file.stem] = load_macro_file(macro_file)
    return result
