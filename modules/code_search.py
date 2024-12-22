from pathlib import Path
from typing import Dict, List, Optional
import ast
import re
from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

@dataclass
class SearchResult:
    file: Path
    line: int
    snippet: str
    relevance: float
    context: str

class CodeSearch:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.index = {}
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        self._build_index()
        
    def _build_index(self):
        """Build searchable index of code"""
        for file_path in self.workspace_path.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.index[file_path] = {
                        'content': content,
                        'embeddings': self._generate_embeddings(content),
                        'ast': ast.parse(content)
                    }
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
                
    def _generate_embeddings(self, code: str) -> np.ndarray:
        """Generate embeddings for code using CodeBERT"""
        inputs = self.tokenizer(code, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()
        
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Search for code using semantic understanding"""
        query_embedding = self._generate_embeddings(query)
        results = []
        
        for file_path, data in self.index.items():
            similarity = self._compute_similarity(query_embedding, data['embeddings'])
            if similarity > 0.7:  # Relevance threshold
                results.extend(self._find_matches(file_path, data, query, similarity))
                
        return sorted(results, key=lambda x: x.relevance, reverse=True)[:limit]
        
    def _find_matches(self, file_path: Path, data: Dict, query: str, 
                     base_similarity: float) -> List[SearchResult]:
        """Find specific matches within a file"""
        matches = []
        lines = data['content'].split('\n')
        
        for i, line in enumerate(lines, 1):
            if self._is_relevant(line, query):
                context = self._get_context(lines, i)
                matches.append(SearchResult(
                    file=file_path,
                    line=i,
                    snippet=line.strip(),
                    relevance=base_similarity,
                    context=context
                ))
                
        return matches
        
    def _get_context(self, lines: List[str], line_num: int, context_size: int = 2) -> str:
        """Get surrounding context for a line of code"""
        start = max(0, line_num - context_size - 1)
        end = min(len(lines), line_num + context_size)
        return '\n'.join(lines[start:end])
