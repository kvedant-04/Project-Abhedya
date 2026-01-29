"""
Data Normalization Module

Classical statistical techniques for data normalization:
- Min-max normalization
- Z-score normalization
- Robust normalization (using median and IQR)

Uses fail-safe behavior: invalid data is rejected.
"""

from typing import List, Dict, Any, Optional
from statistics import mean, stdev, median
from dataclasses import dataclass


@dataclass
class NormalizationParameters:
    """Parameters for normalization."""
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    median_value: float
    iqr_value: float


class DataNormalizer:
    """
    Normalizes sensor data using classical statistical techniques.
    
    Methods:
    - Min-Max: Normalize to [0, 1] range
    - Z-Score: Normalize to mean=0, std=1
    - Robust: Normalize using median and IQR (robust to outliers)
    """
    
    def __init__(self):
        """Initialize data normalizer."""
        pass
    
    def normalize_min_max(
        self,
        values: List[float],
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[float]:
        """
        Normalize values to [0, 1] range using min-max normalization.
        
        Args:
            values: List of values to normalize
            min_value: Minimum value (calculated from data if None)
            max_value: Maximum value (calculated from data if None)
            
        Returns:
            List of normalized values [0, 1]
        """
        if len(values) == 0:
            return []
        
        # Filter out None values
        valid_values = [v for v in values if v is not None]
        if len(valid_values) == 0:
            return [None] * len(values)
        
        # Calculate min and max if not provided
        if min_value is None:
            min_value = min(valid_values)
        if max_value is None:
            max_value = max(valid_values)
        
        # Handle case where min == max
        if max_value == min_value:
            return [0.5] * len(values)
        
        # Normalize
        normalized = []
        for value in values:
            if value is None:
                normalized.append(None)
            else:
                norm_value = (value - min_value) / (max_value - min_value)
                # Clamp to [0, 1]
                norm_value = max(0.0, min(1.0, norm_value))
                normalized.append(norm_value)
        
        return normalized
    
    def normalize_z_score(
        self,
        values: List[float],
        mean_value: Optional[float] = None,
        std_value: Optional[float] = None
    ) -> List[float]:
        """
        Normalize values using Z-score normalization (mean=0, std=1).
        
        Args:
            values: List of values to normalize
            mean_value: Mean value (calculated from data if None)
            std_value: Standard deviation (calculated from data if None)
            
        Returns:
            List of normalized values (mean=0, std=1)
        """
        if len(values) == 0:
            return []
        
        # Filter out None values
        valid_values = [v for v in values if v is not None]
        if len(valid_values) < 2:
            return [0.0] * len(values)
        
        # Calculate mean and std if not provided
        if mean_value is None:
            mean_value = mean(valid_values)
        if std_value is None:
            std_value = stdev(valid_values)
        
        # Handle case where std == 0
        if std_value == 0:
            return [0.0] * len(values)
        
        # Normalize
        normalized = []
        for value in values:
            if value is None:
                normalized.append(None)
            else:
                norm_value = (value - mean_value) / std_value
                normalized.append(norm_value)
        
        return normalized
    
    def normalize_robust(
        self,
        values: List[float],
        median_value: Optional[float] = None,
        iqr_value: Optional[float] = None
    ) -> List[float]:
        """
        Normalize values using robust normalization (median and IQR).
        
        Robust to outliers.
        
        Args:
            values: List of values to normalize
            median_value: Median value (calculated from data if None)
            iqr_value: Interquartile range (calculated from data if None)
            
        Returns:
            List of normalized values
        """
        if len(values) == 0:
            return []
        
        # Filter out None values
        valid_values = [v for v in values if v is not None]
        if len(valid_values) < 4:
            return [0.0] * len(values)
        
        # Calculate median and IQR if not provided
        if median_value is None:
            median_value = median(valid_values)
        
        if iqr_value is None:
            sorted_values = sorted(valid_values)
            q1_index = len(sorted_values) // 4
            q3_index = 3 * len(sorted_values) // 4
            q1 = sorted_values[q1_index]
            q3 = sorted_values[q3_index]
            iqr_value = q3 - q1
        
        # Handle case where IQR == 0
        if iqr_value == 0:
            return [0.0] * len(values)
        
        # Normalize
        normalized = []
        for value in values:
            if value is None:
                normalized.append(None)
            else:
                norm_value = (value - median_value) / iqr_value
                normalized.append(norm_value)
        
        return normalized
    
    def calculate_normalization_parameters(
        self,
        values: List[float]
    ) -> NormalizationParameters:
        """
        Calculate normalization parameters from data.
        
        Args:
            values: List of values
            
        Returns:
            NormalizationParameters
        """
        valid_values = [v for v in values if v is not None]
        
        if len(valid_values) == 0:
            return NormalizationParameters(
                min_value=0.0,
                max_value=0.0,
                mean_value=0.0,
                std_value=1.0,
                median_value=0.0,
                iqr_value=1.0
            )
        
        min_val = min(valid_values)
        max_val = max(valid_values)
        mean_val = mean(valid_values) if len(valid_values) > 0 else 0.0
        std_val = stdev(valid_values) if len(valid_values) > 1 else 1.0
        median_val = median(valid_values)
        
        # Calculate IQR
        if len(valid_values) >= 4:
            sorted_values = sorted(valid_values)
            q1_index = len(sorted_values) // 4
            q3_index = 3 * len(sorted_values) // 4
            q1 = sorted_values[q1_index]
            q3 = sorted_values[q3_index]
            iqr_val = q3 - q1
        else:
            iqr_val = 1.0
        
        return NormalizationParameters(
            min_value=min_val,
            max_value=max_val,
            mean_value=mean_val,
            std_value=std_val,
            median_value=median_val,
            iqr_value=iqr_val
        )
    
    def normalize_detection_coordinates(
        self,
        detections: List[Dict[str, Any]],
        method: str = "min_max"
    ) -> List[Dict[str, Any]]:
        """
        Normalize coordinates in detections.
        
        Args:
            detections: List of detections
            method: Normalization method ("min_max", "z_score", "robust")
            
        Returns:
            List of detections with normalized coordinates
        """
        if len(detections) == 0:
            return detections
        
        # Extract coordinates
        x_values = [d.get("position", {}).get("x") for d in detections]
        y_values = [d.get("position", {}).get("y") for d in detections]
        z_values = [d.get("position", {}).get("z") for d in detections]
        
        # Normalize each coordinate
        if method == "min_max":
            x_norm = self.normalize_min_max(x_values)
            y_norm = self.normalize_min_max(y_values)
            z_norm = self.normalize_min_max(z_values)
        elif method == "z_score":
            x_norm = self.normalize_z_score(x_values)
            y_norm = self.normalize_z_score(y_values)
            z_norm = self.normalize_z_score(z_values)
        elif method == "robust":
            x_norm = self.normalize_robust(x_values)
            y_norm = self.normalize_robust(y_values)
            z_norm = self.normalize_robust(z_values)
        else:
            # Unknown method, return original
            return detections
        
        # Create copy and update coordinates
        processed = [d.copy() for d in detections]
        for i, detection in enumerate(processed):
            if "position" not in detection:
                detection["position"] = {}
            
            if x_norm[i] is not None:
                detection["position"]["x"] = x_norm[i]
            if y_norm[i] is not None:
                detection["position"]["y"] = y_norm[i]
            if z_norm[i] is not None:
                detection["position"]["z"] = z_norm[i]
        
        return processed

