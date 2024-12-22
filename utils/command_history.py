from datetime import datetime
from typing import List, Dict
import json
import os

class CommandHistory:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.history: List[Dict] = []
        self.current_index = -1
        self.history_file = "config/command_history.json"
        self._load_history()
        
    def add_command(self, command: str, result: str, success: bool):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result,
            "success": success
        }
        
        self.history.append(entry)
        if len(self.history) > self.max_size:
            self.history.pop(0)
            
        self._save_history()
        
    def get_last_commands(self, count: int = 5) -> List[Dict]:
        return self.history[-count:]
        
    def search_commands(self, query: str) -> List[Dict]:
        return [cmd for cmd in self.history 
                if query.lower() in cmd["command"].lower()]
        
    def _save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)
            
    def _load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []
