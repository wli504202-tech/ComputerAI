from __future__ import annotations
import shutil
from pathlib import Path
from security import ComputerAIError, safe_path

class FileManager:
    def __init__(self, config: dict): self.config = config; self.workspace = config["workspace"]
    def path(self, value: str, exists=False) -> Path: return safe_path(self.workspace, value, exists)
    def list_files(self, relative="."):
        target = self.path(relative, True)
        if not target.is_dir(): raise ComputerAIError("ERROR_004", "Path is not a directory")
        return [{"path": str(p.relative_to(self.workspace)), "type": "directory" if p.is_dir() else "file", "size": None if p.is_dir() else p.stat().st_size} for p in target.rglob("*")]
    def read(self, relative):
        path = self.path(relative, True)
        if not path.is_file(): raise ComputerAIError("ERROR_004", "Path is not a file")
        if path.stat().st_size > self.config["max_file_size"]: raise ComputerAIError("ERROR_005", "File exceeds configured limit")
        return path.read_text(encoding="utf-8")
    def write(self, relative, content, append=False):
        if not isinstance(content, str): raise ComputerAIError("ERROR_003", "content must be a string")
        if len(content.encode("utf-8")) > self.config["max_file_size"]: raise ComputerAIError("ERROR_005", "Content exceeds configured file limit")
        path = self.path(relative); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a" if append else "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        return path
    def mkdir(self, relative):
        path = self.path(relative); path.mkdir(parents=True, exist_ok=True); return path
    def copy(self, src, dst):
        source, dest = self.path(src, True), self.path(dst); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, dest); return dest
    def move(self, src, dst):
        source, dest = self.path(src, True), self.path(dst); dest.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(source), str(dest)); return dest
    def delete(self, relative):
        path = self.path(relative, True)
        if path.is_dir(): raise ComputerAIError("ERROR_005", "Directory deletion is not supported by this command")
        path.unlink(); return path
