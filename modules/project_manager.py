from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

class ProjectManager:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.project_data = self._load_project_data()
        
    def _load_project_data(self) -> Dict:
        project_file = self.workspace_path / '.canopus' / 'project.json'
        if project_file.exists():
            return json.loads(project_file.read_text())
        return self._create_default_project()
        
    def _create_default_project(self) -> Dict:
        project_data = {
            "name": self.workspace_path.name,
            "created_at": datetime.now().isoformat(),
            "tasks": [],
            "dependencies": [],
            "environment": {},
            "metrics": {
                "lines_of_code": 0,
                "test_coverage": 0,
                "last_build": None
            }
        }
        self._save_project_data(project_data)
        return project_data
        
    def _save_project_data(self, data: Dict):
        project_file = self.workspace_path / '.canopus' / 'project.json'
        project_file.parent.mkdir(exist_ok=True)
        project_file.write_text(json.dumps(data, indent=2))
        
    def add_task(self, task: Dict):
        """Add a project task"""
        self.project_data["tasks"].append({
            **task,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        })
        self._save_project_data(self.project_data)
        
    def update_metrics(self, metrics: Dict):
        """Update project metrics"""
        self.project_data["metrics"].update(metrics)
        self._save_project_data(self.project_data)
        
    def get_project_summary(self) -> Dict:
        """Get project summary with key metrics"""
        return {
            "name": self.project_data["name"],
            "tasks_count": len(self.project_data["tasks"]),
            "metrics": self.project_data["metrics"],
            "dependencies": len(self.project_data["dependencies"])
        }
