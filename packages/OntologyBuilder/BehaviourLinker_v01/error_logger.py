#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Centralized error logging utility for BehaviourLinker application

Provides consistent error logging across all modules with optional file logging.
===============================================================================
"""

__project__ = "ProcessModeller Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2026. 01. 23"
__license__ = "GPL planned -- until further notice for internal Bio4Fuel & MarketPlace use only"
__version__ = "12"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys
from datetime import datetime
from typing import Optional


class ErrorLogger:
    """Centralized error logging utility"""
    
    def __init__(self, log_to_file: bool = False, log_file_path: Optional[str] = None):
        """
        Initialize the error logger
        
        Args:
            log_to_file: Whether to also log errors to a file
            log_file_path: Custom path for log file (optional)
        """
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path or os.path.join(
            os.path.dirname(__file__), 'error_log.txt'
        )
        
        # Initialize log file if needed
        if self.log_to_file:
            self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Initialize the log file with header"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"BehaviourLinker Error Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            print(f"Warning: Could not initialize log file: {e}")
    
    def log_error(self, method_name: str, error: Exception, context: str = ""):
        """
        Log error with method name and context for debugging
        
        Args:
            method_name: Name of the method where error occurred
            error: The exception that occurred
            context: Additional context information (optional)
        """
        error_msg = f"ERROR in {method_name}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        # Always print to console for debugging
        print(error_msg)
        
        # Optionally log to file
        if self.log_to_file:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] {error_msg}\n")
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")


# Global logger instance
_global_logger = None


def get_logger(log_to_file: bool = False, log_file_path: Optional[str] = None) -> ErrorLogger:
    """
    Get the global error logger instance
    
    Args:
        log_to_file: Whether to also log errors to a file
        log_file_path: Custom path for log file (optional)
    
    Returns:
        ErrorLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = ErrorLogger(log_to_file, log_file_path)
    return _global_logger


def log_error(method_name: str, error: Exception, context: str = ""):
    """
    Convenience function for logging errors using the global logger
    
    Args:
        method_name: Name of the method where error occurred
        error: The exception that occurred
        context: Additional context information (optional)
    """
    get_logger().log_error(method_name, error, context)


# Backward compatibility - provide the function directly for existing code
def log_error(method_name: str, error: Exception, context: str = ""):
    """
    Log error with method name and context for debugging
    
    This function provides backward compatibility with existing code that imports
    log_error directly. It uses the global logger instance.
    
    Args:
        method_name: Name of the method where error occurred
        error: The exception that occurred
        context: Additional context information (optional)
    """
    get_logger().log_error(method_name, error, context)
