from __future__ import annotations
import time
from file_manager import FileManager
from process_manager import executable, run
from security import ComputerAIError, command_allowed, validate_command, validate_shell

class CommandRouter:
    def __init__(self, config, logger): self.config=config; self.files=FileManager(config); self.logger=logger; self.completed={}
    def execute(self, request: dict) -> dict:
        validate_command(request); command, params, cmd_id = request["computer"], request["params"], request["id"]
        if cmd_id in self.completed: return self.completed[cmd_id] | {"duplicate": True}
        started=time.perf_counter()
        try:
            command_allowed(command, self.config)
            high_risk={"delete_file", "move_file", "run_python", "run_node", "run_command"}
            if self.config["require_confirmation"] and command in high_risk and not params.get("confirmed"):
                raise ComputerAIError("ERROR_005", "Confirmation required for this operation")
            result=self._dispatch(command, params)
            response={"id":cmd_id,"success":True,"command":command,"duration_ms":round((time.perf_counter()-started)*1000),**result}
            self.logger("OK", command, result.get("path", ""), response["duration_ms"])
        except ComputerAIError as error:
            response={"id":cmd_id,"success":False,"command":command,"error":{"code":error.code,"message":error.message},"duration_ms":round((time.perf_counter()-started)*1000)}
            self.logger("ERROR", command, error.message, response["duration_ms"])
        except Exception as error:
            response={"id":cmd_id,"success":False,"command":command,"error":{"code":"ERROR_012","message":"Command execution failed"},"duration_ms":round((time.perf_counter()-started)*1000)}
            self.logger("ERROR", command, repr(error), response["duration_ms"])
        self.completed[cmd_id]=response
        if len(self.completed)>1000: self.completed.pop(next(iter(self.completed)))
        return response
    def _ok(self, path):
        absolute=str(path); return {"path":absolute,"message":f"I MAKE OK IN {absolute}"}
    def _dispatch(self, command, p):
        if command=="ping": return {"message":"pong"}
        if command=="get_status": return {"status":"ok","workspace":str(self.files.workspace),"protocol_version":self.config["protocol_version"]}
        if command=="get_workspace": return {"workspace":str(self.files.workspace)}
        if command=="list_files": return {"files":self.files.list_files(p.get("path", "."))}
        if command=="read_file": return {"path":str(self.files.path(p.get("path",""), True)),"content":self.files.read(p.get("path",""))}
        if command=="exists":
            try: path=self.files.path(p.get("path","")); return {"path":str(path),"exists":path.exists()}
            except ComputerAIError: raise
        if command=="write_file": return self._ok(self.files.write(p.get("path",""),p.get("content","")))
        if command=="append_file": return self._ok(self.files.write(p.get("path",""),p.get("content",""),True))
        if command=="create_directory": return self._ok(self.files.mkdir(p.get("path","")))
        if command=="copy_file": return self._ok(self.files.copy(p.get("source",""),p.get("destination","")))
        if command=="move_file": return self._ok(self.files.move(p.get("source",""),p.get("destination","")))
        if command=="delete_file": return self._ok(self.files.delete(p.get("path","")))
        if command in {"run_python","run_node"}:
            file=self.files.path(p.get("file",""),True)
            if file.suffix.lower() != (".py" if command=="run_python" else ".js"): raise ComputerAIError("ERROR_003","Unexpected file extension")
            result=run([executable("python" if command=="run_python" else "node"),str(file)],self.files.workspace,min(int(p.get("timeout",self.config["max_command_time"])),self.config["max_command_time"]),self.config["max_output_size"])
            return {"path":str(file),"message":"PROCESS STARTED",**result}
        if command=="run_command":
            result=run(validate_shell(p.get("command","")),self.files.workspace,self.config["max_command_time"],self.config["max_output_size"]); return {"message":"PROCESS STARTED",**result}
        raise ComputerAIError("ERROR_003","Unsupported command")
