"""
Data Validation Module

Validates sensor data for:
- Missing data
- Temporal consistency
- Value ranges
- Data types
- Structural integrity

Uses defensive programming and fail-safe behavior.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from abhedya.infrastructure.config.config import (
    UncertaintyLimits,
    CoordinateSystemConfiguration,
)


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self) -> bool:
        """Allow use in boolean context."""
        return self.is_valid


class DataValidator:
    """
    Validates sensor data using classical statistical techniques.
    
    Implements fail-safe behavior: invalid data is rejected,
    not modified or "fixed".
    """
    
    def __init__(
        self,
        strict_mode: bool = True,
        reject_on_warning: bool = False
    ):
        """
        Initialize data validator.
        
        Args:
            strict_mode: If True, strict validation (default: True)
            reject_on_warning: If True, reject data on warnings (default: False)
        """
        self.strict_mode = strict_mode
        self.reject_on_warning = reject_on_warning
    
    def validate_detection(
        self,
        detection: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a single sensor detection.
        
        Args:
            detection: Detection dictionary to validate
            
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = [
            "sensor_id",
            "sensor_type",
            "timestamp",
            "position",
            "velocity",
            "confidence"
        ]
        
        for field in required_fields:
            if field not in detection:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Validate timestamp
        timestamp_result = self._validate_timestamp(detection["timestamp"])
        if not timestamp_result.is_valid:
            errors.extend(timestamp_result.errors)
        warnings.extend(timestamp_result.warnings)
        
        # Validate position
        if "position" in detection:
            position_result = self._validate_position(detection["position"])
            if not position_result.is_valid:
                errors.extend(position_result.errors)
            warnings.extend(position_result.warnings)
        
        # Validate velocity
        if "velocity" in detection:
            velocity_result = self._validate_velocity(detection["velocity"])
            if not velocity_result.is_valid:
                errors.extend(velocity_result.errors)
            warnings.extend(velocity_result.warnings)
        
        # Validate confidence
        if "confidence" in detection:
            confidence_result = self._validate_confidence(detection["confidence"])
            if not confidence_result.is_valid:
                errors.extend(confidence_result.errors)
            warnings.extend(confidence_result.warnings)
        
        # Validate uncertainty if present
        if "uncertainty" in detection:
            uncertainty_result = self._validate_uncertainty(detection["uncertainty"])
            if not uncertainty_result.is_valid:
                errors.extend(uncertainty_result.errors)
            warnings.extend(uncertainty_result.warnings)
        
        # Validate signal strength if present
        if "signal_strength" in detection:
            signal_result = self._validate_signal_strength(detection["signal_strength"])
            if not signal_result.is_valid:
                errors.extend(signal_result.errors)
            warnings.extend(signal_result.warnings)
        
        # Determine validity
        is_valid = len(errors) == 0
        if self.reject_on_warning and len(warnings) > 0:
            is_valid = False
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_timestamp(self, timestamp: Any) -> ValidationResult:
        """Validate timestamp."""
        errors = []
        warnings = []
        
        # Check if timestamp is string (ISO format) or datetime
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp)
            except (ValueError, TypeError) as e:
                errors.append(f"Invalid timestamp format: {e}")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            errors.append(f"Timestamp must be string or datetime, got {type(timestamp)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check if timestamp is in the future (warning, not error)
        now = datetime.now()
        if dt > now:
            warnings.append("Timestamp is in the future")
        
        # Check if timestamp is too old
        time_delta = (now - dt).total_seconds()
        if time_delta > UncertaintyLimits.MAXIMUM_SENSOR_DATA_AGE_SECONDS:
            errors.append(
                f"Timestamp is too old: {time_delta:.1f} seconds "
                f"(max: {UncertaintyLimits.MAXIMUM_SENSOR_DATA_AGE_SECONDS} seconds)"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_position(self, position: Any) -> ValidationResult:
        """Validate position data."""
        errors = []
        warnings = []
        
        if not isinstance(position, dict):
            errors.append(f"Position must be dictionary, got {type(position)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        required_coords = ["x", "y", "z"]
        for coord in required_coords:
            if coord not in position:
                errors.append(f"Missing position coordinate: {coord}")
                continue
            
            value = position[coord]
            if not isinstance(value, (int, float)):
                errors.append(f"Position {coord} must be numeric, got {type(value)}")
                continue
            
            # Check coordinate bounds
            if coord == "x":
                if not (CoordinateSystemConfiguration.MINIMUM_X_COORDINATE_METERS <=
                        value <= CoordinateSystemConfiguration.MAXIMUM_X_COORDINATE_METERS):
                    errors.append(
                        f"Position x out of bounds: {value} "
                        f"(range: {CoordinateSystemConfiguration.MINIMUM_X_COORDINATE_METERS} to "
                        f"{CoordinateSystemConfiguration.MAXIMUM_X_COORDINATE_METERS})"
                    )
            elif coord == "y":
                if not (CoordinateSystemConfiguration.MINIMUM_Y_COORDINATE_METERS <=
                        value <= CoordinateSystemConfiguration.MAXIMUM_Y_COORDINATE_METERS):
                    errors.append(
                        f"Position y out of bounds: {value} "
                        f"(range: {CoordinateSystemConfiguration.MINIMUM_Y_COORDINATE_METERS} to "
                        f"{CoordinateSystemConfiguration.MAXIMUM_Y_COORDINATE_METERS})"
                    )
            elif coord == "z":
                if not (CoordinateSystemConfiguration.MINIMUM_Z_COORDINATE_METERS <=
                        value <= CoordinateSystemConfiguration.MAXIMUM_Z_COORDINATE_METERS):
                    errors.append(
                        f"Position z out of bounds: {value} "
                        f"(range: {CoordinateSystemConfiguration.MINIMUM_Z_COORDINATE_METERS} to "
                        f"{CoordinateSystemConfiguration.MAXIMUM_Z_COORDINATE_METERS})"
                    )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_velocity(self, velocity: Any) -> ValidationResult:
        """Validate velocity data."""
        errors = []
        warnings = []
        
        if not isinstance(velocity, dict):
            errors.append(f"Velocity must be dictionary, got {type(velocity)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        required_components = ["vx", "vy", "vz"]
        for component in required_components:
            if component not in velocity:
                errors.append(f"Missing velocity component: {component}")
                continue
            
            value = velocity[component]
            if not isinstance(value, (int, float)):
                errors.append(f"Velocity {component} must be numeric, got {type(value)}")
                continue
            
            # Check for unrealistic velocities (warning)
            if abs(value) > 1000.0:  # > 3600 km/h
                warnings.append(f"Unrealistic velocity {component}: {value} m/s")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_confidence(self, confidence: Any) -> ValidationResult:
        """Validate confidence value."""
        errors = []
        warnings = []
        
        if not isinstance(confidence, (int, float)):
            errors.append(f"Confidence must be numeric, got {type(confidence)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check range [0.0, 1.0]
        if not (0.0 <= confidence <= 1.0):
            errors.append(f"Confidence out of range [0.0, 1.0]: {confidence}")
        
        # Check minimum confidence threshold
        from abhedya.infrastructure.config.config import ConfidenceThresholds
        if confidence < ConfidenceThresholds.MINIMUM_SENSOR_DETECTION_CONFIDENCE:
            warnings.append(
                f"Confidence below minimum threshold: {confidence} "
                f"(min: {ConfidenceThresholds.MINIMUM_SENSOR_DETECTION_CONFIDENCE})"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_uncertainty(self, uncertainty: Any) -> ValidationResult:
        """Validate uncertainty value."""
        errors = []
        warnings = []
        
        if not isinstance(uncertainty, (int, float)):
            errors.append(f"Uncertainty must be numeric, got {type(uncertainty)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check range [0.0, 1.0]
        if not (0.0 <= uncertainty <= 1.0):
            errors.append(f"Uncertainty out of range [0.0, 1.0]: {uncertainty}")
        
        # Check maximum acceptable uncertainty
        from abhedya.infrastructure.config.config import ConfidenceThresholds
        if uncertainty > ConfidenceThresholds.MAXIMUM_ACCEPTABLE_UNCERTAINTY:
            errors.append(
                f"Uncertainty exceeds maximum acceptable: {uncertainty} "
                f"(max: {ConfidenceThresholds.MAXIMUM_ACCEPTABLE_UNCERTAINTY})"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_signal_strength(self, signal_strength: Any) -> ValidationResult:
        """Validate signal strength value."""
        errors = []
        warnings = []
        
        if not isinstance(signal_strength, (int, float)):
            errors.append(f"Signal strength must be numeric, got {type(signal_strength)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check range [0.0, 1.0]
        if not (0.0 <= signal_strength <= 1.0):
            errors.append(f"Signal strength out of range [0.0, 1.0]: {signal_strength}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_temporal_consistency(
        self,
        detections: List[Dict[str, Any]],
        max_time_gap_seconds: float = 10.0
    ) -> ValidationResult:
        """
        Validate temporal consistency of a sequence of detections.
        
        Args:
            detections: List of detections ordered by timestamp
            max_time_gap_seconds: Maximum acceptable time gap between detections
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if len(detections) < 2:
            return ValidationResult(is_valid=True, errors=errors, warnings=warnings)
        
        # Sort by timestamp
        try:
            sorted_detections = sorted(
                detections,
                key=lambda d: self._parse_timestamp(d.get("timestamp"))
            )
        except Exception as e:
            errors.append(f"Failed to sort detections by timestamp: {e}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check for time gaps
        for i in range(1, len(sorted_detections)):
            prev_time = self._parse_timestamp(sorted_detections[i-1].get("timestamp"))
            curr_time = self._parse_timestamp(sorted_detections[i].get("timestamp"))
            
            if prev_time is None or curr_time is None:
                continue
            
            time_gap = (curr_time - prev_time).total_seconds()
            if time_gap > max_time_gap_seconds:
                warnings.append(
                    f"Large time gap detected: {time_gap:.1f} seconds "
                    f"(max: {max_time_gap_seconds} seconds)"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse timestamp to datetime object."""
        if timestamp is None:
            return None
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp)
            except (ValueError, TypeError):
                return None
        
        return None

