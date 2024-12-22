import importlib
import inspect
from plugins.plugin_template import BasePlugin
import requests

class DocHelper(BasePlugin):
    def __init__(self):
        super().__init__()
        self.doc_cache = {}
        
    def get_commands(self):
        return {
            "get_docs": self.get_documentation,
            "search_pypi": self.search_pypi,
            "get_examples": self.get_examples
        }
        
    def get_documentation(self, module_name: str, symbol: str = None):
        try:
            module = importlib.import_module(module_name)
            if symbol:
                obj = getattr(module, symbol)
                return inspect.getdoc(obj)
            return inspect.getdoc(module)
        except Exception as e:
            return f"Error fetching documentation: {str(e)}"
            
    def search_pypi(self, package_name: str):
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data["info"]["name"],
                    "version": data["info"]["version"],
                    "summary": data["info"]["summary"],
                    "homepage": data["info"]["home_page"]
                }
            return "Package not found"
        except Exception as e:
            return f"Error searching PyPI: {str(e)}"
            
    def execute(self, command: str, args: dict):
        cmd = self.get_commands().get(command)
        if cmd:
            return cmd(**args)
        return "Command not found"
        
    def help(self):
        return """
        Documentation Helper Commands:
        - get_docs <module> [symbol]: Get documentation for module/symbol
        - search_pypi <package>: Search for package on PyPI
        - get_examples <topic>: Get usage examples
        """
