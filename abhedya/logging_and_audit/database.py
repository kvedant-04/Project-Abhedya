"""
Audit Database

SQLite database for immutable audit logs.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import threading


class AuditDatabase:
    """
    SQLite database for audit logs.
    
    Provides immutable, append-only logging with structured JSON storage.
    """
    
    def __init__(self, db_path: str = "abhedya_audit.db"):
        """
        Initialize audit database.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Input validation
        if not isinstance(db_path, str) or not db_path:
            db_path = "abhedya_audit.db"
        
        # Sanitize path (prevent directory traversal)
        db_path = str(db_path).replace('..', '').replace('/', '_').replace('\\', '_')
        
        self.db_path = db_path
        self._lock = threading.Lock()
        
        try:
            self._ensure_database_exists()
        except Exception:
            # If initialization fails, use in-memory database as fallback
            self.db_path = ":memory:"
            try:
                self._ensure_database_exists()
            except Exception:
                # Last resort: raise with clear error
                raise RuntimeError("Failed to initialize audit database")
    
    def _ensure_database_exists(self):
        """Ensure database and tables exist."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                try:
                    self._create_schema(conn)
                    conn.commit()
                finally:
                    conn.close()
        except sqlite3.Error as e:
            # Log error but don't crash
            raise RuntimeError(f"Database initialization error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {str(e)}")
    
    def _create_schema(self, conn: sqlite3.Connection):
        """
        Create database schema.
        
        Args:
            conn: Database connection
        """
        cursor = conn.cursor()
        
        # Advisory logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advisory_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                module_name TEXT NOT NULL,
                advisory_state TEXT NOT NULL,
                confidence REAL NOT NULL,
                data_json TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Create index on timestamp for efficient queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_advisory_logs_timestamp 
            ON advisory_logs(timestamp)
        """)
        
        # Create index on module_name
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_advisory_logs_module 
            ON advisory_logs(module_name)
        """)
        
        # Create index on advisory_state
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_advisory_logs_state 
            ON advisory_logs(advisory_state)
        """)
        
        # Acknowledgments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acknowledgments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                item_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                acknowledged_by TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Create index on timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_acknowledgments_timestamp 
            ON acknowledgments(timestamp)
        """)
        
        # Create index on item_id
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_acknowledgments_item_id 
            ON acknowledgments(item_id)
        """)
        
        # System events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data_json TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Create index on timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_events_timestamp 
            ON system_events(timestamp)
        """)
        
        # Create index on event_type
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_events_type 
            ON system_events(event_type)
        """)
    
    def log_advisory(
        self,
        module_name: str,
        advisory_state: str,
        confidence: float,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Log an advisory output.
        
        Args:
            module_name: Name of the module
            advisory_state: Advisory state
            confidence: Confidence value [0.0, 1.0]
            data: Advisory data dictionary
            metadata: Optional metadata dictionary
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Log entry ID (0 on error)
        """
        # Input validation
        if not isinstance(module_name, str) or not module_name:
            module_name = "unknown"
        
        if not isinstance(advisory_state, str) or not advisory_state:
            advisory_state = "NORMAL"
        
        confidence = max(0.0, min(1.0, float(confidence))) if isinstance(confidence, (int, float)) else 0.0
        
        if not isinstance(data, dict):
            data = {}
        
        if metadata is not None and not isinstance(metadata, dict):
            metadata = None
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.utcnow()
        
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO advisory_logs 
                        (timestamp, module_name, advisory_state, confidence, data_json, metadata_json)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp.isoformat(),
                        str(module_name)[:100],  # Limit length
                        str(advisory_state)[:50],  # Limit length
                        confidence,
                        json.dumps(data, default=str),
                        json.dumps(metadata, default=str) if metadata else None
                    ))
                    log_id = cursor.lastrowid
                    conn.commit()
                    return log_id if log_id else 0
                finally:
                    conn.close()
        except sqlite3.Error:
            # Fail silently - don't crash system
            return 0
        except Exception:
            # Fail silently - don't crash system
            return 0
    
    def log_acknowledgment(
        self,
        item_id: str,
        item_type: str,
        acknowledged_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Log a human acknowledgment.
        
        Args:
            item_id: ID of the acknowledged item
            item_type: Type of the item
            acknowledged_by: Optional identifier of who acknowledged
            metadata: Optional metadata dictionary
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Log entry ID (0 on error)
        """
        # Input validation
        if not isinstance(item_id, str) or not item_id:
            return 0
        
        if not isinstance(item_type, str) or not item_type:
            item_type = "unknown"
        
        if acknowledged_by is not None and not isinstance(acknowledged_by, str):
            acknowledged_by = None
        
        if metadata is not None and not isinstance(metadata, dict):
            metadata = None
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.utcnow()
        
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO acknowledgments 
                        (timestamp, item_id, item_type, acknowledged_by, metadata_json)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        timestamp.isoformat(),
                        str(item_id)[:200],  # Limit length
                        str(item_type)[:100],  # Limit length
                        str(acknowledged_by)[:100] if acknowledged_by else None,  # Limit length
                        json.dumps(metadata, default=str) if metadata else None
                    ))
                    log_id = cursor.lastrowid
                    conn.commit()
                    return log_id if log_id else 0
                finally:
                    conn.close()
        except sqlite3.Error:
            # Fail silently - don't crash system
            return 0
        except Exception:
            # Fail silently - don't crash system
            return 0
    
    def log_system_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Log a system event.
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
            metadata: Optional metadata dictionary
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Log entry ID
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_events 
                    (timestamp, event_type, event_data_json, metadata_json)
                    VALUES (?, ?, ?, ?)
                """, (
                    timestamp.isoformat(),
                    event_type,
                    json.dumps(event_data, default=str),
                    json.dumps(metadata, default=str) if metadata else None
                ))
                log_id = cursor.lastrowid
                conn.commit()
                return log_id
            finally:
                conn.close()
    
    def query_advisory_logs(
        self,
        module_name: Optional[str] = None,
        advisory_state: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query advisory logs.
        
        Args:
            module_name: Filter by module name
            advisory_state: Filter by advisory state
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of log entries (empty list on error)
        """
        # Input validation
        if limit is not None:
            limit = max(1, min(10000, int(limit))) if isinstance(limit, (int, float)) else None
        
        if offset is not None:
            offset = max(0, int(offset)) if isinstance(offset, (int, float)) else None
        
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                try:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    query = "SELECT * FROM advisory_logs WHERE 1=1"
                    params = []
                    
                    if module_name:
                        query += " AND module_name = ?"
                        params.append(module_name)
                    
                    if advisory_state:
                        query += " AND advisory_state = ?"
                        params.append(advisory_state)
                    
                    if start_timestamp:
                        query += " AND timestamp >= ?"
                        params.append(start_timestamp.isoformat())
                    
                    if end_timestamp:
                        query += " AND timestamp <= ?"
                        params.append(end_timestamp.isoformat())
                    
                    query += " ORDER BY timestamp DESC"
                    
                    if limit:
                        query += " LIMIT ?"
                        params.append(limit)
                    
                    if offset:
                        query += " OFFSET ?"
                        params.append(offset)
                    
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        result = dict(row)
                        result['data'] = json.loads(result['data_json'])
                        if result['metadata_json']:
                            result['metadata'] = json.loads(result['metadata_json'])
                        del result['data_json']
                        del result['metadata_json']
                        results.append(result)
                    
                    return results
                finally:
                    conn.close()
        except sqlite3.Error:
            # Fail silently - don't crash system
            return []
        except Exception:
            # Fail silently - don't crash system
            return []
    
    def query_acknowledgments(
        self,
        item_id: Optional[str] = None,
        item_type: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query acknowledgment logs.
        
        Args:
            item_id: Filter by item ID
            item_type: Filter by item type
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of acknowledgment entries
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM acknowledgments WHERE 1=1"
                params = []
                
                if item_id:
                    query += " AND item_id = ?"
                    params.append(item_id)
                
                if item_type:
                    query += " AND item_type = ?"
                    params.append(item_type)
                
                if start_timestamp:
                    query += " AND timestamp >= ?"
                    params.append(start_timestamp.isoformat())
                
                if end_timestamp:
                    query += " AND timestamp <= ?"
                    params.append(end_timestamp.isoformat())
                
                query += " ORDER BY timestamp DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                if offset:
                    query += " OFFSET ?"
                    params.append(offset)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    if result['metadata_json']:
                        result['metadata'] = json.loads(result['metadata_json'])
                    del result['metadata_json']
                    results.append(result)
                
                return results
            finally:
                conn.close()
    
    def query_system_events(
        self,
        event_type: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query system event logs.
        
        Args:
            event_type: Filter by event type
            start_timestamp: Start timestamp filter
            end_timestamp: End timestamp filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of system event entries
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM system_events WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if start_timestamp:
                    query += " AND timestamp >= ?"
                    params.append(start_timestamp.isoformat())
                
                if end_timestamp:
                    query += " AND timestamp <= ?"
                    params.append(end_timestamp.isoformat())
                
                query += " ORDER BY timestamp DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                if offset:
                    query += " OFFSET ?"
                    params.append(offset)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    result['event_data'] = json.loads(result['event_data_json'])
                    if result['metadata_json']:
                        result['metadata'] = json.loads(result['metadata_json'])
                    del result['event_data_json']
                    del result['metadata_json']
                    results.append(result)
                
                return results
            finally:
                conn.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count advisory logs
                cursor.execute("SELECT COUNT(*) FROM advisory_logs")
                stats['advisory_logs_count'] = cursor.fetchone()[0]
                
                # Count acknowledgments
                cursor.execute("SELECT COUNT(*) FROM acknowledgments")
                stats['acknowledgments_count'] = cursor.fetchone()[0]
                
                # Count system events
                cursor.execute("SELECT COUNT(*) FROM system_events")
                stats['system_events_count'] = cursor.fetchone()[0]
                
                # Get earliest and latest timestamps
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM advisory_logs")
                row = cursor.fetchone()
                if row[0]:
                    stats['earliest_log'] = row[0]
                    stats['latest_log'] = row[1]
                
                return stats
            finally:
                conn.close()

