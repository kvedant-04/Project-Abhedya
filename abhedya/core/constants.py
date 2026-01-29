"""
System-wide constants and configuration defaults.

All constants enforce fail-safe, ethical defaults.
"""

# System Modes
SYSTEM_MODE_MONITORING = "MONITORING"
SYSTEM_MODE_ALERT = "ALERT"
SYSTEM_MODE_MAINTENANCE = "MAINTENANCE"
SYSTEM_MODE_OFFLINE = "OFFLINE"

# Default Actions (Fail-Safe)
DEFAULT_ACTION = "NO_ACTION"
DEFAULT_THREAT_LEVEL = "NONE"
DEFAULT_ENTITY_TYPE = "UNKNOWN"

# Sensor Defaults
DEFAULT_SENSOR_RANGE = 100000.0  # meters (100 km)
DEFAULT_SENSOR_UPDATE_RATE = 1.0  # Hz (1 update per second)
DEFAULT_DETECTION_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detection

# Threat Assessment Thresholds
THREAT_LEVEL_NONE_THRESHOLD = 0.0
THREAT_LEVEL_LOW_THRESHOLD = 0.3
THREAT_LEVEL_MEDIUM_THRESHOLD = 0.6
THREAT_LEVEL_HIGH_THRESHOLD = 0.8
THREAT_LEVEL_CRITICAL_THRESHOLD = 0.95

# Advisory Confidence Thresholds
MIN_ADVISORY_CONFIDENCE = 0.5  # Minimum confidence for advisory output
HIGH_CONFIDENCE_THRESHOLD = 0.8

# Human-in-the-Loop Requirements
MANDATORY_HUMAN_APPROVAL = True  # Cannot be disabled
MIN_HUMAN_RESPONSE_TIME = 5.0  # seconds (minimum time for human review)

# Audit and Logging
AUDIT_LOG_ENABLED = True
AUDIT_LOG_RETENTION_DAYS = 365
EXPLAINABILITY_REQUIRED = True

# Safety Constraints
MAX_TRACKS_PER_UPDATE = 1000  # Prevent system overload
MAX_RECOMMENDATIONS_QUEUE = 100  # Prevent recommendation queue overflow
SYSTEM_TIMEOUT_SECONDS = 30.0  # Maximum processing time per cycle

# Coordinate System
COORDINATE_SYSTEM = "CARTESIAN"  # X, Y, Z in meters
ORIGIN_POSITION = (0.0, 0.0, 0.0)  # System origin

