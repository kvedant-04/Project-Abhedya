"""
Early Warning Engine

Main engine for early warning system.
Aggregates baseline analysis and trend analysis to produce
advisory early warning outputs.

ADVISORY ONLY - No action recommendations or execution logic.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from abhedya.early_warning.models import (
    EarlyWarningState,
    EarlyWarningResult,
    SystemPosture,
    BaselineStatistics,
    TrendAnalysisResult
)
from abhedya.early_warning.baseline import BaselineAnalyzer
from abhedya.early_warning.trend_analysis import TrendAnalyzer
from abhedya.tracking.models import Track
from abhedya.infrastructure.config.config import (
    ConfidenceThresholds,
    UncertaintyLimits,
    FailSafeConfiguration
)


class EarlyWarningEngine:
    """
    Early Warning System Engine.
    
    ADVISORY ONLY - Produces advisory early warning outputs.
    No action recommendations or execution logic.
    
    FAIL-SAFE: Insufficient or stale data defaults to MONITORING_ONLY.
    """
    
    def __init__(
        self,
        baseline_minimum_samples: int = 10,
        enable_baseline_analysis: bool = True,
        enable_trend_analysis: bool = True
    ):
        """
        Initialize early warning engine.
        
        Args:
            baseline_minimum_samples: Minimum samples for baseline
            enable_baseline_analysis: Enable baseline analysis
            enable_trend_analysis: Enable trend analysis
        """
        self.enable_baseline = enable_baseline_analysis
        self.enable_trend = enable_trend_analysis
        self.baseline_analyzer = BaselineAnalyzer(
            minimum_samples_for_baseline=baseline_minimum_samples
        )
        self.trend_analyzer = TrendAnalyzer()
        self.current_baseline: Optional[BaselineStatistics] = None
    
    def analyze(
        self,
        tracks: List[Track],
        historical_tracks: Optional[List[List[Track]]] = None
    ) -> EarlyWarningResult:
        """
        Analyze tracks and produce early warning result.
        
        FAIL-SAFE: If insufficient or stale data, defaults to MONITORING_ONLY.
        
        ADVISORY ONLY - No action recommendations or execution logic.
        
        Args:
            tracks: Current tracks
            historical_tracks: Historical track data (optional)
            
        Returns:
            EarlyWarningResult (advisory only)
        """
        current_time = datetime.now()
        
        # Check data quality
        data_quality_flags = self._check_data_quality(tracks)
        
        # Fail-safe: If data is insufficient or stale, default to MONITORING_ONLY
        if self._is_data_insufficient(tracks, data_quality_flags):
            return self._create_monitoring_only_result(
                current_time,
                data_quality_flags,
                "Insufficient or stale data - defaulting to MONITORING_ONLY"
            )
        
        # Establish or update baseline
        baseline = None
        if self.enable_baseline:
            if self.current_baseline is None:
                baseline = self.baseline_analyzer.establish_baseline(tracks, historical_tracks)
                if baseline:
                    self.current_baseline = baseline
            else:
                # Update baseline
                updated = self.baseline_analyzer.update_baseline(self.current_baseline, tracks)
                if updated:
                    self.current_baseline = updated
                    baseline = updated
                else:
                    baseline = self.current_baseline
        
        # Perform trend analysis
        trend_result = None
        if self.enable_trend:
            baseline_mean = baseline.track_density_mean if baseline else None
            trend_result = self.trend_analyzer.analyze_trends(tracks, baseline_mean)
        
        # Compare to baseline
        baseline_comparison = None
        if baseline:
            baseline_comparison = self.baseline_analyzer.compare_to_baseline(baseline, tracks)
        
        # Determine warning state
        warning_state = self._determine_warning_state(
            baseline_comparison,
            trend_result,
            data_quality_flags
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            tracks,
            baseline,
            trend_result,
            data_quality_flags
        )
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(
            tracks,
            baseline,
            trend_result
        )
        
        # Determine recommended posture (INFORMATIONAL ONLY)
        recommended_posture = self._determine_recommended_posture(warning_state)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            warning_state,
            baseline,
            baseline_comparison,
            trend_result,
            data_quality_flags
        )
        
        # Identify anomaly indicators
        anomaly_indicators = self._identify_anomaly_indicators(
            baseline_comparison,
            trend_result
        )
        
        return EarlyWarningResult(
            result_id=str(uuid.uuid4()),
            timestamp=current_time,
            warning_state=warning_state,
            confidence=confidence,
            uncertainty=uncertainty,
            reasoning=reasoning,
            recommended_posture=recommended_posture,
            baseline_statistics=baseline,
            trend_analysis=trend_result,
            anomaly_indicators=anomaly_indicators,
            data_quality_flags=data_quality_flags,
            advisory_statement="ADVISORY OUTPUT ONLY - No action recommendations. Recommended posture is informational only and does not map to any actions."
        )
    
    def _check_data_quality(self, tracks: List[Track]) -> List[str]:
        """Check data quality and return flags."""
        flags = []
        
        if len(tracks) == 0:
            flags.append("No tracks available")
        
        # Check for stale tracks
        stale_count = 0
        for track in tracks:
            if track.is_stale():
                stale_count += 1
        
        if stale_count > 0:
            flags.append(f"{stale_count} stale tracks detected")
        
        # Check for low confidence tracks
        low_confidence_count = sum(
            1 for t in tracks
            if t.confidence < ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE
        )
        if low_confidence_count > len(tracks) * 0.5:
            flags.append(f"High proportion of low-confidence tracks: {low_confidence_count}/{len(tracks)}")
        
        # Check for insufficient data
        if len(tracks) < 3:
            flags.append("Insufficient tracks for analysis")
        
        return flags
    
    def _is_data_insufficient(
        self,
        tracks: List[Track],
        data_quality_flags: List[str]
    ) -> bool:
        """Check if data is insufficient (fail-safe condition)."""
        # Critical flags that trigger fail-safe
        critical_flags = [
            "No tracks available",
            "Insufficient tracks for analysis"
        ]
        
        for flag in data_quality_flags:
            if flag in critical_flags:
                return True
        
        # Check for too many stale tracks
        stale_count = sum(1 for t in tracks if t.is_stale())
        if stale_count > len(tracks) * 0.7:  # More than 70% stale
            return True
        
        return False
    
    def _create_monitoring_only_result(
        self,
        timestamp: datetime,
        data_quality_flags: List[str],
        reason: str
    ) -> EarlyWarningResult:
        """Create MONITORING_ONLY result (fail-safe)."""
        return EarlyWarningResult(
            result_id=str(uuid.uuid4()),
            timestamp=timestamp,
            warning_state=EarlyWarningState.NORMAL,
            confidence=0.5,  # Low confidence due to insufficient data
            uncertainty=0.5,  # High uncertainty
            reasoning=[reason] + data_quality_flags,
            recommended_posture=SystemPosture.MONITORING_ONLY,
            baseline_statistics=None,
            trend_analysis=None,
            anomaly_indicators=[],
            data_quality_flags=data_quality_flags,
            advisory_statement="ADVISORY OUTPUT ONLY - No action recommendations. Recommended posture is informational only and does not map to any actions."
        )
    
    def _determine_warning_state(
        self,
        baseline_comparison: Optional[Dict[str, Any]],
        trend_result: Optional[TrendAnalysisResult],
        data_quality_flags: List[str]
    ) -> EarlyWarningState:
        """
        Determine early warning state.
        
        ADVISORY ONLY - State is informational and does not map to actions.
        """
        # Start with NORMAL
        state_score = 0.0
        
        # Baseline comparison contribution
        if baseline_comparison:
            if baseline_comparison.get("is_anomalous", False):
                state_score += 0.5
            
            anomaly_score = baseline_comparison.get("anomaly_score", 0.0)
            state_score += anomaly_score * 0.3
        
        # Trend analysis contribution
        if trend_result:
            if trend_result.cusum_value > self.trend_analyzer.cusum_threshold:
                state_score += 0.3
            
            if trend_result.convergence_detected:
                state_score += 0.2
            
            state_score += trend_result.anomaly_score * 0.2
        
        # Data quality contribution
        if len(data_quality_flags) > 2:
            state_score += 0.1
        
        # Map to warning state
        if state_score >= 0.7:
            return EarlyWarningState.HIGH
        elif state_score >= 0.4:
            return EarlyWarningState.ELEVATED
        else:
            return EarlyWarningState.NORMAL
    
    def _calculate_confidence(
        self,
        tracks: List[Track],
        baseline: Optional[BaselineStatistics],
        trend_result: Optional[TrendAnalysisResult],
        data_quality_flags: List[str]
    ) -> float:
        """Calculate confidence in early warning assessment."""
        confidence = 1.0
        
        # Reduce confidence for data quality issues
        if len(data_quality_flags) > 0:
            confidence -= len(data_quality_flags) * 0.1
        
        # Reduce confidence if no baseline
        if baseline is None:
            confidence -= 0.2
        
        # Reduce confidence for low track confidence
        if len(tracks) > 0:
            avg_confidence = sum(t.confidence for t in tracks) / len(tracks)
            confidence = (confidence + avg_confidence) / 2.0
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_uncertainty(
        self,
        tracks: List[Track],
        baseline: Optional[BaselineStatistics],
        trend_result: Optional[TrendAnalysisResult]
    ) -> float:
        """Calculate uncertainty in early warning assessment."""
        uncertainty = 0.0
        
        # Uncertainty from lack of baseline
        if baseline is None:
            uncertainty += 0.3
        
        # Uncertainty from track confidence
        if len(tracks) > 0:
            avg_confidence = sum(t.confidence for t in tracks) / len(tracks)
            uncertainty += (1.0 - avg_confidence) * 0.4
        
        # Uncertainty from trend analysis
        if trend_result:
            uncertainty += trend_result.anomaly_score * 0.3
        
        return min(1.0, max(0.0, uncertainty))
    
    def _determine_recommended_posture(
        self,
        warning_state: EarlyWarningState
    ) -> SystemPosture:
        """
        Determine recommended system posture (INFORMATIONAL ONLY).
        
        This is an advisory recommendation only - it does not map to any actions.
        """
        if warning_state == EarlyWarningState.HIGH:
            return SystemPosture.ALERT_MONITORING
        elif warning_state == EarlyWarningState.ELEVATED:
            return SystemPosture.ENHANCED_MONITORING
        else:
            return SystemPosture.MONITORING_ONLY
    
    def _generate_reasoning(
        self,
        warning_state: EarlyWarningState,
        baseline: Optional[BaselineStatistics],
        baseline_comparison: Optional[Dict[str, Any]],
        trend_result: Optional[TrendAnalysisResult],
        data_quality_flags: List[str]
    ) -> List[str]:
        """Generate human-readable reasoning."""
        reasoning = []
        
        reasoning.append(f"Early Warning State: {warning_state.value} (ADVISORY ONLY)")
        reasoning.append("")
        
        if baseline:
            reasoning.append("Baseline Statistics:")
            reasoning.append(f"  - Track Density: {baseline.track_density_mean:.2f} ± {baseline.track_density_std:.2f}")
            reasoning.append(f"  - Velocity: {baseline.velocity_mean:.1f} ± {baseline.velocity_std:.1f} m/s")
            reasoning.append(f"  - Trajectory Deviation: {baseline.trajectory_deviation_mean:.2f} ± {baseline.trajectory_deviation_std:.2f}")
            reasoning.append("")
        
        if baseline_comparison:
            reasoning.append("Baseline Comparison:")
            if baseline_comparison.get("is_anomalous", False):
                reasoning.append("  - Anomalous deviation from baseline detected")
            reasoning.append(f"  - Track Density Deviation: {baseline_comparison.get('track_density_deviation', 0.0):.2f}σ")
            reasoning.append(f"  - Velocity Deviation: {baseline_comparison.get('velocity_deviation', 0.0):.2f}σ")
            reasoning.append(f"  - Trajectory Deviation: {baseline_comparison.get('trajectory_deviation', 0.0):.2f}σ")
            reasoning.append("")
        
        if trend_result:
            reasoning.append("Trend Analysis:")
            for line in trend_result.reasoning:
                reasoning.append(f"  - {line}")
            reasoning.append("")
        
        if len(data_quality_flags) > 0:
            reasoning.append("Data Quality Flags:")
            for flag in data_quality_flags:
                reasoning.append(f"  - {flag}")
            reasoning.append("")
        
        reasoning.append("IMPORTANT: This is an ADVISORY OUTPUT ONLY.")
        reasoning.append("No action recommendations are provided.")
        reasoning.append("Recommended posture is informational only and does not map to any actions.")
        
        return reasoning
    
    def _identify_anomaly_indicators(
        self,
        baseline_comparison: Optional[Dict[str, Any]],
        trend_result: Optional[TrendAnalysisResult]
    ) -> List[str]:
        """Identify specific anomaly indicators."""
        indicators = []
        
        if baseline_comparison:
            if baseline_comparison.get("track_density_deviation", 0.0) > 2.0:
                indicators.append("Track density significantly deviates from baseline")
            
            if baseline_comparison.get("velocity_deviation", 0.0) > 2.0:
                indicators.append("Velocity distribution significantly deviates from baseline")
            
            if baseline_comparison.get("trajectory_deviation", 0.0) > 2.0:
                indicators.append("Trajectory deviation significantly differs from baseline")
        
        if trend_result:
            if trend_result.cusum_value > self.trend_analyzer.cusum_threshold:
                indicators.append(f"CUSUM threshold exceeded: {trend_result.cusum_value:.2f}")
            
            if trend_result.convergence_detected:
                indicators.append("Multi-track convergence detected")
            
            if trend_result.anomaly_score > 0.7:
                indicators.append(f"High anomaly score: {trend_result.anomaly_score:.2%}")
        
        return indicators

