"""
Intrusion Detector

Detects anomalies in system behavior using:
- Statistical baselines
- Z-score deviation
- Sequence irregularities
- Rate-limit violations

Uses classical statistical techniques only.
"""

import math
from typing import List, Optional, Dict, Any
from statistics import mean, stdev

from abhedya.cybersecurity.models import (
    SystemEvent,
    AccessPattern,
    AnomalyDetectionResult
)
from abhedya.cybersecurity.log_analyzer import LogAnalyzer


class IntrusionDetector:
    """
    Detects anomalies in system behavior.
    
    Uses classical statistical techniques:
    - Statistical deviation (Z-score)
    - Sequence analysis
    - Rate limit checking
    """
    
    def __init__(
        self,
        z_score_threshold: float = 2.0,
        rate_limit_multiplier: float = 3.0,
        minimum_samples_for_baseline: int = 10
    ):
        """
        Initialize intrusion detector.
        
        Args:
            z_score_threshold: Z-score threshold for anomaly detection
            rate_limit_multiplier: Multiplier for rate limit (e.g., 3x baseline)
            minimum_samples_for_baseline: Minimum samples for baseline
        """
        self.z_score_threshold = z_score_threshold
        self.rate_limit_multiplier = rate_limit_multiplier
        self.minimum_samples = minimum_samples_for_baseline
        self.log_analyzer = LogAnalyzer(minimum_samples_for_baseline=minimum_samples_for_baseline)
        self.baseline_statistics: Dict[str, Dict[str, float]] = {}
    
    def detect_anomalies(
        self,
        events: List[SystemEvent],
        baseline_events: Optional[List[SystemEvent]] = None
    ) -> AnomalyDetectionResult:
        """
        Detect anomalies in system events.
        
        Args:
            events: Current events to analyze
            baseline_events: Baseline events for comparison (optional)
            
        Returns:
            AnomalyDetectionResult
        """
        reasoning = []
        anomaly_score = 0.0
        
        # Calculate baseline if not available
        if baseline_events and len(baseline_events) >= self.minimum_samples:
            baseline_stats = self.log_analyzer.calculate_baseline_statistics(baseline_events)
        else:
            baseline_stats = None
        
        # Analyze current access patterns
        current_patterns = self.log_analyzer.analyze_access_patterns(events)
        
        # Statistical deviation
        statistical_deviation = 0.0
        if baseline_stats and current_patterns:
            # Calculate deviation for each pattern
            deviations = []
            for pattern in current_patterns:
                if pattern.subsystem in self.baseline_statistics:
                    baseline = self.baseline_statistics[pattern.subsystem]
                elif baseline_stats:
                    baseline = baseline_stats
                else:
                    continue
                
                # Calculate Z-scores
                if baseline.get("std_access_rate", 0.0) > 0:
                    z_score_rate = abs(
                        (pattern.access_rate - baseline["mean_access_rate"]) /
                        baseline["std_access_rate"]
                    )
                    deviations.append(z_score_rate)
                
                if baseline.get("std_unique_resources", 0.0) > 0:
                    z_score_resources = abs(
                        (pattern.unique_resources - baseline["mean_unique_resources"]) /
                        baseline["std_unique_resources"]
                    )
                    deviations.append(z_score_resources)
            
            if deviations:
                statistical_deviation = max(deviations)
                
                if statistical_deviation > self.z_score_threshold:
                    anomaly_score += 0.4
                    reasoning.append(
                        f"Statistical deviation from baseline: {statistical_deviation:.2f}σ "
                        f"(threshold: {self.z_score_threshold}σ)"
                    )
        
        # Rate limit violations
        rate_limit_violations = []
        if baseline_stats and current_patterns:
            for pattern in current_patterns:
                baseline_rate = baseline_stats.get("mean_access_rate", 0.0)
                if baseline_rate > 0:
                    rate_limit = baseline_rate * self.rate_limit_multiplier
                    if pattern.access_rate > rate_limit:
                        rate_limit_violations.append(
                            f"{pattern.subsystem}: {pattern.access_rate:.2f} accesses/s "
                            f"(limit: {rate_limit:.2f}, baseline: {baseline_rate:.2f})"
                        )
                        anomaly_score += 0.3
                        reasoning.append(
                            f"Rate limit violation in {pattern.subsystem}: "
                            f"{pattern.access_rate:.2f} accesses/s exceeds limit"
                        )
        
        # Sequence irregularities
        sequence_irregularities = self.log_analyzer.detect_sequence_irregularities(events)
        if sequence_irregularities:
            anomaly_score += 0.2
            reasoning.append(f"Sequence irregularities detected: {len(sequence_irregularities)}")
            for irregularity in sequence_irregularities[:5]:  # Show top 5
                reasoning.append(f"  - {irregularity}")
        
        # Determine if anomalous
        is_anomalous = (
            anomaly_score > 0.5 or
            statistical_deviation > self.z_score_threshold or
            len(rate_limit_violations) > 0
        )
        
        # Generate suspected pattern
        suspected_pattern = self._generate_suspected_pattern(
            statistical_deviation,
            rate_limit_violations,
            sequence_irregularities
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            events,
            baseline_stats,
            anomaly_score
        )
        
        # Add summary
        if is_anomalous:
            reasoning.insert(0, f"Anomaly detected with score: {anomaly_score:.2%}")
        else:
            reasoning.insert(0, "No significant anomalies detected")
        
        return AnomalyDetectionResult(
            is_anomalous=is_anomalous,
            anomaly_score=min(1.0, anomaly_score),
            statistical_deviation=statistical_deviation,
            sequence_irregularities=sequence_irregularities,
            rate_limit_violations=rate_limit_violations,
            suspected_pattern=suspected_pattern,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def _generate_suspected_pattern(
        self,
        statistical_deviation: float,
        rate_limit_violations: List[str],
        sequence_irregularities: List[str]
    ) -> str:
        """Generate suspected pattern description."""
        patterns = []
        
        if statistical_deviation > self.z_score_threshold:
            patterns.append("Statistical deviation from baseline")
        
        if rate_limit_violations:
            patterns.append("Rate limit violations")
        
        if sequence_irregularities:
            patterns.append("Sequence irregularities")
        
        if not patterns:
            return "Normal system behavior"
        
        return ", ".join(patterns)
    
    def _calculate_confidence(
        self,
        events: List[SystemEvent],
        baseline_stats: Optional[Dict[str, float]],
        anomaly_score: float
    ) -> float:
        """Calculate confidence in anomaly detection."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if baseline exists
        if baseline_stats:
            confidence += 0.3
        
        # Increase confidence with anomaly score
        confidence += anomaly_score * 0.2
        
        # Decrease confidence if few events
        if len(events) < 5:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def update_baseline(
        self,
        subsystem: str,
        baseline_statistics: Dict[str, float]
    ):
        """
        Update baseline statistics for a subsystem.
        
        Args:
            subsystem: Subsystem name
            baseline_statistics: Baseline statistics
        """
        self.baseline_statistics[subsystem] = baseline_statistics

