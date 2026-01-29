"""
Physics Validation Module

Validates motion using classical physics constraints:
- Maximum acceleration limits
- Maximum speed limits
- Velocity change validation
- Position change validation

Uses configuration-driven limits.
"""

import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from abhedya.trajectory_analysis.models import (
    PhysicsValidationResult,
    PhysicsViolationType
)
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.infrastructure.config.config import (
    ThreatAssessmentThresholds,
    SystemPerformanceLimits
)


class PhysicsValidator:
    """
    Validates motion using classical physics constraints.
    
    Checks:
    - Maximum acceleration (typical aircraft: ~50 m/s², extreme: ~100 m/s²)
    - Maximum speed (typical aircraft: ~400 m/s, extreme: ~1000 m/s)
    - Velocity change consistency
    - Position change consistency
    """
    
    def __init__(
        self,
        max_acceleration_meters_per_second_squared: float = 100.0,
        max_speed_meters_per_second: float = 1000.0,
        max_velocity_change_meters_per_second: float = 200.0
    ):
        """
        Initialize physics validator.
        
        Args:
            max_acceleration_meters_per_second_squared: Maximum allowed acceleration
            max_speed_meters_per_second: Maximum allowed speed
            max_velocity_change_meters_per_second: Maximum allowed velocity change per second
        """
        self.max_acceleration = max_acceleration_meters_per_second_squared
        self.max_speed = max_speed_meters_per_second
        self.max_velocity_change = max_velocity_change_meters_per_second
    
    def validate_motion(
        self,
        positions: List[Coordinates],
        velocities: List[Velocity],
        timestamps: Optional[List[float]] = None
    ) -> PhysicsValidationResult:
        """
        Validate motion sequence using physics constraints.
        
        Args:
            positions: List of positions
            velocities: List of velocities
            timestamps: List of timestamps in seconds (default: 1s intervals)
            
        Returns:
            PhysicsValidationResult
        """
        violations = []
        accelerations = []
        speeds = []
        
        if len(positions) < 2 or len(velocities) < 2:
            return PhysicsValidationResult(
                is_valid=True,
                violations=[],
                max_acceleration=0.0,
                max_speed=0.0,
                average_acceleration=0.0,
                reasoning="Insufficient data for validation"
            )
        
        # Use provided timestamps or assume 1s intervals
        if timestamps is None:
            timestamps = [float(i) for i in range(len(positions))]
        
        # Check speeds
        for velocity in velocities:
            speed = velocity.speed
            speeds.append(speed)
            if speed > self.max_speed:
                violations.append(PhysicsViolationType.EXCESSIVE_SPEED)
        
        # Check accelerations and velocity changes
        for i in range(1, len(velocities)):
            prev_vel = velocities[i-1]
            curr_vel = velocities[i]
            
            # Calculate velocity change
            dvx = curr_vel.vx - prev_vel.vx
            dvy = curr_vel.vy - prev_vel.vy
            dvz = curr_vel.vz - prev_vel.vz
            velocity_change = math.sqrt(dvx**2 + dvy**2 + dvz**2)
            
            # Calculate time delta
            dt = timestamps[i] - timestamps[i-1]
            if dt <= 0:
                dt = 1.0  # Default to 1 second
            
            # Calculate acceleration
            acceleration = velocity_change / dt
            accelerations.append(acceleration)
            
            # Check acceleration limit
            if acceleration > self.max_acceleration:
                violations.append(PhysicsViolationType.EXCESSIVE_ACCELERATION)
            
            # Check velocity change limit
            if velocity_change > self.max_velocity_change:
                violations.append(PhysicsViolationType.IMPOSSIBLE_VELOCITY_CHANGE)
        
        # Check position changes
        for i in range(1, len(positions)):
            prev_pos = positions[i-1]
            curr_pos = positions[i]
            
            # Calculate position change
            dx = curr_pos.x - prev_pos.x
            dy = curr_pos.y - prev_pos.y
            dz = curr_pos.z - prev_pos.z
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            
            # Calculate time delta
            dt = timestamps[i] - timestamps[i-1]
            if dt <= 0:
                dt = 1.0
            
            # Calculate required speed for this position change
            required_speed = distance / dt
            
            # Check if required speed exceeds maximum
            if required_speed > self.max_speed:
                violations.append(PhysicsViolationType.IMPOSSIBLE_POSITION_CHANGE)
        
        # Calculate statistics
        max_accel = max(accelerations) if accelerations else 0.0
        max_speed_val = max(speeds) if speeds else 0.0
        avg_accel = sum(accelerations) / len(accelerations) if accelerations else 0.0
        
        # Determine validity
        is_valid = len(violations) == 0
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            violations,
            max_accel,
            max_speed_val,
            avg_accel
        )
        
        return PhysicsValidationResult(
            is_valid=is_valid,
            violations=list(set(violations)),  # Remove duplicates
            max_acceleration=max_accel,
            max_speed=max_speed_val,
            average_acceleration=avg_accel,
            reasoning=reasoning
        )
    
    def validate_single_step(
        self,
        previous_position: Coordinates,
        current_position: Coordinates,
        previous_velocity: Velocity,
        current_velocity: Velocity,
        time_delta: float
    ) -> PhysicsValidationResult:
        """
        Validate a single motion step.
        
        Args:
            previous_position: Previous position
            current_position: Current position
            previous_velocity: Previous velocity
            current_velocity: Current velocity
            time_delta: Time delta in seconds
            
        Returns:
            PhysicsValidationResult
        """
        return self.validate_motion(
            positions=[previous_position, current_position],
            velocities=[previous_velocity, current_velocity],
            timestamps=[0.0, time_delta]
        )
    
    def _generate_reasoning(
        self,
        violations: List[PhysicsViolationType],
        max_accel: float,
        max_speed: float,
        avg_accel: float
    ) -> str:
        """Generate human-readable reasoning for validation."""
        reasoning_parts = []
        
        if len(violations) == 0:
            reasoning_parts.append("Motion is physically valid.")
        else:
            reasoning_parts.append(f"Motion violations detected: {len(violations)}")
            for violation in violations:
                reasoning_parts.append(f"  - {violation.value}")
        
        reasoning_parts.append("")
        reasoning_parts.append("Statistics:")
        reasoning_parts.append(f"  - Maximum acceleration: {max_accel:.2f} m/s²")
        reasoning_parts.append(f"  - Maximum speed: {max_speed:.2f} m/s")
        reasoning_parts.append(f"  - Average acceleration: {avg_accel:.2f} m/s²")
        reasoning_parts.append("")
        reasoning_parts.append(f"Limits:")
        reasoning_parts.append(f"  - Maximum acceleration: {self.max_acceleration} m/s²")
        reasoning_parts.append(f"  - Maximum speed: {self.max_speed} m/s")
        
        return "\n".join(reasoning_parts)

