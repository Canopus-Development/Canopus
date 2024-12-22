import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import asyncio

class TaskAutomation:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.task_configs = self._load_task_configs()
        
    def _load_task_configs(self) -> Dict:
        task_file = self.workspace_path / 'canopus.tasks.yaml'
        if task_file.exists():  # Fixed syntax error here
            with open(task_file) as f:
                return yaml.safe_load(f)
        return {"tasks": {}}
        
    async def run_task(self, task_name: str, **kwargs) -> Dict:
        """Execute a predefined task"""
        if task_name not in self.task_configs["tasks"]:
            return {"status": "error", "message": f"Task {task_name} not found"}
            
        task = self.task_configs["tasks"][task_name]
        steps = task.get("steps", [])
        results = []
        
        for step in steps:
            try:
                if step["type"] == "shell":
                    result = await self._run_shell_command(step["command"])
                elif step["type"] == "python":
                    result = await self._run_python_code(step["code"])
                results.append({"step": step, "result": result})
            except Exception as e:
                return {"status": "error", "step": step, "error": str(e)}
                
        return {"status": "success", "results": results}
        
    async def _run_shell_command(self, command: str) -> str:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode() if process.returncode == 0 else stderr.decode()
        
    async def _run_python_code(self, code: str) -> Any:
        namespace = {}
        exec(code, namespace)
        return namespace.get('result', None)
        
    def create_task(self, name: str, steps: List[Dict]) -> bool:
        """Create a new automated task"""
        if name in self.task_configs["tasks"]:
            return False
            
        self.task_configs["tasks"][name] = {"steps": steps}
        self._save_task_configs()
        return True
        
    def _save_task_configs(self):
        with open(self.workspace_path / 'canopus.tasks.yaml', 'w') as f:
            yaml.safe_dump(self.task_configs, f)
