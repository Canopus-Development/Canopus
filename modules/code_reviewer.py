import ast
import radon.metrics as metrics
from typing import Dict, List
from pathlib import Path
import pylint.lint
from io import StringIO
import sys

class CodeReviewer:
    def __init__(self):
        self.metrics_cache = {}
        self.issues_cache = {}
        
    def review_file(self, file_path: str) -> Dict:
        """Perform comprehensive code review"""
        with open(file_path, 'r') as f:
            code = f.read()
            
        return {
            'metrics': self._analyze_metrics(code),
            'issues': self._find_issues(code),
            'suggestions': self._generate_suggestions(code),
            'best_practices': self._check_best_practices(code)
        }
        
    def _analyze_metrics(self, code: str) -> Dict:
        """Analyze code metrics"""
        try:
            return {
                'cyclomatic_complexity': metrics.cyclomatic_complexity(code),
                'maintainability_index': metrics.mi_visit(code),
                'loc': len(code.splitlines()),
                'halstead_metrics': metrics.h_visit(code)
            }
        except Exception as e:
            return {'error': str(e)}
            
    def _find_issues(self, code: str) -> List[Dict]:
        """Find code issues using pylint"""
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        try:
            pylint.lint.Run(['-'], do_exit=False)
        finally:
            sys.stdout = old_stdout
            
        return self._parse_pylint_output(redirected_output.getvalue())
        
    def _generate_suggestions(self, code: str) -> List[Dict]:
        """Generate improvement suggestions"""
        suggestions = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:
                    suggestions.append({
                        'type': 'refactor',
                        'message': f'Function {node.name} has too many parameters',
                        'line': node.lineno
                    })
                    
        return suggestions
        
    def _check_best_practices(self, code: str) -> List[Dict]:
        """Check for Python best practices"""
        practices = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                if not any(isinstance(handler.type, ast.Name) for handler in node.handlers):
                    practices.append({
                        'type': 'warning',
                        'message': 'Bare except clause used',
                        'line': node.lineno
                    })
                    
        return practices
