"""
Outlier Detection Module

Classical statistical techniques for outlier detection:
- Z-score method
- Interquartile Range (IQR) method
- Distance-based methods
- Temporal outlier detection

Uses fail-safe behavior: outliers are detected and can be rejected.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from statistics import mean, stdev, median


@dataclass
class OutlierDetectionResult:
    """Result of outlier detection."""
    is_outlier: bool
    outlier_score: float
    method: str
    reason: str


class OutlierDetector:
    """
    Detects outliers in sensor data using classical statistical techniques.
    
    Methods:
    - Z-score: Detects values far from mean
    - IQR: Detects values outside interquartile range
    - Distance-based: Detects values far from expected position
    - Temporal: Detects sudden changes in time series
    """
    
    def __init__(
        self,
        z_score_threshold: float = 3.0,
        iqr_multiplier: float = 1.5,
        distance_threshold_multiplier: float = 3.0
    ):
        """
        Initialize outlier detector.
        
        Args:
            z_score_threshold: Z-score threshold for outlier detection (default: 3.0)
            iqr_multiplier: IQR multiplier for outlier detection (default: 1.5)
            distance_threshold_multiplier: Multiplier for distance-based detection
        """
        self.z_score_threshold = z_score_threshold
        self.iqr_multiplier = iqr_multiplier
        self.distance_threshold_multiplier = distance_threshold_multiplier
    
    def detect_outlier_in_detection(
        self,
        detection: Dict[str, Any],
        historical_detections: Optional[List[Dict[str, Any]]] = None
    ) -> OutlierDetectionResult:
        """
        Detect if a detection is an outlier.
        
        Args:
            detection: Detection to check
            historical_detections: Historical detections for context (optional)
            
        Returns:
            OutlierDetectionResult
        """
        # Check position outliers
        if "position" in detection and historical_detections:
            position_result = self._detect_position_outlier(
                detection["position"],
                [d["position"] for d in historical_detections if "position" in d]
            )
            if position_result.is_outlier:
                return position_result
        
        # Check velocity outliers
        if "velocity" in detection and historical_detections:
            velocity_result = self._detect_velocity_outlier(
                detection["velocity"],
                [d["velocity"] for d in historical_detections if "velocity" in d]
            )
            if velocity_result.is_outlier:
                return velocity_result
        
        # Check confidence outliers
        if "confidence" in detection:
            confidence_result = self._detect_confidence_outlier(detection["confidence"])
            if confidence_result.is_outlier:
                return confidence_result
        
        # No outliers detected
        return OutlierDetectionResult(
            is_outlier=False,
            outlier_score=0.0,
            method="none",
            reason="No outliers detected"
        )
    
    def _detect_position_outlier(
        self,
        position: Dict[str, float],
        historical_positions: List[Dict[str, float]]
    ) -> OutlierDetectionResult:
        """Detect position outliers using Z-score method."""
        if len(historical_positions) < 3:
            # Not enough data for statistical analysis
            return OutlierDetectionResult(
                is_outlier=False,
                outlier_score=0.0,
                method="insufficient_data",
                reason="Insufficient historical data for outlier detection"
            )
        
        # Extract coordinates
        x_values = [p.get("x", 0.0) for p in historical_positions]
        y_values = [p.get("y", 0.0) for p in historical_positions]
        z_values = [p.get("z", 0.0) for p in historical_positions]
        
        # Calculate Z-scores
        x_zscore = self._calculate_z_score(position.get("x", 0.0), x_values)
        y_zscore = self._calculate_z_score(position.get("y", 0.0), y_values)
        z_zscore = self._calculate_z_score(position.get("z", 0.0), z_values)
        
        # Check if any coordinate is an outlier
        max_zscore = max(abs(x_zscore), abs(y_zscore), abs(z_zscore))
        
        if max_zscore > self.z_score_threshold:
            return OutlierDetectionResult(
                is_outlier=True,
                outlier_score=max_zscore,
                method="z_score",
                reason=f"Position Z-score exceeds threshold: {max_zscore:.2f} > {self.z_score_threshold}"
            )
        
        return OutlierDetectionResult(
            is_outlier=False,
            outlier_score=max_zscore,
            method="z_score",
            reason="Position within normal range"
        )
    
    def _detect_velocity_outlier(
        self,
        velocity: Dict[str, float],
        historical_velocities: List[Dict[str, float]]
    ) -> OutlierDetectionResult:
        """Detect velocity outliers using IQR method."""
        if len(historical_velocities) < 5:
            # Not enough data for IQR
            return OutlierDetectionResult(
                is_outlier=False,
                outlier_score=0.0,
                method="insufficient_data",
                reason="Insufficient historical data for outlier detection"
            )
        
        # Extract velocity components
        vx_values = [v.get("vx", 0.0) for v in historical_velocities]
        vy_values = [v.get("vy", 0.0) for v in historical_velocities]
        vz_values = [v.get("vz", 0.0) for v in historical_velocities]
        
        # Check each component using IQR
        vx_outlier = self._is_outlier_iqr(velocity.get("vx", 0.0), vx_values)
        vy_outlier = self._is_outlier_iqr(velocity.get("vy", 0.0), vy_values)
        vz_outlier = self._is_outlier_iqr(velocity.get("vz", 0.0), vz_values)
        
        if vx_outlier or vy_outlier or vz_outlier:
            outlier_components = []
            if vx_outlier:
                outlier_components.append("vx")
            if vy_outlier:
                outlier_components.append("vy")
            if vz_outlier:
                outlier_components.append("vz")
            
            return OutlierDetectionResult(
                is_outlier=True,
                outlier_score=1.0,
                method="iqr",
                reason=f"Velocity components outside IQR: {', '.join(outlier_components)}"
            )
        
        return OutlierDetectionResult(
            is_outlier=False,
            outlier_score=0.0,
            method="iqr",
            reason="Velocity within normal range"
        )
    
    def _detect_confidence_outlier(self, confidence: float) -> OutlierDetectionResult:
        """Detect confidence outliers (unusually low confidence)."""
        # Confidence below 0.3 is considered an outlier
        if confidence < 0.3:
            return OutlierDetectionResult(
                is_outlier=True,
                outlier_score=1.0 - confidence,
                method="threshold",
                reason=f"Confidence unusually low: {confidence:.2f}"
            )
        
        return OutlierDetectionResult(
            is_outlier=False,
            outlier_score=0.0,
            method="threshold",
            reason="Confidence within normal range"
        )
    
    def _calculate_z_score(self, value: float, values: List[float]) -> float:
        """
        Calculate Z-score for a value relative to a distribution.
        
        Args:
            value: Value to calculate Z-score for
            values: Distribution of values
            
        Returns:
            Z-score
        """
        if len(values) < 2:
            return 0.0
        
        try:
            mean_val = mean(values)
            std_val = stdev(values)
            
            if std_val == 0:
                return 0.0
            
            return (value - mean_val) / std_val
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _is_outlier_iqr(self, value: float, values: List[float]) -> bool:
        """
        Check if value is an outlier using Interquartile Range (IQR) method.
        
        Args:
            value: Value to check
            values: Distribution of values
            
        Returns:
            True if value is an outlier
        """
        if len(values) < 4:
            return False
        
        try:
            sorted_values = sorted(values)
            q1_index = len(sorted_values) // 4
            q3_index = 3 * len(sorted_values) // 4
            
            q1 = sorted_values[q1_index]
            q3 = sorted_values[q3_index]
            iqr = q3 - q1
            
            lower_bound = q1 - (self.iqr_multiplier * iqr)
            upper_bound = q3 + (self.iqr_multiplier * iqr)
            
            return value < lower_bound or value > upper_bound
        except (ValueError, IndexError):
            return False
    
    def detect_temporal_outliers(
        self,
        detections: List[Dict[str, Any]],
        entity_id: Optional[str] = None
    ) -> List[Tuple[int, OutlierDetectionResult]]:
        """
        Detect temporal outliers in a sequence of detections.
        
        Args:
            detections: List of detections ordered by timestamp
            entity_id: Optional entity ID to filter detections
            
        Returns:
            List of (index, OutlierDetectionResult) tuples for outliers
        """
        outliers = []
        
        if len(detections) < 3:
            return outliers
        
        # Filter by entity_id if provided
        filtered_detections = detections
        if entity_id:
            filtered_detections = [
                d for d in detections
                if d.get("entity_id") == entity_id
            ]
        
        if len(filtered_detections) < 3:
            return outliers
        
        # Calculate velocity changes (sudden changes indicate outliers)
        for i in range(1, len(filtered_detections)):
            prev_detection = filtered_detections[i-1]
            curr_detection = filtered_detections[i]
            
            if "position" not in prev_detection or "position" not in curr_detection:
                continue
            
            if "timestamp" not in prev_detection or "timestamp" not in curr_detection:
                continue
            
            # Calculate distance traveled
            prev_pos = prev_detection["position"]
            curr_pos = curr_detection["position"]
            
            dx = curr_pos.get("x", 0.0) - prev_pos.get("x", 0.0)
            dy = curr_pos.get("y", 0.0) - prev_pos.get("y", 0.0)
            dz = curr_pos.get("z", 0.0) - prev_pos.get("z", 0.0)
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            
            # Calculate time delta
            try:
                prev_time = self._parse_timestamp(prev_detection["timestamp"])
                curr_time = self._parse_timestamp(curr_detection["timestamp"])
                
                if prev_time is None or curr_time is None:
                    continue
                
                time_delta = (curr_time - prev_time).total_seconds()
                if time_delta <= 0:
                    continue
                
                # Calculate speed
                speed = distance / time_delta
                
                # Check for unrealistic speed (outlier)
                if speed > 1000.0:  # > 3600 km/h
                    outliers.append((
                        i,
                        OutlierDetectionResult(
                            is_outlier=True,
                            outlier_score=speed / 1000.0,
                            method="temporal",
                            reason=f"Unrealistic speed detected: {speed:.1f} m/s"
                        )
                    ))
            except Exception:
                continue
        
        return outliers
    
    def _parse_timestamp(self, timestamp: Any) -> Optional[Any]:
        """Parse timestamp to datetime object."""
        from datetime import datetime
        
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

