# Configuration Module Documentation

## Overview

The centralized configuration module (`config.py`) contains ALL system constants, thresholds, and configuration values in a single, immutable location. This ensures:

- **Consistency**: All modules use the same configuration values
- **Auditability**: All configuration is visible and traceable
- **Safety**: Fail-safe defaults are enforced
- **Maintainability**: Single source of truth for all configuration

## Critical Safety Rule

**If any module fails, data is stale, confidence is insufficient, or inputs conflict, the system MUST revert to NO ACTION / MONITORING ONLY.**

This rule is enforced through:
1. Configuration validation on import
2. Runtime checks in all modules
3. Fail-safe defaults in all configuration classes
4. Explicit error handling that defaults to safe states

---

## Configuration Sections

### 1. Ethical and Safety Constraints (`EthicalConstraints`)

**Purpose**: Mandatory ethical and safety constraints that CANNOT be disabled.

**Key Values**:
- `MANDATORY_HUMAN_APPROVAL_REQUIRED`: Always `True` - cannot be changed
- `ADVISORY_ONLY_MODE`: Always `True` - system is advisory only
- `FAIL_SAFE_DEFAULT_ACTION`: Always `"NO_ACTION"` - default action on failure
- `FAIL_SAFE_DEFAULT_MODE`: Always `"MONITORING_ONLY"` - default mode on failure

**Safety Guarantee**: These values are validated on import and cannot be modified at runtime.

---

### 2. System Operation Modes (`SystemOperationMode`)

**Purpose**: Defines all valid system operation modes.

**Modes**:
- `MONITORING_ONLY`: Default fail-safe mode - monitoring only, no actions
- `ACTIVE_SURVEILLANCE`: Active monitoring with threat assessment
- `ALERT`: Alert condition active
- `MAINTENANCE`: System maintenance mode
- `OFFLINE`: System offline
- `ERROR`: Error state (triggers fail-safe)

**Default**: System always starts in `MONITORING_ONLY` mode.

---

### 3. Protected Airspace Configuration (`ProtectedAirspaceConfiguration`)

**Purpose**: Defines protected airspace zones and threat assessment parameters.

**Zones**:
1. **Critical Zone**: 20 km radius
   - Immediate threat assessment area
   - Threat multiplier: 2.0
   - Highest priority monitoring

2. **Protected Zone**: 50 km radius
   - Standard threat assessment area
   - Threat multiplier: 1.5
   - Standard monitoring

3. **Extended Zone**: 100 km radius
   - Extended monitoring area
   - Threat multiplier: 1.2
   - Lower priority monitoring

**Key Values**:
- `CRITICAL_ZONE_RADIUS_METERS`: 20,000 meters (20 km)
- `PROTECTED_ZONE_RADIUS_METERS`: 50,000 meters (50 km)
- `EXTENDED_ZONE_RADIUS_METERS`: 100,000 meters (100 km)
- `MAXIMUM_DETECTION_RANGE_METERS`: 200,000 meters (200 km)

**Usage**: Entities within these zones have their threat levels adjusted by the zone multiplier.

---

### 4. Confidence Thresholds (`ConfidenceThresholds`)

**Purpose**: Defines minimum confidence levels for all system operations. If confidence falls below these thresholds, system defaults to NO ACTION.

**Key Thresholds**:
- `MINIMUM_SENSOR_DETECTION_CONFIDENCE`: 0.5 (50%)
  - Minimum confidence for sensor detection to be considered valid
  
- `MINIMUM_TRACK_CREATION_CONFIDENCE`: 0.6 (60%)
  - Minimum confidence to create a new track
  
- `MINIMUM_ENTITY_CLASSIFICATION_CONFIDENCE`: 0.6 (60%)
  - Minimum confidence for entity classification
  
- `MINIMUM_THREAT_ASSESSMENT_CONFIDENCE`: 0.7 (70%)
  - Minimum confidence for threat assessment
  
- `MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE`: 0.7 (70%)
  - Minimum confidence to generate advisory recommendation
  
- `HIGH_CONFIDENCE_THRESHOLD`: 0.8 (80%)
  - Above this, recommendations are high priority
  
- `CRITICAL_CONFIDENCE_THRESHOLD`: 0.95 (95%)
  - Above this, immediate human attention required

**Fail-Safe Behavior**: If any operation's confidence is below the threshold, the system defaults to NO ACTION / MONITORING ONLY.

---

### 5. Uncertainty Limits (`UncertaintyLimits`)

**Purpose**: Defines maximum acceptable uncertainty levels. If uncertainty exceeds these limits, system defaults to NO ACTION.

**Key Limits**:
- `MAXIMUM_POSITION_UNCERTAINTY_METERS`: 5,000 meters (5 km)
  - Maximum acceptable position uncertainty
  
- `MAXIMUM_VELOCITY_UNCERTAINTY_METERS_PER_SECOND`: 50.0 m/s
  - Maximum acceptable velocity uncertainty
  
- `MAXIMUM_TIME_SINCE_LAST_UPDATE_SECONDS`: 30.0 seconds
  - Maximum time since last data update
  
- `MAXIMUM_SENSOR_DATA_AGE_SECONDS`: 10.0 seconds
  - Maximum age of sensor data before considered stale
  
- `MAXIMUM_TRACK_AGE_WITHOUT_UPDATES_SECONDS`: 60.0 seconds
  - Maximum time a track can exist without updates

**Fail-Safe Behavior**: If data is stale or uncertainty is too high, system defaults to NO ACTION.

---

### 6. Threat Assessment Thresholds (`ThreatAssessmentThresholds`)

**Purpose**: Defines thresholds for threat level assessment.

**Threat Level Thresholds** (0.0 to 1.0 scale):
- `THREAT_LEVEL_NONE_THRESHOLD`: 0.0
- `THREAT_LEVEL_LOW_THRESHOLD`: 0.3
- `THREAT_LEVEL_MEDIUM_THRESHOLD`: 0.6
- `THREAT_LEVEL_HIGH_THRESHOLD`: 0.8
- `THREAT_LEVEL_CRITICAL_THRESHOLD`: 0.95

**Speed Thresholds**:
- `HOSTILE_SPEED_THRESHOLD_METERS_PER_SECOND`: 300.0 m/s (~1080 km/h)
  - Speed above which entity is considered potentially hostile
  
- `CIVILIAN_SPEED_THRESHOLD_METERS_PER_SECOND`: 100.0 m/s (~360 km/h)
  - Speed below which entity is considered potentially civilian

**Behavior Thresholds**:
- `HOSTILE_BEHAVIOR_PATTERN_THRESHOLD`: 0.7
  - Behavior pattern score above which entity is considered hostile
  
- `SUSPICIOUS_BEHAVIOR_PATTERN_THRESHOLD`: 0.5
  - Behavior pattern score above which entity is considered suspicious

---

### 7. Sensor Configuration (`SensorConfiguration`)

**Purpose**: Defines sensor system parameters.

**Update Rates** (Hertz):
- `DEFAULT_RADAR_UPDATE_RATE_HERTZ`: 1.0 Hz (1 update per second)
- `DEFAULT_IFF_UPDATE_RATE_HERTZ`: 2.0 Hz (2 updates per second)
- `DEFAULT_OPTICAL_UPDATE_RATE_HERTZ`: 0.5 Hz (1 update per 2 seconds)

**Ranges** (meters):
- `DEFAULT_RADAR_RANGE_METERS`: 150,000 meters (150 km)
- `DEFAULT_IFF_RANGE_METERS`: 200,000 meters (200 km)
- `DEFAULT_OPTICAL_RANGE_METERS`: 50,000 meters (50 km)

**Detection Thresholds**:
- `DEFAULT_RADAR_DETECTION_THRESHOLD`: 0.4
- `DEFAULT_IFF_DETECTION_THRESHOLD`: 0.6
- `DEFAULT_OPTICAL_DETECTION_THRESHOLD`: 0.5

**Noise Parameters**:
- Sensor measurement noise standard deviations for realistic simulation
- Used to model sensor uncertainty

---

### 8. Advisory Recommendation Configuration (`AdvisoryRecommendationConfiguration`)

**Purpose**: Configuration for advisory recommendation generation.

**Key Values**:
- `MINIMUM_RECOMMENDATION_CONFIDENCE`: 0.7 (70%)
  - Minimum confidence to generate recommendation
  
- `MAXIMUM_RECOMMENDATIONS_PER_CYCLE`: 100
  - Maximum recommendations generated per system cycle
  
- `MAXIMUM_PENDING_RECOMMENDATIONS_QUEUE_SIZE`: 100
  - Maximum size of pending recommendations queue
  
- `RECOMMENDATION_TIMEOUT_SECONDS`: 300.0 (5 minutes)
  - Recommendations expire after this time
  
- `DEFAULT_RECOMMENDATION_ACTION`: `"NO_ACTION"`
  - Default action when no specific action recommended

**Important**: All recommendations are ADVISORY ONLY - no execution authority.

---

### 9. System Performance Limits (`SystemPerformanceLimits`)

**Purpose**: Limits to prevent system overload and ensure fail-safe operation.

**Key Limits**:
- `MAXIMUM_ACTIVE_TRACKS`: 1,000
  - Maximum number of active tracks
  
- `MAXIMUM_SENSOR_READINGS_PER_CYCLE`: 5,000
  - Maximum sensor readings processed per cycle
  
- `MAXIMUM_PROCESSING_TIME_PER_CYCLE_SECONDS`: 30.0 seconds
  - Maximum processing time per cycle
  
- `SYSTEM_TIMEOUT_SECONDS`: 30.0 seconds
  - System timeout - if exceeded, fail-safe activated

**Fail-Safe Behavior**: If limits are exceeded, system defaults to NO ACTION / MONITORING ONLY.

---

### 10. Fail-Safe Configuration (`FailSafeConfiguration`)

**Purpose**: Fail-safe and error handling configuration.

**Fail-Safe Activation Conditions**:
- `FAIL_SAFE_ON_SENSOR_FAILURE`: `True`
- `FAIL_SAFE_ON_STALE_DATA`: `True`
- `FAIL_SAFE_ON_INSUFFICIENT_CONFIDENCE`: `True`
- `FAIL_SAFE_ON_INPUT_CONFLICT`: `True`
- `FAIL_SAFE_ON_SYSTEM_ERROR`: `True`
- `FAIL_SAFE_ON_TIMEOUT`: `True`

**Fail-Safe Defaults**:
- `FAIL_SAFE_DEFAULT_ACTION`: `"NO_ACTION"`
- `FAIL_SAFE_DEFAULT_MODE`: `"MONITORING_ONLY"`

**Error Handling**:
- `MAXIMUM_CONSECUTIVE_ERRORS_BEFORE_FAIL_SAFE`: 3
  - Maximum consecutive errors before fail-safe activation
  
- `ERROR_RECOVERY_TIMEOUT_SECONDS`: 10.0 seconds
  - Time to wait before retry after error

---

### 11. Coordinate System Configuration (`CoordinateSystemConfiguration`)

**Purpose**: Coordinate system and spatial reference configuration.

**Key Values**:
- `COORDINATE_SYSTEM_TYPE`: `"CARTESIAN"` (X, Y, Z in meters)
- `SYSTEM_ORIGIN_X_METERS`: 0.0
- `SYSTEM_ORIGIN_Y_METERS`: 0.0
- `SYSTEM_ORIGIN_Z_METERS`: 0.0

**Coordinate Bounds** (for validation):
- X: -1,000,000 to 1,000,000 meters (±1000 km)
- Y: -1,000,000 to 1,000,000 meters (±1000 km)
- Z: -100,000 to 200,000 meters (-100 km to 200 km)

---

## Configuration Validation

All configuration values are validated on module import:

1. **Confidence Values**: Must be in range [0.0, 1.0]
2. **Positive Values**: Must be > 0.0
3. **Non-Negative Values**: Must be >= 0.0
4. **Ethical Constraints**: Must be set to safe values (cannot be disabled)

If validation fails, a `ValueError` is raised immediately, preventing the system from starting with invalid configuration.

---

## Usage Example

```python
from abhedya.infrastructure.config.config import (
    EthicalConstraints,
    ProtectedAirspaceConfiguration,
    ConfidenceThresholds,
    FailSafeConfiguration,
    SystemOperationMode,
)

# Access configuration values
if EthicalConstraints.MANDATORY_HUMAN_APPROVAL_REQUIRED:
    # Human approval is mandatory
    pass

# Check if entity is in critical zone
distance = calculate_distance(entity_position)
if distance < ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS:
    # Entity is in critical zone
    pass

# Check confidence threshold
if confidence < ConfidenceThresholds.MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE:
    # Confidence too low - default to NO ACTION
    return FailSafeConfiguration.FAIL_SAFE_DEFAULT_ACTION

# Get configuration summary for audit
from abhedya.infrastructure.config.config import get_configuration_summary
summary = get_configuration_summary()
```

---

## Safety Guarantees

1. **Immutable Configuration**: All values are class attributes (effectively constants)
2. **Validation on Import**: Configuration is validated when module is imported
3. **Fail-Safe Defaults**: All failure conditions default to NO ACTION / MONITORING ONLY
4. **Explicit Ethical Constraints**: Ethical constraints cannot be disabled
5. **Clear Documentation**: All configuration values are documented with descriptive names

---

## Maintenance Guidelines

1. **Never modify ethical constraints**: These are non-negotiable
2. **Use descriptive names**: No abbreviations - names should be self-documenting
3. **Document all changes**: Update this README when adding new configuration
4. **Validate all values**: Ensure new values pass validation
5. **Test fail-safe behavior**: Verify fail-safe activation with new thresholds

---

**Last Updated**: 2024


