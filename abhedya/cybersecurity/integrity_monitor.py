"""
Integrity Monitor

Monitors system integrity:
- Configuration consistency
- Unexpected changes
- Suspicious access sequences

Uses classical validation techniques only.
"""

import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

from abhedya.cybersecurity.models import (
    SystemEvent,
    IntegrityCheckResult,
    EventType,
    AccessType
)


class IntegrityMonitor:
    """
    Monitors system integrity.
    
    Checks for:
    - Configuration consistency
    - Unexpected changes
    - Suspicious access sequences
    """
    
    def __init__(
        self,
        expected_config_hashes: Optional[Dict[str, str]] = None,
        suspicious_sequences: Optional[List[List[EventType]]] = None
    ):
        """
        Initialize integrity monitor.
        
        Args:
            expected_config_hashes: Expected configuration hashes (optional)
            suspicious_sequences: Suspicious event sequences (optional)
        """
        self.expected_config_hashes = expected_config_hashes or {}
        self.suspicious_sequences = suspicious_sequences or []
        self.config_history: Dict[str, List[datetime]] = {}
    
    def check_integrity(
        self,
        events: List[SystemEvent],
        current_config: Optional[Dict[str, Any]] = None
    ) -> IntegrityCheckResult:
        """
        Check system integrity.
        
        Args:
            events: System events to analyze
            current_config: Current configuration (optional)
            
        Returns:
            IntegrityCheckResult
        """
        reasoning = []
        unexpected_changes = []
        suspicious_sequences = []
        configuration_checks = {}
        
        # Check configuration consistency
        if current_config:
            config_checks = self._check_configuration_consistency(current_config)
            configuration_checks.update(config_checks)
            
            for key, is_consistent in config_checks.items():
                if not is_consistent:
                    unexpected_changes.append(f"Configuration inconsistency: {key}")
                    reasoning.append(f"Configuration check failed: {key}")
        
        # Check for unexpected changes in events
        config_access_events = [e for e in events if e.event_type == EventType.CONFIG_ACCESS]
        if config_access_events:
            for event in config_access_events:
                if event.access_type in [AccessType.WRITE, AccessType.MODIFY]:
                    unexpected_changes.append(
                        f"Configuration modification: {event.resource} at {event.timestamp}"
                    )
                    reasoning.append(
                        f"Configuration modification detected: {event.resource} "
                        f"(subsystem: {event.subsystem})"
                    )
        
        # Check for suspicious access sequences
        if self.suspicious_sequences:
            detected_sequences = self._detect_suspicious_sequences(events)
            suspicious_sequences.extend(detected_sequences)
            
            if detected_sequences:
                reasoning.append(f"Suspicious sequences detected: {len(detected_sequences)}")
                for seq in detected_sequences[:5]:  # Show top 5
                    reasoning.append(f"  - {seq}")
        
        # Check for unusual access patterns
        unusual_patterns = self._detect_unusual_patterns(events)
        if unusual_patterns:
            reasoning.append(f"Unusual access patterns detected: {len(unusual_patterns)}")
            for pattern in unusual_patterns[:5]:
                reasoning.append(f"  - {pattern}")
        
        # Determine if consistent
        is_consistent = (
            len(unexpected_changes) == 0 and
            len(suspicious_sequences) == 0
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            events,
            current_config,
            unexpected_changes,
            suspicious_sequences
        )
        
        # Determine affected subsystem
        affected_subsystem = None
        if events:
            # Most common subsystem in events
            subsystem_counts = {}
            for event in events:
                subsystem_counts[event.subsystem] = subsystem_counts.get(event.subsystem, 0) + 1
            if subsystem_counts:
                affected_subsystem = max(subsystem_counts, key=subsystem_counts.get)
        
        return IntegrityCheckResult(
            check_id=f"integrity_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            subsystem=affected_subsystem or "unknown",
            is_consistent=is_consistent,
            unexpected_changes=unexpected_changes,
            suspicious_sequences=suspicious_sequences,
            configuration_checks=configuration_checks,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _check_configuration_consistency(
        self,
        current_config: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Check configuration consistency.
        
        Args:
            current_config: Current configuration
            
        Returns:
            Dictionary of check results
        """
        checks = {}
        
        # Check if expected hashes match
        for key, expected_hash in self.expected_config_hashes.items():
            if key in current_config:
                # Calculate hash of current value
                config_value = str(current_config[key])
                current_hash = hashlib.sha256(config_value.encode()).hexdigest()
                
                checks[key] = (current_hash == expected_hash)
            else:
                checks[key] = False  # Key missing
        
        return checks
    
    def _detect_suspicious_sequences(
        self,
        events: List[SystemEvent]
    ) -> List[str]:
        """
        Detect suspicious event sequences.
        
        Args:
            events: System events
            
        Returns:
            List of detected suspicious sequences
        """
        detected = []
        
        if len(events) < 2:
            return detected
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        event_sequence = [e.event_type for e in sorted_events]
        
        # Check for suspicious sequences
        for suspicious_seq in self.suspicious_sequences:
            if len(event_sequence) >= len(suspicious_seq):
                for i in range(len(event_sequence) - len(suspicious_seq) + 1):
                    if event_sequence[i:i+len(suspicious_seq)] == suspicious_seq:
                        detected.append(
                            f"Suspicious sequence detected: {' -> '.join(e.value for e in suspicious_seq)}"
                        )
                        break  # Only report once per sequence
        
        return detected
    
    def _detect_unusual_patterns(
        self,
        events: List[SystemEvent]
    ) -> List[str]:
        """
        Detect unusual access patterns.
        
        Args:
            events: System events
            
        Returns:
            List of detected unusual patterns
        """
        patterns = []
        
        if len(events) < 2:
            return patterns
        
        # Check for rapid config modifications
        config_mods = [
            e for e in events
            if e.event_type == EventType.CONFIG_ACCESS and
            e.access_type in [AccessType.WRITE, AccessType.MODIFY]
        ]
        
        if len(config_mods) > 3:
            patterns.append(f"Multiple configuration modifications: {len(config_mods)}")
        
        # Check for access to multiple subsystems in short time
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        subsystem_switches = 0
        for i in range(1, len(sorted_events)):
            if sorted_events[i].subsystem != sorted_events[i-1].subsystem:
                interval = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
                if interval < 1.0:  # Less than 1 second
                    subsystem_switches += 1
        
        if subsystem_switches > 5:
            patterns.append(f"Rapid subsystem switching: {subsystem_switches} switches")
        
        # Check for unusual resource access
        resource_access_counts = {}
        for event in events:
            resource_access_counts[event.resource] = resource_access_counts.get(event.resource, 0) + 1
        
        # Flag resources with unusually high access
        for resource, count in resource_access_counts.items():
            if count > 10:  # Threshold
                patterns.append(f"Unusual access frequency: {resource} ({count} accesses)")
        
        return patterns
    
    def _calculate_confidence(
        self,
        events: List[SystemEvent],
        current_config: Optional[Dict[str, Any]],
        unexpected_changes: List[str],
        suspicious_sequences: List[str]
    ) -> float:
        """Calculate confidence in integrity check."""
        confidence = 0.7  # Base confidence
        
        # Increase confidence if config provided
        if current_config:
            confidence += 0.2
        
        # Decrease confidence for inconsistencies
        if unexpected_changes:
            confidence -= len(unexpected_changes) * 0.1
        
        if suspicious_sequences:
            confidence -= len(suspicious_sequences) * 0.1
        
        # Decrease confidence if few events
        if len(events) < 3:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def update_expected_config(self, key: str, config_value: Any):
        """
        Update expected configuration.
        
        Args:
            key: Configuration key
            config_value: Configuration value
        """
        config_str = str(config_value)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()
        self.expected_config_hashes[key] = config_hash

