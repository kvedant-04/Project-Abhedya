"""
Anomaly Detector

Detects anomalies in spectrum data using:
- Statistical deviation from baseline
- Entropy spikes
- Noise floor elevation
- Unknown emission patterns

Uses classical statistical techniques only.
"""

import math
import numpy as np
from typing import List, Optional, Dict, Any
from statistics import mean, stdev

from abhedya.ew_analysis.models import (
    SpectrumData,
    SpectralFeatures,
    AnomalyDetectionResult
)


class AnomalyDetector:
    """
    Detects anomalies in spectrum data.
    
    Uses classical statistical techniques:
    - Statistical deviation (Z-score)
    - Entropy analysis
    - Noise floor comparison
    - Pattern recognition
    """
    
    def __init__(
        self,
        z_score_threshold: float = 2.0,
        entropy_spike_threshold: float = 0.3,
        noise_floor_elevation_threshold_db: float = 5.0
    ):
        """
        Initialize anomaly detector.
        
        Args:
            z_score_threshold: Z-score threshold for statistical deviation
            entropy_spike_threshold: Threshold for entropy spike detection
            noise_floor_elevation_threshold_db: Threshold for noise floor elevation (dB)
        """
        self.z_score_threshold = z_score_threshold
        self.entropy_spike_threshold = entropy_spike_threshold
        self.noise_floor_elevation_threshold = noise_floor_elevation_threshold_db
        self.baseline_features: List[SpectralFeatures] = []
    
    def detect_anomalies(
        self,
        spectrum: SpectrumData,
        features: SpectralFeatures,
        baseline_features: Optional[List[SpectralFeatures]] = None
    ) -> AnomalyDetectionResult:
        """
        Detect anomalies in spectrum data.
        
        Args:
            spectrum: SpectrumData to analyze
            features: Extracted spectral features
            baseline_features: Baseline features for comparison (optional)
            
        Returns:
            AnomalyDetectionResult
        """
        reasoning = []
        anomaly_indicators = []
        anomaly_score = 0.0
        
        # Statistical deviation from baseline
        statistical_deviation = 0.0
        if baseline_features and len(baseline_features) > 0:
            statistical_deviation = self._calculate_statistical_deviation(
                features,
                baseline_features
            )
            
            if statistical_deviation > self.z_score_threshold:
                anomaly_score += 0.4
                reasoning.append(f"Statistical deviation from baseline: {statistical_deviation:.2f}σ (threshold: {self.z_score_threshold}σ)")
                anomaly_indicators.append("Significant statistical deviation from baseline")
        
        # Entropy spike detection
        entropy_spike = False
        if baseline_features and len(baseline_features) > 0:
            baseline_entropy = mean([f.spectral_entropy for f in baseline_features])
            entropy_change = abs(features.spectral_entropy - baseline_entropy)
            
            if entropy_change > self.entropy_spike_threshold:
                entropy_spike = True
                anomaly_score += 0.3
                reasoning.append(f"Entropy spike detected: change of {entropy_change:.3f} (baseline: {baseline_entropy:.3f}, current: {features.spectral_entropy:.3f})")
                anomaly_indicators.append("Spectral entropy spike detected")
        
        # Noise floor elevation
        noise_floor_elevation = False
        if baseline_features and len(baseline_features) > 0:
            baseline_noise = mean([f.average_power for f in baseline_features])
            noise_elevation = features.average_power - baseline_noise
            
            if noise_elevation > self.noise_floor_elevation_threshold:
                noise_floor_elevation = True
                anomaly_score += 0.2
                reasoning.append(f"Noise floor elevation: {noise_elevation:.2f} dB above baseline")
                anomaly_indicators.append("Noise floor elevation detected")
        
        # Unknown emission detection
        unknown_emission = False
        if len(features.dominant_frequencies) > 0:
            # Check if dominant frequencies are unusual
            # Simplified: check if SNR is high but frequencies are not in expected range
            if features.signal_to_noise_ratio > 10.0:
                # High SNR suggests strong signals
                if baseline_features and len(baseline_features) > 0:
                    baseline_snr = mean([f.signal_to_noise_ratio for f in baseline_features])
                    if features.signal_to_noise_ratio > baseline_snr * 1.5:
                        unknown_emission = True
                        anomaly_score += 0.1
                        reasoning.append(f"Unknown emission detected: SNR {features.signal_to_noise_ratio:.2f} dB (baseline: {baseline_snr:.2f} dB)")
                        anomaly_indicators.append("Unknown emission pattern detected")
        
        # Determine if anomalous
        is_anomalous = anomaly_score > 0.5 or statistical_deviation > self.z_score_threshold
        
        # Generate suspected pattern description
        suspected_pattern = self._generate_suspected_pattern(
            entropy_spike,
            noise_floor_elevation,
            unknown_emission,
            features
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            features,
            baseline_features,
            anomaly_score
        )
        
        # Add summary reasoning
        if is_anomalous:
            reasoning.insert(0, f"Anomaly detected with score: {anomaly_score:.2%}")
        else:
            reasoning.insert(0, "No significant anomalies detected")
        
        return AnomalyDetectionResult(
            is_anomalous=is_anomalous,
            anomaly_score=min(1.0, anomaly_score),
            statistical_deviation=statistical_deviation,
            entropy_spike_detected=entropy_spike,
            noise_floor_elevation=noise_floor_elevation,
            unknown_emission_detected=unknown_emission,
            suspected_pattern=suspected_pattern,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def _calculate_statistical_deviation(
        self,
        features: SpectralFeatures,
        baseline_features: List[SpectralFeatures]
    ) -> float:
        """
        Calculate statistical deviation from baseline (Z-score).
        
        Args:
            features: Current features
            baseline_features: Baseline features
            
        Returns:
            Maximum Z-score across features
        """
        if len(baseline_features) < 2:
            return 0.0
        
        # Extract baseline feature vectors
        baseline_vectors = np.array([f.feature_vector for f in baseline_features])
        
        # Calculate mean and std for each feature
        baseline_mean = np.mean(baseline_vectors, axis=0)
        baseline_std = np.std(baseline_vectors, axis=0)
        
        # Avoid division by zero
        baseline_std = np.where(baseline_std == 0, 1.0, baseline_std)
        
        # Calculate Z-scores
        z_scores = np.abs((features.feature_vector - baseline_mean) / baseline_std)
        
        # Return maximum Z-score
        return float(np.max(z_scores))
    
    def _generate_suspected_pattern(
        self,
        entropy_spike: bool,
        noise_floor_elevation: bool,
        unknown_emission: bool,
        features: SpectralFeatures
    ) -> str:
        """Generate suspected pattern description."""
        patterns = []
        
        if entropy_spike:
            patterns.append("High spectral entropy")
        
        if noise_floor_elevation:
            patterns.append("Elevated noise floor")
        
        if unknown_emission:
            patterns.append("Unknown emission")
        
        if features.bandwidth_utilization > 0.5:
            patterns.append("High bandwidth utilization")
        
        if len(features.dominant_frequencies) > 5:
            patterns.append("Multiple dominant frequencies")
        
        if not patterns:
            return "Normal spectrum pattern"
        
        return ", ".join(patterns)
    
    def _calculate_confidence(
        self,
        features: SpectralFeatures,
        baseline_features: Optional[List[SpectralFeatures]],
        anomaly_score: float
    ) -> float:
        """Calculate confidence in anomaly detection."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if baseline exists
        if baseline_features and len(baseline_features) >= 5:
            confidence += 0.3
        
        # Increase confidence with anomaly score
        confidence += anomaly_score * 0.2
        
        # Decrease confidence if SNR is low
        if features.signal_to_noise_ratio < 3.0:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def update_baseline(self, features: SpectralFeatures):
        """
        Update baseline with new features.
        
        Args:
            features: Features to add to baseline
        """
        self.baseline_features.append(features)
        
        # Keep only recent baseline (last 100 samples)
        if len(self.baseline_features) > 100:
            self.baseline_features = self.baseline_features[-100:]

