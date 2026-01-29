"""
Decision Engine Data Models

Data models for system modes, advisory states, and decision results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from abhedya.tracking.models import Track
from abhedya.analysis.threat_assessment.models import ThreatAssessmentResult


class SystemMode(str, Enum):
    """
    System operational modes.
    
    These modes define the advisory state of the system.
    They do NOT execute any actions.
    """
    ADVISORY_RECOMMENDATION = "ADVISORY_RECOMMENDATION"  # Normal advisory operation
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"  # Human review required
    MONITORING_ONLY = "MONITORING_ONLY"                  # Monitoring only, no recommendations
    DEGRADED_SAFE = "DEGRADED_SAFE"                      # Degraded but safe mode


class HumanReviewState(str, Enum):
    """Human review state requirements."""
    REVIEW_REQUIRED = "REVIEW_REQUIRED"      # Human review required
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"  # Review in progress
    REVIEW_COMPLETE = "REVIEW_COMPLETE"      # Review complete
    NO_REVIEW_NEEDED = "NO_REVIEW_NEEDED"    # No review needed


@dataclass
class AdvisorySystemState:
    """
    Advisory system state output.
    
    IMPORTANT: This is an ADVISORY STATE ONLY.
    It does NOT contain executable commands.
    It only describes the advisory state of the system.
    """
    state_id: str
    timestamp: datetime
    system_mode: SystemMode
    human_review_state: HumanReviewState
    active_tracks_count: int
    pending_recommendations_count: int
    default_action: str = "NO_ACTION"  # Always NO_ACTION
    advisory_summary: str = ""  # Summary of advisory outputs
    ethical_constraints_active: bool = True
    protected_airspace_violations: List[str] = field(default_factory=list)
    civilian_airspace_violations: List[str] = field(default_factory=list)
    uncertainty_flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate system state."""
        if self.default_action != "NO_ACTION":
            raise ValueError("Default action must always be NO_ACTION")


@dataclass
class DecisionResult:
    """
    Decision engine result.
    
    IMPORTANT: This is an ADVISORY RESULT ONLY.
    It does NOT contain executable commands.
    It only describes advisory system states and recommendations.
    """
    result_id: str
    timestamp: datetime
    system_state: AdvisorySystemState
    aggregated_recommendations: List[Dict[str, Any]]  # Advisory recommendations only
    ethical_constraints_status: Dict[str, bool]
    airspace_compliance_status: Dict[str, bool]
    human_review_required: bool
    uncertainty_level: float  # [0.0, 1.0]
    fail_safe_activated: bool
    reasoning: str
    advisory_statement: str = "ADVISORY STATE ONLY - No executable commands. All outputs require human interpretation and approval."

