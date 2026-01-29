"""
Geometry and Relative Motion Analysis

Mathematical analysis of relative motion and geometry.
No control laws, no guidance, no execution timelines.
"""

import math
from typing import Dict

from abhedya.interception_simulation.models import GeometryAnalysisResult
from abhedya.domain.value_objects import Coordinates, Velocity


class GeometryAnalyzer:
    """
    Analyzes relative motion and geometry between objects.
    
    Mathematical analysis only - no control laws or guidance.
    """
    
    def __init__(self):
        """Initialize geometry analyzer."""
        pass
    
    def analyze_relative_motion(
        self,
        defender_position: Coordinates,
        defender_velocity: Velocity,
        target_position: Coordinates,
        target_velocity: Velocity
    ) -> GeometryAnalysisResult:
        """
        Analyze relative motion and geometry.
        
        Mathematical analysis only - no control laws or guidance.
        
        Args:
            defender_position: Defender position
            defender_velocity: Defender velocity
            target_position: Target position
            target_velocity: Target velocity
            
        Returns:
            GeometryAnalysisResult
        """
        # Calculate relative position
        relative_position = Coordinates(
            x=target_position.x - defender_position.x,
            y=target_position.y - defender_position.y,
            z=target_position.z - defender_position.z
        )
        
        # Calculate relative velocity
        relative_velocity = Velocity(
            vx=target_velocity.vx - defender_velocity.vx,
            vy=target_velocity.vy - defender_velocity.vy,
            vz=target_velocity.vz - defender_velocity.vz
        )
        
        # Calculate range (distance)
        range_meters = math.sqrt(
            relative_position.x**2 +
            relative_position.y**2 +
            relative_position.z**2
        )
        
        # Calculate line of sight vector (unit vector)
        if range_meters > 0:
            los_x = relative_position.x / range_meters
            los_y = relative_position.y / range_meters
            los_z = relative_position.z / range_meters
        else:
            los_x = 0.0
            los_y = 0.0
            los_z = 0.0
        
        line_of_sight_vector = Coordinates(x=los_x, y=los_y, z=los_z)
        
        # Calculate closing velocity (component along line of sight)
        closing_velocity = (
            relative_velocity.vx * los_x +
            relative_velocity.vy * los_y +
            relative_velocity.vz * los_z
        )
        
        # Range rate (rate of change of range)
        range_rate = closing_velocity
        
        # Calculate bearing angle (horizontal)
        if range_meters > 0:
            horizontal_range = math.sqrt(relative_position.x**2 + relative_position.y**2)
            if horizontal_range > 0:
                bearing_rad = math.atan2(relative_position.y, relative_position.x)
                bearing_angle = math.degrees(bearing_rad)
            else:
                bearing_angle = 0.0
        else:
            bearing_angle = 0.0
        
        # Normalize bearing to [0, 360)
        if bearing_angle < 0:
            bearing_angle += 360.0
        
        # Calculate elevation angle
        if range_meters > 0:
            horizontal_range = math.sqrt(relative_position.x**2 + relative_position.y**2)
            if horizontal_range > 0:
                elevation_rad = math.atan2(relative_position.z, horizontal_range)
                elevation_angle = math.degrees(elevation_rad)
            else:
                elevation_angle = 90.0 if relative_position.z > 0 else -90.0
        else:
            elevation_angle = 0.0
        
        # Calculate relative speed
        relative_speed = math.sqrt(
            relative_velocity.vx**2 +
            relative_velocity.vy**2 +
            relative_velocity.vz**2
        )
        
        # Additional geometry parameters
        geometry_parameters = {
            "range_meters": range_meters,
            "horizontal_range_meters": math.sqrt(relative_position.x**2 + relative_position.y**2),
            "vertical_separation_meters": relative_position.z,
            "relative_speed_meters_per_second": relative_speed,
            "closing_velocity_meters_per_second": closing_velocity,
            "range_rate_meters_per_second": range_rate
        }
        
        return GeometryAnalysisResult(
            relative_position=relative_position,
            relative_velocity=relative_velocity,
            closing_velocity=closing_velocity,
            range_rate=range_rate,
            bearing_angle_degrees=bearing_angle,
            elevation_angle_degrees=elevation_angle,
            line_of_sight_vector=line_of_sight_vector,
            relative_speed=relative_speed,
            geometry_parameters=geometry_parameters
        )
    
    def calculate_time_to_closest_approach(
        self,
        relative_position: Coordinates,
        relative_velocity: Velocity
    ) -> float:
        """
        Calculate time to closest approach.
        
        Mathematical calculation only - no execution timelines.
        
        Uses: t = -r · v / |v|²
        
        Args:
            relative_position: Relative position vector
            relative_velocity: Relative velocity vector
            
        Returns:
            Time to closest approach in seconds (negative if past closest approach)
        """
        # Calculate relative speed squared
        v_squared = (
            relative_velocity.vx**2 +
            relative_velocity.vy**2 +
            relative_velocity.vz**2
        )
        
        if v_squared == 0:
            # No relative motion, already at closest approach
            return 0.0
        
        # Calculate dot product r · v
        r_dot_v = (
            relative_position.x * relative_velocity.vx +
            relative_position.y * relative_velocity.vy +
            relative_position.z * relative_velocity.vz
        )
        
        # Time to closest approach: t = -r · v / |v|²
        time_to_ca = -r_dot_v / v_squared
        
        return time_to_ca
    
    def calculate_closest_approach_distance(
        self,
        relative_position: Coordinates,
        relative_velocity: Velocity,
        time_to_closest_approach: float
    ) -> float:
        """
        Calculate closest approach distance.
        
        Mathematical calculation only.
        
        Args:
            relative_position: Current relative position
            relative_velocity: Relative velocity
            time_to_closest_approach: Time to closest approach
            
        Returns:
            Closest approach distance in meters
        """
        # Position at closest approach: r_ca = r + v * t_ca
        ca_x = relative_position.x + relative_velocity.vx * time_to_closest_approach
        ca_y = relative_position.y + relative_velocity.vy * time_to_closest_approach
        ca_z = relative_position.z + relative_velocity.vz * time_to_closest_approach
        
        # Distance at closest approach
        distance = math.sqrt(ca_x**2 + ca_y**2 + ca_z**2)
        
        return distance
    
    def calculate_closest_approach_position(
        self,
        defender_position: Coordinates,
        relative_position: Coordinates,
        relative_velocity: Velocity,
        time_to_closest_approach: float
    ) -> Coordinates:
        """
        Calculate position at closest approach.
        
        Mathematical calculation only.
        
        Args:
            defender_position: Defender position
            relative_position: Current relative position
            relative_velocity: Relative velocity
            time_to_closest_approach: Time to closest approach
            
        Returns:
            Target position at closest approach
        """
        # Relative position at closest approach
        ca_relative_x = relative_position.x + relative_velocity.vx * time_to_closest_approach
        ca_relative_y = relative_position.y + relative_velocity.vy * time_to_closest_approach
        ca_relative_z = relative_position.z + relative_velocity.vz * time_to_closest_approach
        
        # Target position at closest approach
        ca_target_x = defender_position.x + ca_relative_x
        ca_target_y = defender_position.y + ca_relative_y
        ca_target_z = defender_position.z + ca_relative_z
        
        return Coordinates(
            x=ca_target_x,
            y=ca_target_y,
            z=ca_target_z
        )

