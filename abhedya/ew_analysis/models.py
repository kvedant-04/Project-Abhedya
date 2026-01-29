"""
Electronic Warfare Signal Analysis Data Models

Data models for spectrum data, features, and analysis results.
All outputs are advisory only - signal analysis only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import numpy as np


class EWState(str, Enum):
    """
    Electronic Warfare analysis state (ADVISORY ONLY).
    
    These states are informational and do NOT map to any actions.
    """
    NORMAL = "NORMAL"           # Normal spectrum behavior
    ANOMALOUS = "ANOMALOUS"      # Anomalous signals detected


@dataclass
class SpectrumData:
    """
    RF spectrum data representation.
    
    Time-frequency matrix with power levels.
    """
    timestamp: datetime
    frequency_axis: np.ndarray  # Frequency bins (Hz)
    time_axis: np.ndarray       # Time samples (seconds)
    power_matrix: np.ndarray     # Power levels [frequency, time] (dBm)
    noise_floor: float          # Noise floor level (dBm)
    sample_rate: float          # Sample rate (Hz)
    frequency_resolution: float  # Frequency resolution (Hz)
    
    def __post_init__(self):
        """Validate spectrum data."""
        if self.power_matrix.shape[0] != len(self.frequency_axis):
            raise ValueError("Power matrix frequency dimension mismatch")
        if self.power_matrix.shape[1] != len(self.time_axis):
            raise ValueError("Power matrix time dimension mismatch")


@dataclass
class SpectralFeatures:
    """
    Extracted spectral features.
    
    Explainable features from signal analysis.
    """
    dominant_frequencies: List[float]  # Dominant frequency components (Hz)
    spectral_entropy: float            # Spectral entropy [0.0, 1.0]
    signal_to_noise_ratio: float       # SNR (dB)
    bandwidth_utilization: float        # Bandwidth utilization [0.0, 1.0]
    peak_power: float                  # Peak power level (dBm)
    average_power: float               # Average power level (dBm)
    power_variance: float              # Power variance
    frequency_centroid: float          # Frequency centroid (Hz)
    bandwidth: float                    # Occupied bandwidth (Hz)
    feature_vector: np.ndarray         # Feature vector for analysis


@dataclass
class AnomalyDetectionResult:
    """
    Anomaly detection result.
    
    Detected anomalies in spectrum data.
    """
    is_anomalous: bool
    anomaly_score: float  # [0.0, 1.0]
    statistical_deviation: float  # Statistical deviation from baseline
    entropy_spike_detected: bool
    noise_floor_elevation: bool
    unknown_emission_detected: bool
    suspected_pattern: str
    reasoning: List[str]
    confidence: float  # [0.0, 1.0]


@dataclass
class EWAnalysisResult:
    """
    Electronic Warfare analysis result.
    
    IMPORTANT: This is SIGNAL ANALYSIS ONLY.
    It does NOT provide:
    - EW response actions
    - Counter-EW logic
    - Control laws
    - Jamming capabilities
    - Countermeasures
    
    It only performs signal analysis and anomaly detection.
    """
    result_id: str
    timestamp: datetime
    ew_state: EWState
    confidence: float  # [0.0, 1.0]
    uncertainty: float  # [0.0, 1.0]
    spectrum_data: Optional[SpectrumData]
    spectral_features: Optional[SpectralFeatures]
    anomaly_detection: Optional[AnomalyDetectionResult]
    reasoning: List[str]  # Human-readable reasoning
    suspected_pattern_description: str
    data_quality_flags: List[str]
    analysis_statement: str = "SIGNAL ANALYSIS ONLY - No EW response actions. No counter-EW logic. No control laws. No jamming capabilities. No countermeasures. Advisory analysis only."

