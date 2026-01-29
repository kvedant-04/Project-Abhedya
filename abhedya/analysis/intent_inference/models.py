"""
Intent Inference Data Models

Data models for intent probability assessment results.
All outputs are ADVISORY ONLY - no action recommendations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class IntentCategory(str, Enum):
    """
    Intent categories for probabilistic assessment.
    
    These categories are ADVISORY ONLY and do NOT map to any actions.
    """
    TRANSIT = "transit"
    SURVEILLANCE = "surveillance"
    HOSTILE = "hostile"


@dataclass
class IntentProbabilityResult:
    """
    Intent probability assessment result.
    
    IMPORTANT: This is an ADVISORY ASSESSMENT ONLY.
    It does NOT recommend any actions.
    Intent probabilities do NOT map to any actions.
    
    Probabilities must sum to ≤ 100% (1.0).
    """
    assessment_id: str
    timestamp: datetime
    track_id: Optional[str] = None
    
    # Intent probabilities [0.0, 1.0]
    transit_probability: float = 0.0
    surveillance_probability: float = 0.0
    hostile_probability: float = 0.0
    
    # Overall confidence in assessment [0.0, 1.0]
    intent_confidence: float = 0.0
    
    # Human-readable reasoning
    reasoning: List[str] = field(default_factory=list)
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Training mode flag
    is_training_mode: bool = False
    
    # Advisory-only statement
    advisory_statement: str = field(
        default="ADVISORY ASSESSMENT ONLY - No action recommendations. "
                "Intent probabilities do not map to any actions."
    )
    
    def __post_init__(self):
        """Validate intent probability result."""
        # Validate probabilities are in [0.0, 1.0]
        if not 0.0 <= self.transit_probability <= 1.0:
            raise ValueError(
                f"Transit probability must be in [0.0, 1.0], got {self.transit_probability}"
            )
        if not 0.0 <= self.surveillance_probability <= 1.0:
            raise ValueError(
                f"Surveillance probability must be in [0.0, 1.0], "
                f"got {self.surveillance_probability}"
            )
        if not 0.0 <= self.hostile_probability <= 1.0:
            raise ValueError(
                f"Hostile probability must be in [0.0, 1.0], got {self.hostile_probability}"
            )
        
        # Validate probabilities sum to ≤ 1.0
        total_probability = (
            self.transit_probability +
            self.surveillance_probability +
            self.hostile_probability
        )
        if total_probability > 1.0 + 1e-6:  # Allow small floating point errors
            raise ValueError(
                f"Intent probabilities must sum to ≤ 1.0, got {total_probability}"
            )
        
        # Validate confidence
        if not 0.0 <= self.intent_confidence <= 1.0:
            raise ValueError(
                f"Intent confidence must be in [0.0, 1.0], got {self.intent_confidence}"
            )
    
    def get_intent_probabilities_dict(self) -> Dict[str, float]:
        """
        Get intent probabilities as dictionary.
        
        Returns:
            Dictionary mapping intent categories to probabilities
        """
        return {
            IntentCategory.TRANSIT.value: self.transit_probability,
            IntentCategory.SURVEILLANCE.value: self.surveillance_probability,
            IntentCategory.HOSTILE.value: self.hostile_probability
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "assessment_id": self.assessment_id,
            "timestamp": self.timestamp.isoformat(),
            "track_id": self.track_id,
            "intent_probabilities": self.get_intent_probabilities_dict(),
            "intent_confidence": self.intent_confidence,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
            "is_training_mode": self.is_training_mode,
            "advisory_statement": self.advisory_statement
        }

