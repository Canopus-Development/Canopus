import pytest
import coverage
from pathlib import Path
from typing import Dict, List, Optional
import asyncio
import os
from datetime import datetime

class TestRunner:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.coverage = coverage.Coverage()
        
    async def run_tests(self, path: Optional[str] = None) -> Dict:
        """Run tests with coverage"""
        test_path = path or str(self.workspace_path / 'tests')
        self.coverage.start()
        
        try:
            pytest_output = await self._run_pytest(test_path)
            self.coverage.stop()
            self.coverage.save()
            
            coverage_data = self.coverage.report(include=f"{self.workspace_path}/**/*.py")
            
            return {
                "status": "complete",
                "output": pytest_output,
                "coverage": coverage_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
            
    async def _run_pytest(self, path: str) -> str:
        """Run pytest asynchronously"""
        process = await asyncio.create_subprocess_exec(
            'pytest',
            path,
            '-v',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode() if process.returncode == 0 else stderr.decode()
        
    def get_test_summary(self) -> Dict:
        """Get summary of test results"""
        if hasattr(self.coverage, '_data'):
            return {
                "total_files": len(self.coverage._data.measured_files()),
                "coverage": self.coverage.report(show_missing=False),
                "uncovered_lines": self.coverage.get_uncovered_lines()
            }
        return {"status": "No tests run yet"}
