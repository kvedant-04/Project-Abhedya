"""
Kalman Filter for State Estimation

Classical Kalman filter implementation for tracking position and velocity.
Uses explainable mathematical logic only.
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

from abhedya.domain.value_objects import Coordinates, Velocity


@dataclass
class KalmanState:
    """
    Kalman filter state.
    
    State vector: [x, y, z, vx, vy, vz]
    """
    position: Coordinates
    velocity: Velocity
    covariance: np.ndarray  # 6x6 covariance matrix
    timestamp: float  # Timestamp for state
    
    def __post_init__(self):
        """Initialize covariance if not provided."""
        if self.covariance is None or self.covariance.size == 0:
            # Initialize with large uncertainty
            self.covariance = np.eye(6) * 1000.0


class KalmanFilter:
    """
    Kalman filter for state estimation in tracking.
    
    Uses classical Kalman filter equations:
    - Prediction step: x_k|k-1 = F * x_k-1|k-1
    - Update step: x_k|k = x_k|k-1 + K * (z_k - H * x_k|k-1)
    
    State vector: [x, y, z, vx, vy, vz]
    """
    
    def __init__(
        self,
        process_noise: float = 1.0,
        measurement_noise: float = 10.0,
        initial_uncertainty: float = 100.0
    ):
        """
        Initialize Kalman filter.
        
        Args:
            process_noise: Process noise covariance (Q)
            measurement_noise: Measurement noise covariance (R)
            initial_uncertainty: Initial state uncertainty
        """
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.initial_uncertainty = initial_uncertainty
        
        # State transition matrix F (constant velocity model)
        # x' = x + vx*dt, y' = y + vy*dt, z' = z + vz*dt
        # vx' = vx, vy' = vy, vz' = vz
        self.F = np.eye(6)
        
        # Measurement matrix H (we measure position only)
        # z = [x, y, z] = H * [x, y, z, vx, vy, vz]
        self.H = np.array([
            [1, 0, 0, 0, 0, 0],  # x measurement
            [0, 1, 0, 0, 0, 0],  # y measurement
            [0, 0, 1, 0, 0, 0],  # z measurement
        ])
        
        # Process noise covariance Q
        self.Q = np.eye(6) * process_noise
        
        # Measurement noise covariance R
        self.R = np.eye(3) * measurement_noise
    
    def initialize(
        self,
        position: Coordinates,
        velocity: Optional[Velocity] = None,
        timestamp: float = 0.0
    ) -> KalmanState:
        """
        Initialize Kalman filter state.
        
        Args:
            position: Initial position
            velocity: Initial velocity (default: zero)
            timestamp: Initial timestamp
            
        Returns:
            Initialized Kalman state
        """
        if velocity is None:
            velocity = Velocity(vx=0.0, vy=0.0, vz=0.0)
        
        # Initial state vector
        state_vector = np.array([
            position.x,
            position.y,
            position.z,
            velocity.vx,
            velocity.vy,
            velocity.vz
        ])
        
        # Initial covariance (large uncertainty)
        covariance = np.eye(6) * self.initial_uncertainty
        
        return KalmanState(
            position=position,
            velocity=velocity,
            covariance=covariance,
            timestamp=timestamp
        )
    
    def predict(
        self,
        state: KalmanState,
        dt: float
    ) -> KalmanState:
        """
        Predict next state (prediction step).
        
        Args:
            state: Current state
            dt: Time step in seconds
            
        Returns:
            Predicted state
        """
        # Update state transition matrix with time step
        F = self.F.copy()
        F[0, 3] = dt  # x += vx * dt
        F[1, 4] = dt  # y += vy * dt
        F[2, 5] = dt  # z += vz * dt
        
        # State vector
        x = np.array([
            state.position.x,
            state.position.y,
            state.position.z,
            state.velocity.vx,
            state.velocity.vy,
            state.velocity.vz
        ])
        
        # Predict state: x_k|k-1 = F * x_k-1|k-1
        x_pred = F @ x
        
        # Predict covariance: P_k|k-1 = F * P_k-1|k-1 * F^T + Q
        P_pred = F @ state.covariance @ F.T + self.Q
        
        # Create predicted state
        predicted_position = Coordinates(
            x=float(x_pred[0]),
            y=float(x_pred[1]),
            z=float(x_pred[2])
        )
        predicted_velocity = Velocity(
            vx=float(x_pred[3]),
            vy=float(x_pred[4]),
            vz=float(x_pred[5])
        )
        
        return KalmanState(
            position=predicted_position,
            velocity=predicted_velocity,
            covariance=P_pred,
            timestamp=state.timestamp + dt
        )
    
    def update(
        self,
        state: KalmanState,
        measurement: Coordinates,
        measurement_uncertainty: Optional[float] = None
    ) -> KalmanState:
        """
        Update state with measurement (update step).
        
        Args:
            state: Predicted state
            measurement: Position measurement
            measurement_uncertainty: Measurement uncertainty (optional)
            
        Returns:
            Updated state
        """
        # Measurement vector
        z = np.array([measurement.x, measurement.y, measurement.z])
        
        # State vector
        x = np.array([
            state.position.x,
            state.position.y,
            state.position.z,
            state.velocity.vx,
            state.velocity.vy,
            state.velocity.vz
        ])
        
        # Measurement noise (use provided or default)
        R = self.R.copy()
        if measurement_uncertainty is not None:
            R = np.eye(3) * measurement_uncertainty
        
        # Innovation: y = z - H * x
        y = z - self.H @ x
        
        # Innovation covariance: S = H * P * H^T + R
        S = self.H @ state.covariance @ self.H.T + R
        
        # Kalman gain: K = P * H^T * S^-1
        try:
            K = state.covariance @ self.H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            # If inversion fails, use identity gain (no update)
            K = np.zeros((6, 3))
        
        # Update state: x_k|k = x_k|k-1 + K * y
        x_updated = x + K @ y
        
        # Update covariance: P_k|k = (I - K * H) * P_k|k-1
        I = np.eye(6)
        P_updated = (I - K @ self.H) @ state.covariance
        
        # Ensure covariance is positive semi-definite
        P_updated = (P_updated + P_updated.T) / 2
        
        # Create updated state
        updated_position = Coordinates(
            x=float(x_updated[0]),
            y=float(x_updated[1]),
            z=float(x_updated[2])
        )
        updated_velocity = Velocity(
            vx=float(x_updated[3]),
            vy=float(x_updated[4]),
            vz=float(x_updated[5])
        )
        
        return KalmanState(
            position=updated_position,
            velocity=updated_velocity,
            covariance=P_updated,
            timestamp=state.timestamp
        )
    
    def predict_and_update(
        self,
        state: KalmanState,
        measurement: Coordinates,
        dt: float,
        measurement_uncertainty: Optional[float] = None
    ) -> KalmanState:
        """
        Predict and update in one step.
        
        Args:
            state: Current state
            measurement: New measurement
            dt: Time step
            measurement_uncertainty: Measurement uncertainty (optional)
            
        Returns:
            Updated state
        """
        # Predict
        predicted = self.predict(state, dt)
        
        # Update
        updated = self.update(predicted, measurement, measurement_uncertainty)
        
        return updated
    
    def get_position_uncertainty(self, state: KalmanState) -> float:
        """
        Get position uncertainty from covariance matrix.
        
        Args:
            state: Kalman state
            
        Returns:
            Position uncertainty (standard deviation in meters)
        """
        # Position uncertainty is diagonal of covariance matrix (x, y, z)
        position_cov = state.covariance[:3, :3]
        
        # Calculate average standard deviation
        variances = np.diag(position_cov)
        avg_variance = np.mean(variances)
        
        return float(np.sqrt(avg_variance))
    
    def get_velocity_uncertainty(self, state: KalmanState) -> float:
        """
        Get velocity uncertainty from covariance matrix.
        
        Args:
            state: Kalman state
            
        Returns:
            Velocity uncertainty (standard deviation in m/s)
        """
        # Velocity uncertainty is diagonal of covariance matrix (vx, vy, vz)
        velocity_cov = state.covariance[3:6, 3:6]
        
        # Calculate average standard deviation
        variances = np.diag(velocity_cov)
        avg_variance = np.mean(variances)
        
        return float(np.sqrt(avg_variance))

