#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Centralized debug logging utility for BehaviourLinker application

Provides consistent debug logging across all modules with easy enable/disable.
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
from typing import Optional


class DebugLogger:
    """Centralized debug logging utility with easy enable/disable"""
    
    def __init__(self, enabled: bool = False):
        """
        Initialize the debug logger
        
        Args:
            enabled: Whether debug logging is enabled
        """
        self.enabled = enabled
        
        # Can be controlled via environment variable
        if os.getenv('BEHAVIOUR_LINKER_DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
            self.enabled = True
    
    def debug_print(self, category: str, message: str, context: str = ""):
        """
        Print debug message with consistent formatting
        
        Args:
            category: Debug category (e.g., "STATE", "EQUATION", "POPULATE")
            message: Debug message
            context: Additional context (optional)
        """
        if not self.enabled:
            return
            
        debug_msg = f"=== {category} DEBUG: {message}"
        if context:
            debug_msg += f" ({context})"
        print(debug_msg)
    
    def is_enabled(self) -> bool:
        """Check if debug logging is enabled"""
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        """Enable or disable debug logging"""
        self.enabled = enabled


# Global debug logger instance
_global_debug_logger = None


def get_debug_logger(enabled: Optional[bool] = None) -> DebugLogger:
    """
    Get the global debug logger instance
    
    Args:
        enabled: Override enabled status (optional)
    
    Returns:
        DebugLogger instance
    """
    global _global_debug_logger
    if _global_debug_logger is None:
        _global_debug_logger = DebugLogger(enabled or False)
    
    if enabled is not None:
        _global_debug_logger.set_enabled(enabled)
    
    return _global_debug_logger


def debug_print(category: str, message: str, context: str = ""):
    """
    Convenience function for debug printing using the global logger
    
    Args:
        category: Debug category (e.g., "STATE", "EQUATION", "POPULATE")
        message: Debug message
        context: Additional context (optional)
    """
    get_debug_logger().debug_print(category, message, context)


# Common debug categories for consistency
class DebugCategories:
    """Standard debug categories"""
    STATE = "STATE"
    EQUATION = "EQUATION"
    POPULATE = "POPULATE"
    CONNECTION = "CONNECTION"
    FRONTEND = "FRONTEND"
    BEHAVIOR = "BEHAVIOR"
    LEFT_CLICK = "LEFT-CLICK"


# Backward compatibility - provide direct functions for common patterns
def state_debug(message: str, context: str = ""):
    """State-specific debug logging"""
    debug_print(DebugCategories.STATE, message, context)


def equation_debug(message: str, context: str = ""):
    """Equation-specific debug logging"""
    debug_print(DebugCategories.EQUATION, message, context)


def populate_debug(message: str, context: str = ""):
    """Populate-specific debug logging"""
    debug_print(DebugCategories.POPULATE, message, context)
