from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from security import ComputerAIError

def run(args: list[str], workspace: Path, timeout: int, output_limit: int) -> dict:
    try:
        completed = subprocess.run(args, cwd=workspace, capture_output=True, text=True, timeout=timeout, shell=False, encoding="utf-8", errors="replace")
    except FileNotFoundError: raise ComputerAIError("ERROR_008", f"Executable not found: {args[0]}")
    except subprocess.TimeoutExpired: raise ComputerAIError("ERROR_007", f"Process exceeded {timeout} seconds")
    output = (completed.stdout or "") + ("\nSTDERR:\n" + completed.stderr if completed.stderr else "")
    if len(output.encode("utf-8")) > output_limit: output = output[:output_limit] + "\n[OUTPUT TRUNCATED]"
    return {"exit_code": completed.returncode, "output": output}

def executable(kind: str) -> str:
    candidates = {"python": ["python", "py"], "node": ["node"]}[kind]
    for value in candidates:
        if shutil.which(value): return value
    raise ComputerAIError("ERROR_NODE_NOT_FOUND" if kind == "node" else "ERROR_008", f"{kind.title()} was not found")
