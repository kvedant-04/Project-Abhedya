# Data Preprocessing and Validation Layer

## Overview

The Data Preprocessing and Validation Layer provides classical statistical techniques for preprocessing sensor data. It ensures data quality through validation, outlier detection, noise reduction, missing data handling, and normalization.

**Key Principles**:
- **Classical Statistical Techniques Only**: No machine learning
- **Defensive Programming**: Extensive error checking and validation
- **Fail-Safe Behavior**: Corrupted or inconsistent data is rejected, not modified
- **Transparency**: All operations are explainable and auditable

## Components

### 1. Data Validator (`validator.py`)

Validates sensor data for:
- **Missing Data**: Checks for required fields
- **Temporal Consistency**: Validates timestamp ordering and gaps
- **Value Ranges**: Ensures values are within acceptable ranges
- **Data Types**: Validates data types and structure
- **Configuration Compliance**: Checks against system configuration thresholds

**Methods**:
- `validate_detection()`: Validate a single detection
- `validate_temporal_consistency()`: Validate temporal ordering of detections

**Fail-Safe Behavior**: Invalid data is rejected with detailed error messages.

### 2. Outlier Detector (`outlier_detection.py`)

Detects outliers using classical statistical techniques:
- **Z-Score Method**: Detects values far from mean (default threshold: 3.0σ)
- **Interquartile Range (IQR)**: Detects values outside 1.5 × IQR
- **Distance-Based**: Detects values far from expected position
- **Temporal Outliers**: Detects sudden changes in time series

**Methods**:
- `detect_outlier_in_detection()`: Detect outliers in a single detection
- `detect_temporal_outliers()`: Detect outliers in a sequence

**Fail-Safe Behavior**: Outliers can be rejected or flagged based on configuration.

### 3. Noise Reducer (`noise_reduction.py`)

Reduces noise using classical statistical filters:
- **Moving Average**: Smooths data using rolling average (default window: 5)
- **Median Filter**: Removes outliers using median (default window: 5)
- **Exponential Smoothing**: Weighted average with exponential decay (α=0.3)

**Methods**:
- `reduce_noise_moving_average()`: Apply moving average filter
- `reduce_noise_median_filter()`: Apply median filter
- `reduce_noise_exponential_smoothing()`: Apply exponential smoothing
- `reduce_position_noise()`: Reduce noise in position measurements
- `reduce_velocity_noise()`: Reduce noise in velocity measurements

**Fail-Safe Behavior**: If noise reduction fails, original data is used (not rejected).

### 4. Data Normalizer (`normalizer.py`)

Normalizes data using classical statistical techniques:
- **Min-Max Normalization**: Normalize to [0, 1] range
- **Z-Score Normalization**: Normalize to mean=0, std=1
- **Robust Normalization**: Normalize using median and IQR (robust to outliers)

**Methods**:
- `normalize_min_max()`: Min-max normalization
- `normalize_z_score()`: Z-score normalization
- `normalize_robust()`: Robust normalization
- `normalize_detection_coordinates()`: Normalize coordinates in detections

**Fail-Safe Behavior**: If normalization fails, original data is used.

### 5. Data Preprocessor (`preprocessor.py`)

Main orchestrator that coordinates all preprocessing operations:
- **Validation**: Validates all detections
- **Outlier Detection**: Detects and optionally rejects outliers
- **Missing Data Handling**: Handles missing data (rejects critical missing, fills optional)
- **Temporal Consistency**: Validates temporal ordering
- **Noise Reduction**: Optional noise reduction
- **Normalization**: Optional normalization

**Methods**:
- `preprocess()`: Preprocess a list of detections
- `preprocess_single()`: Preprocess a single detection

**Fail-Safe Behavior**: Invalid data is rejected, not modified.

## Usage Example

```python
from abhedya.preprocessing import DataPreprocessor

# Initialize preprocessor
preprocessor = DataPreprocessor(
    enable_validation=True,
    enable_outlier_detection=True,
    enable_noise_reduction=False,  # Optional
    enable_normalization=False,  # Optional
    reject_outliers=True,
    strict_mode=True
)

# Preprocess detections
result = preprocessor.preprocess(
    detections=raw_detections,
    historical_detections=previous_detections  # Optional, for context
)

# Check results
if result.is_success:
    processed = result.processed_detections
    print(f"Processed {len(processed)} detections")
else:
    print(f"Preprocessing failed: {result.validation_errors}")
    print(f"Rejected {len(result.rejected_detections)} detections")
    print(f"Outliers detected: {result.outlier_count}")
    print(f"Missing data: {result.missing_data_count}")
```

## Preprocessing Pipeline

The preprocessing pipeline executes in the following order:

1. **Missing Data Handling**
   - Critical missing data: Detection is rejected
   - Optional missing data: Default values are filled

2. **Validation**
   - Required fields check
   - Value range validation
   - Data type validation
   - Configuration compliance

3. **Outlier Detection**
   - Statistical outlier detection (Z-score, IQR)
   - Temporal outlier detection
   - Outliers are rejected or flagged based on configuration

4. **Temporal Consistency Validation**
   - Timestamp ordering check
   - Time gap validation
   - In strict mode, failures reject all detections

5. **Noise Reduction** (Optional)
   - Moving average, median filter, or exponential smoothing
   - Applied to position and velocity measurements
   - Fail-safe: If fails, original data is used

6. **Normalization** (Optional)
   - Min-max, Z-score, or robust normalization
   - Applied to coordinates
   - Fail-safe: If fails, original data is used

7. **Final Validation**
   - Re-validate processed data
   - Ensure processed data still meets requirements

## Fail-Safe Behavior

### Rejection vs. Modification

**Rejected Data**:
- Missing critical fields
- Invalid data types
- Out of range values
- Failed validation
- Detected outliers (if `reject_outliers=True`)

**Modified Data**:
- Optional missing fields (filled with defaults)
- Noise reduction (if enabled)
- Normalization (if enabled)

**Never Modified**:
- Invalid data is never "fixed" or "corrected"
- Corrupted data is rejected
- Inconsistent data is rejected

### Error Handling

All operations use defensive programming:
- Try-except blocks around all operations
- Fail-safe defaults on errors
- Detailed error messages
- No silent failures

### Configuration Compliance

All operations check against system configuration:
- Confidence thresholds
- Uncertainty limits
- Coordinate bounds
- Temporal limits

## Statistical Techniques Used

### Outlier Detection
- **Z-Score**: `z = (x - μ) / σ`, threshold: 3.0σ
- **IQR**: `outlier if x < Q1 - 1.5×IQR or x > Q3 + 1.5×IQR`
- **Temporal**: Speed-based outlier detection

### Noise Reduction
- **Moving Average**: `S_t = (1/n) × Σ(X_{t-i})` for i=0 to n-1
- **Median Filter**: `S_t = median(X_{t-w/2} to X_{t+w/2})`
- **Exponential Smoothing**: `S_t = α×X_t + (1-α)×S_{t-1}`

### Normalization
- **Min-Max**: `X_norm = (X - X_min) / (X_max - X_min)`
- **Z-Score**: `X_norm = (X - μ) / σ`
- **Robust**: `X_norm = (X - median) / IQR`

## Configuration

The preprocessing layer uses configuration from `abhedya.infrastructure.config.config`:
- `ConfidenceThresholds`: Minimum confidence thresholds
- `UncertaintyLimits`: Maximum uncertainty limits
- `CoordinateSystemConfiguration`: Coordinate bounds
- `FailSafeConfiguration`: Fail-safe behavior settings

## Performance Considerations

- **Efficiency**: All operations use efficient classical algorithms
- **Memory**: Minimal memory overhead, processes data in-place where possible
- **Scalability**: Handles large datasets efficiently
- **Deterministic**: All operations are deterministic (no randomness)

## Testing and Validation

The preprocessing layer includes:
- **Unit Tests**: Test each component independently
- **Integration Tests**: Test full preprocessing pipeline
- **Edge Cases**: Test with missing data, outliers, corrupted data
- **Fail-Safe Tests**: Verify fail-safe behavior

## Limitations

1. **Classical Techniques Only**: No machine learning or advanced methods
2. **Statistical Assumptions**: Assumes normal distribution for some methods
3. **Window Size**: Fixed window sizes for filters (not adaptive)
4. **No Learning**: Does not learn from historical data patterns

## Future Enhancements

Potential additions (while maintaining safety):
- Adaptive window sizes
- More sophisticated outlier detection methods
- Additional noise reduction techniques
- Real-time preprocessing support

---

**Last Updated**: 2024

