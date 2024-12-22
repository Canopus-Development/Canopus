import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class IDEIntegration:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.supported_ides = {
            'vscode': self._handle_vscode,
            'pycharm': self._handle_pycharm,
            'atom': self._handle_atom
        }
        
    def open_file(self, file_path: str, line: int = None) -> bool:
        """Opens a file in the detected IDE at specified line"""
        ide = self._detect_ide()
        if ide and ide in self.supported_ides:
            return self.supported_ides[ide](file_path, line)
        return False
        
    def _detect_ide(self) -> Optional[str]:
        """Detect which IDE is being used in the workspace"""
        if (self.workspace_path / '.vscode').exists():
            return 'vscode'
        if list(self.workspace_path.glob('*.iml')):
            return 'pycharm'
        if (self.workspace_path / '.atom').exists():
            return 'atom'
        return None
        
    def _handle_vscode(self, file_path: str, line: int = None) -> bool:
        cmd = ['code', '--goto', f"{file_path}:{line}" if line else file_path]
        return subprocess.run(cmd).returncode == 0
        
    def _handle_pycharm(self, file_path: str, line: int = None) -> bool:
        cmd = ['pycharm', '--line', str(line), file_path] if line else ['pycharm', file_path]
        return subprocess.run(cmd).returncode == 0
        
    def _handle_atom(self, file_path: str, line: int = None) -> bool:
        cmd = ['atom', f"{file_path}:{line}" if line else file_path]
        return subprocess.run(cmd).returncode == 0
