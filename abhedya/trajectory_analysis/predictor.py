"""
Trajectory Prediction Module

Predicts short-term future positions using classical mechanics:
- Constant velocity model
- Constant acceleration model

Uses configuration-driven limits for prediction horizon.
"""

import math
from datetime import datetime, timedelta
from typing import List, Optional

from abhedya.trajectory_analysis.models import (
    TrajectoryPrediction,
    MotionModel
)
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.infrastructure.config.config import (
    ProtectedAirspaceConfiguration,
    SystemPerformanceLimits
)


class TrajectoryPredictor:
    """
    Predicts short-term future positions using classical mechanics.
    
    Models:
    - Constant velocity: x(t) = x0 + v*t
    - Constant acceleration: x(t) = x0 + v0*t + 0.5*a*t²
    """
    
    def __init__(
        self,
        prediction_horizon_seconds: float = 60.0,
        time_step_seconds: float = 1.0,
        max_prediction_horizon: float = 300.0  # 5 minutes max
    ):
        """
        Initialize trajectory predictor.
        
        Args:
            prediction_horizon_seconds: Prediction horizon in seconds (default: 60s)
            time_step_seconds: Time step for predictions (default: 1s)
            max_prediction_horizon: Maximum allowed prediction horizon (default: 300s)
        """
        self.prediction_horizon = min(prediction_horizon_seconds, max_prediction_horizon)
        self.time_step = time_step_seconds
        self.max_horizon = max_prediction_horizon
    
    def predict_constant_velocity(
        self,
        position: Coordinates,
        velocity: Velocity,
        timestamp: Optional[datetime] = None
    ) -> TrajectoryPrediction:
        """
        Predict future positions using constant velocity model.
        
        Classical mechanics: x(t) = x0 + v*t
        
        Args:
            position: Current position
            velocity: Current velocity
            timestamp: Current timestamp (default: now)
            
        Returns:
            TrajectoryPrediction
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        predicted_positions = []
        time_steps = []
        
        current_time = 0.0
        while current_time <= self.prediction_horizon:
            # Constant velocity: x(t) = x0 + v*t
            predicted_x = position.x + velocity.vx * current_time
            predicted_y = position.y + velocity.vy * current_time
            predicted_z = position.z + velocity.vz * current_time
            
            predicted_positions.append(Coordinates(
                x=predicted_x,
                y=predicted_y,
                z=predicted_z
            ))
            
            time_steps.append(current_time)
            current_time += self.time_step
        
        # Calculate confidence (decreases with prediction horizon)
        confidence = 1.0 - (self.prediction_horizon / self.max_horizon) * 0.5
        
        # Calculate uncertainty (increases with time and speed)
        speed = velocity.speed
        uncertainty = min(1.0, (self.prediction_horizon / 100.0) * (speed / 500.0))
        
        return TrajectoryPrediction(
            current_position=position,
            current_velocity=velocity,
            predicted_positions=predicted_positions,
            time_steps=time_steps,
            motion_model=MotionModel.CONSTANT_VELOCITY,
            confidence=confidence,
            uncertainty=uncertainty,
            timestamp=timestamp
        )
    
    def predict_constant_acceleration(
        self,
        position: Coordinates,
        velocity: Velocity,
        acceleration: Optional[Velocity] = None,
        timestamp: Optional[datetime] = None
    ) -> TrajectoryPrediction:
        """
        Predict future positions using constant acceleration model.
        
        Classical mechanics: x(t) = x0 + v0*t + 0.5*a*t²
        
        Args:
            position: Current position
            velocity: Current velocity
            acceleration: Current acceleration (default: zero)
            timestamp: Current timestamp (default: now)
            
        Returns:
            TrajectoryPrediction
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if acceleration is None:
            acceleration = Velocity(vx=0.0, vy=0.0, vz=0.0)
        
        predicted_positions = []
        time_steps = []
        
        current_time = 0.0
        while current_time <= self.prediction_horizon:
            # Constant acceleration: x(t) = x0 + v0*t + 0.5*a*t²
            t = current_time
            t_squared = t * t
            
            predicted_x = position.x + velocity.vx * t + 0.5 * acceleration.vx * t_squared
            predicted_y = position.y + velocity.vy * t + 0.5 * acceleration.vy * t_squared
            predicted_z = position.z + velocity.vz * t + 0.5 * acceleration.vz * t_squared
            
            predicted_positions.append(Coordinates(
                x=predicted_x,
                y=predicted_y,
                z=predicted_z
            ))
            
            time_steps.append(current_time)
            current_time += self.time_step
        
        # Calculate confidence (lower than constant velocity due to acceleration uncertainty)
        confidence = (1.0 - (self.prediction_horizon / self.max_horizon) * 0.5) * 0.8
        
        # Calculate uncertainty (higher due to acceleration)
        speed = velocity.speed
        accel_magnitude = math.sqrt(
            acceleration.vx**2 + acceleration.vy**2 + acceleration.vz**2
        )
        uncertainty = min(1.0, (self.prediction_horizon / 100.0) * (speed / 500.0) + (accel_magnitude / 50.0))
        
        return TrajectoryPrediction(
            current_position=position,
            current_velocity=velocity,
            predicted_positions=predicted_positions,
            time_steps=time_steps,
            motion_model=MotionModel.CONSTANT_ACCELERATION,
            confidence=confidence,
            uncertainty=uncertainty,
            timestamp=timestamp
        )
    
    def predict(
        self,
        position: Coordinates,
        velocity: Velocity,
        acceleration: Optional[Velocity] = None,
        motion_model: MotionModel = MotionModel.CONSTANT_VELOCITY,
        timestamp: Optional[datetime] = None
    ) -> TrajectoryPrediction:
        """
        Predict future positions using specified motion model.
        
        Args:
            position: Current position
            velocity: Current velocity
            acceleration: Current acceleration (required for constant acceleration model)
            motion_model: Motion model to use
            timestamp: Current timestamp (default: now)
            
        Returns:
            TrajectoryPrediction
        """
        if motion_model == MotionModel.CONSTANT_VELOCITY:
            return self.predict_constant_velocity(position, velocity, timestamp)
        elif motion_model == MotionModel.CONSTANT_ACCELERATION:
            return self.predict_constant_acceleration(position, velocity, acceleration, timestamp)
        else:
            # Default to constant velocity
            return self.predict_constant_velocity(position, velocity, timestamp)
    
    def estimate_acceleration(
        self,
        previous_velocity: Velocity,
        current_velocity: Velocity,
        time_delta: float
    ) -> Velocity:
        """
        Estimate acceleration from velocity change.
        
        Classical mechanics: a = (v - v0) / t
        
        Args:
            previous_velocity: Previous velocity
            current_velocity: Current velocity
            time_delta: Time delta in seconds
            
        Returns:
            Estimated acceleration
        """
        if time_delta <= 0:
            return Velocity(vx=0.0, vy=0.0, vz=0.0)
        
        acceleration = Velocity(
            vx=(current_velocity.vx - previous_velocity.vx) / time_delta,
            vy=(current_velocity.vy - previous_velocity.vy) / time_delta,
            vz=(current_velocity.vz - previous_velocity.vz) / time_delta
        )
        
        return acceleration

