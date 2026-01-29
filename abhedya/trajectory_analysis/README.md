# Trajectory Prediction and Physics Validation Engine

## Overview

The Trajectory Prediction and Physics Validation Engine provides:
- Short-term future position prediction using classical mechanics
- Motion validation using classical physics constraints
- Detection of physically implausible or anomalous motion
- Time-to-proximity estimation for protected zones

**Key Principles**:
- **Classical Mechanics Only**: No speculative or tactical motion modeling
- **Configuration-Driven**: All limits are configuration-driven
- **Anomalies ≠ Hostile Intent**: Anomalies do NOT imply hostile intent

## Components

### 1. Trajectory Predictor (`predictor.py`)

Predicts short-term future positions using classical mechanics:
- **Constant Velocity Model**: `x(t) = x0 + v*t`
- **Constant Acceleration Model**: `x(t) = x0 + v0*t + 0.5*a*t²`

**Methods**:
- `predict_constant_velocity()`: Predict using constant velocity
- `predict_constant_acceleration()`: Predict using constant acceleration
- `predict()`: Predict using specified motion model
- `estimate_acceleration()`: Estimate acceleration from velocity change

**Features**:
- Configurable prediction horizon (default: 60 seconds, max: 300 seconds)
- Confidence and uncertainty calculation
- Time-stepped predictions

### 2. Physics Validator (`physics_validator.py`)

Validates motion using classical physics constraints:
- **Maximum Acceleration**: Typical aircraft ~50 m/s², extreme ~100 m/s²
- **Maximum Speed**: Typical aircraft ~400 m/s, extreme ~1000 m/s
- **Velocity Change Consistency**: Validates velocity changes are physically possible
- **Position Change Consistency**: Validates position changes match velocity

**Methods**:
- `validate_motion()`: Validate motion sequence
- `validate_single_step()`: Validate single motion step

**Validation Checks**:
- Excessive acceleration detection
- Excessive speed detection
- Impossible velocity changes
- Impossible position changes

### 3. Anomaly Detector (`anomaly_detector.py`)

Detects physically implausible or anomalous motion patterns.

**IMPORTANT**: Anomalies do NOT imply hostile intent. They indicate unusual motion that may require investigation.

**Detects**:
- **Sudden Direction Changes**: Large changes in heading (>45°)
- **Sudden Speed Changes**: Large changes in speed (>50%)
- **Unusual Acceleration**: Acceleration exceeding threshold (>50 m/s²)
- **Unusual Trajectory**: Non-smooth trajectory patterns
- **Physics Violations**: Motion that violates physical laws

**Methods**:
- `detect_anomalies()`: Detect anomalies in motion sequence

**Features**:
- Anomaly score calculation (0.0 to 1.0)
- Multiple anomaly type detection
- Clear reasoning and explanation

### 4. Proximity Calculator (`proximity_calculator.py`)

Estimates time-to-proximity for protected zones using classical mechanics.

**Methods**:
- `calculate_time_to_proximity()`: Calculate time to specific zone
- `calculate_all_zones()`: Calculate time to all protected zones

**Features**:
- Constant velocity model for prediction
- Approach/departure detection
- Confidence calculation
- Support for all protected zones (Critical, Protected, Extended)

## Usage Example

```python
from abhedya.trajectory_analysis import (
    TrajectoryPredictor,
    PhysicsValidator,
    AnomalyDetector,
    ProximityCalculator
)
from abhedya.domain.value_objects import Coordinates, Velocity
from datetime import datetime

# Initialize components
predictor = TrajectoryPredictor(prediction_horizon_seconds=60.0)
physics_validator = PhysicsValidator()
anomaly_detector = AnomalyDetector()
proximity_calculator = ProximityCalculator()

# Current state
position = Coordinates(x=50000.0, y=60000.0, z=10000.0)
velocity = Velocity(vx=-100.0, vy=-80.0, vz=0.0)

# Predict trajectory
prediction = predictor.predict_constant_velocity(position, velocity)
print(f"Predicted {len(prediction.predicted_positions)} positions")
print(f"Confidence: {prediction.confidence:.2%}")

# Validate physics
validation = physics_validator.validate_single_step(
    previous_position=position,
    current_position=prediction.predicted_positions[10],
    previous_velocity=velocity,
    current_velocity=velocity,
    time_delta=10.0
)
print(f"Physics valid: {validation.is_valid}")

# Detect anomalies
anomaly_result = anomaly_detector.detect_anomalies(
    positions=[position] + prediction.predicted_positions[:5],
    velocities=[velocity] * 6
)
print(f"Anomalous: {anomaly_result.is_anomalous}")
print(f"Note: {anomaly_result.note}")

# Calculate proximity
proximity = proximity_calculator.calculate_time_to_proximity(
    position=position,
    velocity=velocity,
    zone_center=Coordinates(x=0.0, y=0.0, z=0.0),
    zone_radius_meters=20000.0,
    zone_name="CRITICAL_ZONE"
)
if proximity.is_approaching:
    print(f"Time to proximity: {proximity.estimated_time_to_proximity_seconds:.1f} seconds")
```

## Classical Mechanics Models

### Constant Velocity Model
```
x(t) = x0 + vx * t
y(t) = y0 + vy * t
z(t) = z0 + vz * t
```

### Constant Acceleration Model
```
x(t) = x0 + vx0 * t + 0.5 * ax * t²
y(t) = y0 + vy0 * t + 0.5 * ay * t²
z(t) = z0 + vz0 * t + 0.5 * az * t²
```

### Acceleration Estimation
```
a = (v - v0) / t
```

## Physics Constraints

### Maximum Acceleration
- **Typical Aircraft**: ~50 m/s²
- **Extreme**: ~100 m/s²
- **Configuration**: Default 100 m/s²

### Maximum Speed
- **Typical Aircraft**: ~400 m/s (~1440 km/h)
- **Extreme**: ~1000 m/s (~3600 km/h)
- **Configuration**: Default 1000 m/s

### Velocity Change
- **Maximum per second**: 200 m/s
- **Configuration**: Default 200 m/s

## Anomaly Detection

### Anomaly Types

1. **Sudden Direction Change**
   - Threshold: >45° change in heading
   - Indicates: Rapid course change

2. **Sudden Speed Change**
   - Threshold: >50% change in speed
   - Indicates: Rapid acceleration or deceleration

3. **Unusual Acceleration**
   - Threshold: >50 m/s²
   - Indicates: Extreme acceleration

4. **Unusual Trajectory**
   - Threshold: >60° turn angle
   - Indicates: Non-smooth trajectory

5. **Physics Violation**
   - Any violation of physics constraints
   - Indicates: Impossible motion

### Anomaly Score
- Calculated from detected anomalies
- Range: 0.0 to 1.0
- Higher score = more anomalous

**IMPORTANT**: Anomalies do NOT imply hostile intent. They indicate unusual motion patterns that may require investigation.

## Time-to-Proximity Calculation

### Method
Uses constant velocity model to predict when object will reach protected zone boundary.

### Calculation
```
distance_to_boundary = current_distance - zone_radius
approach_velocity = velocity · unit_vector_to_zone_center
time_to_proximity = distance_to_boundary / approach_velocity
```

### Zones
- **Critical Zone**: 20 km radius
- **Protected Zone**: 50 km radius
- **Extended Zone**: 100 km radius

## Configuration

The trajectory analysis module uses configuration from `abhedya.infrastructure.config.config`:
- `ProtectedAirspaceConfiguration`: Zone definitions
- `SystemPerformanceLimits`: Maximum prediction horizon
- `ThreatAssessmentThresholds`: Speed thresholds

## Limitations

1. **Constant Velocity/Acceleration**: Assumes constant motion (no maneuvering)
2. **No Tactical Modeling**: No speculative or tactical motion patterns
3. **Short-Term Only**: Predictions are short-term (minutes, not hours)
4. **Simplified Physics**: Simplified models (no air resistance, etc.)

## Future Enhancements

Potential additions (while maintaining classical mechanics):
- More sophisticated motion models
- Adaptive prediction horizons
- Uncertainty propagation
- Multiple hypothesis predictions

---

**Last Updated**: 2024

