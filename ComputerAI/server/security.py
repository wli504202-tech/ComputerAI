"""Workspace, command, and request validation."""
from __future__ import annotations
import os
import re
import shlex
from pathlib import Path

class ComputerAIError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message); self.code = code; self.message = message

def safe_path(workspace: Path, value: str, must_exist: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ComputerAIError("ERROR_004", "Invalid path")
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts:
        raise ComputerAIError("ERROR_004", "Path must stay inside the configured workspace")
    resolved = (workspace / raw).resolve()
    try: resolved.relative_to(workspace.resolve())
    except ValueError: raise ComputerAIError("ERROR_004", "Path traversal blocked")
    if must_exist and not resolved.exists():
        raise ComputerAIError("ERROR_006", "File not found")
    return resolved

def validate_command(command: dict) -> None:
    if not isinstance(command, dict): raise ComputerAIError("ERROR_003", "Command must be a JSON object")
    if not isinstance(command.get("id"), str) or not command["id"].strip() or len(command["id"]) > 128:
        raise ComputerAIError("ERROR_003", "A command id is required")
    if not isinstance(command.get("computer"), str) or not isinstance(command.get("params"), dict):
        raise ComputerAIError("ERROR_003", "computer and params are required")

def command_allowed(command: str, config: dict) -> None:
    permitted = {"ping", "get_status", "get_workspace", "list_files", "read_file", "write_file", "append_file", "create_directory", "copy_file", "move_file", "delete_file", "exists", "run_python", "run_node", "run_command"}
    if command not in permitted: raise ComputerAIError("ERROR_003", f"Unsupported command: {command}")
    if command == "run_python" and not config["allow_python"]: raise ComputerAIError("ERROR_005", "Python execution is disabled")
    if command == "run_node" and not config["allow_node"]: raise ComputerAIError("ERROR_005", "Node execution is disabled")
    if command == "run_command" and not config["allow_shell"]: raise ComputerAIError("ERROR_005", "Shell execution is disabled in Settings")

def validate_shell(command: str) -> list[str]:
    if not isinstance(command, str) or len(command) > 1000: raise ComputerAIError("ERROR_003", "Invalid shell command")
    # No shell is invoked: permit a short, explicit read-only tool allow-list only.
    parts = shlex.split(command, posix=False)
    if not parts or parts[0].lower() not in {"python", "py", "node", "npm", "git"}:
        raise ComputerAIError("ERROR_005", "Command is not in the allowed command list")
    if any(token.lower() in {"del", "erase", "rmdir", "rd", "format", "powershell", "cmd"} for token in parts):
        raise ComputerAIError("ERROR_005", "Destructive shell syntax is blocked")
    return parts

SECRET = re.compile(r"(password|token|api[_ -]?key|cookie|credit[_ -]?card)\s*[:=]\s*[^\s]+", re.I)
def redact(value: object) -> str:
    return SECRET.sub(r"\1=[REDACTED]", str(value))
