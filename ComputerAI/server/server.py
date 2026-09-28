"""Computer.AI local-only HTTP server. Run: python server.py"""
from __future__ import annotations
import json, logging, threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from config import load_config, save_config
from command_router import CommandRouter
from security import redact

VERSION="1.0.0"; CONFIG=load_config(); LOG_FILE=Path(__file__).with_name("computer-ai.log")
EXTENSIONS=set()
def write_log(status, command, detail, duration=0):
    line=f"{datetime.now():%H:%M:%S} [{status}] {command} {redact(detail)} {duration}ms"
    logging.info(line)
    with LOG_FILE.open("a",encoding="utf-8") as f: f.write(line+"\n")
ROUTER=CommandRouter(CONFIG,write_log)

class Handler(BaseHTTPRequestHandler):
    server_version="ComputerAI/1.0"
    def log_message(self, fmt,*args): write_log("HTTP",self.command,fmt%args)
    def _headers(self,status=200):
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
        origin=self.headers.get("Origin","")
        if origin.startswith(("chrome-extension://","edge-extension://")):
            self.send_header("Access-Control-Allow-Origin",origin); self.send_header("Vary","Origin")
        self.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    def reply(self,data,status=200): self._headers(status); self.wfile.write(json.dumps(data,ensure_ascii=False).encode("utf-8"))
    def do_OPTIONS(self): self._headers(204)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health": self.reply({"status":"ok","computerAI":True,"version":VERSION,"protocol_version":CONFIG["protocol_version"]})
        elif path=="/status": self.reply({"status":"ok","server":"connected","workspace":str(CONFIG["workspace"]),"extension_connections":len(EXTENSIONS),"protocol_version":CONFIG["protocol_version"]})
        elif path=="/workspace": self.reply({"workspace":str(CONFIG["workspace"])})
        elif path=="/logs":
            try: lines=LOG_FILE.read_text(encoding="utf-8").splitlines()[-200:]
            except OSError: lines=[]
            self.reply({"logs":lines})
        else: self.reply({"error":{"code":"ERROR_006","message":"Endpoint not found"}},404)
    def do_POST(self):
        length=int(self.headers.get("Content-Length","0"))
        if length>CONFIG["max_request_size"]: return self.reply({"success":False,"error":{"code":"ERROR_005","message":"Request too large"}},413)
        try: payload=json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception: return self.reply({"success":False,"error":{"code":"ERROR_003","message":"Invalid JSON"}},400)
        path=urlparse(self.path).path
        if path=="/command": return self.reply(ROUTER.execute(payload))
        if path=="/extension/hello":
            version=payload.get("protocol_version"); extension_id=payload.get("extension_id",self.client_address[0])
            if version!=CONFIG["protocol_version"]: return self.reply({"success":False,"error":{"code":"ERROR_PROTOCOL_MISMATCH","message":"Extension and server protocol versions are incompatible"}},409)
            EXTENSIONS.add(extension_id); return self.reply({"success":True,"message":"Extension registered","protocol_version":CONFIG["protocol_version"]})
        if path=="/settings":
            allowed={"workspace","allow_python","allow_node","allow_shell","require_confirmation","max_command_time","max_file_size","max_output_size"}
            for k,v in payload.items():
                if k in allowed: CONFIG[k]=v
            if "workspace" in payload:
                candidate=Path(payload["workspace"]).expanduser().resolve(); candidate.mkdir(parents=True,exist_ok=True); CONFIG["workspace"]=candidate; ROUTER.files.workspace=candidate
            save_config(CONFIG); return self.reply({"success":True,"settings":{k:(str(v) if k=="workspace" else v) for k,v in CONFIG.items() if k in allowed}})
        self.reply({"success":False,"error":{"code":"ERROR_006","message":"Endpoint not found"}},404)

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO,format="%(message)s")
    httpd=ThreadingHTTPServer((CONFIG["host"],int(CONFIG["port"])),Handler)
    print(f"Computer.AI Local Server running at http://{CONFIG['host']}:{CONFIG['port']}",flush=True)
    try: httpd.serve_forever()
    except KeyboardInterrupt: print("\nComputer.AI Local Server stopped.")
    finally: httpd.server_close()
