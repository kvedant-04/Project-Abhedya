"""
Trajectory Visualization Helpers

Provides FlightRadar-style trajectory visualization layers:
- Past track trail (fade with age)
- Current velocity vector (arrow)
- Predicted trajectory cone (uncertainty fan)

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import streamlit as st


class TrajectoryVisualization:
    """
    Trajectory visualization helpers for radar/battlespace view.
    
    ADVISORY ONLY - Provides visual layers only, no control logic.
    """
    
    @staticmethod
    def add_trajectory_trail(
        fig: go.Figure,
        track_id: str,
        history: List[Dict[str, Any]],
        color: str = '#4A90E2',
        max_trail_points: int = 60,
        max_trail_age_seconds: float = 120.0
    ) -> None:
        """
        Add trajectory history trail behind moving targets.
        
        Features:
        - Thin lines behind moving targets
        - Color-coded by classification
        - Fixed-length trail window (max_trail_points)
        - Gradual fade opacity (older points fade more)
        
        Supports:
        - Trajectory explanation
        - Interception geometry understanding
        - Training demonstrations
        
        Args:
            fig: Plotly figure
            track_id: Track identifier
            history: List of historical points with timestamp, x, y, altitude
            color: Base color for trail (derived from track classification)
            max_trail_points: Maximum number of trail points to display (fixed-length window)
            max_trail_age_seconds: Maximum age of trail points in seconds
        """
        try:
            if not history or len(history) < 2:
                return
            
            current_time = datetime.now()
            
            # Filter and sort history by timestamp (oldest first)
            # Apply fixed-length window and age limit
            filtered_history = []
            for point in history:
                timestamp = point.get('timestamp')
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except Exception:
                        timestamp = current_time
                elif not isinstance(timestamp, datetime):
                    timestamp = current_time
                
                age_seconds = (current_time - timestamp).total_seconds()
                if age_seconds <= max_trail_age_seconds:
                    filtered_history.append((timestamp, point, age_seconds))
            
            # Sort by timestamp (oldest first)
            filtered_history.sort(key=lambda x: x[0])
            
            # Apply fixed-length window (keep most recent max_trail_points)
            if len(filtered_history) > max_trail_points:
                filtered_history = filtered_history[-max_trail_points:]
            
            if len(filtered_history) < 2:
                return
            
            # Extract coordinates and ages
            trail_x = []
            trail_y = []
            trail_ages = []
            
            for timestamp, point, age_seconds in filtered_history:
                trail_ages.append(age_seconds)
                trail_x.append(float(point.get('x', 0.0)))
                trail_y.append(float(point.get('y', 0.0)))
            
            # Extract RGB from color (color-coded by classification)
            if color.startswith('#'):
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                except Exception:
                    r, g, b = 74, 144, 226  # Default blue
            else:
                r, g, b = 74, 144, 226  # Default blue
            
            # Create trail segments with gradual fade opacity
            # Older points fade more (opacity decreases with age)
            max_age = max(trail_ages) if trail_ages else 1.0
            
            for i in range(len(trail_x) - 1):
                # Calculate opacity based on age (gradual fade)
                # Newest point: opacity ~0.6, oldest point: opacity ~0.1
                age_normalized = trail_ages[i] / max_age if max_age > 0 else 0.0
                opacity = max(0.1, 0.6 * (1.0 - age_normalized))  # Fade from 0.6 to 0.1
                
                # Thin line (width 1.0 for subtle trail)
                fig.add_trace(go.Scatter(
                    x=[trail_x[i], trail_x[i + 1]],
                    y=[trail_y[i], trail_y[i + 1]],
                    mode='lines',
                    line=dict(
                        color=f'rgba({r}, {g}, {b}, {opacity})',
                        width=1.0,  # Thin line
                        dash='dot'  # Dashed for subtle appearance
                    ),
                    name=f'Trail {track_id}',
                    showlegend=False,
                    hoverinfo='skip'
                ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def add_velocity_vector(
        fig: go.Figure,
        x: float,
        y: float,
        vx: float,
        vy: float,
        speed_scale: float = 1.0,
        color: str = 'rgba(74, 144, 226, 0.6)'
    ) -> None:
        """
        Add current velocity vector arrow.
        
        Args:
            fig: Plotly figure
            x: Current X position
            y: Current Y position
            vx: Velocity X component (m/s)
            vy: Velocity Y component (m/s)
            speed_scale: Scale factor for arrow length (meters per pixel)
            color: Arrow color (subtle opacity)
        """
        try:
            speed = math.sqrt(vx**2 + vy**2)
            if speed < 0.1:  # Too slow to show
                return
            
            # Scale arrow length (e.g., 1 second of travel)
            arrow_length = speed * 1.0  # 1 second projection
            arrow_length = min(arrow_length, 10000.0)  # Cap at 10km
            
            # Calculate arrow endpoint
            end_x = x + (vx / speed) * arrow_length
            end_y = y + (vy / speed) * arrow_length
            
            # Add arrow line
            fig.add_trace(go.Scatter(
                x=[x, end_x],
                y=[y, end_y],
                mode='lines',
                line=dict(color=color, width=2),
                name='Velocity Vector',
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Add arrowhead (small triangle)
            arrow_angle = math.atan2(vy, vx)
            arrowhead_size = min(arrow_length * 0.1, 500.0)
            arrowhead_angle = math.pi / 6  # 30 degrees
            
            arrowhead_x = [
                end_x,
                end_x - arrowhead_size * math.cos(arrow_angle - arrowhead_angle),
                end_x - arrowhead_size * math.cos(arrow_angle + arrowhead_angle),
                end_x
            ]
            arrowhead_y = [
                end_y,
                end_y - arrowhead_size * math.sin(arrow_angle - arrowhead_angle),
                end_y - arrowhead_size * math.sin(arrow_angle + arrowhead_angle),
                end_y
            ]
            
            fig.add_trace(go.Scatter(
                x=arrowhead_x,
                y=arrowhead_y,
                mode='lines',
                fill='toself',
                fillcolor=color,
                line=dict(color=color, width=1),
                name='Velocity Arrowhead',
                showlegend=False,
                hoverinfo='skip'
            ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def add_prediction_cone(
        fig: go.Figure,
        x0: float,
        y0: float,
        vx: float,
        vy: float,
        prediction_horizon: float = 20.0,
        uncertainty_angle: float = 15.0,
        confidence: float = 0.5,
        color: str = 'rgba(250, 173, 20, 0.2)',
        atmospheric_conditions: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add predicted trajectory cone (uncertainty fan).
        
        ADVISORY ONLY — Visual uncertainty envelope only, NOT predictive logic.
        
        Args:
            fig: Plotly figure
            x0: Starting X position
            y0: Starting Y position
            vx: Velocity X component (m/s)
            vy: Velocity Y component (m/s)
            prediction_horizon: Prediction time horizon (seconds, 10-30s)
            uncertainty_angle: Uncertainty spread angle (degrees)
            confidence: Prediction confidence (0.0-1.0, affects cone width)
            color: Cone fill color (semi-transparent)
            atmospheric_conditions: Optional atmospheric conditions dict (affects visual uncertainty only)
        """
        try:
            speed = math.sqrt(vx**2 + vy**2)
            if speed < 0.1:
                return
            
            # Clamp prediction horizon to 10-30 seconds
            prediction_horizon = max(10.0, min(30.0, float(prediction_horizon)))
            
            # Apply atmospheric uncertainty expansion (visual only)
            uncertainty_expansion = 1.0
            if atmospheric_conditions:
                try:
                    from abhedya.dashboard.atmospheric_modeling import AtmosphericModel
                    stability = atmospheric_conditions.get("stability")
                    wind_speed_ms = atmospheric_conditions.get("wind_speed_ms", 0.0)
                    uncertainty_expansion = AtmosphericModel.get_trajectory_uncertainty_factor(
                        stability, wind_speed_ms
                    )
                except Exception:
                    pass  # Fail-safe: use default expansion
            
            # Uncertainty angle scales with (1 - confidence) and atmospheric expansion
            uncertainty_rad = math.radians(uncertainty_angle * (1.0 - confidence) * uncertainty_expansion)
            
            # Base trajectory angle
            base_angle = math.atan2(vy, vx)
            
            # Generate cone points
            cone_x = [x0]
            cone_y = [y0]
            
            # Left edge of cone
            left_angle = base_angle - uncertainty_rad
            for t in [5.0, 10.0, 15.0, 20.0, 25.0, prediction_horizon]:
                if t <= prediction_horizon:
                    dist = speed * t
                    cone_x.append(x0 + dist * math.cos(left_angle))
                    cone_y.append(y0 + dist * math.sin(left_angle))
            
            # Right edge of cone (reverse order)
            right_angle = base_angle + uncertainty_rad
            for t in reversed([5.0, 10.0, 15.0, 20.0, 25.0, prediction_horizon]):
                if t <= prediction_horizon:
                    dist = speed * t
                    cone_x.append(x0 + dist * math.cos(right_angle))
                    cone_y.append(y0 + dist * math.sin(right_angle))
            
            # Close the cone
            cone_x.append(x0)
            cone_y.append(y0)
            
            # Add cone fill
            fig.add_trace(go.Scatter(
                x=cone_x,
                y=cone_y,
                mode='lines',
                fill='toself',
                fillcolor=color,
                line=dict(color='rgba(250, 173, 20, 0.4)', width=1),
                name='Prediction Cone',
                showlegend=False,
                hovertemplate=None,
                hoverinfo='skip'
            ))
        except Exception:
            pass  # Fail silently
