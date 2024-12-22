import os
import ast
from typing import List, Dict
from plugins.plugin_template import BasePlugin

class CodeNavigator(BasePlugin):
    def __init__(self):
        super().__init__()
        self.file_index = {}
        self.symbol_cache = {}
        
    def get_commands(self):
        return {
            "find_definition": self.find_definition,
            "find_references": self.find_references,
            "list_symbols": self.list_symbols
        }
        
    def index_workspace(self, path: str):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._parse_file(file_path)
                    
    def _parse_file(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read(), filename=file_path)
                symbols = self._extract_symbols(tree)
                self.file_index[file_path] = symbols
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
    def _extract_symbols(self, tree: ast.AST) -> Dict:
        symbols = {
            'classes': {},
            'functions': {},
            'variables': []
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols['classes'][node.name] = {
                    'lineno': node.lineno,
                    'methods': []
                }
            elif isinstance(node, ast.FunctionDef):
                symbols['functions'][node.name] = node.lineno
                
        return symbols
        
    def execute(self, command: str, args: Dict):
        cmd = self.get_commands().get(command)
        if cmd:
            return cmd(**args)
        return "Command not found"
        
    def help(self):
        return """
        Code Navigation Commands:
        - find_definition <symbol>: Find where a symbol is defined
        - find_references <symbol>: Find all references to a symbol
        - list_symbols: List all symbols in current workspace
        """
