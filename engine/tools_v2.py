from __future__ import annotations
import os, subprocess, webbrowser, shutil
from pathlib import Path

TOOL_SCHEMAS = [
 {"type":"function","function":{"name":"open_application","description":"Open a desktop application.","parameters":{"type":"object","properties":{"application":{"type":"string"}},"required":["application"]}}},
 {"type":"function","function":{"name":"open_url","description":"Open a URL in the default browser.","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},
 {"type":"function","function":{"name":"get_system_info","description":"Return CPU, memory and disk usage.","parameters":{"type":"object","properties":{}}}},
 {"type":"function","function":{"name":"list_directory","description":"List files in a directory.","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
]

class PermissionGate:
    CONFIRM = {"delete_file", "run_shell_command", "close_application"}
    def allow(self, name: str) -> bool:
        if name in self.CONFIRM:
            return input(f"[Mr Ayo] Confirm {name}? (y/N): ").strip().lower() == "y"
        return True

class Tools:
    def __init__(self): self.permissions = PermissionGate()
    def execute(self, name: str, args: dict):
        if not self.permissions.allow(name): return {"ok":False,"error":"User denied action."}
        if name == "open_url": webbrowser.open(args["url"]); return {"ok":True}
        if name == "open_application":
            app=args["application"]
            try: subprocess.Popen([app]); return {"ok":True}
            except Exception as e: return {"ok":False,"error":str(e)}
        if name == "list_directory":
            p=Path(os.path.expandvars(os.path.expanduser(args["path"])))
            return {"ok":True,"files":[x.name for x in p.iterdir()]} if p.exists() else {"ok":False,"error":"Directory not found"}
        if name == "get_system_info":
            import psutil
            return {"ok":True,"cpu_percent":psutil.cpu_percent(0.5),"memory_percent":psutil.virtual_memory().percent,"disk_percent":psutil.disk_usage(os.getcwd()).percent}
        return {"ok":False,"error":f"Unknown tool: {name}"}
