"""
Feature Extractor

Extracts explainable features from spectrum data:
- FFT-based spectral components
- Spectral entropy
- Signal-to-noise ratio (SNR)
- Bandwidth utilization

Uses classical signal processing techniques only.
"""

import math
import numpy as np
from typing import List, Tuple

from abhedya.ew_analysis.models import SpectrumData, SpectralFeatures


class FeatureExtractor:
    """
    Extracts explainable features from spectrum data.
    
    Uses classical signal processing techniques:
    - FFT for spectral analysis
    - Entropy calculation
    - SNR estimation
    - Bandwidth analysis
    """
    
    def __init__(
        self,
        snr_threshold_db: float = 3.0,
        entropy_normalization: bool = True
    ):
        """
        Initialize feature extractor.
        
        Args:
            snr_threshold_db: SNR threshold for signal detection (dB)
            entropy_normalization: Whether to normalize entropy
        """
        self.snr_threshold = snr_threshold_db
        self.normalize_entropy = entropy_normalization
    
    def extract_features(self, spectrum: SpectrumData) -> SpectralFeatures:
        """
        Extract features from spectrum data.
        
        Args:
            spectrum: SpectrumData to analyze
            
        Returns:
            SpectralFeatures
        """
        # Calculate average power spectrum
        avg_power_spectrum = np.mean(spectrum.power_matrix, axis=1)
        
        # Find dominant frequencies (FFT-based)
        dominant_frequencies = self._find_dominant_frequencies(
            spectrum.frequency_axis,
            avg_power_spectrum,
            spectrum.noise_floor
        )
        
        # Calculate spectral entropy
        spectral_entropy = self._calculate_spectral_entropy(avg_power_spectrum)
        
        # Calculate SNR
        snr = self._calculate_snr(avg_power_spectrum, spectrum.noise_floor)
        
        # Calculate bandwidth utilization
        bandwidth_utilization = self._calculate_bandwidth_utilization(
            spectrum.frequency_axis,
            avg_power_spectrum,
            spectrum.noise_floor
        )
        
        # Calculate power statistics
        peak_power = np.max(avg_power_spectrum)
        average_power = np.mean(avg_power_spectrum)
        power_variance = np.var(avg_power_spectrum)
        
        # Calculate frequency centroid
        frequency_centroid = self._calculate_frequency_centroid(
            spectrum.frequency_axis,
            avg_power_spectrum
        )
        
        # Calculate occupied bandwidth
        bandwidth = self._calculate_bandwidth(
            spectrum.frequency_axis,
            avg_power_spectrum,
            spectrum.noise_floor
        )
        
        # Create feature vector
        feature_vector = np.array([
            spectral_entropy,
            snr,
            bandwidth_utilization,
            peak_power,
            average_power,
            power_variance,
            frequency_centroid / 1e9,  # Normalize to GHz
            bandwidth / 1e9  # Normalize to GHz
        ])
        
        return SpectralFeatures(
            dominant_frequencies=dominant_frequencies,
            spectral_entropy=spectral_entropy,
            signal_to_noise_ratio=snr,
            bandwidth_utilization=bandwidth_utilization,
            peak_power=peak_power,
            average_power=average_power,
            power_variance=power_variance,
            frequency_centroid=frequency_centroid,
            bandwidth=bandwidth,
            feature_vector=feature_vector
        )
    
    def _find_dominant_frequencies(
        self,
        frequency_axis: np.ndarray,
        power_spectrum: np.ndarray,
        noise_floor: float
    ) -> List[float]:
        """
        Find dominant frequency components using FFT-based analysis.
        
        Args:
            frequency_axis: Frequency axis
            power_spectrum: Power spectrum
            noise_floor: Noise floor level
            
        Returns:
            List of dominant frequencies (Hz)
        """
        # Threshold for signal detection (noise floor + threshold)
        threshold = noise_floor + self.snr_threshold
        
        # Find frequencies above threshold
        signal_mask = power_spectrum > threshold
        
        if not np.any(signal_mask):
            return []
        
        # Find peaks (local maxima)
        peaks = []
        for i in range(1, len(power_spectrum) - 1):
            if signal_mask[i] and power_spectrum[i] > power_spectrum[i-1] and power_spectrum[i] > power_spectrum[i+1]:
                peaks.append((i, power_spectrum[i]))
        
        # Sort by power and take top frequencies
        peaks.sort(key=lambda x: x[1], reverse=True)
        dominant_frequencies = [frequency_axis[idx] for idx, _ in peaks[:10]]  # Top 10
        
        return dominant_frequencies
    
    def _calculate_spectral_entropy(self, power_spectrum: np.ndarray) -> float:
        """
        Calculate spectral entropy.
        
        Entropy measures the randomness/unpredictability of the spectrum.
        Higher entropy = more random, lower entropy = more structured.
        
        Args:
            power_spectrum: Power spectrum
            
        Returns:
            Spectral entropy [0.0, 1.0]
        """
        # Convert to linear scale (power)
        power_linear = 10.0 ** (power_spectrum / 10.0)
        
        # Normalize to probability distribution
        total_power = np.sum(power_linear)
        if total_power == 0:
            return 1.0  # Maximum entropy if no power
        
        probabilities = power_linear / total_power
        
        # Calculate entropy: H = -Σ(p * log2(p))
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normalize to [0, 1]
        if self.normalize_entropy:
            max_entropy = math.log2(len(probabilities))
            if max_entropy > 0:
                entropy = entropy / max_entropy
        
        return entropy
    
    def _calculate_snr(
        self,
        power_spectrum: np.ndarray,
        noise_floor: float
    ) -> float:
        """
        Calculate signal-to-noise ratio.
        
        Args:
            power_spectrum: Power spectrum
            noise_floor: Noise floor level (dBm)
            
        Returns:
            SNR in dB
        """
        # Average signal power
        avg_signal_power = np.mean(power_spectrum)
        
        # SNR = signal_power - noise_floor
        snr = avg_signal_power - noise_floor
        
        return snr
    
    def _calculate_bandwidth_utilization(
        self,
        frequency_axis: np.ndarray,
        power_spectrum: np.ndarray,
        noise_floor: float
    ) -> float:
        """
        Calculate bandwidth utilization.
        
        Fraction of frequency bins with power above noise floor.
        
        Args:
            frequency_axis: Frequency axis
            power_spectrum: Power spectrum
            noise_floor: Noise floor level
            
        Returns:
            Bandwidth utilization [0.0, 1.0]
        """
        # Count bins above noise floor
        threshold = noise_floor + self.snr_threshold
        occupied_bins = np.sum(power_spectrum > threshold)
        total_bins = len(power_spectrum)
        
        if total_bins == 0:
            return 0.0
        
        return occupied_bins / total_bins
    
    def _calculate_frequency_centroid(
        self,
        frequency_axis: np.ndarray,
        power_spectrum: np.ndarray
    ) -> float:
        """
        Calculate frequency centroid (weighted average frequency).
        
        Args:
            frequency_axis: Frequency axis
            power_spectrum: Power spectrum
            
        Returns:
            Frequency centroid (Hz)
        """
        # Convert to linear scale
        power_linear = 10.0 ** (power_spectrum / 10.0)
        total_power = np.sum(power_linear)
        
        if total_power == 0:
            return np.mean(frequency_axis)
        
        # Weighted average
        centroid = np.sum(frequency_axis * power_linear) / total_power
        
        return centroid
    
    def _calculate_bandwidth(
        self,
        frequency_axis: np.ndarray,
        power_spectrum: np.ndarray,
        noise_floor: float
    ) -> float:
        """
        Calculate occupied bandwidth.
        
        Bandwidth where power is above noise floor.
        
        Args:
            frequency_axis: Frequency axis
            power_spectrum: Power spectrum
            noise_floor: Noise floor level
            
        Returns:
            Occupied bandwidth (Hz)
        """
        threshold = noise_floor + self.snr_threshold
        signal_mask = power_spectrum > threshold
        
        if not np.any(signal_mask):
            return 0.0
        
        # Find frequency range
        min_freq = np.min(frequency_axis[signal_mask])
        max_freq = np.max(frequency_axis[signal_mask])
        
        return max_freq - min_freq

