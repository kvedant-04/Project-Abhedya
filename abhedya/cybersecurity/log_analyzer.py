"""
Log Analyzer

Analyzes system logs to extract access patterns and behavior statistics.
Uses classical statistical techniques only.
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from statistics import mean, stdev

from abhedya.cybersecurity.models import SystemEvent, AccessPattern, EventType, AccessType


class LogAnalyzer:
    """
    Analyzes system logs to extract access patterns.
    
    Uses classical statistical techniques to identify patterns.
    """
    
    def __init__(
        self,
        time_window_seconds: float = 3600.0,  # 1 hour default
        minimum_samples_for_baseline: int = 10
    ):
        """
        Initialize log analyzer.
        
        Args:
            time_window_seconds: Time window for pattern analysis
            minimum_samples_for_baseline: Minimum samples for baseline
        """
        self.time_window = time_window_seconds
        self.minimum_samples = minimum_samples_for_baseline
        self.event_history: List[SystemEvent] = []
    
    def analyze_access_patterns(
        self,
        events: List[SystemEvent],
        time_window: Optional[float] = None
    ) -> List[AccessPattern]:
        """
        Analyze access patterns from events.
        
        Args:
            events: List of system events
            time_window: Time window for analysis (optional)
            
        Returns:
            List of AccessPattern objects
        """
        if time_window is None:
            time_window = self.time_window
        
        # Filter events within time window
        if events:
            cutoff_time = events[-1].timestamp - timedelta(seconds=time_window)
            recent_events = [e for e in events if e.timestamp >= cutoff_time]
        else:
            recent_events = []
        
        # Group by subsystem
        subsystem_events: Dict[str, List[SystemEvent]] = defaultdict(list)
        for event in recent_events:
            subsystem_events[event.subsystem].append(event)
        
        patterns = []
        
        for subsystem, subsystem_event_list in subsystem_events.items():
            if len(subsystem_event_list) < 1:
                continue
            
            # Calculate access statistics
            access_count = len(subsystem_event_list)
            unique_resources = len(set(e.resource for e in subsystem_event_list))
            
            # Calculate access rate
            if time_window > 0:
                access_rate = access_count / time_window
            else:
                access_rate = 0.0
            
            # Calculate average interval
            intervals = []
            sorted_events = sorted(subsystem_event_list, key=lambda e: e.timestamp)
            for i in range(1, len(sorted_events)):
                interval = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
                intervals.append(interval)
            
            average_interval = mean(intervals) if intervals else 0.0
            
            # Additional metadata
            event_types = [e.event_type.value for e in subsystem_event_list]
            access_types = [e.access_type.value for e in subsystem_event_list]
            
            pattern_metadata = {
                "event_types": list(set(event_types)),
                "access_types": list(set(access_types)),
                "unique_users": len(set(e.user_id for e in subsystem_event_list if e.user_id)),
                "time_span_seconds": (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds() if len(sorted_events) > 1 else 0.0
            }
            
            pattern = AccessPattern(
                subsystem=subsystem,
                access_count=access_count,
                unique_resources=unique_resources,
                access_rate=access_rate,
                average_interval=average_interval,
                time_window_seconds=time_window,
                pattern_metadata=pattern_metadata
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def calculate_baseline_statistics(
        self,
        events: List[SystemEvent],
        subsystem: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate baseline statistics for events.
        
        Args:
            events: List of system events
            subsystem: Subsystem to filter (optional)
            
        Returns:
            Dictionary with baseline statistics
        """
        if subsystem:
            filtered_events = [e for e in events if e.subsystem == subsystem]
        else:
            filtered_events = events
        
        if len(filtered_events) < self.minimum_samples:
            return {
                "mean_access_rate": 0.0,
                "std_access_rate": 0.0,
                "mean_unique_resources": 0.0,
                "std_unique_resources": 0.0
            }
        
        # Group by time windows
        time_windows = []
        sorted_events = sorted(filtered_events, key=lambda e: e.timestamp)
        
        current_window_start = sorted_events[0].timestamp
        current_window_events = []
        
        for event in sorted_events:
            if (event.timestamp - current_window_start).total_seconds() <= self.time_window:
                current_window_events.append(event)
            else:
                # Process window
                if current_window_events:
                    patterns = self.analyze_access_patterns(current_window_events, self.time_window)
                    if patterns:
                        pattern = patterns[0]
                        time_windows.append({
                            "access_rate": pattern.access_rate,
                            "unique_resources": pattern.unique_resources
                        })
                
                # Start new window
                current_window_start = event.timestamp
                current_window_events = [event]
        
        # Process last window
        if current_window_events:
            patterns = self.analyze_access_patterns(current_window_events, self.time_window)
            if patterns:
                pattern = patterns[0]
                time_windows.append({
                    "access_rate": pattern.access_rate,
                    "unique_resources": pattern.unique_resources
                })
        
        if len(time_windows) < 2:
            return {
                "mean_access_rate": time_windows[0]["access_rate"] if time_windows else 0.0,
                "std_access_rate": 0.0,
                "mean_unique_resources": time_windows[0]["unique_resources"] if time_windows else 0.0,
                "std_unique_resources": 0.0
            }
        
        access_rates = [w["access_rate"] for w in time_windows]
        unique_resources = [w["unique_resources"] for w in time_windows]
        
        return {
            "mean_access_rate": mean(access_rates),
            "std_access_rate": stdev(access_rates) if len(access_rates) > 1 else 0.0,
            "mean_unique_resources": mean(unique_resources),
            "std_unique_resources": stdev(unique_resources) if len(unique_resources) > 1 else 0.0
        }
    
    def detect_sequence_irregularities(
        self,
        events: List[SystemEvent],
        expected_sequences: Optional[List[List[EventType]]] = None
    ) -> List[str]:
        """
        Detect sequence irregularities.
        
        Args:
            events: List of system events
            expected_sequences: Expected event sequences (optional)
            
        Returns:
            List of detected irregularities
        """
        irregularities = []
        
        if len(events) < 2:
            return irregularities
        
        # Check for rapid repeated access
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        for i in range(1, len(sorted_events)):
            interval = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
            if interval < 0.1:  # Less than 100ms
                irregularities.append(
                    f"Rapid repeated access: {sorted_events[i-1].resource} -> {sorted_events[i].resource} "
                    f"({interval*1000:.1f}ms interval)"
                )
        
        # Check for unusual access sequences
        if expected_sequences:
            event_sequence = [e.event_type for e in sorted_events]
            for expected_seq in expected_sequences:
                # Check if expected sequence appears
                if len(event_sequence) >= len(expected_seq):
                    for i in range(len(event_sequence) - len(expected_seq) + 1):
                        if event_sequence[i:i+len(expected_seq)] == expected_seq:
                            # Expected sequence found - check for deviations
                            pass
        
        # Check for access to multiple subsystems in short time
        subsystem_changes = []
        for i in range(1, len(sorted_events)):
            if sorted_events[i].subsystem != sorted_events[i-1].subsystem:
                interval = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
                subsystem_changes.append((interval, sorted_events[i-1].subsystem, sorted_events[i].subsystem))
        
        # Flag rapid subsystem switching
        for interval, from_subsys, to_subsys in subsystem_changes:
            if interval < 1.0:  # Less than 1 second
                irregularities.append(
                    f"Rapid subsystem switching: {from_subsys} -> {to_subsys} ({interval:.2f}s)"
                )
        
        return irregularities
    
    def update_history(self, events: List[SystemEvent]):
        """
        Update event history.
        
        Args:
            events: New events to add
        """
        self.event_history.extend(events)
        
        # Keep only recent history (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.event_history = [e for e in self.event_history if e.timestamp >= cutoff_time]

