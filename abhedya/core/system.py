"""
Main Abhedya Air Defense System class.

This is the central orchestrator that coordinates all system components
while enforcing ethical constraints and fail-safe defaults.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from abhedya.core.models import (
    SystemState,
    Track,
    AdvisoryRecommendation,
    EntityType,
    ThreatLevel,
    AdvisoryAction
)
from abhedya.core.constants import (
    SYSTEM_MODE_MONITORING,
    DEFAULT_ACTION,
    DEFAULT_THREAT_LEVEL,
    MANDATORY_HUMAN_APPROVAL
)
from abhedya.core.interfaces import (
    ISensor,
    IThreatAssessor,
    IAdvisoryEngine,
    IHumanInterface,
    IAuditLogger
)


class AbhedyaSystem:
    """
    Main Abhedya Air Defense System.
    
    IMPORTANT: This system is advisory and analytical only.
    It does not control, authorize, or execute any real-world actions.
    """
    
    def __init__(
        self,
        sensors: Optional[List[ISensor]] = None,
        threat_assessor: Optional[IThreatAssessor] = None,
        advisory_engine: Optional[IAdvisoryEngine] = None,
        human_interface: Optional[IHumanInterface] = None,
        audit_logger: Optional[IAuditLogger] = None
    ):
        """
        Initialize Abhedya system with fail-safe defaults.
        
        Args:
            sensors: List of sensor modules (optional)
            threat_assessor: Threat assessment module (optional)
            advisory_engine: Advisory decision-support module (optional)
            human_interface: Human-in-the-loop interface (optional)
            audit_logger: Audit logging module (optional)
        """
        self.sensors = sensors or []
        self.threat_assessor = threat_assessor
        self.advisory_engine = advisory_engine
        self.human_interface = human_interface
        self.audit_logger = audit_logger
        
        # System state
        self.state = SystemState(
            state_id=str(uuid.uuid4()),
            system_mode=SYSTEM_MODE_MONITORING,
            human_operator_present=True  # Default: assume human present
        )
        
        # Track management
        self.tracks: Dict[str, Track] = {}
        
        # Safety constraints
        self._enforce_safety_constraints()
        
        # Log initialization
        if self.audit_logger:
            self.audit_logger.log_event(
                "SYSTEM_INITIALIZED",
                {
                    "system_id": self.state.state_id,
                    "mode": self.state.system_mode,
                    "sensor_count": len(self.sensors)
                }
            )
    
    def _enforce_safety_constraints(self):
        """Enforce mandatory safety constraints."""
        # Ensure human approval is always required
        if not MANDATORY_HUMAN_APPROVAL:
            raise RuntimeError(
                "CRITICAL: Human approval requirement cannot be disabled"
            )
    
    def add_sensor(self, sensor: ISensor):
        """Add a sensor module to the system."""
        if not isinstance(sensor, ISensor):
            raise TypeError("Sensor must implement ISensor interface")
        
        self.sensors.append(sensor)
        
        if self.audit_logger:
            self.audit_logger.log_event(
                "SENSOR_ADDED",
                {
                    "sensor_id": sensor.get_sensor_id(),
                    "sensor_type": sensor.get_sensor_type()
                }
            )
    
    def update_sensors(self) -> List:
        """
        Collect sensor readings from all sensors.
        
        Returns:
            List of sensor readings
        """
        all_readings = []
        current_time = datetime.now()
        
        for sensor in self.sensors:
            try:
                readings = sensor.detect(current_time)
                all_readings.extend(readings)
            except Exception as e:
                # Log sensor errors but continue operation
                if self.audit_logger:
                    self.audit_logger.log_event(
                        "SENSOR_ERROR",
                        {
                            "sensor_id": sensor.get_sensor_id(),
                            "error": str(e)
                        }
                    )
        
        return all_readings
    
    def update_tracks(self, readings: List):
        """
        Update tracks with new sensor readings.
        
        Args:
            readings: List of sensor readings
        """
        from abhedya.core.models import SensorReading
        
        for reading in readings:
            if not isinstance(reading, SensorReading):
                continue
            
            # Simple track association (can be enhanced with fusion logic)
            # For now, associate by sensor and position proximity
            associated_track = self._find_or_create_track(reading)
            
            if associated_track:
                associated_track.update(reading)
                
                # Re-assess threat if assessor available
                if self.threat_assessor:
                    try:
                        associated_track = self.threat_assessor.assess_track(
                            associated_track
                        )
                        self.tracks[associated_track.track_id] = associated_track
                    except Exception as e:
                        if self.audit_logger:
                            self.audit_logger.log_event(
                                "ASSESSMENT_ERROR",
                                {
                                    "track_id": associated_track.track_id,
                                    "error": str(e)
                                }
                            )
    
    def _find_or_create_track(self, reading) -> Optional[Track]:
        """
        Find existing track or create new one for sensor reading.
        
        Simple implementation - can be enhanced with sophisticated
        track association algorithms.
        """
        from abhedya.core.models import Track, EntityType, ThreatLevel
        
        # Simple proximity-based association
        # In production, use proper track association algorithms
        for track in self.tracks.values():
            if self._is_reading_associated(reading, track):
                return track
        
        # Create new track
        new_track = Track(
            track_id=str(uuid.uuid4()),
            entity_type=EntityType.UNKNOWN,
            position=reading.position,
            velocity=reading.velocity,
            threat_level=ThreatLevel.NONE,
            confidence=reading.confidence
        )
        new_track.update(reading)
        self.tracks[new_track.track_id] = new_track
        
        if self.audit_logger:
            self.audit_logger.log_event(
                "TRACK_CREATED",
                {
                    "track_id": new_track.track_id,
                    "position": {
                        "x": reading.position.x,
                        "y": reading.position.y,
                        "z": reading.position.z
                    }
                }
            )
        
        return new_track
    
    def _is_reading_associated(self, reading, track) -> bool:
        """
        Determine if sensor reading belongs to existing track.
        
        Simple distance-based association.
        """
        import math
        
        distance = math.sqrt(
            (reading.position.x - track.position.x)**2 +
            (reading.position.y - track.position.y)**2 +
            (reading.position.z - track.position.z)**2
        )
        
        # Association threshold: 5000 meters (5 km)
        return distance < 5000.0
    
    def generate_advisories(self) -> List[AdvisoryRecommendation]:
        """
        Generate advisory recommendations for all active tracks.
        
        IMPORTANT: These are advisory only. No actions are executed.
        
        Returns:
            List of advisory recommendations
        """
        recommendations = []
        
        if not self.advisory_engine:
            return recommendations
        
        for track in self.tracks.values():
            try:
                recommendation = self.advisory_engine.generate_recommendation(
                    track,
                    self.state
                )
                
                if recommendation:
                    # Ensure human approval is required
                    recommendation.requires_human_approval = True
                    recommendations.append(recommendation)
                    
                    if self.audit_logger:
                        self.audit_logger.log_event(
                            "RECOMMENDATION_GENERATED",
                            {
                                "recommendation_id": recommendation.recommendation_id,
                                "track_id": track.track_id,
                                "action": recommendation.action.value,
                                "threat_level": recommendation.threat_level.value
                            }
                        )
            except Exception as e:
                if self.audit_logger:
                    self.audit_logger.log_event(
                        "ADVISORY_ERROR",
                        {
                            "track_id": track.track_id,
                            "error": str(e)
                        }
                    )
        
        return recommendations
    
    def present_to_human(self, recommendation: AdvisoryRecommendation) -> bool:
        """
        Present recommendation to human operator.
        
        Args:
            recommendation: Recommendation to present
            
        Returns:
            True if successfully presented
        """
        if not self.human_interface:
            # If no human interface, log and return False
            if self.audit_logger:
                self.audit_logger.log_event(
                    "HUMAN_INTERFACE_UNAVAILABLE",
                    {
                        "recommendation_id": recommendation.recommendation_id
                    }
                )
            return False
        
        try:
            return self.human_interface.present_recommendation(recommendation)
        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_event(
                    "HUMAN_INTERFACE_ERROR",
                    {
                        "recommendation_id": recommendation.recommendation_id,
                        "error": str(e)
                    }
                )
            return False
    
    def run_cycle(self):
        """
        Execute one system cycle:
        1. Collect sensor readings
        2. Update tracks
        3. Generate advisories
        4. Present to human (if interface available)
        
        This is the main operational loop.
        """
        # Update system state timestamp
        self.state.timestamp = datetime.now()
        
        # Step 1: Collect sensor readings
        readings = self.update_sensors()
        
        # Step 2: Update tracks
        self.update_tracks(readings)
        
        # Step 3: Generate advisory recommendations
        recommendations = self.generate_advisories()
        
        # Step 4: Present to human operator
        for recommendation in recommendations:
            self.present_to_human(recommendation)
        
        # Update system state
        self.state.active_tracks = list(self.tracks.values())
        self.state.pending_recommendations = recommendations
        
        if self.audit_logger:
            self.audit_logger.log_event(
                "CYCLE_COMPLETE",
                {
                    "readings_count": len(readings),
                    "tracks_count": len(self.tracks),
                    "recommendations_count": len(recommendations)
                }
            )
    
    def run_simulation(self, duration_seconds: float = 60.0, cycle_rate: float = 1.0):
        """
        Run simulation for specified duration.
        
        Args:
            duration_seconds: Simulation duration in seconds
            cycle_rate: Cycles per second
        """
        import time
        
        cycles = int(duration_seconds * cycle_rate)
        
        if self.audit_logger:
            self.audit_logger.log_event(
                "SIMULATION_STARTED",
                {
                    "duration_seconds": duration_seconds,
                    "cycle_rate": cycle_rate,
                    "total_cycles": cycles
                }
            )
        
        for cycle in range(cycles):
            self.run_cycle()
            time.sleep(1.0 / cycle_rate)
        
        if self.audit_logger:
            self.audit_logger.log_event(
                "SIMULATION_COMPLETE",
                {
                    "cycles_completed": cycles
                }
            )
    
    def get_state(self) -> SystemState:
        """Get current system state."""
        return self.state
    
    def get_tracks(self) -> List[Track]:
        """Get all active tracks."""
        return list(self.tracks.values())

