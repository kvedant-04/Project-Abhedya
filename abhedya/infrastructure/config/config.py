"""
Centralized Configuration Module

This module contains ALL system constants, thresholds, and configuration values
in a single, immutable location. This ensures consistency, auditability, and
enforces fail-safe defaults throughout the system.

CRITICAL SAFETY RULE:
If any module fails, data is stale, confidence is insufficient, or inputs conflict,
the system MUST revert to NO ACTION / MONITORING ONLY.

All configuration values are immutable and cannot be modified at runtime.
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
from enum import Enum


# ============================================================================
# ETHICAL AND SAFETY CONSTRAINTS (MANDATORY - NON-NEGOTIABLE)
# ============================================================================

class EthicalConstraints:
    """
    Ethical and safety constraints that CANNOT be disabled or modified.
    These are enforced at multiple levels (code, runtime, validation).
    """
    
    # Mandatory human approval requirement
    MANDATORY_HUMAN_APPROVAL_REQUIRED: bool = True
    
    # System must have human operator present
    HUMAN_OPERATOR_REQUIRED: bool = True
    
    # Advisory-only operation (no execution authority)
    ADVISORY_ONLY_MODE: bool = True
    
    # No autonomous actions allowed
    AUTONOMOUS_ACTIONS_PROHIBITED: bool = True
    
    # Fail-safe default action
    FAIL_SAFE_DEFAULT_ACTION: str = "NO_ACTION"
    
    # Fail-safe default mode
    FAIL_SAFE_DEFAULT_MODE: str = "MONITORING_ONLY"
    
    # Maximum time without human interaction before fail-safe
    MAXIMUM_TIME_WITHOUT_HUMAN_INTERACTION_SECONDS: float = 300.0  # 5 minutes
    
    # Minimum human response time (for realistic simulation)
    MINIMUM_HUMAN_RESPONSE_TIME_SECONDS: float = 5.0


# ============================================================================
# SYSTEM OPERATION MODES
# ============================================================================

class SystemOperationMode(str, Enum):
    """
    System operation modes. System defaults to MONITORING_ONLY on any failure.
    """
    MONITORING_ONLY = "MONITORING_ONLY"           # Default fail-safe mode
    ACTIVE_SURVEILLANCE = "ACTIVE_SURVEILLANCE"   # Active monitoring with assessment
    ALERT = "ALERT"                                # Alert condition active
    MAINTENANCE = "MAINTENANCE"                    # System maintenance mode
    OFFLINE = "OFFLINE"                            # System offline
    ERROR = "ERROR"                                # Error state (fail-safe)


# ============================================================================
# PROTECTED AIRSPACE DEFINITIONS
# ============================================================================

@dataclass(frozen=True)
class ProtectedAirspaceZone:
    """
    Immutable protected airspace zone definition.
    """
    zone_name: str
    center_coordinates: Tuple[float, float, float]  # (x, y, z) in meters
    radius_meters: float
    threat_multiplier: float  # Threat assessment multiplier for entities in zone
    description: str


class ProtectedAirspaceConfiguration:
    """
    Protected airspace configuration. All zones are defined relative to
    system origin (0, 0, 0).
    """
    
    # System origin coordinates (meters)
    SYSTEM_ORIGIN_COORDINATES: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Critical zone: Immediate threat area
    CRITICAL_ZONE_RADIUS_METERS: float = 20000.0  # 20 km
    CRITICAL_ZONE_THREAT_MULTIPLIER: float = 2.0
    CRITICAL_ZONE_DESCRIPTION: str = "Critical protected zone - immediate threat assessment area"
    
    # Protected zone: Standard protected area
    PROTECTED_ZONE_RADIUS_METERS: float = 50000.0  # 50 km
    PROTECTED_ZONE_THREAT_MULTIPLIER: float = 1.5
    PROTECTED_ZONE_DESCRIPTION: str = "Protected zone - standard threat assessment area"
    
    # Extended zone: Extended monitoring area
    EXTENDED_ZONE_RADIUS_METERS: float = 100000.0  # 100 km
    EXTENDED_ZONE_THREAT_MULTIPLIER: float = 1.2
    EXTENDED_ZONE_DESCRIPTION: str = "Extended zone - extended monitoring area"
    
    # Maximum detection range
    MAXIMUM_DETECTION_RANGE_METERS: float = 200000.0  # 200 km
    
    # Minimum safe distance for entity classification
    MINIMUM_SAFE_DISTANCE_METERS: float = 1000.0  # 1 km


# ============================================================================
# CONFIDENCE THRESHOLDS AND UNCERTAINTY LIMITS
# ============================================================================

class ConfidenceThresholds:
    """
    Confidence thresholds for system operations. All values are in range [0.0, 1.0].
    If confidence falls below these thresholds, system defaults to NO ACTION.
    """
    
    # Minimum confidence for sensor detection to be considered valid
    MINIMUM_SENSOR_DETECTION_CONFIDENCE: float = 0.5
    
    # Minimum confidence for track creation
    MINIMUM_TRACK_CREATION_CONFIDENCE: float = 0.6
    
    # Minimum confidence for track maintenance (below this, track is dropped)
    MINIMUM_TRACK_MAINTENANCE_CONFIDENCE: float = 0.4
    
    # Minimum confidence for entity classification
    MINIMUM_ENTITY_CLASSIFICATION_CONFIDENCE: float = 0.6
    
    # Minimum confidence for threat assessment
    MINIMUM_THREAT_ASSESSMENT_CONFIDENCE: float = 0.7
    
    # Minimum confidence for advisory recommendation generation
    MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE: float = 0.7
    
    # High confidence threshold (above this, recommendations are high priority)
    HIGH_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Critical confidence threshold (above this, immediate human attention required)
    CRITICAL_CONFIDENCE_THRESHOLD: float = 0.95
    
    # Maximum acceptable uncertainty (above this, system defaults to NO ACTION)
    MAXIMUM_ACCEPTABLE_UNCERTAINTY: float = 0.3  # 30% uncertainty max
    
    # Minimum confidence for IFF identification
    MINIMUM_IFF_IDENTIFICATION_CONFIDENCE: float = 0.9
    
    # Minimum confidence for sensor fusion
    MINIMUM_SENSOR_FUSION_CONFIDENCE: float = 0.65


class UncertaintyLimits:
    """
    Uncertainty limits for system operations. If uncertainty exceeds these limits,
    system defaults to NO ACTION / MONITORING ONLY.
    """
    
    # Maximum acceptable position uncertainty (meters)
    MAXIMUM_POSITION_UNCERTAINTY_METERS: float = 5000.0  # 5 km
    
    # Maximum acceptable velocity uncertainty (meters per second)
    MAXIMUM_VELOCITY_UNCERTAINTY_METERS_PER_SECOND: float = 50.0
    
    # Maximum acceptable time since last update (seconds)
    MAXIMUM_TIME_SINCE_LAST_UPDATE_SECONDS: float = 30.0
    
    # Maximum acceptable sensor data age (seconds)
    MAXIMUM_SENSOR_DATA_AGE_SECONDS: float = 10.0
    
    # Maximum acceptable track age without updates (seconds)
    MAXIMUM_TRACK_AGE_WITHOUT_UPDATES_SECONDS: float = 60.0


# ============================================================================
# THREAT ASSESSMENT THRESHOLDS
# ============================================================================

class ThreatAssessmentThresholds:
    """
    Thresholds for threat level assessment. All values are in range [0.0, 1.0].
    """
    
    # Threat level thresholds
    THREAT_LEVEL_NONE_THRESHOLD: float = 0.0
    THREAT_LEVEL_LOW_THRESHOLD: float = 0.3
    THREAT_LEVEL_MEDIUM_THRESHOLD: float = 0.6
    THREAT_LEVEL_HIGH_THRESHOLD: float = 0.8
    THREAT_LEVEL_CRITICAL_THRESHOLD: float = 0.95
    
    # Speed thresholds for threat assessment (meters per second)
    HOSTILE_SPEED_THRESHOLD_METERS_PER_SECOND: float = 300.0  # ~1080 km/h
    CIVILIAN_SPEED_THRESHOLD_METERS_PER_SECOND: float = 100.0  # ~360 km/h
    
    # Behavior pattern thresholds
    HOSTILE_BEHAVIOR_PATTERN_THRESHOLD: float = 0.7
    SUSPICIOUS_BEHAVIOR_PATTERN_THRESHOLD: float = 0.5
    
    # Proximity threat multipliers
    CRITICAL_ZONE_PROXIMITY_MULTIPLIER: float = 2.0
    PROTECTED_ZONE_PROXIMITY_MULTIPLIER: float = 1.5
    EXTENDED_ZONE_PROXIMITY_MULTIPLIER: float = 1.2


# ============================================================================
# SENSOR CONFIGURATION
# ============================================================================

class SensorConfiguration:
    """
    Sensor system configuration parameters.
    """
    
    # Default sensor update rates (Hertz)
    DEFAULT_RADAR_UPDATE_RATE_HERTZ: float = 1.0
    DEFAULT_IFF_UPDATE_RATE_HERTZ: float = 2.0
    DEFAULT_OPTICAL_UPDATE_RATE_HERTZ: float = 0.5
    
    # Default sensor ranges (meters)
    DEFAULT_RADAR_RANGE_METERS: float = 150000.0  # 150 km
    DEFAULT_IFF_RANGE_METERS: float = 200000.0    # 200 km
    DEFAULT_OPTICAL_RANGE_METERS: float = 50000.0  # 50 km
    
    # Default detection thresholds
    DEFAULT_RADAR_DETECTION_THRESHOLD: float = 0.4
    DEFAULT_IFF_DETECTION_THRESHOLD: float = 0.6
    DEFAULT_OPTICAL_DETECTION_THRESHOLD: float = 0.5
    
    # Sensor measurement noise parameters (standard deviation)
    RADAR_POSITION_NOISE_STANDARD_DEVIATION_METERS: float = 50.0
    RADAR_VELOCITY_NOISE_STANDARD_DEVIATION_METERS_PER_SECOND: float = 5.0
    IFF_POSITION_NOISE_STANDARD_DEVIATION_METERS: float = 30.0
    IFF_VELOCITY_NOISE_STANDARD_DEVIATION_METERS_PER_SECOND: float = 3.0
    
    # Sensor fusion parameters
    SENSOR_FUSION_CORRELATION_DISTANCE_THRESHOLD_METERS: float = 5000.0  # 5 km
    SENSOR_FUSION_TIME_WINDOW_SECONDS: float = 2.0


# ============================================================================
# ADVISORY RECOMMENDATION CONFIGURATION
# ============================================================================

class AdvisoryRecommendationConfiguration:
    """
    Advisory recommendation generation configuration.
    IMPORTANT: All recommendations are ADVISORY ONLY - no execution authority.
    """
    
    # Minimum confidence for recommendation generation
    MINIMUM_RECOMMENDATION_CONFIDENCE: float = 0.7
    
    # Recommendation priority thresholds
    HIGH_PRIORITY_RECOMMENDATION_THRESHOLD: float = 0.8
    CRITICAL_PRIORITY_RECOMMENDATION_THRESHOLD: float = 0.95
    
    # Maximum recommendations per cycle
    MAXIMUM_RECOMMENDATIONS_PER_CYCLE: int = 100
    
    # Maximum pending recommendations queue size
    MAXIMUM_PENDING_RECOMMENDATIONS_QUEUE_SIZE: int = 100
    
    # Recommendation timeout (seconds) - recommendations expire after this time
    RECOMMENDATION_TIMEOUT_SECONDS: float = 300.0  # 5 minutes
    
    # Default recommendation action (when no specific action recommended)
    DEFAULT_RECOMMENDATION_ACTION: str = "NO_ACTION"
    
    # Probabilistic reasoning enabled
    PROBABILISTIC_REASONING_ENABLED: bool = True


# ============================================================================
# SYSTEM PERFORMANCE AND SAFETY LIMITS
# ============================================================================

class SystemPerformanceLimits:
    """
    System performance limits to prevent overload and ensure fail-safe operation.
    """
    
    # Maximum number of active tracks
    MAXIMUM_ACTIVE_TRACKS: int = 1000
    
    # Maximum number of sensor readings per cycle
    MAXIMUM_SENSOR_READINGS_PER_CYCLE: int = 5000
    
    # Maximum processing time per cycle (seconds)
    MAXIMUM_PROCESSING_TIME_PER_CYCLE_SECONDS: float = 30.0
    
    # System timeout (seconds) - if cycle exceeds this, fail-safe
    SYSTEM_TIMEOUT_SECONDS: float = 30.0
    
    # Maximum memory usage warning threshold (bytes) - not enforced, logged only
    MAXIMUM_MEMORY_USAGE_WARNING_BYTES: int = 2 * 1024 * 1024 * 1024  # 2 GB


# ============================================================================
# AUDIT AND LOGGING CONFIGURATION
# ============================================================================

class AuditLoggingConfiguration:
    """
    Audit logging and trail configuration.
    """
    
    # Audit logging enabled
    AUDIT_LOGGING_ENABLED: bool = True
    
    # Explainability required
    EXPLAINABILITY_REQUIRED: bool = True
    
    # Log retention period (days)
    LOG_RETENTION_DAYS: int = 365
    
    # Log file rotation size (bytes)
    LOG_FILE_ROTATION_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB
    
    # Maximum log file size before rotation (bytes)
    MAXIMUM_LOG_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB
    
    # Log directory (relative to project root)
    DEFAULT_LOG_DIRECTORY: str = "logs"
    
    # Events that must be logged (critical events)
    MANDATORY_LOG_EVENTS: Tuple[str, ...] = (
        "SYSTEM_INITIALIZED",
        "SYSTEM_SHUTDOWN",
        "RECOMMENDATION_GENERATED",
        "RECOMMENDATION_APPROVED",
        "RECOMMENDATION_REJECTED",
        "THREAT_ASSESSMENT_CRITICAL",
        "SYSTEM_ERROR",
        "FAIL_SAFE_ACTIVATED",
        "HUMAN_APPROVAL_REQUIRED",
    )


# ============================================================================
# FAIL-SAFE AND ERROR HANDLING CONFIGURATION
# ============================================================================

class FailSafeConfiguration:
    """
    Fail-safe and error handling configuration.
    All failures default to NO ACTION / MONITORING ONLY.
    """
    
    # Fail-safe activation conditions
    FAIL_SAFE_ON_SENSOR_FAILURE: bool = True
    FAIL_SAFE_ON_STALE_DATA: bool = True
    FAIL_SAFE_ON_INSUFFICIENT_CONFIDENCE: bool = True
    FAIL_SAFE_ON_INPUT_CONFLICT: bool = True
    FAIL_SAFE_ON_SYSTEM_ERROR: bool = True
    FAIL_SAFE_ON_TIMEOUT: bool = True
    
    # Fail-safe default action
    FAIL_SAFE_DEFAULT_ACTION: str = "NO_ACTION"
    
    # Fail-safe default mode
    FAIL_SAFE_DEFAULT_MODE: str = "MONITORING_ONLY"
    
    # Maximum consecutive errors before fail-safe
    MAXIMUM_CONSECUTIVE_ERRORS_BEFORE_FAIL_SAFE: int = 3
    
    # Error recovery timeout (seconds) - time to wait before retry
    ERROR_RECOVERY_TIMEOUT_SECONDS: float = 10.0


# ============================================================================
# COORDINATE SYSTEM CONFIGURATION
# ============================================================================

class CoordinateSystemConfiguration:
    """
    Coordinate system and spatial reference configuration.
    """
    
    # Coordinate system type
    COORDINATE_SYSTEM_TYPE: str = "CARTESIAN"  # X, Y, Z in meters
    
    # System origin
    SYSTEM_ORIGIN_X_METERS: float = 0.0
    SYSTEM_ORIGIN_Y_METERS: float = 0.0
    SYSTEM_ORIGIN_Z_METERS: float = 0.0
    
    # Coordinate bounds (for validation)
    MINIMUM_X_COORDINATE_METERS: float = -1000000.0  # -1000 km
    MAXIMUM_X_COORDINATE_METERS: float = 1000000.0   # 1000 km
    MINIMUM_Y_COORDINATE_METERS: float = -1000000.0  # -1000 km
    MAXIMUM_Y_COORDINATE_METERS: float = 1000000.0   # 1000 km
    MINIMUM_Z_COORDINATE_METERS: float = -100000.0   # -100 km (below ground)
    MAXIMUM_Z_COORDINATE_METERS: float = 200000.0    # 200 km (upper atmosphere)


# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRules:
    """
    Validation rules for configuration values.
    These ensure all configuration values are within acceptable ranges.
    """
    
    @staticmethod
    def validate_confidence_value(value: float, name: str) -> None:
        """Validate confidence value is in range [0.0, 1.0]."""
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in range [0.0, 1.0], got {value}")
    
    @staticmethod
    def validate_positive_value(value: float, name: str) -> None:
        """Validate value is positive."""
        if value <= 0.0:
            raise ValueError(f"{name} must be positive, got {value}")
    
    @staticmethod
    def validate_non_negative_value(value: float, name: str) -> None:
        """Validate value is non-negative."""
        if value < 0.0:
            raise ValueError(f"{name} must be non-negative, got {value}")


# ============================================================================
# CONFIGURATION VALIDATION ON IMPORT
# ============================================================================

def _validate_configuration() -> None:
    """
    Validate all configuration values on module import.
    Raises ValueError if any configuration is invalid.
    """
    validator = ValidationRules()
    
    # Validate confidence thresholds
    confidence_configs = [
        (ConfidenceThresholds.MINIMUM_SENSOR_DETECTION_CONFIDENCE, "MINIMUM_SENSOR_DETECTION_CONFIDENCE"),
        (ConfidenceThresholds.MINIMUM_TRACK_CREATION_CONFIDENCE, "MINIMUM_TRACK_CREATION_CONFIDENCE"),
        (ConfidenceThresholds.MINIMUM_ENTITY_CLASSIFICATION_CONFIDENCE, "MINIMUM_ENTITY_CLASSIFICATION_CONFIDENCE"),
        (ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE, "MINIMUM_THREAT_ASSESSMENT_CONFIDENCE"),
        (ConfidenceThresholds.MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE, "MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE"),
    ]
    
    for value, name in confidence_configs:
        validator.validate_confidence_value(value, name)
    
    # Validate threat thresholds
    threat_configs = [
        (ThreatAssessmentThresholds.THREAT_LEVEL_LOW_THRESHOLD, "THREAT_LEVEL_LOW_THRESHOLD"),
        (ThreatAssessmentThresholds.THREAT_LEVEL_MEDIUM_THRESHOLD, "THREAT_LEVEL_MEDIUM_THRESHOLD"),
        (ThreatAssessmentThresholds.THREAT_LEVEL_HIGH_THRESHOLD, "THREAT_LEVEL_HIGH_THRESHOLD"),
        (ThreatAssessmentThresholds.THREAT_LEVEL_CRITICAL_THRESHOLD, "THREAT_LEVEL_CRITICAL_THRESHOLD"),
    ]
    
    for value, name in threat_configs:
        validator.validate_confidence_value(value, name)
    
    # Validate positive values
    positive_configs = [
        (ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS, "CRITICAL_ZONE_RADIUS_METERS"),
        (ProtectedAirspaceConfiguration.PROTECTED_ZONE_RADIUS_METERS, "PROTECTED_ZONE_RADIUS_METERS"),
        (SensorConfiguration.DEFAULT_RADAR_RANGE_METERS, "DEFAULT_RADAR_RANGE_METERS"),
    ]
    
    for value, name in positive_configs:
        validator.validate_positive_value(value, name)
    
    # Validate ethical constraints
    if not EthicalConstraints.MANDATORY_HUMAN_APPROVAL_REQUIRED:
        raise ValueError("CRITICAL: MANDATORY_HUMAN_APPROVAL_REQUIRED must be True")
    
    if not EthicalConstraints.ADVISORY_ONLY_MODE:
        raise ValueError("CRITICAL: ADVISORY_ONLY_MODE must be True")
    
    if EthicalConstraints.FAIL_SAFE_DEFAULT_ACTION != "NO_ACTION":
        raise ValueError("CRITICAL: FAIL_SAFE_DEFAULT_ACTION must be 'NO_ACTION'")


# Validate configuration on import
_validate_configuration()


# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================

def get_configuration_summary() -> Dict[str, Any]:
    """
    Get a summary of all configuration values for documentation/audit purposes.
    
    Returns:
        Dictionary containing all configuration values organized by category.
    """
    return {
        "ethical_constraints": {
            "mandatory_human_approval_required": EthicalConstraints.MANDATORY_HUMAN_APPROVAL_REQUIRED,
            "human_operator_required": EthicalConstraints.HUMAN_OPERATOR_REQUIRED,
            "advisory_only_mode": EthicalConstraints.ADVISORY_ONLY_MODE,
            "autonomous_actions_prohibited": EthicalConstraints.AUTONOMOUS_ACTIONS_PROHIBITED,
            "fail_safe_default_action": EthicalConstraints.FAIL_SAFE_DEFAULT_ACTION,
            "fail_safe_default_mode": EthicalConstraints.FAIL_SAFE_DEFAULT_MODE,
        },
        "protected_airspace": {
            "critical_zone_radius_meters": ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS,
            "protected_zone_radius_meters": ProtectedAirspaceConfiguration.PROTECTED_ZONE_RADIUS_METERS,
            "extended_zone_radius_meters": ProtectedAirspaceConfiguration.EXTENDED_ZONE_RADIUS_METERS,
            "maximum_detection_range_meters": ProtectedAirspaceConfiguration.MAXIMUM_DETECTION_RANGE_METERS,
        },
        "confidence_thresholds": {
            "minimum_sensor_detection_confidence": ConfidenceThresholds.MINIMUM_SENSOR_DETECTION_CONFIDENCE,
            "minimum_track_creation_confidence": ConfidenceThresholds.MINIMUM_TRACK_CREATION_CONFIDENCE,
            "minimum_threat_assessment_confidence": ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE,
            "minimum_advisory_recommendation_confidence": ConfidenceThresholds.MINIMUM_ADVISORY_RECOMMENDATION_CONFIDENCE,
            "high_confidence_threshold": ConfidenceThresholds.HIGH_CONFIDENCE_THRESHOLD,
            "critical_confidence_threshold": ConfidenceThresholds.CRITICAL_CONFIDENCE_THRESHOLD,
        },
        "system_limits": {
            "maximum_active_tracks": SystemPerformanceLimits.MAXIMUM_ACTIVE_TRACKS,
            "maximum_processing_time_per_cycle_seconds": SystemPerformanceLimits.MAXIMUM_PROCESSING_TIME_PER_CYCLE_SECONDS,
            "system_timeout_seconds": SystemPerformanceLimits.SYSTEM_TIMEOUT_SECONDS,
        },
        "fail_safe": {
            "fail_safe_default_action": FailSafeConfiguration.FAIL_SAFE_DEFAULT_ACTION,
            "fail_safe_default_mode": FailSafeConfiguration.FAIL_SAFE_DEFAULT_MODE,
            "maximum_consecutive_errors_before_fail_safe": FailSafeConfiguration.MAXIMUM_CONSECUTIVE_ERRORS_BEFORE_FAIL_SAFE,
        },
    }


