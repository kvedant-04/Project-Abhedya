"""
Human-in-the-loop interface.

Manages presentation of recommendations to human operators and
collection of approval decisions. This is a critical safety component.
"""

import time
from typing import Optional, Dict
from datetime import datetime
from threading import Lock

from abhedya.core.interfaces import IHumanInterface
from abhedya.core.models import AdvisoryRecommendation
from abhedya.core.constants import (
    MIN_HUMAN_RESPONSE_TIME,
    MANDATORY_HUMAN_APPROVAL
)


class HumanInterface(IHumanInterface):
    """
    Human-in-the-loop interface.
    
    This interface ensures all recommendations are presented to
    human operators and approval is obtained before any actions
    (outside this system) can be taken.
    """
    
    def __init__(
        self,
        auto_approve: bool = False,  # For testing only
        default_timeout: float = 300.0  # 5 minutes default
    ):
        """
        Initialize human interface.
        
        Args:
            auto_approve: Auto-approve for testing (should be False in production)
            default_timeout: Default timeout for approval requests (seconds)
        """
        self.auto_approve = auto_approve
        self.default_timeout = default_timeout
        self.pending_approvals: Dict[str, Dict] = {}
        self.approval_lock = Lock()
        
        # Safety check
        if auto_approve and MANDATORY_HUMAN_APPROVAL:
            raise RuntimeError(
                "CRITICAL: Auto-approval cannot be enabled when "
                "mandatory human approval is required"
            )
    
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
        if not recommendation.requires_human_approval:
            # This should never happen due to model validation,
            # but we check anyway for safety
            raise RuntimeError(
                "CRITICAL: Recommendation must require human approval"
            )
        
        # Store pending approval
        with self.approval_lock:
            self.pending_approvals[recommendation.recommendation_id] = {
                "recommendation": recommendation,
                "presented_at": datetime.now(),
                "status": "PENDING",
                "approved": None
            }
        
        # In a real system, this would:
        # - Display recommendation on operator console
        # - Send alert/notification
        # - Log presentation event
        # - Wait for operator response
        
        # For simulation, we log the presentation
        self._log_presentation(recommendation)
        
        return True
    
    def _log_presentation(self, recommendation: AdvisoryRecommendation):
        """Log recommendation presentation (for audit)."""
        # In production, this would integrate with audit logger
        print(f"\n{'='*60}")
        print("RECOMMENDATION PRESENTED TO HUMAN OPERATOR")
        print(f"{'='*60}")
        print(f"Recommendation ID: {recommendation.recommendation_id}")
        print(f"Track ID: {recommendation.track_id}")
        print(f"Action: {recommendation.action.value}")
        print(f"Threat Level: {recommendation.threat_level.value}")
        print(f"Confidence: {recommendation.confidence:.1%}")
        print(f"Probability: {recommendation.probability:.1%}")
        print(f"\nReasoning:\n{recommendation.reasoning}")
        print(f"\n{'='*60}\n")
    
    def get_human_approval(
        self,
        recommendation_id: str,
        timeout: Optional[float] = None
    ) -> Optional[bool]:
        """
        Wait for human approval decision.
        
        Args:
            recommendation_id: ID of recommendation
            timeout: Maximum time to wait (seconds, None = use default)
            
        Returns:
            True if approved, False if rejected, None if timeout
        """
        timeout = timeout or self.default_timeout
        
        if self.auto_approve:
            # For testing only - simulate approval after minimum response time
            time.sleep(MIN_HUMAN_RESPONSE_TIME)
            self._record_approval(recommendation_id, True)
            return True
        
        # In a real system, this would:
        # - Poll operator interface for response
        # - Wait for operator input
        # - Handle timeout
        
        # For simulation, we return None (timeout)
        # In production, this would integrate with actual operator interface
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            with self.approval_lock:
                if recommendation_id in self.pending_approvals:
                    approval_data = self.pending_approvals[recommendation_id]
                    if approval_data["status"] != "PENDING":
                        return approval_data["approved"]
            
            time.sleep(0.1)  # Poll interval
        
        # Timeout
        return None
    
    def _record_approval(
        self,
        recommendation_id: str,
        approved: bool
    ):
        """Record human approval decision."""
        with self.approval_lock:
            if recommendation_id in self.pending_approvals:
                self.pending_approvals[recommendation_id]["status"] = "RESOLVED"
                self.pending_approvals[recommendation_id]["approved"] = approved
                self.pending_approvals[recommendation_id]["decided_at"] = datetime.now()
    
    def simulate_human_approval(
        self,
        recommendation_id: str,
        approved: bool
    ):
        """
        Simulate human approval (for testing/demonstration).
        
        In production, this would not exist - approvals come from
        actual human operators.
        
        Args:
            recommendation_id: ID of recommendation
            approved: Approval decision (True/False)
        """
        if not self.auto_approve:
            # Simulate minimum response time
            time.sleep(MIN_HUMAN_RESPONSE_TIME)
        
        self._record_approval(recommendation_id, approved)
    
    def get_pending_recommendations(self) -> list:
        """Get list of pending recommendations."""
        with self.approval_lock:
            pending = [
                data["recommendation"]
                for data in self.pending_approvals.values()
                if data["status"] == "PENDING"
            ]
        return pending
    
    def get_approval_status(self, recommendation_id: str) -> Optional[Dict]:
        """Get approval status for a recommendation."""
        with self.approval_lock:
            if recommendation_id in self.pending_approvals:
                return self.pending_approvals[recommendation_id].copy()
        return None

