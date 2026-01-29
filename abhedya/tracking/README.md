# Target Detection and Tracking Module

## Overview

The Target Detection and Tracking Module provides multi-target tracking with probabilistic classification and state estimation using Kalman filters. All logic is explainable and uses classical mathematical techniques only.

## Features

### 1. Probabilistic Classification
- **Aerial Drone**: Small, low altitude, low-medium speed, high maneuverability
- **Aircraft**: Medium-large, high altitude, high speed, low maneuverability
- **Unknown Object**: Does not match known patterns (valid and common outcome)

All classifications include:
- Probability for each type
- Classification uncertainty
- Human-readable reasoning

### 2. Multi-Target Tracking
- Tracks multiple objects simultaneously
- Unique and persistent track identifiers
- Track lifecycle management (Initializing → Active → Coasting → Terminated)
- Association of detections to tracks using distance-based gating

### 3. State Estimation
- Kalman filter for position and velocity estimation
- Constant velocity motion model
- Uncertainty quantification from covariance matrix
- Prediction and update steps

### 4. Track Management
- Automatic track creation for new detections
- Track association using distance threshold
- Stale track removal
- Track state transitions

## Components

### 1. Track Models (`models.py`)
- **Track**: Complete track state with position, velocity, classification
- **TrackIdentifier**: Unique and persistent identifier
- **ClassificationResult**: Probabilistic classification with uncertainty
- **TrackState**: Track lifecycle states

### 2. Kalman Filter (`kalman.py`)
- **KalmanFilter**: Classical Kalman filter implementation
- **KalmanState**: Filter state with position, velocity, covariance
- Constant velocity motion model
- Position and velocity uncertainty calculation

### 3. Probabilistic Classifier (`classifier.py`)
- **ProbabilisticClassifier**: Classification using classical statistical techniques
- Feature extraction (speed, altitude, RCS, maneuverability, size)
- Probability calculation for each object type
- Uncertainty calculation using entropy
- Reasoning generation

### 4. Multi-Target Tracker (`tracker.py`)
- **MultiTargetTracker**: Main tracking engine
- Detection-to-track association
- Track creation and management
- State estimation coordination

## Usage Example

```python
from abhedya.tracking import MultiTargetTracker
from datetime import datetime

# Initialize tracker
tracker = MultiTargetTracker(
    association_threshold_meters=5000.0,
    max_track_age_seconds=60.0,
    min_updates_for_active=3
)

# Update with detections
detections = [
    {
        "sensor_id": "RADAR_001",
        "timestamp": datetime.now().isoformat(),
        "position": {"x": 50000.0, "y": 60000.0, "z": 10000.0},
        "velocity": {"vx": -100.0, "vy": -80.0, "vz": 0.0},
        "confidence": 0.8,
        "uncertainty": 0.1,
        "metadata": {
            "radar_cross_section": 0.8,
            "size_category": "LARGE"
        }
    }
]

# Update tracker
tracks = tracker.update(detections)

# Access tracks
for track in tracks:
    print(f"Track ID: {track.identifier.track_id}")
    print(f"Classification: {track.classification.object_type.value}")
    print(f"Probability: {track.classification.probability:.2%}")
    print(f"Uncertainty: {track.classification.uncertainty:.2%}")
    print(f"Position: ({track.position.x:.1f}, {track.position.y:.1f}, {track.position.z:.1f})")
    print(f"State: {track.state.value}")
```

## Classification Logic

### Aerial Drone Characteristics
- **Size**: Small
- **Altitude**: < 1 km typically
- **Speed**: 20-100 m/s
- **Maneuverability**: High
- **RCS**: Small (< 0.3)

### Aircraft Characteristics
- **Size**: Medium to Large
- **Altitude**: > 5 km typically
- **Speed**: 200-400 m/s
- **Maneuverability**: Low
- **RCS**: Medium to Large (> 0.5)

### Unknown Object
- Does not match known patterns well
- Maximum probability below threshold (default: 0.4)
- Ambiguous features (similar probabilities for known types)
- **This is a valid and common outcome**

## Kalman Filter

### State Vector
```
[x, y, z, vx, vy, vz]
```

### Motion Model
Constant velocity model:
- Position: `x' = x + vx*dt`
- Velocity: `vx' = vx` (constant)

### Prediction Step
```
x_k|k-1 = F * x_k-1|k-1
P_k|k-1 = F * P_k-1|k-1 * F^T + Q
```

### Update Step
```
y = z - H * x_k|k-1
S = H * P_k|k-1 * H^T + R
K = P_k|k-1 * H^T * S^-1
x_k|k = x_k|k-1 + K * y
P_k|k = (I - K * H) * P_k|k-1
```

## Track Lifecycle

1. **INITIALIZING**: New track, collecting initial detections
2. **ACTIVE**: Track has sufficient updates, actively tracking
3. **COASTING**: Track without recent updates, may be lost
4. **TERMINATED**: Track terminated (stale or lost)

## Association Logic

Tracks are associated to detections using:
- **Distance-based gating**: Maximum distance threshold (default: 5 km)
- **Nearest neighbor**: Closest track within threshold
- **No association**: New track created if no match found

## Uncertainty and Confidence

### Classification Uncertainty
- Calculated using entropy: `H = -Σ(p * log2(p))`
- High uncertainty when probabilities are similar (ambiguous)
- Low uncertainty when one probability dominates

### Track Confidence
- Inherited from detection confidence
- Updated with each detection
- Used for track quality assessment

### Position/Velocity Uncertainty
- Calculated from Kalman filter covariance matrix
- Position uncertainty: Average of diagonal elements (x, y, z)
- Velocity uncertainty: Average of diagonal elements (vx, vy, vz)

## Configuration

The tracking module uses configuration from `abhedya.infrastructure.config.config`:
- `SystemPerformanceLimits`: Maximum number of tracks
- `UncertaintyLimits`: Maximum acceptable uncertainty
- `ThreatAssessmentThresholds`: Speed thresholds for classification

## Performance Considerations

- **Efficiency**: O(n*m) for n detections and m tracks (association)
- **Memory**: Tracks stored in dictionary for O(1) lookup
- **Scalability**: Handles hundreds of tracks efficiently
- **Deterministic**: All operations are deterministic

## Limitations

1. **Constant Velocity Model**: Assumes constant velocity (simplified)
2. **Distance-Based Association**: Simple association (no advanced data association)
3. **No Track Splitting/Merging**: Tracks don't split or merge
4. **Fixed Thresholds**: Association threshold is fixed (not adaptive)

## Future Enhancements

Potential additions (while maintaining explainability):
- Multiple hypothesis tracking (MHT)
- Track splitting and merging
- Adaptive association thresholds
- More sophisticated motion models
- Track quality metrics

---

**Last Updated**: 2024

