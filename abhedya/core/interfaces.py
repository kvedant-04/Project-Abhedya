"""
Core interfaces and abstract base classes.

All components must implement these interfaces to ensure
consistent, auditable behavior.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from abhedya.core.models import (
    SensorReading,
    Track,
    AdvisoryRecommendation,
    SystemState
)


class ISensor(ABC):
    """Interface for sensor simulation modules."""
    
    @abstractmethod
    def detect(self, timestamp: datetime) -> List[SensorReading]:
        """
        Simulate sensor detection at given timestamp.
        
        Returns:
            List of sensor readings (may be empty)
        """
        pass
    
    @abstractmethod
    def get_sensor_id(self) -> str:
        """Return unique sensor identifier."""
        pass
    
    @abstractmethod
    def get_sensor_type(self) -> str:
        """Return sensor type."""
        pass


class IThreatAssessor(ABC):
    """Interface for threat assessment modules."""
    
    @abstractmethod
    def assess_track(self, track: Track) -> Track:
        """
        Assess threat level and classify entity type for a track.
        
        Args:
            track: Track to assess
            
        Returns:
            Updated track with threat assessment
        """
        pass
    
    @abstractmethod
    def explain_assessment(self, track: Track) -> str:
        """
        Provide human-readable explanation of threat assessment.
        
        Args:
            track: Track to explain
            
        Returns:
            Explanation string
        """
        pass


class IAdvisoryEngine(ABC):
    """Interface for advisory decision-support modules."""
    
    @abstractmethod
    def generate_recommendation(
        self,
        track: Track,
        system_state: SystemState
    ) -> Optional[AdvisoryRecommendation]:
        """
        Generate advisory recommendation for a track.
        
        IMPORTANT: This is advisory only. No actions are executed.
        
        Args:
            track: Track to generate recommendation for
            system_state: Current system state
            
        Returns:
            Advisory recommendation or None if no recommendation
        """
        pass
    
    @abstractmethod
    def explain_recommendation(
        self,
        recommendation: AdvisoryRecommendation
    ) -> str:
        """
        Provide detailed explanation of recommendation reasoning.
        
        Args:
            recommendation: Recommendation to explain
            
        Returns:
            Detailed explanation string
        """
        pass


class IHumanInterface(ABC):
    """Interface for human-in-the-loop approval system."""
    
    @abstractmethod
    def present_recommendation(
        self,
        recommendation: AdvisoryRecommendation
    ) -> bool:
        """
        Present recommendation to human operator for review.
        
        Args:
            recommendation: Recommendation to present
            
        Returns:
            True if recommendation was presented successfully
        """
        pass
    
    @abstractmethod
    def get_human_approval(
        self,
        recommendation_id: str,
        timeout: float
    ) -> Optional[bool]:
        """
        Wait for human approval decision.
        
        Args:
            recommendation_id: ID of recommendation
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if approved, False if rejected, None if timeout
        """
        pass


class IAuditLogger(ABC):
    """Interface for audit and logging system."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass

