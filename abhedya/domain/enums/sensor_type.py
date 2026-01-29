"""
Sensor Type Enumerations

Enumeration of sensor types in the system.
"""

from enum import Enum


class SensorType(str, Enum):
    """Types of sensor systems."""
    RADAR = "RADAR"
    IFF = "IFF"  # Identification Friend or Foe
    OPTICAL = "OPTICAL"
    ACOUSTIC = "ACOUSTIC"

