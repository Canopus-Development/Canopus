import sys
import traceback
import logging
import inspect
from typing import Dict, List, Optional
from pathlib import Path
import stack_data

class DebugAssistant:
    def __init__(self):
        self.logger = logging.getLogger('canopus.debug')
        self.error_history = []
        self.fixes_cache = {}
        
    def analyze_exception(self, exc: Exception, code_context: str = None) -> Dict:
        """Analyze exception and suggest fixes"""
        analysis = {
            'type': type(exc).__name__,
            'message': str(exc),
            'traceback': self._format_traceback(exc),
            'context': self._get_error_context(exc),
            'suggestions': self._generate_fix_suggestions(exc),
            'similar_issues': self._find_similar_issues(exc)
        }
        
        self.error_history.append(analysis)
        return analysis
        
    def _format_traceback(self, exc: Exception) -> List[Dict]:
        """Format traceback into structured data"""
        frames = []
        for frame in stack_data.StackData(exc.__traceback__):
            frames.append({
                'filename': frame.filename,
                'lineno': frame.lineno,
                'function': frame.function,
                'code_context': frame.lines[frame.index].strip(),
                'variables': self._get_frame_variables(frame.frame)
            })
        return frames
        
    def _get_frame_variables(self, frame) -> Dict:
        """Extract relevant variables from frame"""
        return {
            name: str(value)
            for name, value in frame.f_locals.items()
            if not name.startswith('_')
        }
        
    def _generate_fix_suggestions(self, exc: Exception) -> List[str]:
        """Generate potential fix suggestions"""
        suggestions = []
        error_type = type(exc).__name__
        
        if error_type in self.fixes_cache:
            return self.fixes_cache[error_type]
            
        if isinstance(exc, ImportError):
            suggestions.append("Check if required package is installed")
            suggestions.append("Verify import statement path")
        elif isinstance(exc, TypeError):
            suggestions.append("Verify argument types")
            suggestions.append("Check method signature")
            
        self.fixes_cache[error_type] = suggestions
        return suggestions
