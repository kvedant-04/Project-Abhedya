"""
Main Data Preprocessing Module

Orchestrates all preprocessing operations:
- Validation
- Outlier detection and rejection
- Missing data handling
- Noise reduction
- Temporal consistency validation
- Data normalization

Uses fail-safe behavior: corrupted or inconsistent data is rejected.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from abhedya.preprocessing.validator import DataValidator, ValidationResult
from abhedya.preprocessing.outlier_detection import OutlierDetector, OutlierDetectionResult
from abhedya.preprocessing.noise_reduction import NoiseReducer
from abhedya.preprocessing.normalizer import DataNormalizer
from abhedya.infrastructure.config.config import FailSafeConfiguration


@dataclass
class PreprocessingResult:
    """Result of preprocessing operation."""
    processed_detections: List[Dict[str, Any]]
    rejected_detections: List[Dict[str, Any]]
    validation_errors: List[str]
    outlier_count: int
    missing_data_count: int
    is_success: bool


class DataPreprocessor:
    """
    Main data preprocessing engine.
    
    Orchestrates validation, outlier detection, noise reduction,
    missing data handling, and normalization.
    
    Uses fail-safe behavior: invalid data is rejected, not modified.
    """
    
    def __init__(
        self,
        enable_validation: bool = True,
        enable_outlier_detection: bool = True,
        enable_noise_reduction: bool = False,  # Optional, disabled by default
        enable_normalization: bool = False,  # Optional, disabled by default
        reject_outliers: bool = True,
        strict_mode: bool = True
    ):
        """
        Initialize data preprocessor.
        
        Args:
            enable_validation: Enable data validation (default: True)
            enable_outlier_detection: Enable outlier detection (default: True)
            enable_noise_reduction: Enable noise reduction (default: False)
            enable_normalization: Enable normalization (default: False)
            reject_outliers: Reject outliers instead of flagging (default: True)
            strict_mode: Strict validation mode (default: True)
        """
        self.enable_validation = enable_validation
        self.enable_outlier_detection = enable_outlier_detection
        self.enable_noise_reduction = enable_noise_reduction
        self.enable_normalization = enable_normalization
        self.reject_outliers = reject_outliers
        self.strict_mode = strict_mode
        
        # Initialize components
        self.validator = DataValidator(strict_mode=strict_mode)
        self.outlier_detector = OutlierDetector()
        self.noise_reducer = NoiseReducer()
        self.normalizer = DataNormalizer()
    
    def preprocess(
        self,
        detections: List[Dict[str, Any]],
        historical_detections: Optional[List[Dict[str, Any]]] = None
    ) -> PreprocessingResult:
        """
        Preprocess a list of detections.
        
        Args:
            detections: List of detections to preprocess
            historical_detections: Historical detections for context (optional)
            
        Returns:
            PreprocessingResult with processed and rejected detections
        """
        processed = []
        rejected = []
        validation_errors = []
        outlier_count = 0
        missing_data_count = 0
        
        # Step 1: Handle missing data
        detections_with_missing = self._handle_missing_data(detections)
        missing_data_count = len(detections) - len(detections_with_missing)
        
        # Step 2: Validate detections
        valid_detections = []
        for detection in detections_with_missing:
            if self.enable_validation:
                validation_result = self.validator.validate_detection(detection)
                if not validation_result.is_valid:
                    rejected.append(detection)
                    validation_errors.extend(validation_result.errors)
                    continue
            
            valid_detections.append(detection)
        
        # Step 3: Outlier detection
        if self.enable_outlier_detection:
            outlier_detections = []
            for detection in valid_detections:
                outlier_result = self.outlier_detector.detect_outlier_in_detection(
                    detection,
                    historical_detections
                )
                
                if outlier_result.is_outlier:
                    outlier_count += 1
                    if self.reject_outliers:
                        rejected.append(detection)
                        validation_errors.append(
                            f"Outlier detected: {outlier_result.reason}"
                        )
                    else:
                        # Flag but don't reject
                        detection["_is_outlier"] = True
                        detection["_outlier_reason"] = outlier_result.reason
                        outlier_detections.append(detection)
                else:
                    outlier_detections.append(detection)
            
            valid_detections = outlier_detections
        
        # Step 4: Temporal consistency validation
        if len(valid_detections) > 1:
            temporal_result = self.validator.validate_temporal_consistency(valid_detections)
            if not temporal_result.is_valid and self.strict_mode:
                # Reject all if temporal consistency fails in strict mode
                rejected.extend(valid_detections)
                validation_errors.extend(temporal_result.errors)
                valid_detections = []
        
        # Step 5: Noise reduction (optional)
        if self.enable_noise_reduction and len(valid_detections) > 0:
            try:
                valid_detections = self.noise_reducer.reduce_position_noise(
                    valid_detections,
                    method="moving_average"
                )
                valid_detections = self.noise_reducer.reduce_velocity_noise(
                    valid_detections,
                    method="moving_average"
                )
            except Exception as e:
                # Fail-safe: if noise reduction fails, use original data
                if FailSafeConfiguration.FAIL_SAFE_ON_SYSTEM_ERROR:
                    validation_errors.append(f"Noise reduction failed: {e}")
                    # Don't reject, just skip noise reduction
        
        # Step 6: Normalization (optional)
        if self.enable_normalization and len(valid_detections) > 0:
            try:
                valid_detections = self.normalizer.normalize_detection_coordinates(
                    valid_detections,
                    method="min_max"
                )
            except Exception as e:
                # Fail-safe: if normalization fails, use original data
                if FailSafeConfiguration.FAIL_SAFE_ON_SYSTEM_ERROR:
                    validation_errors.append(f"Normalization failed: {e}")
                    # Don't reject, just skip normalization
        
        # Final validation of processed data
        final_valid = []
        for detection in valid_detections:
            if self.enable_validation:
                validation_result = self.validator.validate_detection(detection)
                if not validation_result.is_valid:
                    rejected.append(detection)
                    validation_errors.extend(validation_result.errors)
                else:
                    final_valid.append(detection)
            else:
                final_valid.append(detection)
        
        # Determine success
        is_success = len(final_valid) > 0 and len(validation_errors) == 0
        
        return PreprocessingResult(
            processed_detections=final_valid,
            rejected_detections=rejected,
            validation_errors=validation_errors,
            outlier_count=outlier_count,
            missing_data_count=missing_data_count,
            is_success=is_success
        )
    
    def _handle_missing_data(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Handle missing data in detections.
        
        Fail-safe behavior: detections with critical missing data are rejected.
        
        Args:
            detections: List of detections
            
        Returns:
            List of detections with missing data handled
        """
        processed = []
        
        for detection in detections:
            # Check for critical missing fields
            critical_fields = ["sensor_id", "timestamp", "position", "confidence"]
            has_critical_missing = False
            
            for field in critical_fields:
                if field not in detection:
                    has_critical_missing = True
                    break
            
            if has_critical_missing:
                # Reject detection with critical missing data
                continue
            
            # Handle optional missing fields
            if "velocity" not in detection:
                # Add default velocity (stationary)
                detection["velocity"] = {"vx": 0.0, "vy": 0.0, "vz": 0.0}
            
            if "uncertainty" not in detection:
                # Calculate uncertainty from confidence if available
                if "confidence" in detection:
                    detection["uncertainty"] = 1.0 - detection["confidence"]
                else:
                    detection["uncertainty"] = 0.5  # Default uncertainty
            
            if "signal_strength" not in detection:
                # Estimate signal strength from confidence if available
                if "confidence" in detection:
                    detection["signal_strength"] = detection["confidence"]
                else:
                    detection["signal_strength"] = 0.5  # Default signal strength
            
            processed.append(detection)
        
        return processed
    
    def preprocess_single(
        self,
        detection: Dict[str, Any],
        historical_detections: Optional[List[Dict[str, Any]]] = None
    ) -> PreprocessingResult:
        """
        Preprocess a single detection.
        
        Args:
            detection: Single detection to preprocess
            historical_detections: Historical detections for context (optional)
            
        Returns:
            PreprocessingResult
        """
        return self.preprocess([detection], historical_detections)

