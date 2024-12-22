import ast
import inspect
from typing import Dict, List
from pathlib import Path
import docstring_parser
import mdutils

class DocGenerator:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def generate_docs(self, module_path: str) -> Dict:
        """Generate documentation for a Python module"""
        module_file = self.workspace_path / module_path
        with open(module_file, 'r') as f:
            code = f.read()
            
        tree = ast.parse(code)
        docs = {
            'classes': self._document_classes(tree),
            'functions': self._document_functions(tree),
            'module_doc': ast.get_docstring(tree)
        }
        
        self._generate_markdown(docs, module_path)
        return docs
        
    def _document_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract documentation for classes"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': self._document_methods(node),
                    'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
                })
        return classes
        
    def _document_methods(self, class_node: ast.ClassDef) -> List[Dict]:
        """Extract documentation for class methods"""
        methods = []
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                methods.append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'params': self._get_parameters(node),
                    'returns': self._get_return_type(node)
                })
        return methods
        
    def _generate_markdown(self, docs: Dict, module_path: str):
        """Generate markdown documentation"""
        mdFile = mdutils.MdUtils(file_name=f'docs/{Path(module_path).stem}.md')
        
        # Add module documentation
        mdFile.new_header(level=1, title=f"Module: {Path(module_path).stem}")
        if docs['module_doc']:
            mdFile.new_paragraph(docs['module_doc'])
            
        # Add classes
        for class_doc in docs['classes']:
            mdFile.new_header(level=2, title=f"Class: {class_doc['name']}")
            if class_doc['docstring']:
                mdFile.new_paragraph(class_doc['docstring'])
                
        mdFile.create_md_file()
