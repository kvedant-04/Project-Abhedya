"""
Cybersecurity Engine

Main engine for cybersecurity and intrusion detection.
Aggregates log analysis, intrusion detection, and integrity monitoring
to produce advisory cybersecurity outputs.

ADVISORY ONLY - Alert and visibility only.
No automated blocking, no shutdown logic, no retaliation.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from abhedya.cybersecurity.models import (
    CybersecurityState,
    CybersecurityResult,
    SystemEvent,
    AccessPattern,
    IntegrityCheckResult,
    AnomalyDetectionResult
)
from abhedya.cybersecurity.log_analyzer import LogAnalyzer
from abhedya.cybersecurity.intrusion_detector import IntrusionDetector
from abhedya.cybersecurity.integrity_monitor import IntegrityMonitor
from abhedya.infrastructure.config.config import ConfidenceThresholds


class CybersecurityEngine:
    """
    Cybersecurity and Intrusion Detection Engine.
    
    ADVISORY ONLY - Alert and visibility only.
    
    Does NOT provide:
    - Automated blocking
    - Shutdown logic
    - Retaliation
    - Automated responses
    
    Only provides alert and visibility for human operator review.
    """
    
    def __init__(
        self,
        enable_log_analysis: bool = True,
        enable_intrusion_detection: bool = True,
        enable_integrity_monitoring: bool = True,
        baseline_minimum_samples: int = 10
    ):
        """
        Initialize cybersecurity engine.
        
        Args:
            enable_log_analysis: Enable log analysis
            enable_intrusion_detection: Enable intrusion detection
            enable_integrity_monitoring: Enable integrity monitoring
            baseline_minimum_samples: Minimum samples for baseline
        """
        self.enable_log_analysis = enable_log_analysis
        self.enable_intrusion = enable_intrusion_detection
        self.enable_integrity = enable_integrity_monitoring
        
        self.log_analyzer = LogAnalyzer(minimum_samples_for_baseline=baseline_minimum_samples)
        self.intrusion_detector = IntrusionDetector(minimum_samples_for_baseline=baseline_minimum_samples)
        self.integrity_monitor = IntegrityMonitor()
        
        self.baseline_events: List[SystemEvent] = []
    
    def analyze(
        self,
        events: List[SystemEvent],
        baseline_events: Optional[List[SystemEvent]] = None,
        current_config: Optional[dict] = None
    ) -> CybersecurityResult:
        """
        Analyze system events and produce cybersecurity result.
        
        ADVISORY ONLY - Alert and visibility only.
        No automated blocking, no shutdown logic, no retaliation.
        
        Args:
            events: Current system events to analyze
            baseline_events: Baseline events for comparison (optional)
            current_config: Current configuration (optional)
            
        Returns:
            CybersecurityResult (advisory only)
        """
        current_time = datetime.now()
        
        # Check data quality
        data_quality_flags = self._check_data_quality(events)
        
        # Fail-safe: If no events, return normal state
        if len(events) == 0:
            return self._create_normal_result(
                current_time,
                "No system events to analyze",
                data_quality_flags
            )
        
        # Analyze access patterns
        access_patterns = []
        if self.enable_log_analysis:
            try:
                access_patterns = self.log_analyzer.analyze_access_patterns(events)
                self.log_analyzer.update_history(events)
            except Exception as e:
                data_quality_flags.append(f"Log analysis error: {str(e)}")
        
        # Detect intrusions
        anomaly_result = None
        if self.enable_intrusion:
            try:
                baseline = baseline_events if baseline_events else self.baseline_events
                anomaly_result = self.intrusion_detector.detect_anomalies(events, baseline)
            except Exception as e:
                data_quality_flags.append(f"Intrusion detection error: {str(e)}")
        
        # Monitor integrity
        integrity_result = None
        if self.enable_integrity:
            try:
                integrity_result = self.integrity_monitor.check_integrity(events, current_config)
            except Exception as e:
                data_quality_flags.append(f"Integrity monitoring error: {str(e)}")
        
        # Determine cybersecurity state
        cybersecurity_state = self._determine_cybersecurity_state(
            anomaly_result,
            integrity_result
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            events,
            anomaly_result,
            integrity_result,
            data_quality_flags
        )
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(
            events,
            anomaly_result,
            integrity_result
        )
        
        # Determine affected subsystem
        affected_subsystem = self._determine_affected_subsystem(
            events,
            anomaly_result,
            integrity_result
        )
        
        # Generate advisory message
        advisory_message = self._generate_advisory_message(
            cybersecurity_state,
            anomaly_result,
            integrity_result,
            affected_subsystem
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            cybersecurity_state,
            access_patterns,
            anomaly_result,
            integrity_result,
            data_quality_flags
        )
        
        return CybersecurityResult(
            result_id=str(uuid.uuid4()),
            timestamp=current_time,
            cybersecurity_state=cybersecurity_state,
            confidence=confidence,
            uncertainty=uncertainty,
            affected_subsystem=affected_subsystem,
            advisory_message=advisory_message,
            access_patterns=access_patterns,
            integrity_check=integrity_result,
            anomaly_detection=anomaly_result,
            reasoning=reasoning,
            data_quality_flags=data_quality_flags,
            advisory_statement="ADVISORY ONLY - Alert and visibility only. No automated blocking. No shutdown logic. No retaliation. Human operator review required."
        )
    
    def _check_data_quality(self, events: List[SystemEvent]) -> List[str]:
        """Check data quality and return flags."""
        flags = []
        
        if len(events) == 0:
            flags.append("No events provided")
        
        # Check for events with missing timestamps
        invalid_timestamps = sum(1 for e in events if e.timestamp is None)
        if invalid_timestamps > 0:
            flags.append(f"{invalid_timestamps} events with invalid timestamps")
        
        # Check for events with missing subsystems
        missing_subsystems = sum(1 for e in events if not e.subsystem)
        if missing_subsystems > 0:
            flags.append(f"{missing_subsystems} events with missing subsystems")
        
        return flags
    
    def _create_normal_result(
        self,
        timestamp: datetime,
        reason: str,
        data_quality_flags: List[str]
    ) -> CybersecurityResult:
        """Create normal result."""
        return CybersecurityResult(
            result_id=str(uuid.uuid4()),
            timestamp=timestamp,
            cybersecurity_state=CybersecurityState.NORMAL,
            confidence=0.5,
            uncertainty=0.5,
            affected_subsystem=None,
            advisory_message=f"Normal state: {reason}",
            access_patterns=[],
            integrity_check=None,
            anomaly_detection=None,
            reasoning=[reason],
            data_quality_flags=data_quality_flags,
            advisory_statement="ADVISORY ONLY - Alert and visibility only. No automated blocking. No shutdown logic. No retaliation. Human operator review required."
        )
    
    def _determine_cybersecurity_state(
        self,
        anomaly_result: Optional[AnomalyDetectionResult],
        integrity_result: Optional[IntegrityCheckResult]
    ) -> CybersecurityState:
        """
        Determine cybersecurity state.
        
        ADVISORY ONLY - State is informational and does not trigger automated actions.
        """
        # Check for alert conditions
        alert_conditions = 0
        
        if anomaly_result and anomaly_result.is_anomalous:
            if anomaly_result.anomaly_score > 0.8:
                alert_conditions += 2
            else:
                alert_conditions += 1
        
        if integrity_result and not integrity_result.is_consistent:
            if len(integrity_result.unexpected_changes) > 3:
                alert_conditions += 2
            else:
                alert_conditions += 1
        
        # Map to state
        if alert_conditions >= 2:
            return CybersecurityState.ALERT
        elif alert_conditions >= 1:
            return CybersecurityState.SUSPICIOUS
        else:
            return CybersecurityState.NORMAL
    
    def _calculate_confidence(
        self,
        events: List[SystemEvent],
        anomaly_result: Optional[AnomalyDetectionResult],
        integrity_result: Optional[IntegrityCheckResult],
        data_quality_flags: List[str]
    ) -> float:
        """Calculate confidence in cybersecurity assessment."""
        confidence = 0.6  # Base confidence
        
        # Reduce confidence for data quality issues
        if len(data_quality_flags) > 0:
            confidence -= len(data_quality_flags) * 0.1
        
        # Increase confidence if both analyses succeeded
        if anomaly_result and integrity_result:
            confidence = (confidence + anomaly_result.confidence + integrity_result.confidence) / 3.0
        elif anomaly_result:
            confidence = (confidence + anomaly_result.confidence) / 2.0
        elif integrity_result:
            confidence = (confidence + integrity_result.confidence) / 2.0
        
        # Adjust based on event count
        if len(events) < 3:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_uncertainty(
        self,
        events: List[SystemEvent],
        anomaly_result: Optional[AnomalyDetectionResult],
        integrity_result: Optional[IntegrityCheckResult]
    ) -> float:
        """Calculate uncertainty in cybersecurity assessment."""
        uncertainty = 0.3  # Base uncertainty
        
        # Increase uncertainty if analyses failed
        if anomaly_result is None:
            uncertainty += 0.2
        if integrity_result is None:
            uncertainty += 0.2
        
        # Increase uncertainty for few events
        if len(events) < 5:
            uncertainty += 0.2
        
        return min(1.0, max(0.0, uncertainty))
    
    def _determine_affected_subsystem(
        self,
        events: List[SystemEvent],
        anomaly_result: Optional[AnomalyDetectionResult],
        integrity_result: Optional[IntegrityCheckResult]
    ) -> Optional[str]:
        """Determine affected subsystem."""
        # Check integrity result first
        if integrity_result and integrity_result.subsystem:
            return integrity_result.subsystem
        
        # Check anomaly result
        if anomaly_result and anomaly_result.rate_limit_violations:
            # Extract subsystem from rate limit violations
            for violation in anomaly_result.rate_limit_violations:
                if ":" in violation:
                    subsystem = violation.split(":")[0]
                    return subsystem
        
        # Use most common subsystem in events
        if events:
            subsystem_counts = {}
            for event in events:
                subsystem_counts[event.subsystem] = subsystem_counts.get(event.subsystem, 0) + 1
            if subsystem_counts:
                return max(subsystem_counts, key=subsystem_counts.get)
        
        return None
    
    def _generate_advisory_message(
        self,
        state: CybersecurityState,
        anomaly_result: Optional[AnomalyDetectionResult],
        integrity_result: Optional[IntegrityCheckResult],
        affected_subsystem: Optional[str]
    ) -> str:
        """Generate advisory message for human operator."""
        messages = []
        
        if state == CybersecurityState.ALERT:
            messages.append("ALERT: High-priority cybersecurity concern detected")
        elif state == CybersecurityState.SUSPICIOUS:
            messages.append("SUSPICIOUS: Unusual system behavior detected")
        else:
            messages.append("NORMAL: System behavior within expected parameters")
        
        if affected_subsystem:
            messages.append(f"Affected subsystem: {affected_subsystem}")
        
        if anomaly_result and anomaly_result.is_anomalous:
            messages.append(f"Anomaly score: {anomaly_result.anomaly_score:.2%}")
        
        if integrity_result and not integrity_result.is_consistent:
            messages.append(f"Integrity issues: {len(integrity_result.unexpected_changes)}")
        
        messages.append("Human operator review recommended")
        
        return " | ".join(messages)
    
    def _generate_reasoning(
        self,
        state: CybersecurityState,
        access_patterns: List[AccessPattern],
        anomaly_result: Optional[AnomalyDetectionResult],
        integrity_result: Optional[IntegrityCheckResult],
        data_quality_flags: List[str]
    ) -> List[str]:
        """Generate human-readable reasoning."""
        reasoning = []
        
        reasoning.append(f"Cybersecurity State: {state.value} (ADVISORY ONLY)")
        reasoning.append("")
        
        if access_patterns:
            reasoning.append("Access Patterns:")
            for pattern in access_patterns:
                reasoning.append(f"  - {pattern.subsystem}: {pattern.access_count} accesses, "
                               f"{pattern.access_rate:.2f} accesses/s, "
                               f"{pattern.unique_resources} unique resources")
            reasoning.append("")
        
        if anomaly_result:
            reasoning.append("Anomaly Detection:")
            for line in anomaly_result.reasoning:
                reasoning.append(f"  - {line}")
            reasoning.append("")
        
        if integrity_result:
            reasoning.append("Integrity Check:")
            reasoning.append(f"  - Consistent: {integrity_result.is_consistent}")
            if integrity_result.unexpected_changes:
                reasoning.append(f"  - Unexpected Changes: {len(integrity_result.unexpected_changes)}")
                for change in integrity_result.unexpected_changes[:5]:
                    reasoning.append(f"    - {change}")
            if integrity_result.suspicious_sequences:
                reasoning.append(f"  - Suspicious Sequences: {len(integrity_result.suspicious_sequences)}")
            reasoning.append("")
        
        if len(data_quality_flags) > 0:
            reasoning.append("Data Quality Flags:")
            for flag in data_quality_flags:
                reasoning.append(f"  - {flag}")
            reasoning.append("")
        
        reasoning.append("IMPORTANT: This is ADVISORY ONLY.")
        reasoning.append("No automated blocking is performed.")
        reasoning.append("No shutdown logic is executed.")
        reasoning.append("No retaliation is taken.")
        reasoning.append("Alert and visibility only - Human operator review required.")
        
        return reasoning
    
    def update_baseline(self, events: List[SystemEvent]):
        """
        Update baseline with new events.
        
        Args:
            events: Events to add to baseline
        """
        self.baseline_events.extend(events)
        
        # Keep only recent baseline (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.baseline_events = [e for e in self.baseline_events if e.timestamp >= cutoff_time]

