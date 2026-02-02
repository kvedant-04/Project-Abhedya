"""
Engagement Sequence Visualization Module

Provides visualization of engagement sequences and interception scenarios.

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun

STRICT CONSTRAINTS:
- Visualization only, no autonomous actions
- No weapon control or engagement logic
- All outputs are advisory and informational
- Human-in-the-loop required for all interpretations
- Mathematical simulation only, no actual engagement
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math


class EngagementVisualization:
    """
    Engagement sequence visualization component.
    
    ADVISORY ONLY - Provides visualization of engagement sequences.
    No control logic or autonomous actions.
    """
    
    @staticmethod
    def create_engagement_sequence(
        target_track: Dict[str, Any],
        defender_position: Dict[str, float],
        interception_result: Optional[Dict[str, Any]] = None,
        time_steps: int = 50,
        training_mode: bool = False,
        atmospheric_conditions: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create engagement sequence visualization showing target and interceptor trajectories.
        
        ADVISORY ONLY - This is a mathematical simulation visualization only.
        No actual engagement or control logic.
        
        Args:
            target_track: Target track dictionary with position and velocity
            defender_position: Defender position dict with x, y, z
            interception_result: Optional interception feasibility result
            time_steps: Number of time steps to simulate
            training_mode: Whether training mode is enabled
            
        Returns:
            Plotly figure showing engagement sequence (empty figure on error)
        """
        try:
            fig = go.Figure()
            
            # Extract target position and velocity
            target_pos = target_track.get('position', {})
            target_vel = target_track.get('velocity', {})
            
            if not isinstance(target_pos, dict) or not isinstance(target_vel, dict):
                return go.Figure()
            
            target_x0 = float(target_pos.get('x', 0.0)) if isinstance(target_pos.get('x'), (int, float)) else 0.0
            target_y0 = float(target_pos.get('y', 0.0)) if isinstance(target_pos.get('y'), (int, float)) else 0.0
            target_z0 = float(target_pos.get('z', 0.0)) if isinstance(target_pos.get('z'), (int, float)) else 0.0
            
            target_vx = float(target_vel.get('vx', 0.0)) if isinstance(target_vel.get('vx'), (int, float)) else 0.0
            target_vy = float(target_vel.get('vy', 0.0)) if isinstance(target_vel.get('vy'), (int, float)) else 0.0
            target_vz = float(target_vel.get('vz', 0.0)) if isinstance(target_vel.get('vz'), (int, float)) else 0.0
            
            # Simulate target trajectory
            dt = 1.0  # 1 second time steps
            target_x = []
            target_y = []
            target_z = []
            times = []
            
            for i in range(time_steps):
                t = i * dt
                times.append(t)
                target_x.append(target_x0 + target_vx * t)
                target_y.append(target_y0 + target_vy * t)
                target_z.append(target_z0 + target_vz * t)
            
            # Add target trajectory
            fig.add_trace(go.Scatter3d(
                x=target_x,
                y=target_y,
                z=target_z,
                mode='lines+markers',
                line=dict(color='#FF7875', width=4),
                marker=dict(size=4, color='#FF7875'),
                name='Target Trajectory (Simulated)',
                hovertemplate=None,
                hoverinfo='skip',
                customdata=times,
                showlegend=True
            ))
            
            # If interception result available, show interceptor trajectory
            if interception_result and training_mode:
                EngagementVisualization._add_interceptor_trajectory(
                    fig, target_x, target_y, target_z, times,
                    defender_position, interception_result
                )
            
            # Add defender position marker
            fig.add_trace(go.Scatter3d(
                x=[defender_position['x']],
                y=[defender_position['y']],
                z=[defender_position['z']],
                mode='markers',
                marker=dict(size=15, color='#4A90E2', symbol='diamond', line=dict(width=2, color='white')),
                name='Defender Position',
                hovertemplate=None,
                hoverinfo='skip',
                showlegend=True
            ))
            
            # Add interception window if available
            if interception_result:
                EngagementVisualization._add_interception_window(
                    fig, target_x, target_y, target_z, times, interception_result
                )
            
            # Apply atmospheric confidence shading (visual only, advisory)
            if atmospheric_conditions:
                try:
                    from abhedya.dashboard.atmospheric_modeling import AtmosphericModel
                    visibility = atmospheric_conditions.get("visibility")
                    if visibility:
                        confidence_attenuation = AtmosphericModel.get_visibility_confidence_attenuation(visibility)
                        # Add subtle visual indicator (opacity adjustment) - visual only
                        # This affects display opacity, NOT decision logic
                        if confidence_attenuation < 1.0:
                            # Slightly reduce opacity of target trajectory to indicate reduced confidence
                            for trace in fig.data:
                                if 'Target' in trace.name:
                                    trace.marker.opacity = confidence_attenuation
                                    if hasattr(trace, 'line') and trace.line:
                                        trace.line.color = f'rgba(255, 120, 117, {confidence_attenuation})'
                except Exception:
                    pass  # Fail silently - confidence shading is non-critical
            
            # Update layout
            fig.update_layout(
                title="Engagement Sequence Visualization (Advisory Only - Simulation)",
                scene=dict(
                    xaxis_title="East (meters)",
                    yaxis_title="North (meters)",
                    zaxis_title="Altitude (meters)",
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.2),
                        center=dict(x=0, y=0, z=0),
                        up=dict(x=0, y=0, z=1)
                    )
                ),
                height=700,
                showlegend=True,
                template='plotly_dark'
            )
            
            return fig
        except Exception:
            return go.Figure()
    
    @staticmethod
    def _add_interceptor_trajectory(
        fig: go.Figure,
        target_x: List[float],
        target_y: List[float],
        target_z: List[float],
        times: List[float],
        defender_position: Dict[str, float],
        interception_result: Dict[str, Any]
    ):
        """
        Add simulated interceptor trajectory.
        
        ADVISORY ONLY - Mathematical simulation only, no actual interceptor control.
        """
        try:
            # Extract interception point
            intercept_time = interception_result.get('time_to_intercept', None)
            if intercept_time is None:
                return
            
            intercept_time = float(intercept_time)
            
            # Find closest time step
            intercept_idx = min(range(len(times)), key=lambda i: abs(times[i] - intercept_time))
            if intercept_idx >= len(target_x):
                return
            
            intercept_x = target_x[intercept_idx]
            intercept_y = target_y[intercept_idx]
            intercept_z = target_z[intercept_idx]
            
            # Simulate interceptor trajectory (constant velocity model)
            # This is a simplified mathematical model only
            interceptor_x = []
            interceptor_y = []
            interceptor_z = []
            interceptor_times = []
            
            # Assume interceptor speed (simplified model)
            interceptor_speed = 1000.0  # m/s (example value)
            
            dx = intercept_x - defender_position['x']
            dy = intercept_y - defender_position['y']
            dz = intercept_z - defender_position['z']
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            
            if distance > 0 and intercept_time > 0:
                # Calculate interceptor velocity components
                interceptor_vx = (dx / distance) * interceptor_speed
                interceptor_vy = (dy / distance) * interceptor_speed
                interceptor_vz = (dz / distance) * interceptor_speed
                
                # Generate interceptor trajectory points
                dt = 0.1  # 0.1 second steps
                for t in [i * dt for i in range(int(intercept_time / dt) + 1)]:
                    if t <= intercept_time:
                        interceptor_x.append(defender_position['x'] + interceptor_vx * t)
                        interceptor_y.append(defender_position['y'] + interceptor_vy * t)
                        interceptor_z.append(defender_position['z'] + interceptor_vz * t)
                        interceptor_times.append(t)
                
                # Add interceptor trajectory
                fig.add_trace(go.Scatter3d(
                    x=interceptor_x,
                    y=interceptor_y,
                    z=interceptor_z,
                    mode='lines+markers',
                    line=dict(color='#52C41A', width=4, dash='dot'),
                    marker=dict(size=4, color='#52C41A'),
                    name='Interceptor Trajectory (Simulated)',
                    hovertemplate='<b>Interceptor (Simulated)</b><br>Time: %{customdata:.1f}s<br>Position: (%{x:.0f}, %{y:.0f}, %{z:.0f}) m<extra></extra>',
                    customdata=interceptor_times,
                    showlegend=True
                ))
                
                # Mark interception point
                fig.add_trace(go.Scatter3d(
                    x=[intercept_x],
                    y=[intercept_y],
                    z=[intercept_z],
                    mode='markers',
                    marker=dict(size=12, color='#FF4D4F', symbol='x', line=dict(width=2, color='white')),
                    name='Interception Point (Simulated)',
                    hovertemplate=f'<b>Interception Point (Simulated)</b><br>Time: {intercept_time:.1f}s<br>Position: ({intercept_x:.0f}, {intercept_y:.0f}, {intercept_z:.0f}) m<extra></extra>',
                    showlegend=True
                ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_interception_window(
        fig: go.Figure,
        target_x: List[float],
        target_y: List[float],
        target_z: List[float],
        times: List[float],
        interception_result: Dict[str, Any]
    ):
        """
        Add interception feasibility window visualization.
        
        ADVISORY ONLY - Shows mathematical feasibility window only.
        """
        try:
            window_start = interception_result.get('window_start_time', None)
            window_end = interception_result.get('window_end_time', None)
            
            if window_start is None or window_end is None:
                return
            
            window_start = float(window_start)
            window_end = float(window_end)
            
            # Find indices for window
            start_idx = min(range(len(times)), key=lambda i: abs(times[i] - window_start))
            end_idx = min(range(len(times)), key=lambda i: abs(times[i] - window_end))
            
            if start_idx >= len(target_x) or end_idx >= len(target_x):
                return
            
            # Extract window trajectory segment
            window_x = target_x[start_idx:end_idx+1]
            window_y = target_y[start_idx:end_idx+1]
            window_z = target_z[start_idx:end_idx+1]
            window_times = times[start_idx:end_idx+1]
            
            # Add window highlight
            fig.add_trace(go.Scatter3d(
                x=window_x,
                y=window_y,
                z=window_z,
                mode='lines',
                line=dict(color='rgba(250, 173, 20, 0.6)', width=6),
                name='Interception Window (Feasible)',
                hovertemplate='<b>Interception Window</b><br>Time: %{customdata:.1f}s<br>ADVISORY ONLY - Mathematical feasibility<extra></extra>',
                customdata=window_times,
                showlegend=True
            ))
        except Exception:
            pass  # Fail silently
