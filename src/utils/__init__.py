"""Utility modules for Evolving-sun system."""

from .logging_utils import (
    StructuredLogger,
    get_logger,
    log_evolution_event,
    log_benchmark_event,
    log_security_event,
    log_agent_event
)

from .secure_logging import (
    watermark_log,
    append_watermarked_log,
    verify_log_integrity
)

__all__ = [
    'StructuredLogger',
    'get_logger',
    'log_evolution_event',
    'log_benchmark_event',
    'log_security_event',
    'log_agent_event',
    'watermark_log',
    'append_watermarked_log',
    'verify_log_integrity'
]
