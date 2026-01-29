"""
Advisory Logger

Main logging engine for advisory outputs.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from abhedya.logging_and_audit.database import AuditDatabase
from abhedya.logging_and_audit.models import (
    LogModule,
    AdvisoryState,
    EventType
)


class AdvisoryLogger:
    """
    Advisory logger for system modules.
    
    Provides immutable logging of advisory outputs.
    """
    
    def __init__(self, db_path: str = "abhedya_audit.db"):
        """
        Initialize advisory logger.
        
        Args:
            db_path: Path to SQLite database file
        """
        self._db = AuditDatabase(db_path)
    
    def log_early_warning(
        self,
        warning_state: str,
        confidence: float,
        reasoning: Any,
        trend_analysis: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log early warning system advisory output.
        
        Args:
            warning_state: Warning state (NORMAL, ELEVATED, HIGH)
            confidence: Confidence value [0.0, 1.0]
            reasoning: Reasoning (list or string)
            trend_analysis: Optional trend analysis data
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        data = {
            'warning_state': warning_state,
            'confidence': confidence,
            'reasoning': reasoning if isinstance(reasoning, list) else [reasoning],
            'trend_analysis': trend_analysis
        }
        
        return self._db.log_advisory(
            module_name=LogModule.EARLY_WARNING.value,
            advisory_state=warning_state,
            confidence=confidence,
            data=data,
            metadata=metadata
        )
    
    def log_ew_analysis(
        self,
        ew_state: str,
        confidence: float,
        spectral_features: Optional[Dict[str, Any]] = None,
        anomaly_detection: Optional[Dict[str, Any]] = None,
        reasoning: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log electronic warfare analysis advisory output.
        
        Args:
            ew_state: EW state (NORMAL, ANOMALOUS)
            confidence: Confidence value [0.0, 1.0]
            spectral_features: Optional spectral features
            anomaly_detection: Optional anomaly detection results
            reasoning: Optional reasoning
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        data = {
            'ew_state': ew_state,
            'confidence': confidence,
            'spectral_features': spectral_features,
            'anomaly_detection': anomaly_detection,
            'reasoning': reasoning if isinstance(reasoning, list) else [reasoning] if reasoning else []
        }
        
        return self._db.log_advisory(
            module_name=LogModule.EW_ANALYSIS.value,
            advisory_state=ew_state,
            confidence=confidence,
            data=data,
            metadata=metadata
        )
    
    def log_cybersecurity(
        self,
        cybersecurity_state: str,
        confidence: float,
        affected_subsystem: Optional[str] = None,
        integrity_check: Optional[Dict[str, Any]] = None,
        anomaly_detection: Optional[Dict[str, Any]] = None,
        reasoning: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log cybersecurity advisory output.
        
        Args:
            cybersecurity_state: Cybersecurity state (NORMAL, SUSPICIOUS, ALERT)
            confidence: Confidence value [0.0, 1.0]
            affected_subsystem: Optional affected subsystem
            integrity_check: Optional integrity check results
            anomaly_detection: Optional anomaly detection results
            reasoning: Optional reasoning
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        data = {
            'cybersecurity_state': cybersecurity_state,
            'confidence': confidence,
            'affected_subsystem': affected_subsystem,
            'integrity_check': integrity_check,
            'anomaly_detection': anomaly_detection,
            'reasoning': reasoning if isinstance(reasoning, list) else [reasoning] if reasoning else []
        }
        
        return self._db.log_advisory(
            module_name=LogModule.CYBERSECURITY.value,
            advisory_state=cybersecurity_state,
            confidence=confidence,
            data=data,
            metadata=metadata
        )
    
    def log_dashboard_acknowledgment(
        self,
        item_id: str,
        item_type: str,
        acknowledged_by: Optional[str] = None,
        item_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log dashboard acknowledgment.
        
        Args:
            item_id: ID of the acknowledged item
            item_type: Type of the item
            acknowledged_by: Optional identifier of who acknowledged
            item_data: Optional item data
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        ack_metadata = metadata or {}
        if item_data:
            ack_metadata['item_data'] = item_data
        
        return self._db.log_acknowledgment(
            item_id=item_id,
            item_type=item_type,
            acknowledged_by=acknowed_by,
            metadata=ack_metadata
        )
    
    def log_threat_assessment(
        self,
        threat_level: str,
        confidence: float,
        risk_score: Optional[float] = None,
        risk_factors: Optional[Dict[str, Any]] = None,
        reasoning: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log threat assessment advisory output.
        
        Args:
            threat_level: Threat level (LOW, MEDIUM, HIGH, CRITICAL)
            confidence: Confidence value [0.0, 1.0]
            risk_score: Optional risk score
            risk_factors: Optional risk factors
            reasoning: Optional reasoning
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        data = {
            'threat_level': threat_level,
            'confidence': confidence,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'reasoning': reasoning if isinstance(reasoning, list) else [reasoning] if reasoning else []
        }
        
        return self._db.log_advisory(
            module_name=LogModule.THREAT_ASSESSMENT.value,
            advisory_state=threat_level,
            confidence=confidence,
            data=data,
            metadata=metadata
        )
    
    def log_intent_assessment(
        self,
        track_id: Optional[str],
        transit_probability: float,
        surveillance_probability: float,
        hostile_probability: float,
        intent_confidence: float,
        reasoning: Optional[Any] = None,
        is_training_mode: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log intent assessment advisory output.
        
        Args:
            track_id: Optional track ID
            transit_probability: Transit intent probability [0.0, 1.0]
            surveillance_probability: Surveillance intent probability [0.0, 1.0]
            hostile_probability: Hostile intent probability [0.0, 1.0]
            intent_confidence: Intent confidence [0.0, 1.0]
            reasoning: Optional reasoning
            is_training_mode: Training mode flag
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        # Determine primary intent category for advisory state
        if hostile_probability >= max(transit_probability, surveillance_probability):
            advisory_state = "HOSTILE_INTENT"
        elif surveillance_probability >= transit_probability:
            advisory_state = "SURVEILLANCE_INTENT"
        else:
            advisory_state = "TRANSIT_INTENT"
        
        data = {
            'track_id': track_id,
            'transit_probability': transit_probability,
            'surveillance_probability': surveillance_probability,
            'hostile_probability': hostile_probability,
            'intent_confidence': intent_confidence,
            'reasoning': reasoning if isinstance(reasoning, list) else [reasoning] if reasoning else [],
            'is_training_mode': is_training_mode
        }
        
        log_metadata = metadata or {}
        log_metadata['is_training_mode'] = is_training_mode
        
        return self._db.log_advisory(
            module_name=LogModule.INTENT_INFERENCE.value,
            advisory_state=advisory_state,
            confidence=intent_confidence,
            data=data,
            metadata=log_metadata
        )
    
    def log_advisory_state_change(
        self,
        old_state: str,
        new_state: str,
        module_name: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log advisory state change.
        
        Args:
            old_state: Previous advisory state
            new_state: New advisory state
            module_name: Module name
            confidence: Confidence value [0.0, 1.0]
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        event_data = {
            'old_state': old_state,
            'new_state': new_state,
            'module_name': module_name,
            'confidence': confidence
        }
        
        return self._db.log_system_event(
            event_type=EventType.ADVISORY_STATE_CHANGE.value,
            event_data=event_data,
            metadata=metadata
        )
    
    def log_system_startup(self, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Log system startup.
        
        Args:
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        return self._db.log_system_event(
            event_type=EventType.SYSTEM_STARTUP.value,
            event_data={'timestamp': datetime.utcnow().isoformat()},
            metadata=metadata
        )
    
    def log_system_shutdown(self, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Log system shutdown.
        
        Args:
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        return self._db.log_system_event(
            event_type=EventType.SYSTEM_SHUTDOWN.value,
            event_data={'timestamp': datetime.utcnow().isoformat()},
            metadata=metadata
        )
    
    def log_error(
        self,
        error_message: str,
        error_context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log system error.
        
        Args:
            error_message: Error message
            error_context: Optional error context
            metadata: Optional metadata
            
        Returns:
            Log entry ID
        """
        event_data = {
            'error_message': error_message,
            'error_context': error_context
        }
        
        return self._db.log_system_event(
            event_type=EventType.ERROR.value,
            event_data=event_data,
            metadata=metadata
        )
    
    def query_advisory_logs(
        self,
        module_name: Optional[str] = None,
        advisory_state: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> list:
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
            List of log entries
        """
        return self._db.query_advisory_logs(
            module_name=module_name,
            advisory_state=advisory_state,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit,
            offset=offset
        )
    
    def query_acknowledgments(
        self,
        item_id: Optional[str] = None,
        item_type: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> list:
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
        return self._db.query_acknowledgments(
            item_id=item_id,
            item_type=item_type,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit,
            offset=offset
        )
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self._db.get_database_stats()

