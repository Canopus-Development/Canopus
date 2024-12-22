import pkg_resources
import subprocess
from typing import Dict, List, Optional
import toml
import requests
from packaging import version
from pathlib import Path

class DependencyManager:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.pyproject_path = self.workspace_path / "pyproject.toml"
        self.requirements_path = self.workspace_path / "requirements.txt"
        
    def analyze_dependencies(self) -> Dict:
        """Analyze project dependencies"""
        installed = self._get_installed_packages()
        required = self._get_required_packages()
        outdated = self._check_outdated_packages(installed)
        
        return {
            'installed': installed,
            'required': required,
            'outdated': outdated,
            'conflicts': self._find_conflicts(installed, required),
            'security_issues': self._check_security_issues(installed)
        }
        
    def update_package(self, package_name: str) -> bool:
        """Update a specific package"""
        try:
            subprocess.run(
                ["pip", "install", "--upgrade", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
            
    def _get_installed_packages(self) -> Dict[str, str]:
        """Get all installed packages and versions"""
        return {
            pkg.key: pkg.version
            for pkg in pkg_resources.working_set
        }
        
    def _get_required_packages(self) -> Dict[str, str]:
        """Get required packages from project files"""
        required = {}
        
        if self.pyproject_path.exists():
            data = toml.load(self.pyproject_path)
            required.update(data.get('tool', {}).get('poetry', {}).get('dependencies', {}))
            
        if self.requirements_path.exists():
            with open(self.requirements_path) as f:
                for line in f:
                    if '==' in line:
                        name, ver = line.strip().split('==')
                        required[name] = ver
                        
        return required
        
    def _check_security_issues(self, packages: Dict[str, str]) -> List[Dict]:
        """Check for known security vulnerabilities"""
        issues = []
        for pkg, ver in packages.items():
            response = requests.get(
                f"https://pypi.org/pypi/{pkg}/json"
            )
            if response.status_code == 200:
                data = response.json()
                if 'vulnerabilities' in data:
                    for vuln in data['vulnerabilities']:
                        if version.parse(ver) in vuln['affected_versions']:
                            issues.append({
                                'package': pkg,
                                'version': ver,
                                'vulnerability': vuln
                            })
        return issues
