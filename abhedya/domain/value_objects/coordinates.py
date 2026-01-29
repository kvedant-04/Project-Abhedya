"""
Coordinate Value Objects

Immutable value objects for spatial coordinates.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Coordinates:
    """
    Immutable 3D spatial coordinates.
    
    All coordinates are in meters relative to system origin.
    """
    x: float  # X coordinate in meters
    y: float  # Y coordinate in meters
    z: float  # Z coordinate in meters (altitude)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple representation."""
        return (self.x, self.y, self.z)
    
    def distance_to(self, other: "Coordinates") -> float:
        """
        Calculate Euclidean distance to another coordinate.
        
        Args:
            other: Target coordinates
            
        Returns:
            Distance in meters
        """
        import math
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx**2 + dy**2 + dz**2)

