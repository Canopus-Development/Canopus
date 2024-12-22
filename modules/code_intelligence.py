import ast
import jedi
from typing import Dict, List, Optional
from pathlib import Path

class CodeIntelligence:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.symbol_cache = {}
        self.project = jedi.Project(workspace_path)
        
    def find_references(self, symbol: str) -> List[Dict]:
        """Find all references to a symbol"""
        script = jedi.Script(project=self.project)
        references = script.get_references(symbol)
        return [{
            'path': ref.module_path,
            'line': ref.line,
            'column': ref.column,
            'description': ref.description
        } for ref in references]
        
    def get_completion(self, code: str, line: int, column: int) -> List[str]:
        """Get code completion suggestions"""
        script = jedi.Script(code, project=self.project)
        completions = script.complete(line, column)
        return [completion.name for completion in completions]
        
    def analyze_code(self, code: str) -> Dict:
        """Analyze code for potential issues"""
        try:
            tree = ast.parse(code)
            analyzer = CodeAnalyzer()
            analyzer.visit(tree)
            return analyzer.get_report()
        except SyntaxError as e:
            return {'error': str(e)}
            
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.complexity = 0
        
    def visit_FunctionDef(self, node):
        """Analyze function definitions"""
        if len(node.args.args) > 5:
            self.issues.append({
                'type': 'warning',
                'message': f'Function {node.name} has too many parameters',
                'line': node.lineno
            })
        self.generic_visit(node)
        
    def get_report(self) -> Dict:
        return {
            'issues': self.issues,
            'complexity': self.complexity
        }
