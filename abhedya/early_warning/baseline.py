"""
Baseline Statistics Module

Establishes statistical baselines for airspace behavior:
- Track density
- Velocity distributions
- Trajectory deviation patterns
- Confidence decay over time

Uses classical statistical techniques only.
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from statistics import mean, stdev

from abhedya.early_warning.models import BaselineStatistics
from abhedya.tracking.models import Track
from abhedya.domain.value_objects import Velocity


class BaselineAnalyzer:
    """
    Analyzes and establishes statistical baselines for airspace behavior.
    
    Uses classical statistical techniques to establish normal behavior patterns.
    """
    
    def __init__(
        self,
        minimum_samples_for_baseline: int = 10,
        baseline_update_window: int = 100
    ):
        """
        Initialize baseline analyzer.
        
        Args:
            minimum_samples_for_baseline: Minimum samples to establish baseline
            baseline_update_window: Window size for baseline updates
        """
        self.minimum_samples = minimum_samples_for_baseline
        self.update_window = baseline_update_window
        self.baseline_history: List[BaselineStatistics] = []
    
    def establish_baseline(
        self,
        tracks: List[Track],
        historical_tracks: Optional[List[List[Track]]] = None
    ) -> Optional[BaselineStatistics]:
        """
        Establish statistical baseline from tracks.
        
        FAIL-SAFE: If insufficient data, returns None (defaults to MONITORING_ONLY).
        
        Args:
            tracks: Current tracks
            historical_tracks: Historical track data (optional)
            
        Returns:
            BaselineStatistics or None if insufficient data
        """
        # Combine current and historical tracks
        all_tracks = tracks.copy()
        if historical_tracks:
            for track_list in historical_tracks:
                all_tracks.extend(track_list)
        
        # Check if sufficient data
        if len(all_tracks) < self.minimum_samples:
            return None  # Insufficient data - fail-safe
        
        # Calculate track density (tracks per unit area)
        track_density = self._calculate_track_density(all_tracks)
        
        # Calculate velocity distribution
        velocity_stats = self._calculate_velocity_distribution(all_tracks)
        
        # Calculate trajectory deviation
        trajectory_stats = self._calculate_trajectory_deviation(all_tracks)
        
        # Calculate confidence decay rate
        confidence_decay = self._calculate_confidence_decay(all_tracks)
        
        baseline = BaselineStatistics(
            track_density_mean=track_density["mean"],
            track_density_std=track_density["std"],
            velocity_mean=velocity_stats["mean"],
            velocity_std=velocity_stats["std"],
            trajectory_deviation_mean=trajectory_stats["mean"],
            trajectory_deviation_std=trajectory_stats["std"],
            confidence_decay_rate=confidence_decay,
            sample_count=len(all_tracks),
            established_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.baseline_history.append(baseline)
        
        # Keep only recent history
        if len(self.baseline_history) > self.update_window:
            self.baseline_history = self.baseline_history[-self.update_window:]
        
        return baseline
    
    def update_baseline(
        self,
        baseline: BaselineStatistics,
        new_tracks: List[Track]
    ) -> Optional[BaselineStatistics]:
        """
        Update existing baseline with new tracks.
        
        Args:
            baseline: Existing baseline
            new_tracks: New tracks to incorporate
            
        Returns:
            Updated BaselineStatistics or None if insufficient data
        """
        # Combine with existing baseline data
        # For simplicity, recalculate from history + new tracks
        # In production, would use incremental update algorithms
        
        if len(new_tracks) < 1:
            return baseline  # No new data
        
        # Re-establish baseline (would be optimized in production)
        return self.establish_baseline(new_tracks)
    
    def _calculate_track_density(
        self,
        tracks: List[Track]
    ) -> Dict[str, float]:
        """Calculate track density statistics."""
        if len(tracks) == 0:
            return {"mean": 0.0, "std": 0.0}
        
        # Simplified: tracks per unit time
        # In production, would calculate spatial density
        track_counts = [1.0] * len(tracks)  # Simplified
        
        if len(track_counts) < 2:
            return {"mean": float(len(tracks)), "std": 0.0}
        
        return {
            "mean": mean(track_counts),
            "std": stdev(track_counts) if len(track_counts) > 1 else 0.0
        }
    
    def _calculate_velocity_distribution(
        self,
        tracks: List[Track]
    ) -> Dict[str, float]:
        """Calculate velocity distribution statistics."""
        velocities = []
        
        for track in tracks:
            if track.velocity:
                speed = track.velocity.speed
                velocities.append(speed)
        
        if len(velocities) == 0:
            return {"mean": 0.0, "std": 0.0}
        
        if len(velocities) < 2:
            return {"mean": velocities[0], "std": 0.0}
        
        return {
            "mean": mean(velocities),
            "std": stdev(velocities)
        }
    
    def _calculate_trajectory_deviation(
        self,
        tracks: List[Track]
    ) -> Dict[str, float]:
        """Calculate trajectory deviation patterns."""
        deviations = []
        
        for track in tracks:
            if len(track.metadata.get("sensor_readings", [])) < 2:
                continue
            
            # Calculate trajectory deviation (simplified)
            # In production, would use more sophisticated trajectory analysis
            readings = track.metadata.get("sensor_readings", [])
            if len(readings) >= 2:
                # Simple deviation measure
                deviation = 0.0
                for i in range(1, len(readings)):
                    prev_pos = readings[i-1].position
                    curr_pos = readings[i].position
                    dx = curr_pos.x - prev_pos.x
                    dy = curr_pos.y - prev_pos.y
                    dz = curr_pos.z - prev_pos.z
                    distance = math.sqrt(dx**2 + dy**2 + dz**2)
                    deviation += distance
                
                if len(readings) > 1:
                    deviation = deviation / (len(readings) - 1)
                    deviations.append(deviation)
        
        if len(deviations) == 0:
            return {"mean": 0.0, "std": 0.0}
        
        if len(deviations) < 2:
            return {"mean": deviations[0], "std": 0.0}
        
        return {
            "mean": mean(deviations),
            "std": stdev(deviations)
        }
    
    def _calculate_confidence_decay(
        self,
        tracks: List[Track]
    ) -> float:
        """Calculate confidence decay rate over time."""
        if len(tracks) < 2:
            return 0.0
        
        decay_rates = []
        
        for track in tracks:
            age = track.get_age_seconds()
            if age > 0:
                # Calculate decay rate: (initial_confidence - current_confidence) / age
                # Simplified: assume initial confidence was 1.0
                initial_confidence = 1.0
                current_confidence = track.confidence
                decay_rate = (initial_confidence - current_confidence) / age
                decay_rates.append(max(0.0, decay_rate))
        
        if len(decay_rates) == 0:
            return 0.0
        
        return mean(decay_rates)
    
    def compare_to_baseline(
        self,
        baseline: BaselineStatistics,
        current_tracks: List[Track]
    ) -> Dict[str, Any]:
        """
        Compare current tracks to baseline.
        
        Returns:
            Dictionary with comparison metrics
        """
        if len(current_tracks) == 0:
            return {
                "track_density_deviation": 0.0,
                "velocity_deviation": 0.0,
                "trajectory_deviation": 0.0,
                "is_anomalous": False
            }
        
        # Calculate current statistics
        current_density = self._calculate_track_density(current_tracks)
        current_velocity = self._calculate_velocity_distribution(current_tracks)
        current_trajectory = self._calculate_trajectory_deviation(current_tracks)
        
        # Calculate deviations (Z-scores)
        density_zscore = 0.0
        if baseline.track_density_std > 0:
            density_zscore = abs(
                (current_density["mean"] - baseline.track_density_mean) /
                baseline.track_density_std
            )
        
        velocity_zscore = 0.0
        if baseline.velocity_std > 0:
            velocity_zscore = abs(
                (current_velocity["mean"] - baseline.velocity_mean) /
                baseline.velocity_std
            )
        
        trajectory_zscore = 0.0
        if baseline.trajectory_deviation_std > 0:
            trajectory_zscore = abs(
                (current_trajectory["mean"] - baseline.trajectory_deviation_mean) /
                baseline.trajectory_deviation_std
            )
        
        # Determine if anomalous (Z-score > 2.0)
        is_anomalous = (
            density_zscore > 2.0 or
            velocity_zscore > 2.0 or
            trajectory_zscore > 2.0
        )
        
        return {
            "track_density_deviation": density_zscore,
            "velocity_deviation": velocity_zscore,
            "trajectory_deviation": trajectory_zscore,
            "is_anomalous": is_anomalous,
            "anomaly_score": max(density_zscore, velocity_zscore, trajectory_zscore) / 3.0
        }

