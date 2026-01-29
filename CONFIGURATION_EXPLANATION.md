# Centralized Configuration Module - Explanation

## Overview

The centralized configuration module (`abhedya/infrastructure/config/config.py`) contains **ALL** system constants, thresholds, and configuration values in a single, immutable location. This ensures consistency, auditability, and enforces fail-safe defaults throughout the system.

## Critical Safety Rule

**If any module fails, data is stale, confidence is insufficient, or inputs conflict, the system MUST revert to NO ACTION / MONITORING ONLY.**

This rule is enforced through:
1. Configuration validation on module import
2. Runtime checks in all modules
3. Fail-safe defaults in all configuration classes
4. Explicit error handling that defaults to safe states

---

## Configuration Sections Explained

### 1. Ethical and Safety Constraints (`EthicalConstraints`)

**Purpose**: Mandatory ethical and safety constraints that **CANNOT** be disabled or modified.

**Key Values**:
- `MANDATORY_HUMAN_APPROVAL_REQUIRED`: Always `True` - ensures all recommendations require human approval
- `HUMAN_OPERATOR_REQUIRED`: Always `True` - system requires human operator presence
- `ADVISORY_ONLY_MODE`: Always `True` - system operates in advisory-only mode (no execution authority)
- `AUTONOMOUS_ACTIONS_PROHIBITED`: Always `True` - no autonomous actions allowed
- `FAIL_SAFE_DEFAULT_ACTION`: Always `"NO_ACTION"` - default action on any failure
- `FAIL_SAFE_DEFAULT_MODE`: Always `"MONITORING_ONLY"` - default mode on any failure

**Safety Guarantee**: These values are validated on import. If any attempt is made to set them to unsafe values, the system will raise a `ValueError` and refuse to start.

**Usage**: All modules check these constraints before performing any operations. If constraints are violated, the system immediately defaults to `NO_ACTION / MONITORING_ONLY`.

---

### 2. System Operation Modes (`SystemOperationMode`)

**Purpose**: Defines all valid system operation modes as an enumeration.

**Modes**:
- `MONITORING_ONLY`: Default fail-safe mode - monitoring only, no actions taken
- `ACTIVE_SURVEILLANCE`: Active monitoring with threat assessment enabled
- `ALERT`: Alert condition active - elevated monitoring and assessment
- `MAINTENANCE`: System maintenance mode - limited functionality
- `OFFLINE`: System offline - no operations
- `ERROR`: Error state - automatically triggers fail-safe to `MONITORING_ONLY`

**Default Behavior**: System always starts in `MONITORING_ONLY` mode. Any error automatically transitions to `MONITORING_ONLY`.

**Fail-Safe**: If system enters `ERROR` mode or any failure is detected, it immediately reverts to `MONITORING_ONLY`.

---

### 3. Protected Airspace Configuration (`ProtectedAirspaceConfiguration`)

**Purpose**: Defines protected airspace zones and their threat assessment parameters.

**Zone Definitions**:

1. **Critical Zone** (20 km radius):
   - `CRITICAL_ZONE_RADIUS_METERS`: 20,000 meters
   - `CRITICAL_ZONE_THREAT_MULTIPLIER`: 2.0
   - Entities in this zone have threat levels multiplied by 2.0
   - Highest priority monitoring and assessment

2. **Protected Zone** (50 km radius):
   - `PROTECTED_ZONE_RADIUS_METERS`: 50,000 meters
   - `PROTECTED_ZONE_THREAT_MULTIPLIER`: 1.5
   - Entities in this zone have threat levels multiplied by 1.5
   - Standard monitoring and assessment

3. **Extended Zone** (100 km radius):
   - `EXTENDED_ZONE_RADIUS_METERS`: 100,000 meters
   - `EXTENDED_ZONE_THREAT_MULTIPLIER`: 1.2
   - Entities in this zone have threat levels multiplied by 1.2
   - Lower priority monitoring

**Additional Parameters**:
- `MAXIMUM_DETECTION_RANGE_METERS`: 200,000 meters (200 km) - maximum sensor range
- `MINIMUM_SAFE_DISTANCE_METERS`: 1,000 meters (1 km) - minimum distance for safe classification

**Usage**: Threat assessment algorithms use these zones to adjust threat levels based on proximity to the protected area. Entities closer to the system origin have higher threat multipliers.

---

### 4. Confidence Thresholds (`ConfidenceThresholds`)

**Purpose**: Defines minimum confidence levels for all system operations. **If confidence falls below these thresholds, the system defaults to NO ACTION.**

**Key Thresholds**:

- `MINIMUM_SENSOR_DETECTION_CONFIDENCE`: 0.5 (50%)
  - Minimum confidence for sensor detection to be considered valid
  - Below this: Detection is ignored, system continues monitoring

- `MINIMUM_TRACK_CREATION_CONFIDENCE`: 0.6 (60%)
  - Minimum confidence to create a new track from sensor readings
  - Below this: Track is not created, system continues monitoring

- `MINIMUM_ENTITY_CLASSIFICATION_CONFIDENCE`: 0.6 (60%)
  - Minimum confidence for entity type classification
  - Below this: Entity remains `UNKNOWN`, system defaults to monitoring

- `MINIMUM_THREAT_ASSESSMENT_CONFIDENCE`: 0.7 (70%)
  - Minimum confidence for threat level assessment
  - Below this: Threat level remains `NONE`, no recommendations generated

- `MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE`: 0.7 (70%)
  - Minimum confidence to generate an advisory recommendation
  - Below this: No recommendation generated, system defaults to `NO_ACTION`

- `HIGH_CONFIDENCE_THRESHOLD`: 0.8 (80%)
  - Above this: Recommendations are marked as high priority
  - Used for prioritization in human interface

- `CRITICAL_CONFIDENCE_THRESHOLD`: 0.95 (95%)
  - Above this: Immediate human attention required
  - Triggers urgent presentation to operators

**Fail-Safe Behavior**: If any operation's confidence is below its threshold, the system:
1. Does not perform the operation
2. Logs the confidence failure
3. Defaults to `NO_ACTION / MONITORING_ONLY`
4. Continues monitoring without taking action

---

### 5. Uncertainty Limits (`UncertaintyLimits`)

**Purpose**: Defines maximum acceptable uncertainty levels. **If uncertainty exceeds these limits, the system defaults to NO ACTION / MONITORING ONLY.**

**Key Limits**:

- `MAXIMUM_POSITION_UNCERTAINTY_METERS`: 5,000 meters (5 km)
  - Maximum acceptable uncertainty in entity position
  - Above this: Position is considered unreliable, system defaults to monitoring

- `MAXIMUM_VELOCITY_UNCERTAINTY_METERS_PER_SECOND`: 50.0 m/s
  - Maximum acceptable uncertainty in entity velocity
  - Above this: Velocity is considered unreliable, system defaults to monitoring

- `MAXIMUM_TIME_SINCE_LAST_UPDATE_SECONDS`: 30.0 seconds
  - Maximum time since last data update
  - Above this: Data is considered stale, system defaults to monitoring

- `MAXIMUM_SENSOR_DATA_AGE_SECONDS`: 10.0 seconds
  - Maximum age of sensor data before considered stale
  - Above this: Sensor data is ignored, system defaults to monitoring

- `MAXIMUM_TRACK_AGE_WITHOUT_UPDATES_SECONDS`: 60.0 seconds
  - Maximum time a track can exist without updates
  - Above this: Track is dropped, system continues monitoring

**Fail-Safe Behavior**: If any uncertainty limit is exceeded:
1. The system detects stale or unreliable data
2. Logs the uncertainty violation
3. Defaults to `NO_ACTION / MONITORING_ONLY`
4. Continues monitoring with fresh data only

---

### 6. Threat Assessment Thresholds (`ThreatAssessmentThresholds`)

**Purpose**: Defines thresholds for threat level assessment and behavior analysis.

**Threat Level Thresholds** (0.0 to 1.0 scale):
- `THREAT_LEVEL_NONE_THRESHOLD`: 0.0 - No threat
- `THREAT_LEVEL_LOW_THRESHOLD`: 0.3 - Low threat level
- `THREAT_LEVEL_MEDIUM_THRESHOLD`: 0.6 - Medium threat level
- `THREAT_LEVEL_HIGH_THRESHOLD`: 0.8 - High threat level
- `THREAT_LEVEL_CRITICAL_THRESHOLD`: 0.95 - Critical threat level

**Speed Thresholds**:
- `HOSTILE_SPEED_THRESHOLD_METERS_PER_SECOND`: 300.0 m/s (~1080 km/h)
  - Speed above which entity is considered potentially hostile
  - Used in entity classification

- `CIVILIAN_SPEED_THRESHOLD_METERS_PER_SECOND`: 100.0 m/s (~360 km/h)
  - Speed below which entity is considered potentially civilian
  - Used in entity classification

**Behavior Pattern Thresholds**:
- `HOSTILE_BEHAVIOR_PATTERN_THRESHOLD`: 0.7
  - Behavior pattern score above which entity is classified as hostile
  - Based on trajectory, speed, and proximity patterns

- `SUSPICIOUS_BEHAVIOR_PATTERN_THRESHOLD`: 0.5
  - Behavior pattern score above which entity is considered suspicious
  - Triggers additional monitoring and assessment

**Proximity Multipliers**:
- `CRITICAL_ZONE_PROXIMITY_MULTIPLIER`: 2.0
- `PROTECTED_ZONE_PROXIMITY_MULTIPLIER`: 1.5
- `EXTENDED_ZONE_PROXIMITY_MULTIPLIER`: 1.2

**Usage**: Threat assessment algorithms use these thresholds to classify entities and assess threat levels. Higher threat levels trigger more urgent advisory recommendations.

---

### 7. Sensor Configuration (`SensorConfiguration`)

**Purpose**: Defines sensor system parameters for simulation.

**Update Rates** (Hertz - updates per second):
- `DEFAULT_RADAR_UPDATE_RATE_HERTZ`: 1.0 Hz (1 update per second)
- `DEFAULT_IFF_UPDATE_RATE_HERTZ`: 2.0 Hz (2 updates per second)
- `DEFAULT_OPTICAL_UPDATE_RATE_HERTZ`: 0.5 Hz (1 update per 2 seconds)

**Detection Ranges** (meters):
- `DEFAULT_RADAR_RANGE_METERS`: 150,000 meters (150 km)
- `DEFAULT_IFF_RANGE_METERS`: 200,000 meters (200 km)
- `DEFAULT_OPTICAL_RANGE_METERS`: 50,000 meters (50 km)

**Detection Thresholds** (0.0 to 1.0):
- `DEFAULT_RADAR_DETECTION_THRESHOLD`: 0.4
- `DEFAULT_IFF_DETECTION_THRESHOLD`: 0.6
- `DEFAULT_OPTICAL_DETECTION_THRESHOLD`: 0.5

**Noise Parameters** (for realistic simulation):
- `RADAR_POSITION_NOISE_STANDARD_DEVIATION_METERS`: 50.0 meters
- `RADAR_VELOCITY_NOISE_STANDARD_DEVIATION_METERS_PER_SECOND`: 5.0 m/s
- `IFF_POSITION_NOISE_STANDARD_DEVIATION_METERS`: 30.0 meters
- `IFF_VELOCITY_NOISE_STANDARD_DEVIATION_METERS_PER_SECOND`: 3.0 m/s

**Sensor Fusion Parameters**:
- `SENSOR_FUSION_CORRELATION_DISTANCE_THRESHOLD_METERS`: 5,000 meters (5 km)
  - Maximum distance for sensor readings to be correlated to the same track
- `SENSOR_FUSION_TIME_WINDOW_SECONDS`: 2.0 seconds
  - Time window for sensor fusion correlation

**Usage**: Sensor simulation modules use these parameters to generate realistic sensor readings with appropriate noise and update rates.

---

### 8. Advisory Recommendation Configuration (`AdvisoryRecommendationConfiguration`)

**Purpose**: Configuration for advisory recommendation generation.

**Important**: All recommendations are **ADVISORY ONLY** - no execution authority.

**Key Values**:
- `MINIMUM_RECOMMENDATION_CONFIDENCE`: 0.7 (70%)
  - Minimum confidence to generate a recommendation
  - Below this: No recommendation generated, system defaults to `NO_ACTION`

- `HIGH_PRIORITY_RECOMMENDATION_THRESHOLD`: 0.8 (80%)
  - Above this: Recommendation is marked as high priority
  - Used for prioritization in human interface

- `CRITICAL_PRIORITY_RECOMMENDATION_THRESHOLD`: 0.95 (95%)
  - Above this: Recommendation is marked as critical priority
  - Triggers urgent presentation to operators

- `MAXIMUM_RECOMMENDATIONS_PER_CYCLE`: 100
  - Maximum recommendations generated per system cycle
  - Prevents system overload

- `MAXIMUM_PENDING_RECOMMENDATIONS_QUEUE_SIZE`: 100
  - Maximum size of pending recommendations queue
  - Above this: New recommendations are not generated until queue has space

- `RECOMMENDATION_TIMEOUT_SECONDS`: 300.0 seconds (5 minutes)
  - Recommendations expire after this time
  - Expired recommendations are removed from queue

- `DEFAULT_RECOMMENDATION_ACTION`: `"NO_ACTION"`
  - Default action when no specific action is recommended
  - Ensures fail-safe behavior

- `PROBABILISTIC_REASONING_ENABLED`: `True`
  - Enables probabilistic reasoning in recommendation generation
  - Provides probability assessments along with recommendations

**Fail-Safe Behavior**: If confidence is insufficient or queue is full, no recommendations are generated and system defaults to `NO_ACTION`.

---

### 9. System Performance Limits (`SystemPerformanceLimits`)

**Purpose**: Limits to prevent system overload and ensure fail-safe operation.

**Key Limits**:
- `MAXIMUM_ACTIVE_TRACKS`: 1,000
  - Maximum number of active tracks
  - Above this: New tracks are not created, system continues monitoring existing tracks

- `MAXIMUM_SENSOR_READINGS_PER_CYCLE`: 5,000
  - Maximum sensor readings processed per cycle
  - Above this: Excess readings are queued for next cycle

- `MAXIMUM_PROCESSING_TIME_PER_CYCLE_SECONDS`: 30.0 seconds
  - Maximum processing time per cycle
  - Above this: Cycle is terminated, system defaults to monitoring

- `SYSTEM_TIMEOUT_SECONDS`: 30.0 seconds
  - System timeout - if exceeded, fail-safe is activated
  - System reverts to `MONITORING_ONLY` mode

- `MAXIMUM_MEMORY_USAGE_WARNING_BYTES`: 2,147,483,648 bytes (2 GB)
  - Memory usage warning threshold (logged only, not enforced)
  - Used for monitoring and alerting

**Fail-Safe Behavior**: If any limit is exceeded:
1. System detects overload condition
2. Logs the limit violation
3. Defaults to `NO_ACTION / MONITORING_ONLY`
4. Continues operation within limits

---

### 10. Fail-Safe Configuration (`FailSafeConfiguration`)

**Purpose**: Fail-safe and error handling configuration.

**Fail-Safe Activation Conditions** (all default to `True`):
- `FAIL_SAFE_ON_SENSOR_FAILURE`: `True`
  - Activate fail-safe if sensor fails
- `FAIL_SAFE_ON_STALE_DATA`: `True`
  - Activate fail-safe if data is stale
- `FAIL_SAFE_ON_INSUFFICIENT_CONFIDENCE`: `True`
  - Activate fail-safe if confidence is insufficient
- `FAIL_SAFE_ON_INPUT_CONFLICT`: `True`
  - Activate fail-safe if inputs conflict
- `FAIL_SAFE_ON_SYSTEM_ERROR`: `True`
  - Activate fail-safe on any system error
- `FAIL_SAFE_ON_TIMEOUT`: `True`
  - Activate fail-safe on timeout

**Fail-Safe Defaults**:
- `FAIL_SAFE_DEFAULT_ACTION`: `"NO_ACTION"`
  - Default action when fail-safe is activated
- `FAIL_SAFE_DEFAULT_MODE`: `"MONITORING_ONLY"`
  - Default mode when fail-safe is activated

**Error Handling**:
- `MAXIMUM_CONSECUTIVE_ERRORS_BEFORE_FAIL_SAFE`: 3
  - Maximum consecutive errors before fail-safe activation
  - Allows transient errors without immediate fail-safe
- `ERROR_RECOVERY_TIMEOUT_SECONDS`: 10.0 seconds
  - Time to wait before retry after error
  - Prevents rapid retry loops

**Usage**: All modules check these conditions and activate fail-safe when appropriate. Fail-safe always defaults to `NO_ACTION / MONITORING_ONLY`.

---

### 11. Audit and Logging Configuration (`AuditLoggingConfiguration`)

**Purpose**: Audit logging and trail configuration.

**Key Values**:
- `AUDIT_LOGGING_ENABLED`: `True`
  - Enable audit logging
  - All system events are logged for traceability

- `EXPLAINABILITY_REQUIRED`: `True`
  - Require explainability for all decisions
  - All recommendations include reasoning

- `LOG_RETENTION_DAYS`: 365
  - Log retention period in days
  - Logs older than this are archived or deleted

- `LOG_FILE_ROTATION_SIZE_BYTES`: 104,857,600 bytes (100 MB)
  - Log file rotation size
  - Log files are rotated when they reach this size

- `MAXIMUM_LOG_FILE_SIZE_BYTES`: 104,857,600 bytes (100 MB)
  - Maximum log file size before rotation

- `DEFAULT_LOG_DIRECTORY`: `"logs"`
  - Default directory for log files

- `MANDATORY_LOG_EVENTS`: Tuple of event types that must be logged
  - Critical events that are always logged
  - Includes: system initialization, shutdown, recommendations, approvals, errors, fail-safe activation

**Usage**: Audit logger uses these parameters to manage log files and ensure all critical events are recorded.

---

### 12. Coordinate System Configuration (`CoordinateSystemConfiguration`)

**Purpose**: Coordinate system and spatial reference configuration.

**Key Values**:
- `COORDINATE_SYSTEM_TYPE`: `"CARTESIAN"`
  - Coordinate system type (X, Y, Z in meters)

- `SYSTEM_ORIGIN_X_METERS`: 0.0
- `SYSTEM_ORIGIN_Y_METERS`: 0.0
- `SYSTEM_ORIGIN_Z_METERS`: 0.0
  - System origin coordinates

**Coordinate Bounds** (for validation):
- X: -1,000,000 to 1,000,000 meters (±1000 km)
- Y: -1,000,000 to 1,000,000 meters (±1000 km)
- Z: -100,000 to 200,000 meters (-100 km to 200 km)

**Usage**: All position calculations use these coordinates. Coordinates outside these bounds are considered invalid and trigger fail-safe.

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

# Check ethical constraints
if EthicalConstraints.MANDATORY_HUMAN_APPROVAL_REQUIRED:
    # Human approval is mandatory - cannot proceed without it
    pass

# Check if entity is in critical zone
distance = calculate_distance(entity_position)
if distance < ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS:
    # Entity is in critical zone - apply threat multiplier
    threat_level *= ProtectedAirspaceConfiguration.CRITICAL_ZONE_THREAT_MULTIPLIER

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
3. **Fail-Safe Defaults**: All failure conditions default to `NO_ACTION / MONITORING_ONLY`
4. **Explicit Ethical Constraints**: Ethical constraints cannot be disabled
5. **Clear Documentation**: All configuration values use descriptive names (no abbreviations)
6. **Single Source of Truth**: All configuration is in one location

---

## Maintenance Guidelines

1. **Never modify ethical constraints**: These are non-negotiable
2. **Use descriptive names**: No abbreviations - names should be self-documenting
3. **Document all changes**: Update this explanation when adding new configuration
4. **Validate all values**: Ensure new values pass validation
5. **Test fail-safe behavior**: Verify fail-safe activation with new thresholds
6. **Maintain immutability**: Configuration values should not be modified at runtime

---

**Last Updated**: 2024

