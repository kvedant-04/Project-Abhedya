"""
Velocity Value Objects

Immutable value objects for velocity vectors.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Velocity:
    """
    Immutable 3D velocity vector.
    
    All velocities are in meters per second.
    """
    vx: float  # Velocity in X direction (m/s)
    vy: float  # Velocity in Y direction (m/s)
    vz: float  # Velocity in Z direction (m/s)
    
    @property
    def speed(self) -> float:
        """
        Calculate speed magnitude.
        
        Returns:
            Speed in meters per second
        """
        return math.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
    
    @property
    def heading(self) -> float:
        """
        Calculate horizontal heading in degrees.
        
        Returns:
            Heading in degrees (0-360, where 0 is North/East)
        """
        heading_rad = math.atan2(self.vy, self.vx)
        heading_deg = math.degrees(heading_rad)
        return heading_deg if heading_deg >= 0 else heading_deg + 360.0

