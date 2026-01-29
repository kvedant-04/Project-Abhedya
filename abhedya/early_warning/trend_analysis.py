"""
Trend Analysis Module

Detects slow-building or subtle anomalies using:
- Rolling mean and variance
- Exponentially Weighted Moving Average (EWMA)
- Cumulative Sum Control (CUSUM)
- Multi-track convergence detection

Uses classical statistical techniques only.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from statistics import mean, variance

from abhedya.early_warning.models import TrendAnalysisResult
from abhedya.tracking.models import Track
from abhedya.domain.value_objects import Coordinates


class TrendAnalyzer:
    """
    Analyzes trends to detect slow-building anomalies.
    
    Uses classical statistical techniques:
    - Rolling mean and variance
    - EWMA (Exponentially Weighted Moving Average)
    - CUSUM (Cumulative Sum Control)
    - Multi-track convergence detection
    """
    
    def __init__(
        self,
        rolling_window_size: int = 10,
        ewma_alpha: float = 0.3,
        cusum_threshold: float = 5.0,
        cusum_drift: float = 0.5
    ):
        """
        Initialize trend analyzer.
        
        Args:
            rolling_window_size: Window size for rolling statistics
            ewma_alpha: EWMA smoothing factor (0-1)
            cusum_threshold: CUSUM threshold for anomaly detection
            cusum_drift: CUSUM drift parameter
        """
        self.rolling_window = rolling_window_size
        self.ewma_alpha = ewma_alpha
        self.cusum_threshold = cusum_threshold
        self.cusum_drift = cusum_drift
        self.history: List[float] = []
    
    def analyze_trends(
        self,
        tracks: List[Track],
        baseline_mean: Optional[float] = None
    ) -> TrendAnalysisResult:
        """
        Analyze trends in track data.
        
        Args:
            tracks: Current tracks
            baseline_mean: Baseline mean value (optional)
            
        Returns:
            TrendAnalysisResult
        """
        # Extract metric (e.g., track count or average speed)
        current_metric = self._extract_metric(tracks)
        
        # Add to history
        self.history.append(current_metric)
        
        # Keep only recent history
        if len(self.history) > self.rolling_window * 2:
            self.history = self.history[-self.rolling_window * 2:]
        
        # Calculate rolling statistics
        rolling_mean, rolling_variance = self._calculate_rolling_statistics()
        
        # Calculate EWMA
        ewma_value = self._calculate_ewma(baseline_mean)
        
        # Calculate CUSUM
        cusum_value = self._calculate_cusum(baseline_mean)
        
        # Detect convergence
        convergence_detected = self._detect_convergence(tracks)
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(
            rolling_mean,
            rolling_variance,
            ewma_value,
            cusum_value,
            baseline_mean
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            rolling_mean,
            rolling_variance,
            ewma_value,
            cusum_value,
            convergence_detected,
            anomaly_score
        )
        
        return TrendAnalysisResult(
            rolling_mean=rolling_mean,
            rolling_variance=rolling_variance,
            ewma_value=ewma_value,
            cusum_value=cusum_value,
            convergence_detected=convergence_detected,
            anomaly_score=anomaly_score,
            reasoning=reasoning
        )
    
    def _extract_metric(self, tracks: List[Track]) -> float:
        """Extract metric value from tracks (e.g., track count)."""
        # Use track count as primary metric
        # In production, could use other metrics (average speed, density, etc.)
        return float(len(tracks))
    
    def _calculate_rolling_statistics(self) -> tuple[float, float]:
        """Calculate rolling mean and variance."""
        if len(self.history) < self.rolling_window:
            # Not enough data
            if len(self.history) > 0:
                return (mean(self.history), 0.0)
            return (0.0, 0.0)
        
        # Get rolling window
        window = self.history[-self.rolling_window:]
        
        rolling_mean = mean(window)
        
        if len(window) < 2:
            rolling_variance = 0.0
        else:
            rolling_variance = variance(window)
        
        return (rolling_mean, rolling_variance)
    
    def _calculate_ewma(self, baseline_mean: Optional[float]) -> float:
        """
        Calculate Exponentially Weighted Moving Average.
        
        EWMA: S_t = α * X_t + (1 - α) * S_{t-1}
        """
        if len(self.history) == 0:
            return 0.0
        
        current_value = self.history[-1]
        
        if len(self.history) == 1:
            # First value
            return current_value
        
        # Use previous EWMA value (simplified - would maintain state in production)
        # For now, calculate from history
        ewma = current_value
        for i in range(len(self.history) - 2, -1, -1):
            ewma = self.ewma_alpha * self.history[i] + (1 - self.ewma_alpha) * ewma
        
        return ewma
    
    def _calculate_cusum(
        self,
        baseline_mean: Optional[float]
    ) -> float:
        """
        Calculate Cumulative Sum Control (CUSUM).
        
        CUSUM detects shifts from baseline mean.
        """
        if len(self.history) < 2:
            return 0.0
        
        if baseline_mean is None:
            # Use mean of history as baseline
            baseline_mean = mean(self.history)
        
        # Calculate CUSUM
        cusum_positive = 0.0
        cusum_negative = 0.0
        
        for value in self.history:
            deviation = value - baseline_mean - self.cusum_drift
            cusum_positive = max(0.0, cusum_positive + deviation)
            
            deviation = baseline_mean - value - self.cusum_drift
            cusum_negative = max(0.0, cusum_negative + deviation)
        
        # Return maximum CUSUM
        return max(cusum_positive, cusum_negative)
    
    def _detect_convergence(self, tracks: List[Track]) -> bool:
        """
        Detect multi-track convergence (multiple tracks heading towards same point).
        
        Args:
            tracks: Current tracks
            
        Returns:
            True if convergence detected
        """
        if len(tracks) < 3:
            return False
        
        # Check if multiple tracks are heading towards similar points
        # Simplified: check if tracks are converging in position
        
        positions = [track.position for track in tracks if track.velocity]
        velocities = [track.velocity for track in tracks if track.velocity]
        
        if len(positions) < 3 or len(velocities) < 3:
            return False
        
        # Calculate convergence score
        # Tracks converging if their velocity vectors point towards each other
        convergence_count = 0
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                pos1 = positions[i]
                pos2 = positions[j]
                vel1 = velocities[i]
                vel2 = velocities[j]
                
                # Vector from pos1 to pos2
                dx = pos2.x - pos1.x
                dy = pos2.y - pos1.y
                dz = pos2.z - pos1.z
                distance = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if distance == 0:
                    continue
                
                # Unit vector from pos1 to pos2
                unit_x = dx / distance
                unit_y = dy / distance
                unit_z = dz / distance
                
                # Check if velocities point towards each other
                # vel1 should have positive component along unit vector
                # vel2 should have negative component
                vel1_component = vel1.vx * unit_x + vel1.vy * unit_y + vel1.vz * unit_z
                vel2_component = vel2.vx * (-unit_x) + vel2.vy * (-unit_y) + vel2.vz * (-unit_z)
                
                if vel1_component > 0 and vel2_component > 0:
                    convergence_count += 1
        
        # If more than 30% of pairs show convergence, consider it detected
        total_pairs = len(positions) * (len(positions) - 1) / 2
        convergence_ratio = convergence_count / total_pairs if total_pairs > 0 else 0.0
        
        return convergence_ratio > 0.3
    
    def _calculate_anomaly_score(
        self,
        rolling_mean: float,
        rolling_variance: float,
        ewma_value: float,
        cusum_value: float,
        baseline_mean: Optional[float]
    ) -> float:
        """Calculate overall anomaly score."""
        score = 0.0
        
        # EWMA deviation
        if baseline_mean is not None:
            ewma_deviation = abs(ewma_value - baseline_mean) / baseline_mean if baseline_mean > 0 else 0.0
            score += min(1.0, ewma_deviation) * 0.3
        else:
            # Use variance as indicator
            if rolling_variance > 0:
                score += min(1.0, rolling_variance / 100.0) * 0.2
        
        # CUSUM indicator
        if cusum_value > self.cusum_threshold:
            cusum_factor = min(1.0, (cusum_value - self.cusum_threshold) / self.cusum_threshold)
            score += cusum_factor * 0.5
        
        # Variance increase
        if rolling_variance > 0:
            # High variance indicates instability
            variance_factor = min(1.0, rolling_variance / 50.0)
            score += variance_factor * 0.2
        
        return min(1.0, score)
    
    def _generate_reasoning(
        self,
        rolling_mean: float,
        rolling_variance: float,
        ewma_value: float,
        cusum_value: float,
        convergence_detected: bool,
        anomaly_score: float
    ) -> List[str]:
        """Generate human-readable reasoning."""
        reasoning = []
        
        reasoning.append(f"Rolling Mean: {rolling_mean:.2f}")
        reasoning.append(f"Rolling Variance: {rolling_variance:.2f}")
        reasoning.append(f"EWMA Value: {ewma_value:.2f}")
        reasoning.append(f"CUSUM Value: {cusum_value:.2f}")
        
        if cusum_value > self.cusum_threshold:
            reasoning.append(f"CUSUM threshold exceeded: {cusum_value:.2f} > {self.cusum_threshold}")
        
        if convergence_detected:
            reasoning.append("Multi-track convergence detected")
        
        reasoning.append(f"Anomaly Score: {anomaly_score:.2%}")
        
        return reasoning

