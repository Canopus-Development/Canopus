import sys
import traceback
from typing import Callable, Optional
from functools import wraps
import logging

logger = logging.getLogger('canopus')

class ErrorHandler:
    def __init__(self):
        self.error_callbacks = {}
        self.recovery_strategies = {}
        
    def register_handler(self, error_type: type, callback: Callable):
        self.error_callbacks[error_type] = callback
        
    def register_recovery(self, error_type: type, strategy: Callable):
        self.recovery_strategies[error_type] = strategy
        
    def handle_error(self, error: Exception) -> Optional[bool]:
        error_type = type(error)
        
        # Log the error
        logger.error(f"Error occurred: {str(error)}")
        logger.debug(traceback.format_exc())
        
        # Execute handler if registered
        if error_type in self.error_callbacks:
            self.error_callbacks[error_type](error)
            
        # Attempt recovery if strategy exists
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type](error)
            
        return False

def with_error_handling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler().handle_error(e)
            raise
    return wrapper
