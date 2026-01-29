"""
Live Data Stub Provider

Safe placeholder for live data in development/demo mode.
Returns empty or minimal data structures to indicate "no live data available".

ADVISORY ONLY - No real-world data connections.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class LiveStubProvider:
    """
    Safe placeholder for live data provider.
    
    Returns empty or minimal data structures to indicate "no live data available".
    This allows the dashboard to function in development/demo mode without
    requiring actual sensor/backend connections.
    """
    
    @staticmethod
    def get_tracking_data() -> List[Dict[str, Any]]:
        """
        Get tracking data (stub - returns empty list).
        
        Returns:
            Empty list indicating no live data available
        """
        return []
    
    @staticmethod
    def get_early_warning_data() -> Optional[Dict[str, Any]]:
        """
        Get early warning data (stub - returns None).
        
        Returns:
            None indicating no live data available
        """
        return None
    
    @staticmethod
    def get_ew_analysis_data() -> Optional[Dict[str, Any]]:
        """
        Get electronic warfare analysis data (stub - returns None).
        
        Returns:
            None indicating no live data available
        """
        return None
    
    @staticmethod
    def get_cybersecurity_data() -> Optional[Dict[str, Any]]:
        """
        Get cybersecurity data (stub - returns None).
        
        Returns:
            None indicating no live data available
        """
        return None
    
    @staticmethod
    def get_threat_assessment_data() -> Optional[Dict[str, Any]]:
        """
        Get threat assessment data (stub - returns None).
        
        Returns:
            None indicating no live data available
        """
        return None
    
    @staticmethod
    def get_intent_assessment_data() -> Optional[Dict[str, Any]]:
        """
        Get intent assessment data (stub - returns None).
        
        Returns:
            None indicating no live data available
        """
        return None
    
    @staticmethod
    def get_advisory_state() -> Optional[Dict[str, Any]]:
        """
        Get advisory state (stub - returns safe default).
        
        Returns:
            Safe default advisory state (MONITORING_ONLY)
        """
        return {
            'advisory_state': 'MONITORING_ONLY',
            'confidence': 0.0,
            'reasoning': ['No live data available - monitoring only'],
            'timestamp': datetime.now().isoformat(),
            'is_live': True,
            'is_simulation': False
        }
