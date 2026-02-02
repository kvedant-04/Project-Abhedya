"""
Interception Window Visualization Module

Provides visualization of interception feasibility windows.

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
- Mathematical feasibility assessment display only
- All outputs are advisory and informational
- NO weapon control
- NO fire authorization
- NO autonomous decisions
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math


class InterceptionWindowVisualization:
    """
    Interception window visualization component.
    
    ADVISORY ONLY - Provides visualization of interception feasibility windows.
    No control logic or autonomous actions.
    """
    
    @staticmethod
    def create_interception_window_visualization(
        target_track: Dict[str, Any],
        defender_position: Dict[str, float],
        interception_result: Dict[str, Any],
        view_range: float = 50000.0
    ) -> go.Figure:
        """
        Create interception window visualization showing feasibility envelope.
        
        ADVISORY ONLY - This is a mathematical feasibility visualization only.
        No actual interception or control logic.
        
        Args:
            target_track: Target track dictionary with position and velocity
            defender_position: Defender position dict with x, y, z
            interception_result: Interception feasibility result
            view_range: View range in meters
            
        Returns:
            Plotly figure showing interception window (empty figure on error)
        """
        try:
            fig = go.Figure()
            
            # Extract target position
            target_pos = target_track.get('position', {})
            if not isinstance(target_pos, dict):
                return go.Figure()
            
            target_x = float(target_pos.get('x', 0.0)) if isinstance(target_pos.get('x'), (int, float)) else 0.0
            target_y = float(target_pos.get('y', 0.0)) if isinstance(target_pos.get('y'), (int, float)) else 0.0
            target_z = float(target_pos.get('z', 0.0)) if isinstance(target_pos.get('z'), (int, float)) else 0.0
            
            # Extract interception data
            feasibility_level = interception_result.get('feasibility_level', 'NOT_FEASIBLE')
            time_to_intercept = interception_result.get('time_to_intercept', None)
            closest_approach = interception_result.get('closest_approach_distance', None)
            
            # Add defender position
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
            
            # Add target position
            fig.add_trace(go.Scatter3d(
                x=[target_x],
                y=[target_y],
                z=[target_z],
                mode='markers',
                marker=dict(size=12, color='#FF7875', symbol='circle', line=dict(width=2, color='white')),
                name='Target Position',
                hovertemplate=None,
                hoverinfo='skip',
                showlegend=True
            ))
            
            # Add line of sight
            fig.add_trace(go.Scatter3d(
                x=[defender_position['x'], target_x],
                y=[defender_position['y'], target_y],
                z=[defender_position['z'], target_z],
                mode='lines',
                line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dot'),
                name='Line of Sight',
                hovertemplate=None,
                hoverinfo='skip',
                showlegend=True
            ))
            
            # Add feasibility envelope based on feasibility level
            InterceptionWindowVisualization._add_feasibility_envelope(
                fig, target_x, target_y, target_z, defender_position,
                feasibility_level, closest_approach
            )
            
            # Add time-to-intercept annotation if available
            if time_to_intercept is not None:
                InterceptionWindowVisualization._add_time_annotation(
                    fig, target_x, target_y, target_z, time_to_intercept
                )
            
            # Update layout
            fig.update_layout(
                title="Interception Window Visualization (Advisory Only - Mathematical Feasibility)",
                scene=dict(
                    xaxis_title="East (meters)",
                    yaxis_title="North (meters)",
                    zaxis_title="Altitude (meters)",
                    xaxis=dict(range=[-view_range, view_range]),
                    yaxis=dict(range=[-view_range, view_range]),
                    zaxis=dict(range=[0, view_range * 0.5]),
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
    def _add_feasibility_envelope(
        fig: go.Figure,
        target_x: float, target_y: float, target_z: float,
        defender_position: Dict[str, float],
        feasibility_level: str,
        closest_approach: Optional[float]
    ):
        """Add feasibility envelope visualization."""
        try:
            # Calculate distance
            dx = target_x - defender_position['x']
            dy = target_y - defender_position['y']
            dz = target_z - defender_position['z']
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            
            # Determine envelope radius based on feasibility
            if feasibility_level == 'HIGHLY_FEASIBLE':
                envelope_radius = distance * 0.1  # 10% of distance
                color = 'rgba(255, 77, 79, 0.3)'
            elif feasibility_level == 'FEASIBLE':
                envelope_radius = distance * 0.15  # 15% of distance
                color = 'rgba(250, 173, 20, 0.3)'
            elif feasibility_level == 'MARGINALLY_FEASIBLE':
                envelope_radius = distance * 0.2  # 20% of distance
                color = 'rgba(74, 144, 226, 0.3)'
            else:
                envelope_radius = distance * 0.3  # 30% of distance
                color = 'rgba(100, 100, 100, 0.2)'
            
            # Use closest approach if available
            if closest_approach is not None:
                envelope_radius = float(closest_approach)
            
            # Create sphere around target
            u = [i * math.pi / 15 for i in range(16)]  # Theta
            v = [i * math.pi / 15 for i in range(16)]  # Phi
            
            sphere_x = []
            sphere_y = []
            sphere_z = []
            
            for theta in u:
                for phi in v:
                    sphere_x.append(target_x + envelope_radius * math.sin(phi) * math.cos(theta))
                    sphere_y.append(target_y + envelope_radius * math.sin(phi) * math.sin(theta))
                    sphere_z.append(target_z + envelope_radius * math.cos(phi))
            
            # Add feasibility envelope
            fig.add_trace(go.Mesh3d(
                x=sphere_x,
                y=sphere_y,
                z=sphere_z,
                opacity=0.2,
                color=color,
                name=f'Feasibility Envelope ({feasibility_level})',
                hovertemplate=None,
                hoverinfo='skip',
                showlegend=True
            ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_time_annotation(
        fig: go.Figure,
        target_x: float, target_y: float, target_z: float,
        time_to_intercept: float
    ):
        """Add time-to-intercept annotation."""
        try:
            # Add text annotation near target
            fig.add_annotation(
                x=target_x,
                y=target_y,
                z=target_z,
                text=f"T-{time_to_intercept:.1f}s<br>(Advisory Only)",
                showarrow=True,
                arrowhead=2,
                arrowcolor='rgba(250, 173, 20, 0.8)',
                font=dict(color='rgba(250, 173, 20, 1.0)', size=12)
            )
        except Exception:
            pass  # Fail silently


class InterceptionFeasibilityAnalyzer:
    """
    Interception feasibility analyzer for advisory assessment.
    
    ADVISORY ONLY - Computes mathematical feasibility only.
    No weapon control, no fire authorization, no autonomous decisions.
    """
    
    # Interceptor parameters (STATIC, ADVISORY)
    MAX_INTERCEPTOR_SPEED_MPS = 3000.0  # 3 km/s
    MAX_ENGAGEMENT_ALTITUDE_M = 30000.0  # 30 km
    MAX_ENGAGEMENT_RANGE_M = 200000.0  # 200 km
    REACTION_DELAY_SECONDS = 5.0  # 5 seconds
    
    @staticmethod
    def compute_feasibility(
        track: Dict[str, Any],
        defender_position: Optional[Dict[str, float]] = None,
        is_training_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Compute interception feasibility for a track.
        
        ADVISORY ONLY - This is a mathematical feasibility assessment only.
        No weapon control, no fire authorization, no autonomous decisions.
        
        Args:
            track: Track dictionary with position, velocity, track_id
            defender_position: Defender position dict with x, y, z (default: origin)
            is_training_mode: Whether training mode is enabled
            
        Returns:
            Dictionary with feasibility assessment:
            {
                "track_id": str,
                "feasible": bool,
                "intercept_window": {
                    "start_time": float,
                    "end_time": float,
                    "duration": float
                },
                "confidence": float,
                "constraints": List[str],
                "is_training_mode": bool
            }
        """
        try:
            if not isinstance(track, dict):
                return InterceptionFeasibilityAnalyzer._fail_safe_result(
                    "UNKNOWN", is_training_mode
                )
            
            track_id = str(track.get('track_id', 'UNKNOWN'))
            
            # Get trajectory data
            try:
                from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
                trajectory_data = TrajectoryTracker.get_trajectory(track_id)
            except Exception:
                trajectory_data = {'history': [], 'predicted_path': [], 'confidence': 0.0}
            
            # Extract current position and velocity
            pos = track.get('position', {})
            vel = track.get('velocity', {})
            
            if not isinstance(pos, dict) or not isinstance(vel, dict):
                return InterceptionFeasibilityAnalyzer._fail_safe_result(
                    track_id, is_training_mode
                )
            
            target_x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
            target_y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
            target_z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
            
            vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
            vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
            vz = float(vel.get('vz', 0.0)) if isinstance(vel.get('vz'), (int, float)) else 0.0
            
            # Default defender position (origin)
            if defender_position is None:
                defender_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            
            def_x = float(defender_position.get('x', 0.0))
            def_y = float(defender_position.get('y', 0.0))
            def_z = float(defender_position.get('z', 0.0))
            
            # Compute time-aligned target trajectory points (using predicted path)
            predicted_path = trajectory_data.get('predicted_path', [])
            if not predicted_path:
                # Fallback: simple linear prediction
                predicted_path = InterceptionFeasibilityAnalyzer._generate_simple_prediction(
                    target_x, target_y, target_z, vx, vy, vz, horizon_seconds=30.0
                )
            
            # Compute interceptor reachable envelope and find overlap
            feasible = False
            intercept_window = {'start_time': 0.0, 'end_time': 0.0, 'duration': 0.0}
            constraints = []
            confidence = trajectory_data.get('confidence', 0.5)
            
            # Check each predicted point
            window_start = None
            window_end = None
            
            for point in predicted_path:
                time_ahead = point.get('time_ahead', 0.0)
                pred_x = point.get('x', target_x)
                pred_y = point.get('y', target_y)
                pred_z = point.get('altitude', target_z)
                
                # Check if point is within interceptor envelope
                distance = math.sqrt(
                    (pred_x - def_x)**2 + (pred_y - def_y)**2 + (pred_z - def_z)**2
                )
                
                # Check constraints
                within_range = distance <= InterceptionFeasibilityAnalyzer.MAX_ENGAGEMENT_RANGE_M
                within_altitude = pred_z <= InterceptionFeasibilityAnalyzer.MAX_ENGAGEMENT_ALTITUDE_M
                after_reaction = time_ahead >= InterceptionFeasibilityAnalyzer.REACTION_DELAY_SECONDS
                
                if within_range and within_altitude and after_reaction:
                    if window_start is None:
                        window_start = time_ahead
                    window_end = time_ahead
                    feasible = True
                else:
                    # Track constraint violations
                    if not within_range:
                        constraints.append('range-limited')
                    if not within_altitude:
                        constraints.append('altitude-limited')
                    if not after_reaction:
                        constraints.append('reaction-delay')
            
            # Remove duplicate constraints
            constraints = list(set(constraints))
            
            if feasible and window_start is not None and window_end is not None:
                intercept_window = {
                    'start_time': window_start,
                    'end_time': window_end,
                    'duration': window_end - window_start
                }
            else:
                # Check current position as fallback
                current_distance = math.sqrt(
                    (target_x - def_x)**2 + (target_y - def_y)**2 + (target_z - def_z)**2
                )
                if current_distance <= InterceptionFeasibilityAnalyzer.MAX_ENGAGEMENT_RANGE_M and \
                   target_z <= InterceptionFeasibilityAnalyzer.MAX_ENGAGEMENT_ALTITUDE_M:
                    feasible = True
                    intercept_window = {
                        'start_time': InterceptionFeasibilityAnalyzer.REACTION_DELAY_SECONDS,
                        'end_time': InterceptionFeasibilityAnalyzer.REACTION_DELAY_SECONDS + 10.0,
                        'duration': 10.0
                    }
                else:
                    if current_distance > InterceptionFeasibilityAnalyzer.MAX_ENGAGEMENT_RANGE_M:
                        constraints.append('range-limited')
                    if target_z > InterceptionFeasibilityAnalyzer.MAX_ENGAGEMENT_ALTITUDE_M:
                        constraints.append('altitude-limited')
                    constraints.append('reaction-delay')
            
            # Adjust confidence based on constraints
            if constraints:
                confidence = max(0.0, confidence - 0.2 * len(constraints))
            
            return {
                'track_id': track_id,
                'feasible': feasible,
                'intercept_window': intercept_window,
                'confidence': max(0.0, min(1.0, confidence)),
                'constraints': constraints,
                'is_training_mode': is_training_mode
            }
        except Exception:
            return InterceptionFeasibilityAnalyzer._fail_safe_result(
                str(track.get('track_id', 'UNKNOWN') if isinstance(track, dict) else 'UNKNOWN'),
                is_training_mode
            )
    
    @staticmethod
    def _generate_simple_prediction(
        x0: float, y0: float, z0: float,
        vx: float, vy: float, vz: float,
        horizon_seconds: float = 30.0
    ) -> List[Dict[str, Any]]:
        """Generate simple linear prediction."""
        predicted_path = []
        dt = 5.0  # 5 second intervals
        num_points = int(horizon_seconds / dt)
        
        for i in range(num_points + 1):
            t = i * dt
            predicted_path.append({
                'time_ahead': t,
                'x': x0 + vx * t,
                'y': y0 + vy * t,
                'altitude': z0 + vz * t
            })
        
        return predicted_path
    
    @staticmethod
    def _fail_safe_result(track_id: str, is_training_mode: bool) -> Dict[str, Any]:
        """Return fail-safe result when computation fails."""
        return {
            'track_id': track_id,
            'feasible': False,
            'intercept_window': {'start_time': 0.0, 'end_time': 0.0, 'duration': 0.0},
            'confidence': 0.0,
            'constraints': ['insufficient-data'],
            'is_training_mode': is_training_mode
        }


class InterceptionFeasibilityPanel:
    """
    UI panel for displaying interception feasibility assessment.
    
    ADVISORY ONLY - Display only, no control logic.
    """
    
    @staticmethod
    def render_panel(
        feasibility_result: Dict[str, Any],
        track: Optional[Dict[str, Any]] = None,
        atmospheric_conditions: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Render interception feasibility panel.
        
        Args:
            feasibility_result: Result from InterceptionFeasibilityAnalyzer.compute_feasibility
            track: Optional track dictionary for additional display info
        """
        try:
            st.subheader("Intercept Feasibility (Advisory)")
            
            track_id = feasibility_result.get('track_id', 'UNKNOWN')
            feasible = feasibility_result.get('feasible', False)
            intercept_window = feasibility_result.get('intercept_window', {})
            confidence = feasibility_result.get('confidence', 0.0)
            constraints = feasibility_result.get('constraints', [])
            is_training_mode = feasibility_result.get('is_training_mode', False)
            
            # Track classification
            obj_type = 'UNKNOWN'
            if track:
                obj_type = str(track.get('object_type', track.get('entity_type', 'UNKNOWN')))
            
            # Display track info
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Track ID:** {track_id}")
            with col2:
                st.markdown(f"**Classification:** {obj_type}")
            
            # Feasibility status
            if feasible:
                st.success(f"✅ **Interception Feasible: YES**")
            else:
                st.warning(f"⚠️ **Interception Feasible: NO**")
            
            # Intercept window info
            if feasible and intercept_window.get('duration', 0.0) > 0:
                window_start = intercept_window.get('start_time', 0.0)
                window_duration = intercept_window.get('duration', 0.0)
                
                st.markdown(f"**Intercept Window Duration:** {window_duration:.1f} seconds")
                st.markdown(f"**Time to Window Open:** {window_start:.1f} seconds")
            else:
                st.info("ℹ️ No intercept window available")
            
            # Confidence bar
            st.markdown("**Confidence:**")
            st.progress(confidence)
            st.caption(f"{confidence:.1%}")
            
            # Constraints
            if constraints:
                st.markdown("**Constraints:**")
                for constraint in constraints:
                    constraint_label = constraint.replace('-', ' ').title()
                    st.caption(f"• {constraint_label}")
            
            # Training mode indicator
            if is_training_mode:
                st.markdown(
                    """
                    <div style="
                        background:#FFF1F0;
                        border-left:3px solid #F5222D;
                        padding:8px;
                        margin-top:8px;
                        border-radius:4px;
                    ">
                        <small><strong>SIMULATION / TRAINING DATA</strong></small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Environmental annotation (advisory only, no feasibility math changes)
            if atmospheric_conditions:
                try:
                    from abhedya.dashboard.atmospheric_modeling import AtmosphericModel
                    env_note = AtmosphericModel.get_interception_environmental_note(atmospheric_conditions)
                    if env_note:
                        st.info(f"🌦️ {env_note}")
                except Exception:
                    pass  # Fail silently
            
            # Advisory disclaimer
            st.caption("⚠️ **Advisory Only** — Mathematical feasibility assessment. No weapon control or authorization.")
            st.caption("Advisory Only — Environmental visualization does not modify engagement decisions or weapon control. Human judgment required.")
        except Exception:
            st.info("ℹ️ Monitoring Only — Insufficient Data")
