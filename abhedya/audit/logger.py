"""
Audit logging system.

Provides complete traceability and explainability for all system
operations, decisions, and recommendations.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from abhedya.core.interfaces import IAuditLogger
from abhedya.core.constants import (
    AUDIT_LOG_ENABLED,
    AUDIT_LOG_RETENTION_DAYS,
    EXPLAINABILITY_REQUIRED
)


class AuditLogger(IAuditLogger):
    """
    Audit logging system.
    
    Logs all system events for traceability, explainability, and
    compliance with ethical and legal requirements.
    """
    
    def __init__(
        self,
        log_directory: Optional[str] = None,
        enabled: bool = AUDIT_LOG_ENABLED,
        retention_days: int = AUDIT_LOG_RETENTION_DAYS
    ):
        """
        Initialize audit logger.
        
        Args:
            log_directory: Directory for log files (None = in-memory only)
            enabled: Enable audit logging
            retention_days: Log retention period in days
        """
        self.enabled = enabled
        self.retention_days = retention_days
        self.log_directory = Path(log_directory) if log_directory else None
        
        # In-memory log storage
        self.log_entries: List[Dict] = []
        
        # Create log directory if specified
        if self.log_directory:
            self.log_directory.mkdir(parents=True, exist_ok=True)
    
    def log_event(
        self,
        event_type: str,
        event_data: dict,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Log an event to audit trail.
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
            timestamp: Optional timestamp (defaults to now)
        """
        if not self.enabled:
            return
        
        timestamp = timestamp or datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "event_data": event_data
        }
        
        # Add to in-memory log
        self.log_entries.append(log_entry)
        
        # Write to file if directory specified
        if self.log_directory:
            self._write_to_file(log_entry)
        
        # Print to console for visibility (can be disabled in production)
        self._print_event(event_type, event_data)
    
    def _write_to_file(self, log_entry: Dict):
        """Write log entry to file."""
        if not self.log_directory:
            return
        
        # Create daily log file
        date_str = datetime.fromisoformat(log_entry["timestamp"]).strftime("%Y-%m-%d")
        log_file = self.log_directory / f"audit_{date_str}.jsonl"
        
        # Append to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _print_event(self, event_type: str, event_data: dict):
        """Print event to console (for demonstration)."""
        # In production, this might be disabled or use proper logging
        print(f"[AUDIT] {event_type}: {json.dumps(event_data, default=str)}")
    
    def get_audit_trail(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[dict]:
        """
        Retrieve audit trail for time period.
        
        Args:
            start_time: Start of time period
            end_time: End of time period
            
        Returns:
            List of audit events
        """
        filtered_entries = []
        
        for entry in self.log_entries:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if start_time <= entry_time <= end_time:
                filtered_entries.append(entry)
        
        # Also check file logs if directory specified
        if self.log_directory:
            file_entries = self._read_from_files(start_time, end_time)
            filtered_entries.extend(file_entries)
        
        # Sort by timestamp
        filtered_entries.sort(key=lambda x: x["timestamp"])
        
        return filtered_entries
    
    def _read_from_files(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Read log entries from files for time period."""
        entries = []
        
        if not self.log_directory:
            return entries
        
        # Iterate through date range
        current_date = start_time.date()
        end_date = end_time.date()
        
        while current_date <= end_date:
            log_file = self.log_directory / f"audit_{current_date.strftime('%Y-%m-%d')}.jsonl"
            
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry_time = datetime.fromisoformat(entry["timestamp"])
                            if start_time <= entry_time <= end_time:
                                entries.append(entry)
                        except (json.JSONDecodeError, ValueError):
                            continue  # Skip invalid entries
            
            # Move to next day
            from datetime import timedelta
            current_date += timedelta(days=1)
        
        return entries
    
    def get_explanation(
        self,
        recommendation_id: Optional[str] = None,
        track_id: Optional[str] = None
    ) -> str:
        """
        Generate explanation for a recommendation or track.
        
        Args:
            recommendation_id: ID of recommendation
            track_id: ID of track
            
        Returns:
            Explanation string
        """
        if not EXPLAINABILITY_REQUIRED:
            return "Explainability not enabled"
        
        explanation_parts = []
        
        # Find relevant events
        relevant_events = []
        for entry in self.log_entries:
            event_data = entry.get("event_data", {})
            if recommendation_id and event_data.get("recommendation_id") == recommendation_id:
                relevant_events.append(entry)
            elif track_id and event_data.get("track_id") == track_id:
                relevant_events.append(entry)
        
        if not relevant_events:
            return "No relevant events found in audit trail"
        
        explanation_parts.append("Audit Trail Explanation:")
        explanation_parts.append("=" * 60)
        
        for event in relevant_events:
            explanation_parts.append(
                f"\n[{event['timestamp']}] {event['event_type']}"
            )
            explanation_parts.append(
                json.dumps(event['event_data'], indent=2, default=str)
            )
        
        return "\n".join(explanation_parts)
    
    def export_audit_trail(
        self,
        output_file: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """
        Export audit trail to file.
        
        Args:
            output_file: Output file path
            start_time: Start time (None = all entries)
            end_time: End time (None = all entries)
        """
        if start_time and end_time:
            entries = self.get_audit_trail(start_time, end_time)
        else:
            entries = self.log_entries
        
        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, default=str)

