"""
Proximity Calculator Module

Estimates time-to-proximity for protected zones.
Uses classical mechanics to predict when object will reach protected zones.
"""

import math
from datetime import datetime
from typing import List, Optional

from abhedya.trajectory_analysis.models import ProximityEstimate
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.infrastructure.config.config import ProtectedAirspaceConfiguration


class ProximityCalculator:
    """
    Calculates time-to-proximity for protected zones.
    
    Uses classical mechanics to predict when an object will reach
    a protected zone based on current position and velocity.
    """
    
    def __init__(self):
        """Initialize proximity calculator."""
        pass
    
    def calculate_time_to_proximity(
        self,
        position: Coordinates,
        velocity: Velocity,
        zone_center: Coordinates,
        zone_radius_meters: float,
        zone_name: str = "PROTECTED_ZONE",
        timestamp: Optional[datetime] = None
    ) -> ProximityEstimate:
        """
        Calculate time to proximity for a protected zone.
        
        Uses classical mechanics: constant velocity model
        
        Args:
            position: Current position
            velocity: Current velocity
            zone_center: Center of protected zone
            zone_radius_meters: Radius of protected zone
            zone_name: Name of the zone
            timestamp: Current timestamp (default: now)
            
        Returns:
            ProximityEstimate
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Calculate current distance to zone center
        dx = position.x - zone_center.x
        dy = position.y - zone_center.y
        dz = position.z - zone_center.z
        current_distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Calculate distance to zone boundary
        distance_to_boundary = current_distance - zone_radius_meters
        
        # Check if already inside zone
        if current_distance <= zone_radius_meters:
            return ProximityEstimate(
                zone_name=zone_name,
                zone_radius_meters=zone_radius_meters,
                current_distance_meters=current_distance,
                estimated_time_to_proximity_seconds=0.0,
                is_approaching=True,
                approach_velocity_meters_per_second=velocity.speed,
                confidence=1.0,
                timestamp=timestamp
            )
        
        # Calculate velocity component toward zone center
        # Unit vector from position to zone center
        if current_distance > 0:
            unit_x = -dx / current_distance
            unit_y = -dy / current_distance
            unit_z = -dz / current_distance
        else:
            unit_x = 0.0
            unit_y = 0.0
            unit_z = 0.0
        
        # Velocity component toward zone (dot product)
        approach_velocity = (
            velocity.vx * unit_x +
            velocity.vy * unit_y +
            velocity.vz * unit_z
        )
        
        # Check if approaching or departing
        is_approaching = approach_velocity > 0
        
        # Calculate time to proximity
        if is_approaching and approach_velocity > 0:
            time_to_proximity = distance_to_boundary / approach_velocity
            # Ensure non-negative
            time_to_proximity = max(0.0, time_to_proximity)
        else:
            time_to_proximity = None  # Not approaching
        
        # Calculate confidence (decreases with distance and uncertainty)
        # Higher confidence for closer objects and higher approach velocity
        if current_distance > 0:
            distance_factor = 1.0 - min(1.0, current_distance / 200000.0)  # 200 km max
        else:
            distance_factor = 1.0
        
        velocity_factor = min(1.0, abs(approach_velocity) / 100.0) if approach_velocity != 0 else 0.0
        
        confidence = (distance_factor * 0.6 + velocity_factor * 0.4)
        
        return ProximityEstimate(
            zone_name=zone_name,
            zone_radius_meters=zone_radius_meters,
            current_distance_meters=current_distance,
            estimated_time_to_proximity_seconds=time_to_proximity,
            is_approaching=is_approaching,
            approach_velocity_meters_per_second=abs(approach_velocity),
            confidence=confidence,
            timestamp=timestamp
        )
    
    def calculate_all_zones(
        self,
        position: Coordinates,
        velocity: Velocity,
        timestamp: Optional[datetime] = None
    ) -> List[ProximityEstimate]:
        """
        Calculate time to proximity for all protected zones.
        
        Args:
            position: Current position
            velocity: Current velocity
            timestamp: Current timestamp (default: now)
            
        Returns:
            List of ProximityEstimates for all zones
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        zone_center = Coordinates(
            x=ProtectedAirspaceConfiguration.SYSTEM_ORIGIN_COORDINATES[0],
            y=ProtectedAirspaceConfiguration.SYSTEM_ORIGIN_COORDINATES[1],
            z=ProtectedAirspaceConfiguration.SYSTEM_ORIGIN_COORDINATES[2]
        )
        
        estimates = []
        
        # Critical zone
        estimates.append(self.calculate_time_to_proximity(
            position=position,
            velocity=velocity,
            zone_center=zone_center,
            zone_radius_meters=ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS,
            zone_name="CRITICAL_ZONE",
            timestamp=timestamp
        ))
        
        # Protected zone
        estimates.append(self.calculate_time_to_proximity(
            position=position,
            velocity=velocity,
            zone_center=zone_center,
            zone_radius_meters=ProtectedAirspaceConfiguration.PROTECTED_ZONE_RADIUS_METERS,
            zone_name="PROTECTED_ZONE",
            timestamp=timestamp
        ))
        
        # Extended zone
        estimates.append(self.calculate_time_to_proximity(
            position=position,
            velocity=velocity,
            zone_center=zone_center,
            zone_radius_meters=ProtectedAirspaceConfiguration.EXTENDED_ZONE_RADIUS_METERS,
            zone_name="EXTENDED_ZONE",
            timestamp=timestamp
        ))
        
        return estimates

