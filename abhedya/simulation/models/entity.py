"""
Simulation Entity Models

Mathematical models for simulating aerial entities (aircraft, drones, etc.)
in the sensor simulation system.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime
from enum import Enum

from abhedya.domain.value_objects import Coordinates, Velocity


class EntityType(str, Enum):
    """Types of entities that can be simulated."""
    COMMERCIAL_AIRCRAFT = "COMMERCIAL_AIRCRAFT"
    MILITARY_AIRCRAFT = "MILITARY_AIRCRAFT"
    DRONE = "DRONE"
    HELICOPTER = "HELICOPTER"
    UNKNOWN = "UNKNOWN"


class TrajectoryType(str, Enum):
    """Types of trajectory patterns for entity simulation."""
    LINEAR = "LINEAR"              # Straight-line trajectory
    CIRCULAR = "CIRCULAR"          # Circular orbit pattern
    APPROACHING = "APPROACHING"     # Approaching system origin
    DEPARTING = "DEPARTING"        # Departing from system origin
    PATROL = "PATROL"              # Patrol pattern (back and forth)
    HOVER = "HOVER"                # Hovering in place


@dataclass
class EntityCharacteristics:
    """
    Physical and behavioral characteristics of a simulated entity.
    Used to generate realistic sensor readings.
    """
    entity_type: EntityType
    typical_speed_meters_per_second: float
    typical_altitude_meters: float
    radar_cross_section: float  # RCS in square meters (0.0 to 1.0 scale)
    maneuverability: float  # Ability to change direction (0.0 to 1.0)
    size_category: str  # "SMALL", "MEDIUM", "LARGE"
    
    @classmethod
    def for_commercial_aircraft(cls) -> "EntityCharacteristics":
        """Create characteristics for commercial aircraft."""
        return cls(
            entity_type=EntityType.COMMERCIAL_AIRCRAFT,
            typical_speed_meters_per_second=250.0,  # ~900 km/h
            typical_altitude_meters=10000.0,  # 10 km
            radar_cross_section=0.8,  # Large RCS
            maneuverability=0.2,  # Low maneuverability
            size_category="LARGE"
        )
    
    @classmethod
    def for_military_aircraft(cls) -> "EntityCharacteristics":
        """Create characteristics for military aircraft."""
        return cls(
            entity_type=EntityType.MILITARY_AIRCRAFT,
            typical_speed_meters_per_second=400.0,  # ~1440 km/h
            typical_altitude_meters=8000.0,  # 8 km
            radar_cross_section=0.6,  # Medium RCS (stealth considerations)
            maneuverability=0.8,  # High maneuverability
            size_category="MEDIUM"
        )
    
    @classmethod
    def for_drone(cls) -> "EntityCharacteristics":
        """Create characteristics for drone."""
        return cls(
            entity_type=EntityType.DRONE,
            typical_speed_meters_per_second=50.0,  # ~180 km/h
            typical_altitude_meters=500.0,  # 500 m
            radar_cross_section=0.1,  # Small RCS
            maneuverability=0.9,  # Very high maneuverability
            size_category="SMALL"
        )
    
    @classmethod
    def for_helicopter(cls) -> "EntityCharacteristics":
        """Create characteristics for helicopter."""
        return cls(
            entity_type=EntityType.HELICOPTER,
            typical_speed_meters_per_second=80.0,  # ~288 km/h
            typical_altitude_meters=2000.0,  # 2 km
            radar_cross_section=0.4,  # Medium RCS
            maneuverability=0.7,  # High maneuverability
            size_category="MEDIUM"
        )


@dataclass
class SimulatedEntity:
    """
    A simulated aerial entity with position, velocity, and trajectory.
    """
    entity_id: str
    characteristics: EntityCharacteristics
    initial_position: Coordinates
    initial_velocity: Velocity
    trajectory_type: TrajectoryType
    trajectory_parameters: dict  # Parameters specific to trajectory type
    created_at: datetime
    
    def get_position_at_time(self, timestamp: datetime) -> Coordinates:
        """
        Calculate entity position at given timestamp based on trajectory.
        
        Args:
            timestamp: Target timestamp
            
        Returns:
            Coordinates at the given time
        """
        time_delta_seconds = (timestamp - self.created_at).total_seconds()
        
        if self.trajectory_type == TrajectoryType.LINEAR:
            return self._calculate_linear_position(time_delta_seconds)
        elif self.trajectory_type == TrajectoryType.CIRCULAR:
            return self._calculate_circular_position(time_delta_seconds)
        elif self.trajectory_type == TrajectoryType.APPROACHING:
            return self._calculate_approaching_position(time_delta_seconds)
        elif self.trajectory_type == TrajectoryType.DEPARTING:
            return self._calculate_departing_position(time_delta_seconds)
        elif self.trajectory_type == TrajectoryType.PATROL:
            return self._calculate_patrol_position(time_delta_seconds)
        elif self.trajectory_type == TrajectoryType.HOVER:
            return self.initial_position
        else:
            return self._calculate_linear_position(time_delta_seconds)
    
    def get_velocity_at_time(self, timestamp: datetime) -> Velocity:
        """
        Calculate entity velocity at given timestamp.
        
        Args:
            timestamp: Target timestamp
            
        Returns:
            Velocity at the given time
        """
        time_delta_seconds = (timestamp - self.created_at).total_seconds()
        
        if self.trajectory_type == TrajectoryType.LINEAR:
            return self.initial_velocity
        elif self.trajectory_type == TrajectoryType.HOVER:
            return Velocity(vx=0.0, vy=0.0, vz=0.0)
        else:
            # For other trajectories, calculate velocity from position change
            dt = 0.1  # Small time step
            pos1 = self.get_position_at_time(timestamp)
            pos2 = self.get_position_at_time(
                datetime.fromtimestamp(timestamp.timestamp() + dt)
            )
            return Velocity(
                vx=(pos2.x - pos1.x) / dt,
                vy=(pos2.y - pos1.y) / dt,
                vz=(pos2.z - pos1.z) / dt
            )
    
    def _calculate_linear_position(self, time_delta: float) -> Coordinates:
        """Calculate position for linear trajectory."""
        return Coordinates(
            x=self.initial_position.x + self.initial_velocity.vx * time_delta,
            y=self.initial_position.y + self.initial_velocity.vy * time_delta,
            z=self.initial_position.z + self.initial_velocity.vz * time_delta
        )
    
    def _calculate_circular_position(self, time_delta: float) -> Coordinates:
        """Calculate position for circular trajectory."""
        import math
        
        radius = self.trajectory_parameters.get("radius", 10000.0)
        angular_velocity = self.trajectory_parameters.get("angular_velocity", 0.001)
        center = self.trajectory_parameters.get("center", (0.0, 0.0, self.initial_position.z))
        
        angle = angular_velocity * time_delta
        return Coordinates(
            x=center[0] + radius * math.cos(angle),
            y=center[1] + radius * math.sin(angle),
            z=center[2]
        )
    
    def _calculate_approaching_position(self, time_delta: float) -> Coordinates:
        """Calculate position for approaching trajectory (towards origin)."""
        import math
        
        # Calculate direction to origin
        dx = -self.initial_position.x
        dy = -self.initial_position.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return self.initial_position
        
        # Normalize direction
        direction_x = dx / distance
        direction_y = dy / distance
        
        speed = math.sqrt(
            self.initial_velocity.vx**2 + self.initial_velocity.vy**2
        )
        
        return Coordinates(
            x=self.initial_position.x + direction_x * speed * time_delta,
            y=self.initial_position.y + direction_y * speed * time_delta,
            z=self.initial_position.z + self.initial_velocity.vz * time_delta
        )
    
    def _calculate_departing_position(self, time_delta: float) -> Coordinates:
        """Calculate position for departing trajectory (away from origin)."""
        import math
        
        # Calculate direction away from origin
        dx = self.initial_position.x
        dy = self.initial_position.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            # If at origin, use initial velocity direction
            speed = math.sqrt(
                self.initial_velocity.vx**2 + self.initial_velocity.vy**2
            )
            if speed > 0:
                direction_x = self.initial_velocity.vx / speed
                direction_y = self.initial_velocity.vy / speed
            else:
                direction_x = 1.0
                direction_y = 0.0
        else:
            direction_x = dx / distance
            direction_y = dy / distance
        
        speed = math.sqrt(
            self.initial_velocity.vx**2 + self.initial_velocity.vy**2
        )
        
        return Coordinates(
            x=self.initial_position.x + direction_x * speed * time_delta,
            y=self.initial_position.y + direction_y * speed * time_delta,
            z=self.initial_position.z + self.initial_velocity.vz * time_delta
        )
    
    def _calculate_patrol_position(self, time_delta: float) -> Coordinates:
        """Calculate position for patrol trajectory (back and forth)."""
        import math
        
        patrol_length = self.trajectory_parameters.get("patrol_length", 20000.0)
        patrol_speed = self.trajectory_parameters.get("patrol_speed", 100.0)
        patrol_direction = self.trajectory_parameters.get("patrol_direction", (1.0, 0.0))
        
        # Normalize direction
        dir_mag = math.sqrt(patrol_direction[0]**2 + patrol_direction[1]**2)
        if dir_mag > 0:
            dir_x = patrol_direction[0] / dir_mag
            dir_y = patrol_direction[1] / dir_mag
        else:
            dir_x = 1.0
            dir_y = 0.0
        
        # Calculate position along patrol line (sine wave for back and forth)
        distance_traveled = patrol_speed * time_delta
        position_along_line = (distance_traveled % (2 * patrol_length)) - patrol_length
        
        return Coordinates(
            x=self.initial_position.x + dir_x * position_along_line,
            y=self.initial_position.y + dir_y * position_along_line,
            z=self.initial_position.z
        )

