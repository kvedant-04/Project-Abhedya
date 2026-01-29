# Early Warning System

## Overview

The Early Warning System is a backend advisory module that detects slow-building or subtle anomalies in airspace behavior using statistical analysis.

**ADVISORY ONLY** - No action recommendations or execution logic.

**FAIL-SAFE**: Insufficient or stale data defaults to `MONITORING_ONLY`.

## Features

### 1. Statistical Baseline Establishment
- **Track Density**: Tracks per unit area/time
- **Velocity Distributions**: Mean and standard deviation of velocities
- **Trajectory Deviation Patterns**: Deviation from expected trajectories
- **Confidence Decay**: Rate of confidence decay over time

### 2. Anomaly Detection
- **Rolling Mean and Variance**: Statistical measures over rolling windows
- **EWMA (Exponentially Weighted Moving Average)**: Detects gradual changes
- **CUSUM (Cumulative Sum Control)**: Detects shifts from baseline
- **Multi-Track Convergence**: Detects multiple tracks converging

### 3. Advisory Outputs
- **Early Warning State**: `NORMAL`, `ELEVATED`, or `HIGH` (advisory only)
- **Confidence Score**: [0.0, 1.0]
- **Uncertainty**: [0.0, 1.0]
- **Human-Readable Reasoning**: List of reasoning statements
- **Recommended System Posture**: `MONITORING_ONLY`, `ENHANCED_MONITORING`, `ALERT_MONITORING` (informational only)

## Components

### 1. Baseline Analyzer (`baseline.py`)
Establishes statistical baselines for normal airspace behavior:
- Track density statistics
- Velocity distribution statistics
- Trajectory deviation patterns
- Confidence decay rates
- Baseline comparison (Z-score deviations)

### 2. Trend Analyzer (`trend_analysis.py`)
Detects slow-building anomalies:
- Rolling mean and variance
- EWMA calculation
- CUSUM calculation
- Multi-track convergence detection
- Anomaly score calculation

### 3. Early Warning Engine (`early_warning_engine.py`)
Main engine that:
- Aggregates baseline and trend analysis
- Determines warning state
- Calculates confidence and uncertainty
- Generates reasoning
- Produces advisory outputs

## Usage Example

```python
from abhedya.early_warning import EarlyWarningEngine
from abhedya.tracking.models import Track, TrackIdentifier, TrackState, ClassificationResult, ObjectType

# Initialize engine
engine = EarlyWarningEngine(
    baseline_minimum_samples=10,
    enable_baseline_analysis=True,
    enable_trend_analysis=True
)

# Get tracks from tracking module
tracks = [...]  # List of Track objects

# Analyze and get early warning result
result = engine.analyze(tracks)

# Access results
print(f"Warning State: {result.warning_state.value} (ADVISORY ONLY)")
print(f"Confidence: {result.confidence:.2%}")
print(f"Uncertainty: {result.uncertainty:.2%}")
print(f"Recommended Posture: {result.recommended_posture.value} (INFORMATIONAL ONLY)")

# Print reasoning
for reason in result.reasoning:
    print(f"  - {reason}")

# Print anomaly indicators
if result.anomaly_indicators:
    print("\nAnomaly Indicators:")
    for indicator in result.anomaly_indicators:
        print(f"  - {indicator}")

print(f"\n{result.advisory_statement}")
```

## Statistical Methods

### Rolling Mean and Variance
Calculates mean and variance over a rolling window:
```python
rolling_mean = mean(window)
rolling_variance = variance(window)
```

### EWMA (Exponentially Weighted Moving Average)
Detects gradual changes:
```
EWMA_t = α * X_t + (1 - α) * EWMA_{t-1}
```
Where:
- `α` is the smoothing factor (0-1)
- `X_t` is the current value
- `EWMA_{t-1}` is the previous EWMA value

### CUSUM (Cumulative Sum Control)
Detects shifts from baseline:
```
CUSUM_+ = max(0, CUSUM_+ + (X - μ - k))
CUSUM_- = max(0, CUSUM_- + (μ - X - k))
```
Where:
- `μ` is the baseline mean
- `k` is the drift parameter
- Anomaly detected if CUSUM > threshold

### Multi-Track Convergence
Detects if multiple tracks are converging:
- Calculates velocity components along line-of-sight
- Detects if tracks are heading towards each other
- Convergence detected if >30% of track pairs show convergence

## Warning States

### NORMAL
- No significant anomalies detected
- Baseline comparisons within normal range
- Trend analysis shows normal patterns

### ELEVATED
- Some anomaly indicators present
- Baseline deviations detected
- CUSUM or convergence indicators present

### HIGH
- Multiple anomaly indicators
- Significant baseline deviations
- High CUSUM values or strong convergence

**IMPORTANT**: These states are **ADVISORY ONLY** and do not map to any actions.

## Recommended System Postures

### MONITORING_ONLY
- Normal monitoring mode
- Default fail-safe posture
- Used when data is insufficient or stale

### ENHANCED_MONITORING
- Elevated monitoring recommended
- More frequent analysis
- **INFORMATIONAL ONLY** - does not map to actions

### ALERT_MONITORING
- Alert-level monitoring recommended
- Highest monitoring level
- **INFORMATIONAL ONLY** - does not map to actions

**IMPORTANT**: These postures are **INFORMATIONAL ONLY** and do not map to any actions.

## Fail-Safe Behavior

The system implements strict fail-safe behavior:

1. **Insufficient Data**: If insufficient tracks (< 3), defaults to `MONITORING_ONLY`
2. **Stale Data**: If >70% of tracks are stale, defaults to `MONITORING_ONLY`
3. **No Baseline**: If baseline cannot be established, continues with reduced confidence
4. **Data Quality Flags**: Tracks data quality issues and reduces confidence accordingly

## Data Quality Checks

The system performs the following data quality checks:

- **Track Count**: Ensures minimum number of tracks
- **Stale Tracks**: Detects tracks without recent updates
- **Low Confidence**: Detects high proportion of low-confidence tracks
- **Insufficient Data**: Flags when data is insufficient for analysis

## Integration

### Inputs
- **Tracks**: From `abhedya.tracking.models.Track`
- **Historical Tracks**: Optional historical track data for baseline establishment

### Outputs
- **EarlyWarningResult**: Advisory result object
- **No Execution Logic**: Outputs are advisory only
- **No Action Recommendations**: No actions are recommended

### No Coupling
- Does not modify existing modules
- Does not execute any actions
- Pure advisory analysis

## Configuration

The early warning system uses configurable parameters:

- `baseline_minimum_samples`: Minimum samples for baseline (default: 10)
- `rolling_window_size`: Window size for rolling statistics (default: 10)
- `ewma_alpha`: EWMA smoothing factor (default: 0.3)
- `cusum_threshold`: CUSUM threshold (default: 5.0)
- `cusum_drift`: CUSUM drift parameter (default: 0.5)

## Limitations

1. **Simplified Models**: Uses simplified statistical models
2. **Constant Velocity**: Assumes constant velocity for convergence detection
3. **No Environmental Factors**: Weather, atmospheric conditions not considered
4. **Baseline Establishment**: Requires minimum samples to establish baseline

## Safety Guarantees

1. **Advisory Only**: All outputs are advisory only
2. **No Actions**: No action recommendations or execution logic
3. **Fail-Safe Default**: Defaults to `MONITORING_ONLY` on insufficient data
4. **Deterministic**: All calculations are deterministic and explainable
5. **Defensive Programming**: Robust validation and error handling

## Example Output

```python
EarlyWarningResult(
    result_id="...",
    timestamp=datetime.now(),
    warning_state=EarlyWarningState.ELEVATED,
    confidence=0.75,
    uncertainty=0.25,
    reasoning=[
        "Early Warning State: ELEVATED (ADVISORY ONLY)",
        "",
        "Baseline Statistics:",
        "  - Track Density: 5.2 ± 1.3",
        "  - Velocity: 150.5 ± 25.3 m/s",
        "",
        "Baseline Comparison:",
        "  - Track Density Deviation: 2.1σ",
        "",
        "Trend Analysis:",
        "  - CUSUM threshold exceeded: 6.2 > 5.0",
        "",
        "IMPORTANT: This is an ADVISORY OUTPUT ONLY."
    ],
    recommended_posture=SystemPosture.ENHANCED_MONITORING,
    anomaly_indicators=[
        "Track density significantly deviates from baseline",
        "CUSUM threshold exceeded: 6.2"
    ],
    advisory_statement="ADVISORY OUTPUT ONLY - No action recommendations..."
)
```

---

**Last Updated**: 2024

