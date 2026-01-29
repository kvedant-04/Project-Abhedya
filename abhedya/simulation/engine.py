"""
Sensor Simulation Engine

Main engine for simulating multiple sensors detecting multiple concurrent
aerial objects. Provides coordinated, timestamped sensor readings with
realistic noise and uncertainty modeling.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.simulation.models.entity import (
    SimulatedEntity,
    EntityCharacteristics,
    TrajectoryType
)
from abhedya.simulation.sensors.radar_simulator import RadarSimulator
from abhedya.simulation.models.noise import NoiseParameters


@dataclass
class SimulationConfiguration:
    """
    Configuration for the simulation engine.
    """
    random_seed: Optional[int] = None
    enable_deterministic_mode: bool = True
    simulation_start_time: Optional[datetime] = None


class SensorSimulationEngine:
    """
    Main sensor simulation engine.
    
    Coordinates multiple sensors detecting multiple concurrent aerial objects.
    Provides:
    - Multiple concurrent entity simulation
    - Multiple sensor coordination
    - Timestamped, structured output
    - Controlled noise and uncertainty
    - Deterministic random seed support
    """
    
    def __init__(
        self,
        configuration: Optional[SimulationConfiguration] = None
    ):
        """
        Initialize simulation engine.
        
        Args:
            configuration: Simulation configuration
        """
        self.configuration = configuration or SimulationConfiguration()
        self.sensors: List[RadarSimulator] = []
        self.entities: List[SimulatedEntity] = []
        self.simulation_start_time = (
            self.configuration.simulation_start_time or
            datetime.now()
        )
        
        # Initialize random seed if deterministic mode is enabled
        if self.configuration.enable_deterministic_mode:
            import random
            if self.configuration.random_seed is not None:
                random.seed(self.configuration.random_seed)
    
    def add_sensor(
        self,
        sensor_id: str,
        sensor_position: Coordinates,
        detection_range_meters: Optional[float] = None,
        update_rate_hertz: Optional[float] = None,
        random_seed: Optional[int] = None
    ) -> RadarSimulator:
        """
        Add a radar sensor to the simulation.
        
        Args:
            sensor_id: Unique sensor identifier
            sensor_position: Position of the sensor
            detection_range_meters: Maximum detection range
            update_rate_hertz: Update rate in Hz
            random_seed: Random seed for this sensor
            
        Returns:
            Created radar simulator
        """
        # Use engine seed if sensor seed not provided
        sensor_seed = random_seed or self.configuration.random_seed
        
        sensor = RadarSimulator(
            sensor_id=sensor_id,
            sensor_position=sensor_position,
            detection_range_meters=detection_range_meters,
            update_rate_hertz=update_rate_hertz,
            random_seed=sensor_seed
        )
        
        self.sensors.append(sensor)
        return sensor
    
    def add_entity(
        self,
        entity_id: Optional[str] = None,
        characteristics: Optional[EntityCharacteristics] = None,
        initial_position: Optional[Coordinates] = None,
        initial_velocity: Optional[Velocity] = None,
        trajectory_type: TrajectoryType = TrajectoryType.LINEAR,
        trajectory_parameters: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ) -> SimulatedEntity:
        """
        Add a simulated entity to the simulation.
        
        Args:
            entity_id: Unique entity identifier (auto-generated if None)
            characteristics: Entity characteristics (default: commercial aircraft)
            initial_position: Initial position (default: random)
            initial_velocity: Initial velocity (default: based on characteristics)
            trajectory_type: Type of trajectory
            trajectory_parameters: Parameters for trajectory
            created_at: Creation timestamp (default: now)
            
        Returns:
            Created simulated entity
        """
        if entity_id is None:
            entity_id = f"entity_{uuid.uuid4().hex[:8]}"
        
        if characteristics is None:
            characteristics = EntityCharacteristics.for_commercial_aircraft()
        
        if initial_position is None:
            # Default: random position within detection range
            import random
            import math
            if self.configuration.random_seed is not None:
                random.seed(self.configuration.random_seed)
            
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10000, 100000)  # 10-100 km
            initial_position = Coordinates(
                x=distance * math.cos(angle),
                y=distance * math.sin(angle),
                z=characteristics.typical_altitude_meters
            )
        
        if initial_velocity is None:
            # Default: velocity based on characteristics
            speed = characteristics.typical_speed_meters_per_second
            initial_velocity = Velocity(
                vx=speed * 0.707,  # 45-degree angle
                vy=speed * 0.707,
                vz=0.0
            )
        
        if created_at is None:
            created_at = self.simulation_start_time
        
        entity = SimulatedEntity(
            entity_id=entity_id,
            characteristics=characteristics,
            initial_position=initial_position,
            initial_velocity=initial_velocity,
            trajectory_type=trajectory_type,
            trajectory_parameters=trajectory_parameters or {},
            created_at=created_at
        )
        
        self.entities.append(entity)
        return entity
    
    def simulate_step(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Simulate one time step of sensor detection.
        
        Args:
            timestamp: Current simulation timestamp
            
        Returns:
            Dictionary containing all sensor detections for this time step
        """
        all_detections = []
        
        # Get detections from all sensors
        for sensor in self.sensors:
            detections = sensor.detect_entities(
                timestamp=timestamp,
                entities=self.entities
            )
            all_detections.extend(detections)
        
        # Create structured output
        output = {
            "simulation_timestamp": timestamp.isoformat(),
            "sensor_count": len(self.sensors),
            "entity_count": len(self.entities),
            "detection_count": len(all_detections),
            "detections": all_detections,
            "metadata": {
                "simulation_time_delta_seconds": (
                    timestamp - self.simulation_start_time
                ).total_seconds(),
            }
        }
        
        return output
    
    def simulate_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        time_step_seconds: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Simulate sensor detection over a time range.
        
        Args:
            start_time: Simulation start time
            end_time: Simulation end time
            time_step_seconds: Time step in seconds
            
        Returns:
            List of detection outputs for each time step
        """
        from datetime import timedelta
        
        results = []
        current_time = start_time
        
        while current_time <= end_time:
            step_output = self.simulate_step(current_time)
            results.append(step_output)
            current_time += timedelta(seconds=time_step_seconds)
        
        return results
    
    def get_simulation_info(self) -> Dict[str, Any]:
        """
        Get simulation information.
        
        Returns:
            Dictionary with simulation information
        """
        return {
            "simulation_start_time": self.simulation_start_time.isoformat(),
            "sensor_count": len(self.sensors),
            "entity_count": len(self.entities),
            "deterministic_mode": self.configuration.enable_deterministic_mode,
            "random_seed": self.configuration.random_seed,
            "sensors": [sensor.get_sensor_info() for sensor in self.sensors],
            "entities": [
                {
                    "entity_id": entity.entity_id,
                    "entity_type": entity.characteristics.entity_type.value,
                    "trajectory_type": entity.trajectory_type.value,
                }
                for entity in self.entities
            ]
        }
    
    def clear_entities(self):
        """Clear all simulated entities."""
        self.entities = []
    
    def clear_sensors(self):
        """Clear all sensors."""
        self.sensors = []

