"""
Multi-Target Tracking Module

Tracks multiple targets simultaneously with:
- Unique and persistent track identifiers
- State estimation using Kalman Filters
- Probabilistic classification
- Track association and management
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from abhedya.tracking.models import (
    Track,
    TrackState,
    TrackIdentifier,
    ClassificationResult,
    ObjectType
)
from abhedya.tracking.kalman import KalmanFilter, KalmanState
from abhedya.tracking.classifier import ProbabilisticClassifier
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.infrastructure.config.config import (
    SystemPerformanceLimits,
    UncertaintyLimits
)


@dataclass
class TrackAssociation:
    """Association between detection and track."""
    track_id: str
    detection: Dict[str, Any]
    distance: float
    confidence: float


class MultiTargetTracker:
    """
    Multi-target tracker with Kalman filtering and probabilistic classification.
    
    Features:
    - Unique and persistent track identifiers
    - Kalman filter state estimation
    - Probabilistic classification (Drone, Aircraft, Unknown)
    - Track association using distance-based gating
    - Track lifecycle management
    """
    
    def __init__(
        self,
        association_threshold_meters: float = 5000.0,
        max_track_age_seconds: float = 60.0,
        min_updates_for_active: int = 3
    ):
        """
        Initialize multi-target tracker.
        
        Args:
            association_threshold_meters: Maximum distance for track association
            max_track_age_seconds: Maximum age without updates before termination
            min_updates_for_active: Minimum updates before track becomes active
        """
        self.association_threshold = association_threshold_meters
        self.max_track_age = max_track_age_seconds
        self.min_updates_for_active = min_updates_for_active
        
        # Tracking components
        self.kalman_filter = KalmanFilter()
        self.classifier = ProbabilisticClassifier()
        
        # Active tracks
        self.tracks: Dict[str, Track] = {}
        
        # Track history (for classification context)
        self.track_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def update(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[Track]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of new detections
            
        Returns:
            List of updated tracks
        """
        current_time = datetime.now()
        
        # Associate detections to existing tracks
        unassociated_detections = self._associate_detections(detections, current_time)
        
        # Create new tracks for unassociated detections
        for detection in unassociated_detections:
            self._create_new_track(detection, current_time)
        
        # Update track states
        self._update_track_states(current_time)
        
        # Remove stale tracks
        self._remove_stale_tracks(current_time)
        
        # Return active tracks
        return [track for track in self.tracks.values() if track.state == TrackState.ACTIVE]
    
    def _associate_detections(
        self,
        detections: List[Dict[str, Any]],
        current_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Associate detections to existing tracks.
        
        Args:
            detections: List of detections
            current_time: Current timestamp
            
        Returns:
            List of unassociated detections
        """
        unassociated = []
        
        for detection in detections:
            # Extract position
            pos_data = detection.get("position", {})
            if not pos_data:
                continue
            
            measurement = Coordinates(
                x=pos_data.get("x", 0.0),
                y=pos_data.get("y", 0.0),
                z=pos_data.get("z", 0.0)
            )
            
            # Find best matching track
            best_association = None
            best_distance = float('inf')
            
            for track_id, track in self.tracks.items():
                if track.state == TrackState.TERMINATED:
                    continue
                
                # Calculate distance to track
                distance = self._calculate_distance(measurement, track.position)
                
                if distance < self.association_threshold and distance < best_distance:
                    best_distance = distance
                    best_association = track_id
            
            # Associate to best track or mark as unassociated
            if best_association:
                self._update_track(best_association, detection, current_time)
            else:
                unassociated.append(detection)
        
        return unassociated
    
    def _create_new_track(
        self,
        detection: Dict[str, Any],
        current_time: datetime
    ):
        """Create a new track from detection."""
        # Extract position and velocity
        pos_data = detection.get("position", {})
        vel_data = detection.get("velocity", {})
        
        position = Coordinates(
            x=pos_data.get("x", 0.0),
            y=pos_data.get("y", 0.0),
            z=pos_data.get("z", 0.0)
        )
        
        velocity = None
        if vel_data:
            velocity = Velocity(
                vx=vel_data.get("vx", 0.0),
                vy=vel_data.get("vy", 0.0),
                vz=vel_data.get("vz", 0.0)
            )
        
        # Create track identifier
        track_id = f"track_{uuid.uuid4().hex[:8]}"
        identifier = TrackIdentifier(
            track_id=track_id,
            created_at=current_time,
            last_updated=current_time
        )
        
        # Classify object
        classification = self.classifier.classify(detection)
        
        # Initialize Kalman filter
        kalman_state = self.kalman_filter.initialize(
            position=position,
            velocity=velocity,
            timestamp=current_time.timestamp()
        )
        
        # Create track
        track = Track(
            identifier=identifier,
            state=TrackState.INITIALIZING,
            position=position,
            velocity=velocity,
            classification=classification,
            confidence=detection.get("confidence", 0.5),
            created_at=current_time,
            last_updated=current_time,
            metadata={
                "kalman_state": kalman_state,
                "detection_count": 1
            }
        )
        
        self.tracks[track_id] = track
        self.track_history[track_id] = [detection]
    
    def _update_track(
        self,
        track_id: str,
        detection: Dict[str, Any],
        current_time: datetime
    ):
        """Update existing track with new detection."""
        if track_id not in self.tracks:
            return
        
        track = self.tracks[track_id]
        
        # Extract measurement
        pos_data = detection.get("position", {})
        measurement = Coordinates(
            x=pos_data.get("x", 0.0),
            y=pos_data.get("y", 0.0),
            z=pos_data.get("z", 0.0)
        )
        
        # Get Kalman state
        kalman_state = track.metadata.get("kalman_state")
        if kalman_state is None:
            # Initialize if missing
            kalman_state = self.kalman_filter.initialize(
                position=track.position,
                velocity=track.velocity,
                timestamp=current_time.timestamp()
            )
        
        # Calculate time step
        dt = (current_time.timestamp() - kalman_state.timestamp)
        if dt <= 0:
            dt = 1.0  # Default to 1 second
        
        # Get measurement uncertainty
        uncertainty = detection.get("uncertainty", 0.1)
        measurement_noise = uncertainty * 100.0  # Scale to meters
        
        # Update Kalman filter
        updated_kalman = self.kalman_filter.predict_and_update(
            state=kalman_state,
            measurement=measurement,
            dt=dt,
            measurement_uncertainty=measurement_noise
        )
        
        # Update classification with historical context
        if track_id in self.track_history:
            self.track_history[track_id].append(detection)
            # Keep only recent history (last 10 detections)
            if len(self.track_history[track_id]) > 10:
                self.track_history[track_id] = self.track_history[track_id][-10:]
        else:
            self.track_history[track_id] = [detection]
        
        classification = self.classifier.classify(
            detection,
            historical_detections=self.track_history[track_id]
        )
        
        # Update track
        track.update(
            position=updated_kalman.position,
            velocity=updated_kalman.velocity,
            classification=classification,
            confidence=detection.get("confidence", track.confidence)
        )
        
        # Update metadata
        track.metadata["kalman_state"] = updated_kalman
        track.metadata["detection_count"] = track.metadata.get("detection_count", 0) + 1
        
        # Update track state based on update count
        if track.metadata["detection_count"] >= self.min_updates_for_active:
            track.state = TrackState.ACTIVE
    
    def _update_track_states(self, current_time: datetime):
        """Update track states based on age and updates."""
        for track in self.tracks.values():
            if track.state == TrackState.TERMINATED:
                continue
            
            time_since_update = (current_time - track.last_updated).total_seconds()
            
            if time_since_update > self.max_track_age:
                track.state = TrackState.TERMINATED
            elif time_since_update > self.max_track_age / 2:
                track.state = TrackState.COASTING
    
    def _remove_stale_tracks(self, current_time: datetime):
        """Remove stale terminated tracks."""
        to_remove = []
        for track_id, track in self.tracks.items():
            if track.state == TrackState.TERMINATED:
                age = (current_time - track.last_updated).total_seconds()
                if age > self.max_track_age * 2:
                    to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
            if track_id in self.track_history:
                del self.track_history[track_id]
    
    def _calculate_distance(self, pos1: Coordinates, pos2: Coordinates) -> float:
        """Calculate Euclidean distance between two positions."""
        import math
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        dz = pos1.z - pos2.z
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def get_tracks(self, state: Optional[TrackState] = None) -> List[Track]:
        """
        Get tracks, optionally filtered by state.
        
        Args:
            state: Optional track state filter
            
        Returns:
            List of tracks
        """
        if state is None:
            return list(self.tracks.values())
        return [track for track in self.tracks.values() if track.state == state]
    
    def get_track(self, track_id: str) -> Optional[Track]:
        """
        Get track by ID.
        
        Args:
            track_id: Track identifier
            
        Returns:
            Track or None if not found
        """
        return self.tracks.get(track_id)
    
    def clear_tracks(self):
        """Clear all tracks."""
        self.tracks.clear()
        self.track_history.clear()

