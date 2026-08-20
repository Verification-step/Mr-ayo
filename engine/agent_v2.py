from __future__ import annotations
import json
from .ai import OpenRouter
from .tools_v2 import Tools, TOOL_SCHEMAS

SYSTEM = '''You are Mr Ayo, a desktop AI assistant. Be concise. Use tools when they can complete the user's request. Never claim an action succeeded unless the tool result says it succeeded. For sensitive/destructive actions, respect the permission gate. When a task has multiple steps, continue tool-call -> observe result -> next tool-call until complete.'''

class Agent:
    def __init__(self):
        self.ai = OpenRouter(); self.tools = Tools(); self.messages=[{"role":"system","content":SYSTEM}]
    def run(self, user_text: str):
        self.messages.append({"role":"user","content":user_text})
        for _ in range(8):
            msg=self.ai.chat(self.messages, TOOL_SCHEMAS)
            self.messages.append(msg)
            calls=msg.get("tool_calls") or []
            if not calls:
                return msg.get("content", "Done.")
            for call in calls:
                name=call["function"]["name"]
                try: args=json.loads(call["function"].get("arguments") or "{}")
                except json.JSONDecodeError: args={}
                result=self.tools.execute(name,args)
                self.messages.append({"role":"tool","tool_call_id":call["id"],"name":name,"content":json.dumps(result)})
        return "I reached the task step limit before finishing."
