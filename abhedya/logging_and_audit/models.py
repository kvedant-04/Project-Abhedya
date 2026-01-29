"""
Logging and Audit Data Models

Data models for log entries and audit records.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import json


class LogModule(str, Enum):
    """Module names for logging."""
    EARLY_WARNING = "early_warning"
    EW_ANALYSIS = "ew_analysis"
    CYBERSECURITY = "cybersecurity"
    DASHBOARD = "dashboard"
    THREAT_ASSESSMENT = "threat_assessment"
    DECISION_ENGINE = "decision_engine"
    TRACKING = "tracking"
    TRAJECTORY_ANALYSIS = "trajectory_analysis"
    INTENT_INFERENCE = "intent_inference"


class AdvisoryState(str, Enum):
    """Advisory states for logging."""
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    MONITORING_ONLY = "MONITORING_ONLY"
    NO_ACTION = "NO_ACTION"
    SUSPICIOUS = "SUSPICIOUS"
    ALERT = "ALERT"
    ANOMALOUS = "ANOMALOUS"


class EventType(str, Enum):
    """Event types for system events."""
    ADVISORY_STATE_CHANGE = "advisory_state_change"
    HUMAN_ACKNOWLEDGMENT = "human_acknowledgment"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGE = "configuration_change"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class AdvisoryLogEntry:
    """
    Advisory log entry.
    
    Immutable record of an advisory output from a system module.
    """
    module_name: str
    advisory_state: str
    confidence: float
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class AcknowledgmentLogEntry:
    """
    Human acknowledgment log entry.
    
    Immutable record of a human acknowledgment action.
    """
    item_id: str
    item_type: str
    acknowledged_by: Optional[str] = None
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class SystemEventLogEntry:
    """
    System event log entry.
    
    Immutable record of a system event.
    """
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class LogQuery:
    """
    Query parameters for log retrieval.
    """
    module_name: Optional[str] = None
    advisory_state: Optional[str] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.module_name:
            result['module_name'] = self.module_name
        if self.advisory_state:
            result['advisory_state'] = self.advisory_state
        if self.start_timestamp:
            result['start_timestamp'] = self.start_timestamp.isoformat()
        if self.end_timestamp:
            result['end_timestamp'] = self.end_timestamp.isoformat()
        if self.limit:
            result['limit'] = self.limit
        if self.offset:
            result['offset'] = self.offset
        return result

