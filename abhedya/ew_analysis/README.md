# Electronic Warfare (EW) Signal Analysis Module

## Overview

The Electronic Warfare Signal Analysis module performs signal analysis and anomaly detection on RF spectrum data.

**SIGNAL ANALYSIS ONLY** - No EW response actions, no counter-EW logic, no control laws.

**ADVISORY ONLY** - All outputs are advisory and do not map to any actions.

## Features

### 1. RF Spectrum Data Simulation
- **Time-Frequency Matrices**: Power levels across frequency and time
- **Noise Floor Modeling**: Realistic noise floor simulation
- **Signal Power Distributions**: Gaussian-shaped signal modeling
- **Deterministic Simulation**: Reproducible with random seed

### 2. Explainable Feature Extraction
- **FFT-based Spectral Components**: Dominant frequency detection
- **Spectral Entropy**: Measures randomness/unpredictability
- **Signal-to-Noise Ratio (SNR)**: Signal strength relative to noise
- **Bandwidth Utilization**: Fraction of occupied bandwidth
- **Frequency Centroid**: Weighted average frequency
- **Occupied Bandwidth**: Frequency range with signals

### 3. Anomaly Detection
- **Statistical Deviation**: Z-score deviation from baseline
- **Entropy Spikes**: Sudden changes in spectral entropy
- **Noise Floor Elevation**: Elevated noise floor detection
- **Unknown Emission Patterns**: Detection of unusual signals

### 4. Advisory Outputs
- **EW State**: `NORMAL` or `ANOMALOUS` (advisory only)
- **Confidence Score**: [0.0, 1.0]
- **Uncertainty**: [0.0, 1.0]
- **Suspected Pattern Description**: Human-readable pattern description
- **Human-Readable Reasoning**: Detailed analysis reasoning

## Components

### 1. Spectrum Simulator (`spectrum_simulator.py`)
Simulates RF spectrum data:
- Time-frequency power matrices
- Noise floor modeling
- Signal injection with Gaussian shapes
- Normal and anomalous spectrum simulation

### 2. Feature Extractor (`feature_extractor.py`)
Extracts explainable features:
- FFT-based dominant frequency detection
- Spectral entropy calculation
- SNR estimation
- Bandwidth utilization analysis
- Frequency centroid calculation
- Occupied bandwidth calculation

### 3. Anomaly Detector (`anomaly_detector.py`)
Detects anomalies using:
- Statistical deviation (Z-score)
- Entropy spike detection
- Noise floor elevation detection
- Unknown emission pattern detection
- Baseline comparison

### 4. EW Analysis Engine (`ew_analysis_engine.py`)
Main engine that:
- Orchestrates spectrum simulation, feature extraction, and anomaly detection
- Aggregates results
- Determines EW state
- Generates advisory outputs

## Usage Example

```python
from abhedya.ew_analysis import EWAnalysisEngine, SpectrumSimulator

# Initialize engine
engine = EWAnalysisEngine(
    enable_spectrum_simulation=True,
    enable_feature_extraction=True,
    enable_anomaly_detection=True
)

# Option 1: Analyze with simulated spectrum
result = engine.analyze_spectrum(simulate_if_missing=True)

# Option 2: Analyze with provided spectrum
simulator = SpectrumSimulator(
    frequency_range_hz=(1e6, 10e9),
    frequency_resolution_hz=1e6,
    time_duration_seconds=1.0
)
spectrum = simulator.simulate_normal_spectrum()
result = engine.analyze_spectrum(spectrum=spectrum)

# Access results
print(f"EW State: {result.ew_state.value} (ADVISORY ONLY)")
print(f"Confidence: {result.confidence:.2%}")
print(f"Uncertainty: {result.uncertainty:.2%}")
print(f"Suspected Pattern: {result.suspected_pattern_description}")

# Print reasoning
for reason in result.reasoning:
    print(f"  {reason}")

# Access features
if result.spectral_features:
    print(f"\nSpectral Entropy: {result.spectral_features.spectral_entropy:.3f}")
    print(f"SNR: {result.spectral_features.signal_to_noise_ratio:.2f} dB")
    print(f"Bandwidth Utilization: {result.spectral_features.bandwidth_utilization:.2%}")

# Access anomaly detection
if result.anomaly_detection:
    print(f"\nAnomaly Detected: {result.anomaly_detection.is_anomalous}")
    print(f"Anomaly Score: {result.anomaly_detection.anomaly_score:.2%}")

print(f"\n{result.analysis_statement}")
```

## Signal Processing Methods

### FFT-based Spectral Analysis
Uses Fast Fourier Transform to identify dominant frequency components:
- Power spectrum calculation
- Peak detection
- Signal thresholding

### Spectral Entropy
Measures randomness/unpredictability:
```
H = -Σ(p * log2(p))
```
Where `p` is the normalized power distribution.

### Signal-to-Noise Ratio (SNR)
```
SNR = signal_power - noise_floor (dB)
```

### Bandwidth Utilization
Fraction of frequency bins with power above noise floor:
```
utilization = occupied_bins / total_bins
```

### Frequency Centroid
Weighted average frequency:
```
centroid = Σ(f * P(f)) / Σ(P(f))
```

## Anomaly Detection Methods

### Statistical Deviation
Uses Z-score to detect deviations from baseline:
```
Z = |feature - baseline_mean| / baseline_std
```
Anomaly if Z > threshold (default: 2.0σ)

### Entropy Spike Detection
Detects sudden changes in spectral entropy:
- Compares current entropy to baseline
- Spike detected if change > threshold (default: 0.3)

### Noise Floor Elevation
Detects elevated noise floor:
- Compares current average power to baseline
- Elevation detected if increase > threshold (default: 5 dB)

### Unknown Emission Detection
Detects unusual signal patterns:
- High SNR with unexpected frequencies
- Multiple dominant frequencies
- Unusual bandwidth utilization

## EW States

### NORMAL
- No significant anomalies detected
- Spectrum within normal parameters
- Baseline comparisons normal

### ANOMALOUS
- Anomalies detected
- Statistical deviations present
- Entropy spikes or noise floor elevation
- Unknown emissions detected

**IMPORTANT**: These states are **ADVISORY ONLY** and do not map to any actions.

## Safety Guarantees

### What This Module DOES:
- ✅ Signal analysis
- ✅ Feature extraction
- ✅ Anomaly detection
- ✅ Advisory outputs

### What This Module DOES NOT Do:
- ❌ EW response actions
- ❌ Counter-EW logic
- ❌ Control laws
- ❌ Jamming capabilities
- ❌ Countermeasures
- ❌ External API calls
- ❌ Network communication

## Configuration

The EW analysis module uses configurable parameters:

### Spectrum Simulator
- `frequency_range_hz`: Frequency range (default: 1 MHz to 10 GHz)
- `frequency_resolution_hz`: Frequency resolution (default: 1 MHz)
- `time_duration_seconds`: Time duration (default: 1.0 s)
- `sample_rate_hz`: Sample rate (default: 1 kHz)
- `noise_floor_dbm`: Noise floor (default: -100 dBm)
- `random_seed`: Random seed for reproducibility

### Feature Extractor
- `snr_threshold_db`: SNR threshold for signal detection (default: 3.0 dB)
- `entropy_normalization`: Whether to normalize entropy (default: True)

### Anomaly Detector
- `z_score_threshold`: Z-score threshold (default: 2.0)
- `entropy_spike_threshold`: Entropy spike threshold (default: 0.3)
- `noise_floor_elevation_threshold_db`: Noise floor elevation threshold (default: 5.0 dB)

## Limitations

1. **Simplified Models**: Uses simplified signal models
2. **No Real Hardware**: Mathematical simulation only
3. **No Environmental Factors**: Atmospheric conditions not considered
4. **Baseline Requirements**: Requires minimum samples for baseline
5. **Constant Noise Floor**: Assumes constant noise floor

## Example Output

```python
EWAnalysisResult(
    result_id="...",
    timestamp=datetime.now(),
    ew_state=EWState.ANOMALOUS,
    confidence=0.75,
    uncertainty=0.25,
    spectral_features=SpectralFeatures(
        spectral_entropy=0.85,
        signal_to_noise_ratio=12.5,
        bandwidth_utilization=0.65,
        dominant_frequencies=[2.4e9, 5.8e9],
        ...
    ),
    anomaly_detection=AnomalyDetectionResult(
        is_anomalous=True,
        anomaly_score=0.75,
        statistical_deviation=2.5,
        entropy_spike_detected=True,
        suspected_pattern="High spectral entropy, Unknown emission",
        ...
    ),
    reasoning=[
        "EW Analysis State: ANOMALOUS (ADVISORY ONLY)",
        "Spectral Entropy: 0.850",
        "SNR: 12.50 dB",
        "Entropy spike detected: change of 0.350",
        ...
    ],
    suspected_pattern_description="High spectral entropy, Unknown emission",
    analysis_statement="SIGNAL ANALYSIS ONLY - No EW response actions..."
)
```

## Integration

### Inputs
- **SpectrumData**: RF spectrum data (simulated or provided)
- **Optional**: Historical spectrum data for baseline

### Outputs
- **EWAnalysisResult**: Advisory result object
- **No Execution Logic**: Outputs are advisory only
- **No Actions**: No actions are recommended

### No Coupling
- Does not modify existing modules
- Does not execute any actions
- Pure signal analysis

## Dependencies

- `numpy`: For numerical operations and array handling
- `math`: For mathematical functions
- `statistics`: For statistical calculations
- `datetime`: For timestamps
- `typing`: For type hints

---

**Last Updated**: 2024

