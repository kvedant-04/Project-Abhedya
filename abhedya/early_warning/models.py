"""
Early Warning System Data Models

Data models for early warning states, results, and baseline statistics.
All outputs are advisory only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class EarlyWarningState(str, Enum):
    """
    Early warning state (ADVISORY ONLY).
    
    These states are informational and do NOT map to any actions.
    """
    NORMAL = "NORMAL"           # Normal airspace behavior
    ELEVATED = "ELEVATED"        # Elevated anomaly indicators
    HIGH = "HIGH"                # High anomaly indicators


class SystemPosture(str, Enum):
    """
    Recommended system posture (INFORMATIONAL ONLY).
    
    These are advisory recommendations only - no execution.
    """
    MONITORING_ONLY = "MONITORING_ONLY"
    ENHANCED_MONITORING = "ENHANCED_MONITORING"
    ALERT_MONITORING = "ALERT_MONITORING"


@dataclass
class BaselineStatistics:
    """Statistical baseline for airspace behavior."""
    track_density_mean: float
    track_density_std: float
    velocity_mean: float
    velocity_std: float
    trajectory_deviation_mean: float
    trajectory_deviation_std: float
    confidence_decay_rate: float
    sample_count: int
    established_at: datetime
    last_updated: datetime


@dataclass
class TrendAnalysisResult:
    """Result of trend analysis."""
    rolling_mean: float
    rolling_variance: float
    ewma_value: float
    cusum_value: float
    convergence_detected: bool
    anomaly_score: float  # [0.0, 1.0]
    reasoning: List[str]


@dataclass
class EarlyWarningResult:
    """
    Early warning system result.
    
    ADVISORY ONLY - No action recommendations or execution logic.
    """
    result_id: str
    timestamp: datetime
    warning_state: EarlyWarningState
    confidence: float  # [0.0, 1.0]
    uncertainty: float  # [0.0, 1.0]
    reasoning: List[str]  # Human-readable reasoning
    recommended_posture: SystemPosture  # INFORMATIONAL ONLY
    baseline_statistics: Optional[BaselineStatistics]
    trend_analysis: Optional[TrendAnalysisResult]
    anomaly_indicators: List[str]
    data_quality_flags: List[str]
    advisory_statement: str = "ADVISORY OUTPUT ONLY - No action recommendations. Recommended posture is informational only and does not map to any actions."

