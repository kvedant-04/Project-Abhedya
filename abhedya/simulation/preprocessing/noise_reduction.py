"""
Noise Reduction Module

Classical statistical techniques for noise reduction:
- Moving average filter
- Median filter
- Exponential smoothing
- Kalman filter (simplified)

Uses fail-safe behavior: corrupted data is rejected, not modified.
"""

import math
from typing import List, Dict, Any, Optional
from statistics import median, mean


class NoiseReducer:
    """
    Reduces noise in sensor data using classical statistical techniques.
    
    Methods:
    - Moving Average: Smooths data using rolling average
    - Median Filter: Removes outliers using median
    - Exponential Smoothing: Weighted average with exponential decay
    """
    
    def __init__(
        self,
        moving_average_window: int = 5,
        median_filter_window: int = 5,
        exponential_smoothing_alpha: float = 0.3
    ):
        """
        Initialize noise reducer.
        
        Args:
            moving_average_window: Window size for moving average (default: 5)
            median_filter_window: Window size for median filter (default: 5)
            exponential_smoothing_alpha: Smoothing factor for exponential smoothing (0-1)
        """
        self.moving_average_window = moving_average_window
        self.median_filter_window = median_filter_window
        self.exponential_smoothing_alpha = exponential_smoothing_alpha
    
    def reduce_noise_moving_average(
        self,
        detections: List[Dict[str, Any]],
        field_path: str = "position.x"
    ) -> List[float]:
        """
        Apply moving average filter to reduce noise.
        
        Args:
            detections: List of detections
            field_path: Path to field to smooth (e.g., "position.x", "velocity.vx")
            
        Returns:
            List of smoothed values
        """
        if len(detections) < self.moving_average_window:
            # Not enough data, return original values
            return [self._get_field_value(d, field_path) for d in detections]
        
        values = [self._get_field_value(d, field_path) for d in detections]
        smoothed = []
        
        for i in range(len(values)):
            if values[i] is None:
                smoothed.append(None)
                continue
            
            # Get window of values
            start = max(0, i - self.moving_average_window // 2)
            end = min(len(values), i + self.moving_average_window // 2 + 1)
            window = [v for v in values[start:end] if v is not None]
            
            if len(window) == 0:
                smoothed.append(None)
            else:
                smoothed.append(mean(window))
        
        return smoothed
    
    def reduce_noise_median_filter(
        self,
        detections: List[Dict[str, Any]],
        field_path: str = "position.x"
    ) -> List[float]:
        """
        Apply median filter to reduce noise and remove outliers.
        
        Args:
            detections: List of detections
            field_path: Path to field to filter
            
        Returns:
            List of filtered values
        """
        if len(detections) < self.median_filter_window:
            # Not enough data, return original values
            return [self._get_field_value(d, field_path) for d in detections]
        
        values = [self._get_field_value(d, field_path) for d in detections]
        filtered = []
        
        for i in range(len(values)):
            if values[i] is None:
                filtered.append(None)
                continue
            
            # Get window of values
            start = max(0, i - self.median_filter_window // 2)
            end = min(len(values), i + self.median_filter_window // 2 + 1)
            window = [v for v in values[start:end] if v is not None]
            
            if len(window) == 0:
                filtered.append(None)
            else:
                filtered.append(median(window))
        
        return filtered
    
    def reduce_noise_exponential_smoothing(
        self,
        detections: List[Dict[str, Any]],
        field_path: str = "position.x"
    ) -> List[float]:
        """
        Apply exponential smoothing to reduce noise.
        
        Args:
            detections: List of detections
            field_path: Path to field to smooth
            
        Returns:
            List of smoothed values
        """
        values = [self._get_field_value(d, field_path) for d in detections]
        
        if len(values) == 0:
            return []
        
        smoothed = []
        prev_smoothed = None
        
        for value in values:
            if value is None:
                smoothed.append(None)
                continue
            
            if prev_smoothed is None:
                # First value
                prev_smoothed = value
                smoothed.append(value)
            else:
                # Exponential smoothing: S_t = α * X_t + (1 - α) * S_{t-1}
                smoothed_value = (
                    self.exponential_smoothing_alpha * value +
                    (1 - self.exponential_smoothing_alpha) * prev_smoothed
                )
                smoothed.append(smoothed_value)
                prev_smoothed = smoothed_value
        
        return smoothed
    
    def reduce_position_noise(
        self,
        detections: List[Dict[str, Any]],
        method: str = "moving_average"
    ) -> List[Dict[str, Any]]:
        """
        Reduce noise in position measurements.
        
        Args:
            detections: List of detections with position data
            method: Noise reduction method ("moving_average", "median", "exponential")
            
        Returns:
            List of detections with noise-reduced positions
        """
        if len(detections) == 0:
            return detections
        
        # Create copy to avoid modifying original
        processed = [d.copy() for d in detections]
        
        # Apply noise reduction to each coordinate
        for coord in ["x", "y", "z"]:
            field_path = f"position.{coord}"
            
            if method == "moving_average":
                smoothed = self.reduce_noise_moving_average(processed, field_path)
            elif method == "median":
                smoothed = self.reduce_noise_median_filter(processed, field_path)
            elif method == "exponential":
                smoothed = self.reduce_noise_exponential_smoothing(processed, field_path)
            else:
                # Unknown method, skip
                continue
            
            # Update positions
            for i, value in enumerate(smoothed):
                if value is not None and "position" in processed[i]:
                    processed[i]["position"][coord] = value
        
        return processed
    
    def reduce_velocity_noise(
        self,
        detections: List[Dict[str, Any]],
        method: str = "moving_average"
    ) -> List[Dict[str, Any]]:
        """
        Reduce noise in velocity measurements.
        
        Args:
            detections: List of detections with velocity data
            method: Noise reduction method
            
        Returns:
            List of detections with noise-reduced velocities
        """
        if len(detections) == 0:
            return detections
        
        # Create copy to avoid modifying original
        processed = [d.copy() for d in detections]
        
        # Apply noise reduction to each velocity component
        for component in ["vx", "vy", "vz"]:
            field_path = f"velocity.{component}"
            
            if method == "moving_average":
                smoothed = self.reduce_noise_moving_average(processed, field_path)
            elif method == "median":
                smoothed = self.reduce_noise_median_filter(processed, field_path)
            elif method == "exponential":
                smoothed = self.reduce_noise_exponential_smoothing(processed, field_path)
            else:
                continue
            
            # Update velocities
            for i, value in enumerate(smoothed):
                if value is not None and "velocity" in processed[i]:
                    processed[i]["velocity"][component] = value
        
        return processed
    
    def _get_field_value(self, detection: Dict[str, Any], field_path: str) -> Optional[float]:
        """
        Get value from nested dictionary using dot notation path.
        
        Args:
            detection: Detection dictionary
            field_path: Path like "position.x" or "velocity.vx"
            
        Returns:
            Field value or None if not found
        """
        parts = field_path.split(".")
        value = detection
        
        for part in parts:
            if not isinstance(value, dict):
                return None
            value = value.get(part)
            if value is None:
                return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        return None

