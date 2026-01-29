"""
Log Replay

Replay functionality for audit logs.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Iterator, Callable
from abhedya.logging_and_audit.database import AuditDatabase
from abhedya.logging_and_audit.models import LogModule


class LogReplay:
    """
    Log replay engine.
    
    Provides functionality to replay logged events in chronological order.
    """
    
    def __init__(self, db_path: str = "abhedya_audit.db"):
        """
        Initialize log replay.
        
        Args:
            db_path: Path to SQLite database file
        """
        self._db = AuditDatabase(db_path)
    
    def replay_advisory_logs(
        self,
        module_name: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Replay advisory logs in chronological order.
        
        Args:
            module_name: Filter by module name
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            callback: Optional callback function for each log entry
            
        Yields:
            Log entries in chronological order
        """
        # Query logs (ordered by timestamp ASC for replay)
        logs = self._db.query_advisory_logs(
            module_name=module_name,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        )
        
        # Sort by timestamp ascending for chronological replay
        logs_sorted = sorted(logs, key=lambda x: x['timestamp'])
        
        for log_entry in logs_sorted:
            if callback:
                callback(log_entry)
            yield log_entry
    
    def replay_acknowledgments(
        self,
        item_type: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Replay acknowledgment logs in chronological order.
        
        Args:
            item_type: Filter by item type
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            callback: Optional callback function for each acknowledgment
            
        Yields:
            Acknowledgment entries in chronological order
        """
        # Query acknowledgments
        acks = self._db.query_acknowledgments(
            item_type=item_type,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        )
        
        # Sort by timestamp ascending for chronological replay
        acks_sorted = sorted(acks, key=lambda x: x['timestamp'])
        
        for ack_entry in acks_sorted:
            if callback:
                callback(ack_entry)
            yield ack_entry
    
    def replay_system_events(
        self,
        event_type: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Replay system event logs in chronological order.
        
        Args:
            event_type: Filter by event type
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            callback: Optional callback function for each event
            
        Yields:
            System event entries in chronological order
        """
        # Query system events
        events = self._db.query_system_events(
            event_type=event_type,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        )
        
        # Sort by timestamp ascending for chronological replay
        events_sorted = sorted(events, key=lambda x: x['timestamp'])
        
        for event_entry in events_sorted:
            if callback:
                callback(event_entry)
            yield event_entry
    
    def replay_all(
        self,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        callback: Optional[Callable[[Dict[str, Any], str], None]] = None
    ) -> Iterator[tuple]:
        """
        Replay all logs (advisory, acknowledgments, system events) in chronological order.
        
        Args:
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            callback: Optional callback function for each entry (entry, entry_type)
            
        Yields:
            Tuples of (entry, entry_type) in chronological order
        """
        # Get all entries
        advisory_logs = list(self._db.query_advisory_logs(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        ))
        
        acknowledgments = list(self._db.query_acknowledgments(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        ))
        
        system_events = list(self._db.query_system_events(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        ))
        
        # Combine and tag entries
        all_entries = []
        for entry in advisory_logs:
            all_entries.append((entry, 'advisory'))
        for entry in acknowledgments:
            all_entries.append((entry, 'acknowledgment'))
        for entry in system_events:
            all_entries.append((entry, 'system_event'))
        
        # Sort by timestamp ascending
        all_entries_sorted = sorted(all_entries, key=lambda x: x[0]['timestamp'])
        
        # Yield entries
        for entry, entry_type in all_entries_sorted:
            if callback:
                callback(entry, entry_type)
            yield (entry, entry_type)
    
    def get_replay_timeline(
        self,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get replay timeline information.
        
        Args:
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            
        Returns:
            Timeline information dictionary
        """
        # Get all entries
        advisory_logs = list(self._db.query_advisory_logs(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        ))
        
        acknowledgments = list(self._db.query_acknowledgments(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        ))
        
        system_events = list(self._db.query_system_events(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=None,
            offset=None
        ))
        
        # Find earliest and latest timestamps
        all_timestamps = []
        for entry in advisory_logs:
            all_timestamps.append(entry['timestamp'])
        for entry in acknowledgments:
            all_timestamps.append(entry['timestamp'])
        for entry in system_events:
            all_timestamps.append(entry['timestamp'])
        
        timeline = {
            'total_entries': len(advisory_logs) + len(acknowledgments) + len(system_events),
            'advisory_logs_count': len(advisory_logs),
            'acknowledgments_count': len(acknowledgments),
            'system_events_count': len(system_events)
        }
        
        if all_timestamps:
            timeline['earliest_timestamp'] = min(all_timestamps)
            timeline['latest_timestamp'] = max(all_timestamps)
            timeline['duration_seconds'] = (
                datetime.fromisoformat(timeline['latest_timestamp']) -
                datetime.fromisoformat(timeline['earliest_timestamp'])
            ).total_seconds()
        else:
            timeline['earliest_timestamp'] = None
            timeline['latest_timestamp'] = None
            timeline['duration_seconds'] = 0
        
        return timeline

