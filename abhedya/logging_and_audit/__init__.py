"""
Logging and Audit Module

Comprehensive logging and audit trail for the Abhedya Air Defense System.
Provides immutable, timestamped logs of all advisory outputs and human acknowledgments.

Features:
- Immutable logs (append-only)
- Timestamped advisory states
- Human acknowledgment tracking
- Replay support
- SQLite storage with structured JSON logs
"""

from abhedya.logging_and_audit.logger import AdvisoryLogger
from abhedya.logging_and_audit.database import AuditDatabase
from abhedya.logging_and_audit.replay import LogReplay

__all__ = [
    "AdvisoryLogger",
    "AuditDatabase",
    "LogReplay",
]

