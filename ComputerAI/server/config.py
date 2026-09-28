"""Configuration for the local-only Computer.AI server."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULTS = {
    "host": "127.0.0.1", "port": 8765, "workspace": "../workspace",
    "protocol_version": 1, "max_file_size": 10 * 1024 * 1024,
    "max_request_size": 1024 * 1024, "max_output_size": 1024 * 1024,
    "max_command_time": 60, "allow_python": True, "allow_node": True,
    "allow_shell": False, "require_confirmation": True,
}

def load_config() -> dict:
    path = ROOT / "config.json"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        loaded = {}
    config = DEFAULTS | loaded
    candidate = Path(config["workspace"])
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    config["workspace"] = candidate
    candidate.mkdir(parents=True, exist_ok=True)
    return config

def save_config(config: dict) -> None:
    serializable = config.copy()
    workspace = Path(serializable["workspace"])
    try:
        serializable["workspace"] = str(workspace.relative_to(ROOT))
    except ValueError:
        serializable["workspace"] = str(workspace)
    (ROOT / "config.json").write_text(json.dumps(serializable, indent=2), encoding="utf-8")
