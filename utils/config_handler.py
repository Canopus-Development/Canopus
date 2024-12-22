import json
import os
from typing import Any, Dict

class ConfigHandler:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_config()
            
    def _create_default_config(self) -> Dict[str, Any]:
        default_config = {
            "input": {"default_mode": "voice"},
            "output": {"voice_enabled": True},
            "ai": {"model": "gpt-4o"},
            "plugins": {"enabled": True}
        }
        self.save_config(default_config)
        return default_config
        
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
        
    def save_config(self, config: Dict[str, Any]):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
