"""
Core data models for the Abhedya Air Defense System.

All models enforce strict typing and validation to ensure
deterministic, auditable behavior.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class EntityType(str, Enum):
    """Classification of detected entities."""
    UNKNOWN = "UNKNOWN"
    FRIENDLY = "FRIENDLY"
    HOSTILE = "HOSTILE"
    NEUTRAL = "NEUTRAL"
    CIVILIAN = "CIVILIAN"


class ThreatLevel(str, Enum):
    """Threat assessment levels (advisory only)."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SensorType(str, Enum):
    """Types of sensor systems."""
    RADAR = "RADAR"
    IFF = "IFF"  # Identification Friend or Foe
    OPTICAL = "OPTICAL"
    ACOUSTIC = "ACOUSTIC"


class AdvisoryAction(str, Enum):
    """Advisory actions (informational only, no execution)."""
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    ALERT = "ALERT"
    TRACK = "TRACK"
    NO_ACTION = "NO_ACTION"


class Coordinates(BaseModel):
    """3D spatial coordinates."""
    x: float = Field(..., description="X coordinate (meters)")
    y: float = Field(..., description="Y coordinate (meters)")
    z: float = Field(..., description="Z coordinate (meters)")
    
    @validator('x', 'y', 'z')
    def validate_coordinates(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError("Coordinates must be numeric")
        return float(v)


class Velocity(BaseModel):
    """Velocity vector."""
    vx: float = Field(..., description="Velocity in X direction (m/s)")
    vy: float = Field(..., description="Velocity in Y direction (m/s)")
    vz: float = Field(..., description="Velocity in Z direction (m/s)")
    
    @property
    def speed(self) -> float:
        """Calculate speed magnitude."""
        import math
        return math.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
    
    @property
    def heading(self) -> float:
        """Calculate horizontal heading in degrees."""
        import math
        return math.degrees(math.atan2(self.vy, self.vx))


class SensorReading(BaseModel):
    """Raw sensor reading from detection system."""
    sensor_id: str = Field(..., description="Unique sensor identifier")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    timestamp: datetime = Field(default_factory=datetime.now)
    position: Coordinates = Field(..., description="Detected position")
    velocity: Optional[Velocity] = Field(None, description="Detected velocity")
    signal_strength: float = Field(..., ge=0.0, le=1.0, description="Signal strength (0-1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional sensor data")


class Track(BaseModel):
    """Tracked entity with fusion of multiple sensor readings."""
    track_id: str = Field(..., description="Unique track identifier")
    entity_type: EntityType = Field(default=EntityType.UNKNOWN, description="Classified entity type")
    position: Coordinates = Field(..., description="Current position")
    velocity: Optional[Velocity] = Field(None, description="Current velocity")
    threat_level: ThreatLevel = Field(default=ThreatLevel.NONE, description="Assessed threat level")
    first_detected: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Track confidence (0-1)")
    sensor_readings: List[SensorReading] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def update(self, reading: SensorReading):
        """Update track with new sensor reading."""
        self.position = reading.position
        self.velocity = reading.velocity
        self.last_updated = reading.timestamp
        self.sensor_readings.append(reading)


class AdvisoryRecommendation(BaseModel):
    """Advisory recommendation (informational only, no execution)."""
    recommendation_id: str = Field(..., description="Unique recommendation identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    track_id: str = Field(..., description="Associated track")
    action: AdvisoryAction = Field(..., description="Recommended action (advisory only)")
    threat_level: ThreatLevel = Field(..., description="Associated threat level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence")
    reasoning: str = Field(..., description="Explanation of recommendation")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability assessment")
    requires_human_approval: bool = Field(default=True, description="Always requires human approval")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('requires_human_approval')
    def enforce_human_approval(cls, v):
        """Ensure human approval is always required."""
        return True  # Always True, cannot be overridden


class SystemState(BaseModel):
    """Current state of the Abhedya system."""
    state_id: str = Field(..., description="State identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    active_tracks: List[Track] = Field(default_factory=list)
    pending_recommendations: List[AdvisoryRecommendation] = Field(default_factory=list)
    system_mode: str = Field(default="MONITORING", description="System operational mode")
    human_operator_present: bool = Field(default=True, description="Human operator status")
    metadata: Dict[str, Any] = Field(default_factory=dict)

