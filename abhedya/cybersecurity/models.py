"""
Cybersecurity & Intrusion Detection Data Models

Data models for system events, access patterns, and cybersecurity results.
All outputs are advisory only - alert and visibility only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class CybersecurityState(str, Enum):
    """
    Cybersecurity state (ADVISORY ONLY).
    
    These states are informational and do NOT trigger automated actions.
    """
    NORMAL = "NORMAL"           # Normal system behavior
    SUSPICIOUS = "SUSPICIOUS"    # Suspicious activity detected
    ALERT = "ALERT"              # Alert-level activity detected


class EventType(str, Enum):
    """System event types."""
    CONFIG_ACCESS = "CONFIG_ACCESS"
    MODULE_ACCESS = "MODULE_ACCESS"
    DATA_ACCESS = "DATA_ACCESS"
    SYSTEM_ACCESS = "SYSTEM_ACCESS"
    UNKNOWN = "UNKNOWN"


class AccessType(str, Enum):
    """Access type."""
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    MODIFY = "MODIFY"


@dataclass
class SystemEvent:
    """
    System event for monitoring.
    
    Represents a single system event (access, operation, etc.).
    """
    event_id: str
    timestamp: datetime
    event_type: EventType
    access_type: AccessType
    subsystem: str  # Affected subsystem
    resource: str  # Resource accessed
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessPattern:
    """
    Access pattern statistics.
    
    Statistical representation of access patterns.
    """
    subsystem: str
    access_count: int
    unique_resources: int
    access_rate: float  # Accesses per second
    average_interval: float  # Average time between accesses (seconds)
    time_window_seconds: float
    pattern_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrityCheckResult:
    """
    Integrity check result.
    
    Result of integrity monitoring checks.
    """
    check_id: str
    timestamp: datetime
    subsystem: str
    is_consistent: bool
    unexpected_changes: List[str]
    suspicious_sequences: List[str]
    configuration_checks: Dict[str, bool]
    confidence: float  # [0.0, 1.0]
    reasoning: List[str]


@dataclass
class AnomalyDetectionResult:
    """
    Anomaly detection result.
    
    Detected anomalies in system behavior.
    """
    is_anomalous: bool
    anomaly_score: float  # [0.0, 1.0]
    statistical_deviation: float  # Z-score deviation
    sequence_irregularities: List[str]
    rate_limit_violations: List[str]
    suspected_pattern: str
    reasoning: List[str]
    confidence: float  # [0.0, 1.0]


@dataclass
class CybersecurityResult:
    """
    Cybersecurity analysis result.
    
    IMPORTANT: This is ADVISORY ONLY.
    It does NOT provide:
    - Automated blocking
    - Shutdown logic
    - Retaliation
    - Automated responses
    
    It only provides alert and visibility.
    """
    result_id: str
    timestamp: datetime
    cybersecurity_state: CybersecurityState
    confidence: float  # [0.0, 1.0]
    uncertainty: float  # [0.0, 1.0]
    affected_subsystem: Optional[str]
    advisory_message: str
    access_patterns: List[AccessPattern]
    integrity_check: Optional[IntegrityCheckResult]
    anomaly_detection: Optional[AnomalyDetectionResult]
    reasoning: List[str]  # Human-readable reasoning
    data_quality_flags: List[str]
    advisory_statement: str = "ADVISORY ONLY - Alert and visibility only. No automated blocking. No shutdown logic. No retaliation. Human operator review required."

