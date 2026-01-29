"""
Electronic Warfare Analysis Engine

Main engine for EW signal analysis.
Aggregates spectrum simulation, feature extraction, and anomaly detection
to produce advisory EW analysis outputs.

SIGNAL ANALYSIS ONLY - No EW response actions, no counter-EW logic.
"""

import uuid
import numpy as np
from datetime import datetime
from typing import List, Optional

from abhedya.ew_analysis.models import (
    EWState,
    EWAnalysisResult,
    SpectrumData,
    SpectralFeatures,
    AnomalyDetectionResult
)
from abhedya.ew_analysis.spectrum_simulator import SpectrumSimulator
from abhedya.ew_analysis.feature_extractor import FeatureExtractor
from abhedya.ew_analysis.anomaly_detector import AnomalyDetector
from abhedya.infrastructure.config.config import ConfidenceThresholds


class EWAnalysisEngine:
    """
    Electronic Warfare Analysis Engine.
    
    SIGNAL ANALYSIS ONLY - Performs signal analysis and anomaly detection.
    
    Does NOT provide:
    - EW response actions
    - Counter-EW logic
    - Control laws
    - Jamming capabilities
    - Countermeasures
    
    Only performs signal analysis and advisory outputs.
    """
    
    def __init__(
        self,
        enable_spectrum_simulation: bool = True,
        enable_feature_extraction: bool = True,
        enable_anomaly_detection: bool = True,
        baseline_minimum_samples: int = 10
    ):
        """
        Initialize EW analysis engine.
        
        Args:
            enable_spectrum_simulation: Enable spectrum simulation
            enable_feature_extraction: Enable feature extraction
            enable_anomaly_detection: Enable anomaly detection
            baseline_minimum_samples: Minimum samples for baseline
        """
        self.enable_simulation = enable_spectrum_simulation
        self.enable_features = enable_feature_extraction
        self.enable_anomaly = enable_anomaly_detection
        self.baseline_minimum = baseline_minimum_samples
        
        self.spectrum_simulator = SpectrumSimulator()
        self.feature_extractor = FeatureExtractor()
        self.anomaly_detector = AnomalyDetector()
        
        self.baseline_features: List[SpectralFeatures] = []
    
    def analyze_spectrum(
        self,
        spectrum: Optional[SpectrumData] = None,
        simulate_if_missing: bool = True
    ) -> EWAnalysisResult:
        """
        Analyze spectrum data and produce EW analysis result.
        
        SIGNAL ANALYSIS ONLY - No EW response actions or counter-EW logic.
        
        Args:
            spectrum: SpectrumData to analyze (optional)
            simulate_if_missing: Whether to simulate if spectrum is None
            
        Returns:
            EWAnalysisResult (advisory only)
        """
        current_time = datetime.now()
        
        # Get or simulate spectrum
        if spectrum is None and simulate_if_missing:
            spectrum = self.spectrum_simulator.simulate_normal_spectrum()
        elif spectrum is None:
            return self._create_error_result(
                current_time,
                "No spectrum data provided and simulation disabled"
            )
        
        # Check data quality
        data_quality_flags = self._check_data_quality(spectrum)
        
        # Extract features
        features = None
        if self.enable_features:
            try:
                features = self.feature_extractor.extract_features(spectrum)
            except Exception as e:
                data_quality_flags.append(f"Feature extraction error: {str(e)}")
        
        if features is None:
            return self._create_error_result(
                current_time,
                "Failed to extract features",
                data_quality_flags
            )
        
        # Update baseline
        if len(self.baseline_features) < self.baseline_minimum:
            self.baseline_features.append(features)
            baseline_for_comparison = None
        else:
            baseline_for_comparison = self.baseline_features
            # Update baseline (sliding window)
            self.baseline_features.append(features)
            if len(self.baseline_features) > 100:
                self.baseline_features = self.baseline_features[-100:]
        
        # Detect anomalies
        anomaly_result = None
        if self.enable_anomaly:
            try:
                anomaly_result = self.anomaly_detector.detect_anomalies(
                    spectrum,
                    features,
                    baseline_for_comparison
                )
            except Exception as e:
                data_quality_flags.append(f"Anomaly detection error: {str(e)}")
        
        # Determine EW state
        ew_state = self._determine_ew_state(anomaly_result)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            features,
            anomaly_result,
            data_quality_flags
        )
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(
            features,
            anomaly_result,
            len(self.baseline_features)
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            ew_state,
            features,
            anomaly_result,
            data_quality_flags
        )
        
        # Generate suspected pattern description
        suspected_pattern = self._generate_suspected_pattern_description(
            anomaly_result,
            features
        )
        
        return EWAnalysisResult(
            result_id=str(uuid.uuid4()),
            timestamp=current_time,
            ew_state=ew_state,
            confidence=confidence,
            uncertainty=uncertainty,
            spectrum_data=spectrum,
            spectral_features=features,
            anomaly_detection=anomaly_result,
            reasoning=reasoning,
            suspected_pattern_description=suspected_pattern,
            data_quality_flags=data_quality_flags,
            analysis_statement="SIGNAL ANALYSIS ONLY - No EW response actions. No counter-EW logic. No control laws. No jamming capabilities. No countermeasures. Advisory analysis only."
        )
    
    def _check_data_quality(self, spectrum: SpectrumData) -> List[str]:
        """Check data quality and return flags."""
        flags = []
        
        # Check for valid power matrix
        if spectrum.power_matrix.size == 0:
            flags.append("Empty power matrix")
        
        # Check for valid frequency axis
        if len(spectrum.frequency_axis) == 0:
            flags.append("Empty frequency axis")
        
        # Check for valid time axis
        if len(spectrum.time_axis) == 0:
            flags.append("Empty time axis")
        
        # Check for reasonable power levels
        if np.any(np.isnan(spectrum.power_matrix)):
            flags.append("NaN values in power matrix")
        
        if np.any(np.isinf(spectrum.power_matrix)):
            flags.append("Infinite values in power matrix")
        
        return flags
    
    def _create_error_result(
        self,
        timestamp: datetime,
        error_message: str,
        data_quality_flags: Optional[List[str]] = None
    ) -> EWAnalysisResult:
        """Create error result."""
        flags = data_quality_flags or []
        flags.append(error_message)
        
        return EWAnalysisResult(
            result_id=str(uuid.uuid4()),
            timestamp=timestamp,
            ew_state=EWState.NORMAL,  # Default to normal on error
            confidence=0.0,
            uncertainty=1.0,
            spectrum_data=None,
            spectral_features=None,
            anomaly_detection=None,
            reasoning=[f"Error: {error_message}"],
            suspected_pattern_description="Unable to analyze - insufficient data",
            data_quality_flags=flags,
            analysis_statement="SIGNAL ANALYSIS ONLY - No EW response actions. No counter-EW logic. No control laws. No jamming capabilities. No countermeasures. Advisory analysis only."
        )
    
    def _determine_ew_state(
        self,
        anomaly_result: Optional[AnomalyDetectionResult]
    ) -> EWState:
        """
        Determine EW state.
        
        ADVISORY ONLY - State is informational and does not map to actions.
        """
        if anomaly_result is None:
            return EWState.NORMAL
        
        if anomaly_result.is_anomalous:
            return EWState.ANOMALOUS
        
        return EWState.NORMAL
    
    def _calculate_confidence(
        self,
        features: SpectralFeatures,
        anomaly_result: Optional[AnomalyDetectionResult],
        data_quality_flags: List[str]
    ) -> float:
        """Calculate confidence in EW analysis."""
        confidence = 0.7  # Base confidence
        
        # Reduce confidence for data quality issues
        if len(data_quality_flags) > 0:
            confidence -= len(data_quality_flags) * 0.1
        
        # Increase confidence if anomaly detection succeeded
        if anomaly_result:
            confidence = (confidence + anomaly_result.confidence) / 2.0
        
        # Adjust based on SNR
        if features.signal_to_noise_ratio > 10.0:
            confidence += 0.1
        elif features.signal_to_noise_ratio < 3.0:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_uncertainty(
        self,
        features: SpectralFeatures,
        anomaly_result: Optional[AnomalyDetectionResult],
        baseline_size: int
    ) -> float:
        """Calculate uncertainty in EW analysis."""
        uncertainty = 0.3  # Base uncertainty
        
        # Increase uncertainty if baseline is small
        if baseline_size < self.baseline_minimum:
            uncertainty += 0.3
        
        # Increase uncertainty for low SNR
        if features.signal_to_noise_ratio < 3.0:
            uncertainty += 0.2
        
        # Increase uncertainty if anomaly detection failed
        if anomaly_result is None:
            uncertainty += 0.2
        
        return min(1.0, max(0.0, uncertainty))
    
    def _generate_reasoning(
        self,
        ew_state: EWState,
        features: SpectralFeatures,
        anomaly_result: Optional[AnomalyDetectionResult],
        data_quality_flags: List[str]
    ) -> List[str]:
        """Generate human-readable reasoning."""
        reasoning = []
        
        reasoning.append(f"EW Analysis State: {ew_state.value} (ADVISORY ONLY)")
        reasoning.append("")
        
        reasoning.append("Spectral Features:")
        reasoning.append(f"  - Spectral Entropy: {features.spectral_entropy:.3f}")
        reasoning.append(f"  - Signal-to-Noise Ratio: {features.signal_to_noise_ratio:.2f} dB")
        reasoning.append(f"  - Bandwidth Utilization: {features.bandwidth_utilization:.2%}")
        reasoning.append(f"  - Peak Power: {features.peak_power:.2f} dBm")
        reasoning.append(f"  - Average Power: {features.average_power:.2f} dBm")
        reasoning.append(f"  - Frequency Centroid: {features.frequency_centroid/1e9:.3f} GHz")
        reasoning.append(f"  - Occupied Bandwidth: {features.bandwidth/1e9:.3f} GHz")
        
        if len(features.dominant_frequencies) > 0:
            reasoning.append(f"  - Dominant Frequencies: {len(features.dominant_frequencies)} detected")
            for i, freq in enumerate(features.dominant_frequencies[:5]):  # Show top 5
                reasoning.append(f"    {i+1}. {freq/1e9:.3f} GHz")
        
        reasoning.append("")
        
        if anomaly_result:
            reasoning.append("Anomaly Detection:")
            for line in anomaly_result.reasoning:
                reasoning.append(f"  - {line}")
            reasoning.append(f"  - Suspected Pattern: {anomaly_result.suspected_pattern}")
            reasoning.append("")
        
        if len(data_quality_flags) > 0:
            reasoning.append("Data Quality Flags:")
            for flag in data_quality_flags:
                reasoning.append(f"  - {flag}")
            reasoning.append("")
        
        reasoning.append("IMPORTANT: This is SIGNAL ANALYSIS ONLY.")
        reasoning.append("No EW response actions are provided.")
        reasoning.append("No counter-EW logic is included.")
        reasoning.append("No control laws are implemented.")
        reasoning.append("Advisory analysis only.")
        
        return reasoning
    
    def _generate_suspected_pattern_description(
        self,
        anomaly_result: Optional[AnomalyDetectionResult],
        features: SpectralFeatures
    ) -> str:
        """Generate suspected pattern description."""
        if anomaly_result:
            return anomaly_result.suspected_pattern
        
        # Default description based on features
        if features.bandwidth_utilization > 0.5:
            return "High bandwidth utilization detected"
        elif features.signal_to_noise_ratio > 10.0:
            return "Strong signal detected"
        else:
            return "Normal spectrum pattern"

