import os
from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WorkspaceManager:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.file_index = {}
        self.observer = Observer()
        self._setup_workspace()
        
    def _setup_workspace(self):
        """Initialize workspace monitoring"""
        event_handler = WorkspaceEventHandler(self)
        self.observer.schedule(event_handler, self.workspace_path, recursive=True)
        self.observer.start()
        self._index_workspace()
        
    def _index_workspace(self):
        """Index all files in workspace"""
        for filepath in self.workspace_path.rglob('*'):
            if filepath.is_file() and not self._should_ignore(filepath):
                self.file_index[filepath.name] = filepath
                
    def _should_ignore(self, filepath: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = ['.git', '__pycache__', '.pyc', '.env']
        return any(pattern in str(filepath) for pattern in ignore_patterns)
        
    def find_file(self, filename: str) -> Optional[Path]:
        """Find file in workspace"""
        return self.file_index.get(filename)
        
    def get_project_structure(self) -> Dict:
        """Get project structure as tree"""
        return self._build_tree(self.workspace_path)
        
    def _build_tree(self, path: Path) -> Dict:
        """Build tree structure of directory"""
        if path.is_file():
            return str(path)
        return {
            str(path): [
                self._build_tree(p) for p in path.iterdir()
                if not self._should_ignore(p)
            ]
        }

class WorkspaceEventHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager
        
    def on_created(self, event):
        if not event.is_directory:
            self.manager.file_index[Path(event.src_path).name] = Path(event.src_path)
            
    def on_deleted(self, event):
        if not event.is_directory:
            self.manager.file_index.pop(Path(event.src_path).name, None)
