"""
Logging utilities for structured logging across the Evolving-sun system.

This module provides standardized logging functionality for different
subsystems: evolution, benchmarks, security, and agent-activity.
"""

import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# Global logger cache to reuse logger instances
_logger_cache = {}
_logger_cache_lock = threading.Lock()


class StructuredLogger:
    """Structured logger with support for different log categories."""
    
    LOG_CATEGORIES = ["evolution", "benchmarks", "security", "agent-activity"]
    
    def __init__(self, category: str, log_dir: Optional[Path] = None):
        """
        Initialize structured logger.
        
        Args:
            category: Log category (evolution, benchmarks, security, agent-activity)
            log_dir: Base directory for logs (defaults to logs/ in repo root)
        """
        if category not in self.LOG_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Must be one of: {self.LOG_CATEGORIES}"
            )
        
        self.category = category
        self._file_lock = threading.Lock()
        
        if log_dir is None:
            # Assume we're in src/utils and go up to repo root
            current_dir = Path(__file__).parent
            repo_root = current_dir.parent.parent
            self.log_dir = repo_root / "logs" / category
        else:
            self.log_dir = Path(log_dir) / category
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up the logger with appropriate handlers."""
        self.logger = logging.getLogger(f"evolving_sun.{self.category}")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
            
            # File handler
            log_file = self.log_dir / f"{self.category}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log info message with optional metadata."""
        if metadata:
            message = f"{message} | Metadata: {json.dumps(metadata)}"
        self.logger.info(message)
    
    def warning(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log warning message with optional metadata."""
        if metadata:
            message = f"{message} | Metadata: {json.dumps(metadata)}"
        self.logger.warning(message)
    
    def error(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log error message with optional metadata."""
        if metadata:
            message = f"{message} | Metadata: {json.dumps(metadata)}"
        self.logger.error(message)
    
    def debug(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log debug message with optional metadata."""
        if metadata:
            message = f"{message} | Metadata: {json.dumps(metadata)}"
        self.logger.debug(message)
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log a structured event as JSON.
        
        Args:
            event_type: Type of event (e.g., "benchmark_complete", "security_scan")
            data: Event data dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "category": self.category,
            "event_type": event_type,
            "data": data
        }
        
        # Write to JSON log file with thread safety
        json_log_file = self.log_dir / f"events_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Use file lock to ensure thread-safe writes
        with self._file_lock:
            with open(json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        
        self.info(f"Event logged: {event_type}", metadata=data)


# Convenience functions for quick logging
def get_logger(category: str) -> StructuredLogger:
    """
    Get a cached structured logger for the specified category.
    
    This function maintains a cache of logger instances to avoid
    creating duplicate loggers with duplicate handlers.
    """
    with _logger_cache_lock:
        if category not in _logger_cache:
            _logger_cache[category] = StructuredLogger(category)
        return _logger_cache[category]


def log_evolution_event(event_type: str, data: Dict[str, Any]):
    """Log an evolution event."""
    logger = get_logger("evolution")
    logger.log_event(event_type, data)


def log_benchmark_event(event_type: str, data: Dict[str, Any]):
    """Log a benchmark event."""
    logger = get_logger("benchmarks")
    logger.log_event(event_type, data)


def log_security_event(event_type: str, data: Dict[str, Any]):
    """Log a security event."""
    logger = get_logger("security")
    logger.log_event(event_type, data)


def log_agent_event(event_type: str, data: Dict[str, Any]):
    """Log an agent activity event."""
    logger = get_logger("agent-activity")
    logger.log_event(event_type, data)
