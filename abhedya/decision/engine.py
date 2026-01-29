"""
Decision, Ethics, and Human-in-the-Loop Engine

Aggregates advisory outputs and enforces ethical and legal constraints.
CRITICAL: This engine SHALL NOT output executable commands.
It only outputs advisory system states.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from abhedya.decision.models import (
    SystemMode,
    AdvisorySystemState,
    HumanReviewState,
    DecisionResult
)
from abhedya.tracking.models import Track
from abhedya.analysis.threat_assessment.models import ThreatAssessmentResult
from abhedya.infrastructure.config.config import (
    EthicalConstraints,
    ProtectedAirspaceConfiguration,
    ConfidenceThresholds,
    UncertaintyLimits,
    FailSafeConfiguration
)


class DecisionEngine:
    """
    Decision, Ethics, and Human-in-the-Loop Engine.
    
    CRITICAL: This engine SHALL NOT output executable commands.
    It only outputs advisory system states.
    
    Responsibilities:
    - Aggregate advisory outputs
    - Enforce ethical and legal constraints
    - Enforce protected and civilian airspace rules
    - Require explicit human review states
    - Enforce NO_ACTION default under uncertainty
    """
    
    def __init__(
        self,
        human_operator_present: bool = True
    ):
        """
        Initialize decision engine.
        
        Args:
            human_operator_present: Whether human operator is present (default: True)
        """
        self.human_operator_present = human_operator_present
        self.current_mode = SystemMode.MONITORING_ONLY  # Default to monitoring only
    
    def process_advisory_outputs(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """
        Process and aggregate advisory outputs.
        
        CRITICAL: This method does NOT output executable commands.
        It only outputs advisory system states.
        
        Args:
            tracks: List of active tracks
            threat_assessments: List of threat assessment results
            additional_context: Additional context (optional)
            
        Returns:
            DecisionResult with advisory system state
        """
        current_time = datetime.now()
        
        # Determine system mode based on conditions
        system_mode = self._determine_system_mode(
            tracks,
            threat_assessments,
            additional_context
        )
        
        # Determine human review state
        human_review_state = self._determine_human_review_state(
            tracks,
            threat_assessments,
            system_mode
        )
        
        # Check ethical constraints
        ethical_status = self._check_ethical_constraints()
        
        # Check airspace compliance
        airspace_compliance = self._check_airspace_compliance(tracks)
        
        # Calculate uncertainty level
        uncertainty_level = self._calculate_uncertainty_level(
            tracks,
            threat_assessments
        )
        
        # Check if fail-safe should be activated
        fail_safe_activated = self._check_fail_safe_conditions(
            tracks,
            threat_assessments,
            uncertainty_level
        )
        
        # Aggregate recommendations (advisory only)
        aggregated_recommendations = self._aggregate_recommendations(
            tracks,
            threat_assessments
        )
        
        # Create advisory system state
        system_state = AdvisorySystemState(
            state_id=str(uuid.uuid4()),
            timestamp=current_time,
            system_mode=system_mode,
            human_review_state=human_review_state,
            active_tracks_count=len(tracks),
            pending_recommendations_count=len(aggregated_recommendations),
            default_action="NO_ACTION",  # Always NO_ACTION
            advisory_summary=self._generate_advisory_summary(
                tracks,
                threat_assessments,
                system_mode
            ),
            ethical_constraints_active=ethical_status["all_active"],
            protected_airspace_violations=airspace_compliance["protected_violations"],
            civilian_airspace_violations=airspace_compliance["civilian_violations"],
            uncertainty_flags=self._identify_uncertainty_flags(
                tracks,
                threat_assessments,
                uncertainty_level
            ),
            metadata={
                "human_operator_present": self.human_operator_present,
                "uncertainty_level": uncertainty_level,
                "fail_safe_activated": fail_safe_activated
            }
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            system_state,
            ethical_status,
            airspace_compliance,
            uncertainty_level,
            fail_safe_activated
        )
        
        # Create decision result
        return DecisionResult(
            result_id=str(uuid.uuid4()),
            timestamp=current_time,
            system_state=system_state,
            aggregated_recommendations=aggregated_recommendations,
            ethical_constraints_status=ethical_status,
            airspace_compliance_status=airspace_compliance,
            human_review_required=(human_review_state != HumanReviewState.NO_REVIEW_NEEDED),
            uncertainty_level=uncertainty_level,
            fail_safe_activated=fail_safe_activated,
            reasoning=reasoning,
            advisory_statement="ADVISORY STATE ONLY - No executable commands. All outputs require human interpretation and approval."
        )
    
    def _determine_system_mode(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult],
        additional_context: Optional[Dict[str, Any]]
    ) -> SystemMode:
        """
        Determine system mode based on conditions.
        
        Returns:
            SystemMode (advisory state only)
        """
        # Check if human operator is present
        if not self.human_operator_present:
            return SystemMode.DEGRADED_SAFE
        
        # Check for high uncertainty
        uncertainty_level = self._calculate_uncertainty_level(tracks, threat_assessments)
        if uncertainty_level > UncertaintyLimits.MAXIMUM_ACCEPTABLE_UNCERTAINTY:
            return SystemMode.MONITORING_ONLY
        
        # Check for critical threats requiring human approval
        critical_threats = [
            ta for ta in threat_assessments
            if ta.threat_level.value == "CRITICAL"
        ]
        if len(critical_threats) > 0:
            return SystemMode.HUMAN_APPROVAL_REQUIRED
        
        # Check for high threat levels
        high_threats = [
            ta for ta in threat_assessments
            if ta.threat_level.value in ["HIGH", "CRITICAL"]
        ]
        if len(high_threats) > 0:
            return SystemMode.HUMAN_APPROVAL_REQUIRED
        
        # Check for low confidence
        low_confidence_tracks = [
            t for t in tracks
            if t.confidence < ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE
        ]
        if len(low_confidence_tracks) > len(tracks) * 0.5:  # More than 50% low confidence
            return SystemMode.MONITORING_ONLY
        
        # Default: Advisory Recommendation Mode
        return SystemMode.ADVISORY_RECOMMENDATION
    
    def _determine_human_review_state(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult],
        system_mode: SystemMode
    ) -> HumanReviewState:
        """Determine human review state requirement."""
        # If degraded safe mode, no review needed (system in safe state)
        if system_mode == SystemMode.DEGRADED_SAFE:
            return HumanReviewState.NO_REVIEW_NEEDED
        
        # If human approval required mode, review is required
        if system_mode == SystemMode.HUMAN_APPROVAL_REQUIRED:
            return HumanReviewState.REVIEW_REQUIRED
        
        # If monitoring only, no review needed
        if system_mode == SystemMode.MONITORING_ONLY:
            return HumanReviewState.NO_REVIEW_NEEDED
        
        # Check for high threat assessments
        high_threats = [
            ta for ta in threat_assessments
            if ta.threat_level.value in ["HIGH", "CRITICAL"]
        ]
        if len(high_threats) > 0:
            return HumanReviewState.REVIEW_REQUIRED
        
        # Default: No review needed
        return HumanReviewState.NO_REVIEW_NEEDED
    
    def _check_ethical_constraints(self) -> Dict[str, bool]:
        """Check ethical constraints status."""
        return {
            "mandatory_human_approval": EthicalConstraints.MANDATORY_HUMAN_APPROVAL_REQUIRED,
            "human_operator_required": EthicalConstraints.HUMAN_OPERATOR_REQUIRED,
            "advisory_only_mode": EthicalConstraints.ADVISORY_ONLY_MODE,
            "autonomous_actions_prohibited": EthicalConstraints.AUTONOMOUS_ACTIONS_PROHIBITED,
            "all_active": (
                EthicalConstraints.MANDATORY_HUMAN_APPROVAL_REQUIRED and
                EthicalConstraints.HUMAN_OPERATOR_REQUIRED and
                EthicalConstraints.ADVISORY_ONLY_MODE and
                EthicalConstraints.AUTONOMOUS_ACTIONS_PROHIBITED
            )
        }
    
    def _check_airspace_compliance(
        self,
        tracks: List[Track]
    ) -> Dict[str, Any]:
        """Check protected and civilian airspace compliance."""
        import math
        
        protected_violations = []
        civilian_violations = []
        
        for track in tracks:
            # Calculate distance to origin
            distance = math.sqrt(
                track.position.x**2 +
                track.position.y**2 +
                track.position.z**2
            )
            
            # Check protected zone violations
            if distance < ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS:
                protected_violations.append(
                    f"Track {track.identifier.track_id}: "
                    f"Within critical zone ({distance/1000.0:.2f} km)"
                )
            elif distance < ProtectedAirspaceConfiguration.PROTECTED_ZONE_RADIUS_METERS:
                protected_violations.append(
                    f"Track {track.identifier.track_id}: "
                    f"Within protected zone ({distance/1000.0:.2f} km)"
                )
            
            # Check civilian airspace (simplified - would need actual civilian zone definitions)
            # For now, we just note if entity is classified as civilian in protected zone
            if track.classification.object_type.value == "AERIAL_DRONE":
                # Drones in protected zones may violate civilian airspace rules
                if distance < ProtectedAirspaceConfiguration.PROTECTED_ZONE_RADIUS_METERS:
                    civilian_violations.append(
                        f"Track {track.identifier.track_id}: "
                        f"Drone in protected zone ({distance/1000.0:.2f} km)"
                    )
        
        return {
            "protected_violations": protected_violations,
            "civilian_violations": civilian_violations,
            "is_compliant": len(protected_violations) == 0 and len(civilian_violations) == 0
        }
    
    def _calculate_uncertainty_level(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult]
    ) -> float:
        """Calculate overall uncertainty level."""
        if len(tracks) == 0:
            return 0.0
        
        # Average track confidence (inverted to get uncertainty)
        avg_confidence = sum(t.confidence for t in tracks) / len(tracks)
        confidence_uncertainty = 1.0 - avg_confidence
        
        # Average assessment uncertainty
        if len(threat_assessments) > 0:
            avg_assessment_uncertainty = sum(
                ta.uncertainty_percentage / 100.0
                for ta in threat_assessments
            ) / len(threat_assessments)
        else:
            avg_assessment_uncertainty = 0.0
        
        # Combined uncertainty
        uncertainty = (confidence_uncertainty * 0.6 + avg_assessment_uncertainty * 0.4)
        
        return min(1.0, max(0.0, uncertainty))
    
    def _check_fail_safe_conditions(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult],
        uncertainty_level: float
    ) -> bool:
        """Check if fail-safe conditions are met."""
        # Check uncertainty threshold
        if uncertainty_level > UncertaintyLimits.MAXIMUM_ACCEPTABLE_UNCERTAINTY:
            if FailSafeConfiguration.FAIL_SAFE_ON_INSUFFICIENT_CONFIDENCE:
                return True
        
        # Check for low confidence tracks
        low_confidence_count = sum(
            1 for t in tracks
            if t.confidence < ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE
        )
        if low_confidence_count > len(tracks) * 0.5:  # More than 50%
            if FailSafeConfiguration.FAIL_SAFE_ON_INSUFFICIENT_CONFIDENCE:
                return True
        
        # Check for stale data
        from abhedya.infrastructure.config.config import UncertaintyLimits
        stale_tracks = [
            t for t in tracks
            if t.get_time_since_update_seconds() > UncertaintyLimits.MAXIMUM_TIME_SINCE_LAST_UPDATE_SECONDS
        ]
        if len(stale_tracks) > 0:
            if FailSafeConfiguration.FAIL_SAFE_ON_STALE_DATA:
                return True
        
        return False
    
    def _aggregate_recommendations(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate advisory recommendations.
        
        IMPORTANT: These are advisory recommendations only.
        They do NOT contain executable commands.
        """
        recommendations = []
        
        for i, assessment in enumerate(threat_assessments):
            # Find corresponding track
            track = None
            if i < len(tracks):
                track = tracks[i]
            
            recommendation = {
                "recommendation_id": assessment.assessment_id,
                "track_id": track.identifier.track_id if track else "UNKNOWN",
                "threat_level": assessment.threat_level.value,
                "risk_score": assessment.risk_score.total_score,
                "threat_likelihood": assessment.threat_likelihood,
                "confidence": assessment.confidence_percentage,
                "uncertainty": assessment.uncertainty_percentage,
                "advisory_note": "ADVISORY ONLY - No executable commands",
                "requires_human_review": assessment.threat_level.value in ["HIGH", "CRITICAL"]
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _identify_uncertainty_flags(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult],
        uncertainty_level: float
    ) -> List[str]:
        """Identify uncertainty flags."""
        flags = []
        
        if uncertainty_level > UncertaintyLimits.MAXIMUM_ACCEPTABLE_UNCERTAINTY:
            flags.append(f"High uncertainty level: {uncertainty_level:.2%}")
        
        low_confidence_tracks = [
            t for t in tracks
            if t.confidence < ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE
        ]
        if len(low_confidence_tracks) > 0:
            flags.append(f"{len(low_confidence_tracks)} tracks with low confidence")
        
        high_uncertainty_assessments = [
            ta for ta in threat_assessments
            if ta.uncertainty_percentage > 50.0
        ]
        if len(high_uncertainty_assessments) > 0:
            flags.append(f"{len(high_uncertainty_assessments)} assessments with high uncertainty")
        
        return flags
    
    def _generate_advisory_summary(
        self,
        tracks: List[Track],
        threat_assessments: List[ThreatAssessmentResult],
        system_mode: SystemMode
    ) -> str:
        """Generate advisory summary."""
        summary_parts = []
        
        summary_parts.append(f"System Mode: {system_mode.value}")
        summary_parts.append(f"Active Tracks: {len(tracks)}")
        summary_parts.append(f"Threat Assessments: {len(threat_assessments)}")
        
        if len(threat_assessments) > 0:
            threat_levels = [ta.threat_level.value for ta in threat_assessments]
            summary_parts.append(f"Threat Levels: {', '.join(set(threat_levels))}")
        
        summary_parts.append("")
        summary_parts.append("ADVISORY STATE ONLY - No executable commands")
        
        return "\n".join(summary_parts)
    
    def _generate_reasoning(
        self,
        system_state: AdvisorySystemState,
        ethical_status: Dict[str, bool],
        airspace_compliance: Dict[str, Any],
        uncertainty_level: float,
        fail_safe_activated: bool
    ) -> str:
        """Generate detailed reasoning for decision result."""
        reasoning_parts = []
        
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("DECISION ENGINE OUTPUT - ADVISORY STATE ONLY")
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("")
        reasoning_parts.append("CRITICAL: This engine does NOT output executable commands.")
        reasoning_parts.append("It only outputs advisory system states.")
        reasoning_parts.append("")
        
        reasoning_parts.append(f"System Mode: {system_state.system_mode.value}")
        reasoning_parts.append(f"Human Review State: {system_state.human_review_state.value}")
        reasoning_parts.append(f"Default Action: {system_state.default_action}")
        reasoning_parts.append("")
        
        reasoning_parts.append("Ethical Constraints Status:")
        for constraint, active in ethical_status.items():
            status = "ACTIVE" if active else "INACTIVE"
            reasoning_parts.append(f"  - {constraint}: {status}")
        reasoning_parts.append("")
        
        reasoning_parts.append("Airspace Compliance:")
        reasoning_parts.append(f"  - Compliant: {airspace_compliance['is_compliant']}")
        if len(airspace_compliance["protected_violations"]) > 0:
            reasoning_parts.append("  - Protected Zone Violations:")
            for violation in airspace_compliance["protected_violations"]:
                reasoning_parts.append(f"    * {violation}")
        if len(airspace_compliance["civilian_violations"]) > 0:
            reasoning_parts.append("  - Civilian Airspace Violations:")
            for violation in airspace_compliance["civilian_violations"]:
                reasoning_parts.append(f"    * {violation}")
        reasoning_parts.append("")
        
        reasoning_parts.append(f"Uncertainty Level: {uncertainty_level:.2%}")
        if len(system_state.uncertainty_flags) > 0:
            reasoning_parts.append("Uncertainty Flags:")
            for flag in system_state.uncertainty_flags:
                reasoning_parts.append(f"  - {flag}")
        reasoning_parts.append("")
        
        if fail_safe_activated:
            reasoning_parts.append("FAIL-SAFE ACTIVATED")
            reasoning_parts.append(f"Default State: {FailSafeConfiguration.FAIL_SAFE_DEFAULT_ACTION} / {FailSafeConfiguration.FAIL_SAFE_DEFAULT_MODE}")
        reasoning_parts.append("")
        
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("END OF ADVISORY STATE OUTPUT")
        reasoning_parts.append("=" * 60)
        
        return "\n".join(reasoning_parts)
    
    def set_human_operator_present(self, present: bool):
        """
        Set human operator presence status.
        
        Args:
            present: Whether human operator is present
        """
        self.human_operator_present = present

