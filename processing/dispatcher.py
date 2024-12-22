from typing import Dict, Any, Callable
import importlib
import os

class CommandDispatcher:
    def __init__(self):
        self.commands = {}
        self.plugins = {}
        self._load_plugins()
        
    def _load_plugins(self):
        plugin_dir = "plugins"
        for file in os.listdir(plugin_dir):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                try:
                    module = importlib.import_module(f"plugins.{module_name}")
                    if hasattr(module, 'register_commands'):
                        self.plugins[module_name] = module
                        module.register_commands(self)
                except Exception as e:
                    print(f"Error loading plugin {module_name}: {e}")
                    
    def register_command(self, intent: str, handler: Callable):
        self.commands[intent] = handler
        
    def dispatch(self, nlu_result: Dict[str, Any]) -> str:
        intent = nlu_result.get("intent")
        if intent in self.commands:
            return self.commands[intent](nlu_result)
        return f"No handler found for intent: {intent}"
