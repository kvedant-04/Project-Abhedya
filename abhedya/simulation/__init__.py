"""
Sensor Simulation Module

Mathematical simulation of sensor systems for detecting and tracking
aerial entities. Provides radar-style positional data with realistic
noise and uncertainty modeling.
"""

from abhedya.simulation.engine import (
    SensorSimulationEngine,
    SimulationConfiguration
)
from abhedya.simulation.sensors.radar_simulator import RadarSimulator
from abhedya.simulation.models.entity import (
    SimulatedEntity,
    EntityCharacteristics,
    EntityType,
    TrajectoryType
)
from abhedya.simulation.models.noise import (
    NoiseModel,
    NoiseParameters,
    DeterministicNoiseModel
)

__all__ = [
    "SensorSimulationEngine",
    "SimulationConfiguration",
    "RadarSimulator",
    "SimulatedEntity",
    "EntityCharacteristics",
    "EntityType",
    "TrajectoryType",
    "NoiseModel",
    "NoiseParameters",
    "DeterministicNoiseModel",
]
