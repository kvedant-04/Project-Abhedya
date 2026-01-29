"""
RF Spectrum Simulator

Simulates RF spectrum data for analysis.
Mathematical simulation only - no real hardware interaction.
"""

import math
import numpy as np
from datetime import datetime
from typing import List, Optional, Tuple

from abhedya.ew_analysis.models import SpectrumData


class SpectrumSimulator:
    """
    Simulates RF spectrum data.
    
    Mathematical simulation only - no real hardware interaction.
    """
    
    def __init__(
        self,
        frequency_range_hz: Tuple[float, float] = (1e6, 10e9),  # 1 MHz to 10 GHz
        frequency_resolution_hz: float = 1e6,  # 1 MHz resolution
        time_duration_seconds: float = 1.0,
        sample_rate_hz: float = 1000.0,  # 1 kHz sample rate
        noise_floor_dbm: float = -100.0,
        random_seed: Optional[int] = None
    ):
        """
        Initialize spectrum simulator.
        
        Args:
            frequency_range_hz: (min_freq, max_freq) in Hz
            frequency_resolution_hz: Frequency resolution in Hz
            time_duration_seconds: Time duration for simulation
            sample_rate_hz: Sample rate in Hz
            noise_floor_dbm: Noise floor in dBm
            random_seed: Random seed for reproducibility
        """
        self.freq_min, self.freq_max = frequency_range_hz
        self.freq_resolution = frequency_resolution_hz
        self.time_duration = time_duration_seconds
        self.sample_rate = sample_rate_hz
        self.noise_floor = noise_floor_dbm
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Calculate frequency bins
        self.num_freq_bins = int((self.freq_max - self.freq_min) / self.freq_resolution) + 1
        self.num_time_samples = int(self.time_duration * self.sample_rate)
    
    def simulate_spectrum(
        self,
        signal_frequencies: Optional[List[float]] = None,
        signal_powers: Optional[List[float]] = None,
        signal_bandwidths: Optional[List[float]] = None,
        add_noise: bool = True,
        noise_variance: float = 2.0
    ) -> SpectrumData:
        """
        Simulate RF spectrum data.
        
        Args:
            signal_frequencies: List of signal frequencies (Hz)
            signal_powers: List of signal powers (dBm)
            signal_bandwidths: List of signal bandwidths (Hz)
            add_noise: Whether to add noise
            noise_variance: Noise variance (dB)
            
        Returns:
            SpectrumData
        """
        # Create frequency axis
        frequency_axis = np.linspace(
            self.freq_min,
            self.freq_max,
            self.num_freq_bins
        )
        
        # Create time axis
        time_axis = np.linspace(
            0.0,
            self.time_duration,
            self.num_time_samples
        )
        
        # Initialize power matrix with noise floor
        power_matrix = np.full(
            (self.num_freq_bins, self.num_time_samples),
            self.noise_floor
        )
        
        # Add signals if specified
        if signal_frequencies:
            if signal_powers is None:
                signal_powers = [-80.0] * len(signal_frequencies)
            if signal_bandwidths is None:
                signal_bandwidths = [self.freq_resolution * 2] * len(signal_frequencies)
            
            for freq, power, bandwidth in zip(signal_frequencies, signal_powers, signal_bandwidths):
                self._add_signal(
                    power_matrix,
                    frequency_axis,
                    time_axis,
                    freq,
                    power,
                    bandwidth
                )
        
        # Add noise
        if add_noise:
            noise = np.random.normal(0.0, noise_variance, power_matrix.shape)
            power_matrix += noise
        
        return SpectrumData(
            timestamp=datetime.now(),
            frequency_axis=frequency_axis,
            time_axis=time_axis,
            power_matrix=power_matrix,
            noise_floor=self.noise_floor,
            sample_rate=self.sample_rate,
            frequency_resolution=self.freq_resolution
        )
    
    def _add_signal(
        self,
        power_matrix: np.ndarray,
        frequency_axis: np.ndarray,
        time_axis: np.ndarray,
        center_frequency: float,
        power_dbm: float,
        bandwidth_hz: float
    ):
        """
        Add a signal to the power matrix.
        
        Args:
            power_matrix: Power matrix to modify
            frequency_axis: Frequency axis
            time_axis: Time axis
            center_frequency: Center frequency (Hz)
            power_dbm: Signal power (dBm)
            bandwidth_hz: Signal bandwidth (Hz)
        """
        # Find frequency bins within bandwidth
        freq_mask = np.abs(frequency_axis - center_frequency) <= bandwidth_hz / 2.0
        
        if not np.any(freq_mask):
            return
        
        # Add signal power (Gaussian shape in frequency domain)
        for i, freq in enumerate(frequency_axis):
            if freq_mask[i]:
                # Gaussian shape
                freq_offset = freq - center_frequency
                sigma = bandwidth_hz / 4.0  # Standard deviation
                gaussian_factor = math.exp(-0.5 * (freq_offset / sigma) ** 2)
                signal_power = power_dbm * gaussian_factor
                
                # Add to all time samples
                power_matrix[i, :] = np.maximum(
                    power_matrix[i, :],
                    signal_power
                )
    
    def simulate_normal_spectrum(self) -> SpectrumData:
        """
        Simulate normal spectrum (noise only).
        
        Returns:
            SpectrumData with normal noise floor
        """
        return self.simulate_spectrum(
            signal_frequencies=None,
            add_noise=True
        )
    
    def simulate_anomalous_spectrum(
        self,
        unknown_frequencies: List[float],
        elevated_noise: bool = False
    ) -> SpectrumData:
        """
        Simulate anomalous spectrum.
        
        Args:
            unknown_frequencies: Unknown signal frequencies
            elevated_noise: Whether to elevate noise floor
            
        Returns:
            SpectrumData with anomalous signals
        """
        noise_floor = self.noise_floor
        if elevated_noise:
            noise_floor += 10.0  # Elevate by 10 dB
        
        # Create temporary simulator with elevated noise
        temp_sim = SpectrumSimulator(
            frequency_range_hz=(self.freq_min, self.freq_max),
            frequency_resolution_hz=self.freq_resolution,
            time_duration_seconds=self.time_duration,
            sample_rate_hz=self.sample_rate,
            noise_floor_dbm=noise_floor
        )
        
        return temp_sim.simulate_spectrum(
            signal_frequencies=unknown_frequencies,
            signal_powers=[-70.0] * len(unknown_frequencies),  # Stronger signals
            add_noise=True
        )

