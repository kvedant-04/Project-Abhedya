# Sensor and Input Simulation Engine

## Overview

The Sensor and Input Simulation Engine provides mathematical simulation of radar-style sensor systems for detecting and tracking aerial entities (aircraft, drones, etc.). The simulation is **purely mathematical** - no real sensor integration, no external data feeds, and fully deterministic with random seed support.

## Key Features

### 1. Radar-Style Positional Data Simulation
- Position detection with realistic noise modeling
- Velocity measurement with uncertainty
- Signal strength calculation based on distance and Radar Cross Section (RCS)
- Detection confidence assessment
- Timestamped, structured output

### 2. Multiple Concurrent Aerial Objects
- Support for multiple entities simultaneously
- Different entity types (commercial aircraft, military aircraft, drones, helicopters)
- Different trajectory patterns (linear, circular, approaching, departing, patrol, hover)
- Realistic entity characteristics (speed, altitude, RCS, maneuverability)

### 3. Controlled Noise and Uncertainty Modeling
- Gaussian (normal) distribution noise for realistic measurements
- Noise increases with distance (inverse square law effect)
- Configurable noise parameters
- Deterministic noise with random seed support
- Uncertainty quantification for all measurements

### 4. Deterministic Random Seed Support
- Reproducible simulations with fixed random seeds
- Deterministic noise generation
- Useful for testing and validation

## Architecture

### Components

#### 1. Entity Models (`models/entity.py`)
- **SimulatedEntity**: Represents an aerial entity with position, velocity, and trajectory
- **EntityCharacteristics**: Physical and behavioral characteristics (speed, altitude, RCS, etc.)
- **TrajectoryType**: Different trajectory patterns (linear, circular, approaching, etc.)

#### 2. Noise Models (`models/noise.py`)
- **NoiseModel**: Mathematical noise model using Gaussian distribution
- **NoiseParameters**: Configurable noise parameters
- **DeterministicNoiseModel**: Deterministic noise with fixed random seed

#### 3. Radar Simulator (`sensors/radar_simulator.py`)
- **RadarSimulator**: Simulates radar sensor detection
- Position and velocity measurement with noise
- Signal strength and confidence calculation
- Timestamped, structured output

#### 4. Simulation Engine (`engine.py`)
- **SensorSimulationEngine**: Main engine coordinating multiple sensors and entities
- **SimulationConfiguration**: Configuration for simulation behavior
- Time-stepped simulation support
- Multiple sensor coordination

## Usage Example

```python
from datetime import datetime, timedelta
from abhedya.simulation import (
    SensorSimulationEngine,
    SimulationConfiguration,
    EntityCharacteristics,
    TrajectoryType
)
from abhedya.domain.value_objects import Coordinates, Velocity

# Create simulation engine with deterministic seed
config = SimulationConfiguration(
    random_seed=42,
    enable_deterministic_mode=True,
    simulation_start_time=datetime.now()
)
engine = SensorSimulationEngine(configuration=config)

# Add radar sensor
sensor_position = Coordinates(x=0.0, y=0.0, z=0.0)
radar = engine.add_sensor(
    sensor_id="RADAR_001",
    sensor_position=sensor_position,
    detection_range_meters=150000.0,  # 150 km
    update_rate_hertz=1.0
)

# Add commercial aircraft entity
aircraft = engine.add_entity(
    entity_id="AIRCRAFT_001",
    characteristics=EntityCharacteristics.for_commercial_aircraft(),
    initial_position=Coordinates(x=50000.0, y=60000.0, z=10000.0),
    initial_velocity=Velocity(vx=-100.0, vy=-80.0, vz=0.0),
    trajectory_type=TrajectoryType.LINEAR
)

# Add drone entity
drone = engine.add_entity(
    entity_id="DRONE_001",
    characteristics=EntityCharacteristics.for_drone(),
    initial_position=Coordinates(x=30000.0, y=40000.0, z=500.0),
    initial_velocity=Velocity(vx=-20.0, vy=-15.0, vz=0.0),
    trajectory_type=TrajectoryType.PATROL,
    trajectory_parameters={
        "patrol_length": 10000.0,
        "patrol_speed": 30.0,
        "patrol_direction": (1.0, 0.0)
    }
)

# Simulate single time step
timestamp = datetime.now()
detections = engine.simulate_step(timestamp)

# Simulate time range
start_time = datetime.now()
end_time = start_time + timedelta(seconds=60)
results = engine.simulate_time_range(
    start_time=start_time,
    end_time=end_time,
    time_step_seconds=1.0
)
```

## Output Format

Each detection contains:

```python
{
    "sensor_id": "RADAR_001",
    "sensor_type": "RADAR",
    "timestamp": "2024-01-01T12:00:00",
    "entity_id": "AIRCRAFT_001",
    "position": {
        "x": 49950.0,  # Noisy measurement
        "y": 59980.0,
        "z": 10000.0,
        "true_x": 50000.0,  # True position (for validation)
        "true_y": 60000.0,
        "true_z": 10000.0,
    },
    "velocity": {
        "vx": -100.2,  # Noisy measurement
        "vy": -79.8,
        "vz": 0.0,
        "true_vx": -100.0,  # True velocity (for validation)
        "true_vy": -80.0,
        "true_vz": 0.0,
    },
    "signal_strength": 0.75,
    "confidence": 0.82,
    "uncertainty": 0.15,
    "distance_from_sensor_meters": 78102.4,
    "metadata": {
        "entity_type": "COMMERCIAL_AIRCRAFT",
        "radar_cross_section": 0.8,
        "size_category": "LARGE",
    }
}
```

## Realism and Safety

### How Realism is Achieved

1. **Physical Laws**: 
   - Inverse square law for signal strength
   - Distance-dependent noise (noise increases with distance)
   - Realistic RCS values for different entity types

2. **Statistical Modeling**:
   - Gaussian (normal) distribution for noise (realistic sensor noise)
   - Configurable noise parameters matching real sensor characteristics
   - Uncertainty quantification based on distance and signal strength

3. **Entity Behavior**:
   - Realistic speeds for different entity types
   - Typical altitudes for different aircraft types
   - Realistic trajectory patterns

4. **Sensor Characteristics**:
   - Update rates matching real radar systems
   - Detection ranges matching real systems
   - Confidence thresholds based on signal strength and distance

### Safety Guarantees

1. **Mathematical Simulation Only**:
   - No real sensor integration
   - No external data feeds
   - All data is mathematically generated

2. **Deterministic Behavior**:
   - Random seed support for reproducible results
   - No unpredictable external factors
   - All randomness is controlled

3. **Structured Output**:
   - Timestamped data
   - Structured format for easy processing
   - Includes both noisy and true values (for validation)

4. **No Execution Authority**:
   - Simulation only - no real-world actions
   - Output is informational only
   - Requires human interpretation

## Configuration

The simulation uses configuration from `abhedya.infrastructure.config.config`:

- **SensorConfiguration**: Default sensor parameters
- **ConfidenceThresholds**: Minimum confidence for detections
- **NoiseParameters**: Noise model parameters

## Entity Types

### Commercial Aircraft
- Speed: ~250 m/s (~900 km/h)
- Altitude: ~10 km
- RCS: 0.8 (large)
- Maneuverability: 0.2 (low)

### Military Aircraft
- Speed: ~400 m/s (~1440 km/h)
- Altitude: ~8 km
- RCS: 0.6 (medium, stealth considerations)
- Maneuverability: 0.8 (high)

### Drone
- Speed: ~50 m/s (~180 km/h)
- Altitude: ~500 m
- RCS: 0.1 (small)
- Maneuverability: 0.9 (very high)

### Helicopter
- Speed: ~80 m/s (~288 km/h)
- Altitude: ~2 km
- RCS: 0.4 (medium)
- Maneuverability: 0.7 (high)

## Trajectory Types

1. **LINEAR**: Straight-line trajectory
2. **CIRCULAR**: Circular orbit pattern
3. **APPROACHING**: Approaching system origin
4. **DEPARTING**: Departing from system origin
5. **PATROL**: Patrol pattern (back and forth)
6. **HOVER**: Hovering in place

## Testing and Validation

The simulation includes both noisy measurements and true values in the output, allowing for:
- Validation of noise models
- Testing of sensor fusion algorithms
- Verification of detection confidence calculations
- Performance analysis

## Limitations

1. **Simulation Only**: This is mathematical simulation, not real sensor data
2. **Simplified Models**: Some real-world complexities are simplified for clarity
3. **No Environmental Factors**: Weather, atmospheric conditions, etc. are not modeled
4. **No Multi-Path**: Radar multi-path effects are not included

## Future Enhancements

Potential additions (while maintaining safety):
- Additional sensor types (IFF, optical)
- More complex trajectory patterns
- Environmental factor modeling
- Multi-path effects
- Clutter and false alarm modeling

---

**Last Updated**: 2024

