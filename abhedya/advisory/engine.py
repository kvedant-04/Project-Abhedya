"""
Advisory decision-support engine.

Generates probabilistic, advisory recommendations based on threat
assessments. All recommendations are informational only and require
mandatory human approval.
"""

import uuid
from typing import Optional

from abhedya.core.interfaces import IAdvisoryEngine
from abhedya.core.models import (
    Track,
    SystemState,
    AdvisoryRecommendation,
    AdvisoryAction,
    ThreatLevel,
    EntityType
)
from abhedya.core.constants import (
    MIN_ADVISORY_CONFIDENCE,
    HIGH_CONFIDENCE_THRESHOLD,
    MANDATORY_HUMAN_APPROVAL
)


class AdvisoryEngine(IAdvisoryEngine):
    """
    Advisory decision-support engine.
    
    IMPORTANT: This engine generates ADVISORY recommendations only.
    It does not execute, authorize, or trigger any actions.
    All recommendations require mandatory human approval.
    """
    
    def __init__(
        self,
        min_confidence: float = MIN_ADVISORY_CONFIDENCE,
        enable_probabilistic_reasoning: bool = True
    ):
        """
        Initialize advisory engine.
        
        Args:
            min_confidence: Minimum confidence for generating recommendations
            enable_probabilistic_reasoning: Enable probabilistic assessment
        """
        self.min_confidence = min_confidence
        self.enable_probabilistic_reasoning = enable_probabilistic_reasoning
    
    def generate_recommendation(
        self,
        track: Track,
        system_state: SystemState
    ) -> Optional[AdvisoryRecommendation]:
        """
        Generate advisory recommendation for a track.
        
        IMPORTANT: This is advisory only. No actions are executed.
        
        Args:
            track: Track to generate recommendation for
            system_state: Current system state
            
        Returns:
            Advisory recommendation or None if no recommendation
        """
        # Check if track meets minimum confidence threshold
        if track.confidence < self.min_confidence:
            return None
        
        # Determine recommended action based on threat level and entity type
        action = self._determine_action(track, system_state)
        
        if action == AdvisoryAction.NO_ACTION:
            # Don't generate recommendation for NO_ACTION
            return None
        
        # Calculate recommendation confidence
        confidence = self._calculate_recommendation_confidence(track)
        
        # Calculate probability assessment
        probability = self._calculate_probability(track)
        
        # Generate reasoning explanation
        reasoning = self._generate_reasoning(track, action, probability)
        
        # Create recommendation
        recommendation = AdvisoryRecommendation(
            recommendation_id=str(uuid.uuid4()),
            track_id=track.track_id,
            action=action,
            threat_level=track.threat_level,
            confidence=confidence,
            reasoning=reasoning,
            probability=probability,
            requires_human_approval=MANDATORY_HUMAN_APPROVAL,  # Always True
            metadata={
                "entity_type": track.entity_type.value,
                "track_confidence": track.confidence,
                "system_mode": system_state.system_mode
            }
        )
        
        return recommendation
    
    def _determine_action(
        self,
        track: Track,
        system_state: SystemState
    ) -> AdvisoryAction:
        """
        Determine recommended advisory action.
        
        Returns:
            Recommended action (advisory only)
        """
        # Fail-safe: If human operator not present, recommend monitoring only
        if not system_state.human_operator_present:
            return AdvisoryAction.MONITOR
        
        # Decision logic based on threat level and entity type
        if track.entity_type == EntityType.FRIENDLY:
            return AdvisoryAction.TRACK  # Track friendly entities
        
        if track.threat_level == ThreatLevel.CRITICAL:
            return AdvisoryAction.ALERT  # Alert for critical threats
        
        if track.threat_level == ThreatLevel.HIGH:
            return AdvisoryAction.INVESTIGATE  # Investigate high threats
        
        if track.threat_level == ThreatLevel.MEDIUM:
            return AdvisoryAction.INVESTIGATE  # Investigate medium threats
        
        if track.threat_level == ThreatLevel.LOW:
            return AdvisoryAction.MONITOR  # Monitor low threats
        
        # Default: Monitor
        return AdvisoryAction.MONITOR
    
    def _calculate_recommendation_confidence(self, track: Track) -> float:
        """
        Calculate confidence in the recommendation.
        
        Returns:
            Confidence value (0-1)
        """
        # Base confidence from track confidence
        confidence = track.confidence * 0.6
        
        # Boost confidence based on threat level
        threat_boost = {
            ThreatLevel.CRITICAL: 0.3,
            ThreatLevel.HIGH: 0.2,
            ThreatLevel.MEDIUM: 0.1,
            ThreatLevel.LOW: 0.05,
            ThreatLevel.NONE: 0.0
        }
        confidence += threat_boost.get(track.threat_level, 0.0)
        
        # Boost confidence if entity type is well-classified
        if track.entity_type != EntityType.UNKNOWN:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_probability(self, track: Track) -> float:
        """
        Calculate probability assessment for the threat.
        
        Returns:
            Probability value (0-1)
        """
        if not self.enable_probabilistic_reasoning:
            # Simple mapping from threat level
            probability_map = {
                ThreatLevel.CRITICAL: 0.95,
                ThreatLevel.HIGH: 0.80,
                ThreatLevel.MEDIUM: 0.60,
                ThreatLevel.LOW: 0.40,
                ThreatLevel.NONE: 0.10
            }
            return probability_map.get(track.threat_level, 0.5)
        
        # Probabilistic reasoning
        probability = 0.0
        
        # Base probability from threat level
        threat_prob = {
            ThreatLevel.CRITICAL: 0.7,
            ThreatLevel.HIGH: 0.5,
            ThreatLevel.MEDIUM: 0.3,
            ThreatLevel.LOW: 0.15,
            ThreatLevel.NONE: 0.05
        }
        probability += threat_prob.get(track.threat_level, 0.3)
        
        # Adjust based on entity type
        if track.entity_type == EntityType.HOSTILE:
            probability += 0.2
        elif track.entity_type == EntityType.FRIENDLY:
            probability *= 0.1  # Very low probability for friendly
        elif track.entity_type == EntityType.UNKNOWN:
            probability += 0.1
        
        # Adjust based on track confidence
        probability *= (0.5 + track.confidence * 0.5)
        
        return min(1.0, max(0.0, probability))
    
    def _generate_reasoning(
        self,
        track: Track,
        action: AdvisoryAction,
        probability: float
    ) -> str:
        """
        Generate human-readable reasoning for the recommendation.
        
        Args:
            track: Track being assessed
            action: Recommended action
            probability: Probability assessment
            
        Returns:
            Reasoning explanation
        """
        reasoning_parts = []
        
        reasoning_parts.append(f"Recommended Action: {action.value}")
        reasoning_parts.append("")
        reasoning_parts.append("Assessment Summary:")
        reasoning_parts.append(f"  - Entity Type: {track.entity_type.value}")
        reasoning_parts.append(f"  - Threat Level: {track.threat_level.value}")
        reasoning_parts.append(f"  - Threat Probability: {probability:.1%}")
        reasoning_parts.append(f"  - Track Confidence: {track.confidence:.1%}")
        reasoning_parts.append("")
        
        # Action-specific reasoning
        if action == AdvisoryAction.ALERT:
            reasoning_parts.append(
                "Reasoning: Critical threat level detected. "
                "Immediate human attention required."
            )
        elif action == AdvisoryAction.INVESTIGATE:
            reasoning_parts.append(
                "Reasoning: Elevated threat level. "
                "Further investigation recommended."
            )
        elif action == AdvisoryAction.MONITOR:
            reasoning_parts.append(
                "Reasoning: Low to moderate threat level. "
                "Continuous monitoring recommended."
            )
        elif action == AdvisoryAction.TRACK:
            reasoning_parts.append(
                "Reasoning: Friendly or neutral entity. "
                "Standard tracking recommended."
            )
        
        reasoning_parts.append("")
        reasoning_parts.append(
            "IMPORTANT: This is an ADVISORY recommendation only. "
            "No actions are executed automatically. "
            "Human approval required for any operational decisions."
        )
        
        return "\n".join(reasoning_parts)
    
    def explain_recommendation(
        self,
        recommendation: AdvisoryRecommendation
    ) -> str:
        """
        Provide detailed explanation of recommendation reasoning.
        
        Args:
            recommendation: Recommendation to explain
            
        Returns:
            Detailed explanation string
        """
        explanation = recommendation.reasoning
        explanation += "\n\n"
        explanation += "Detailed Analysis:\n"
        explanation += f"  - Recommendation ID: {recommendation.recommendation_id}\n"
        explanation += f"  - Generated at: {recommendation.timestamp}\n"
        explanation += f"  - Confidence: {recommendation.confidence:.1%}\n"
        explanation += f"  - Probability: {recommendation.probability:.1%}\n"
        explanation += f"  - Human Approval Required: {recommendation.requires_human_approval}\n"
        
        if recommendation.metadata:
            explanation += "\nAdditional Context:\n"
            for key, value in recommendation.metadata.items():
                explanation += f"  - {key}: {value}\n"
        
        return explanation

