"""
Trajectory Tracking Module (FlightRadar24-style)

Provides trajectory history tracking and prediction visualization.

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
- Trajectory history and prediction for display only
- All outputs are advisory and informational
- No weapon logic or engagement decisions
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math


class TrajectoryTracker:
    """
    Trajectory tracking component with history and prediction.
    
    ADVISORY ONLY - Provides FlightRadar24-style trajectory visualization.
    No control logic or autonomous actions.
    """
    
    # History configuration
    MAX_HISTORY_POINTS = 120
    MAX_HISTORY_AGE_SECONDS = 300.0  # 5 minutes
    
    @staticmethod
    def update_track_history(track: Dict[str, Any]) -> None:
        """
        Update trajectory history for a track.
        
        Maintains per-track history in session_state with:
        - timestamp
        - x, y, altitude
        - speed, heading (derived)
        
        History is capped at MAX_HISTORY_POINTS and MAX_HISTORY_AGE_SECONDS.
        Never throws if data is sparse.
        
        Args:
            track: Track dictionary with position, velocity, timestamp
        """
        try:
            if not isinstance(track, dict):
                return
            
            track_id = str(track.get('track_id', 'UNKNOWN'))
            if not track_id or track_id == 'UNKNOWN':
                return
            
            pos = track.get('position', {})
            vel = track.get('velocity', {})
            timestamp_str = track.get('timestamp', '')
            
            if not isinstance(pos, dict) or not isinstance(vel, dict):
                return
            
            # Extract position
            x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
            y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
            z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
            
            # Extract velocity
            vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
            vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
            vz = float(vel.get('vz', 0.0)) if isinstance(vel.get('vz', (int, float))) else 0.0
            
            # Calculate speed and heading (derived, not trusted)
            speed = math.sqrt(vx**2 + vy**2 + vz**2)
            heading = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0 if speed > 0.1 else 0.0
            
            # Parse timestamp
            try:
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                elif isinstance(timestamp_str, datetime):
                    timestamp = timestamp_str
                else:
                    timestamp = datetime.now()
            except Exception:
                timestamp = datetime.now()
            
            # Initialize history storage (use canonical 'track_history' key)
            if 'track_history' not in st.session_state:
                st.session_state.track_history = {}

            if track_id not in st.session_state.track_history:
                st.session_state.track_history[track_id] = []
            
            # Add current point to history
            history_point = {
                'timestamp': timestamp,
                'x': x,
                'y': y,
                'altitude': z,
                'speed': speed,
                'heading': heading
            }
            st.session_state.track_history[track_id].append(history_point)
            
            # Clean old history points
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(seconds=TrajectoryTracker.MAX_HISTORY_AGE_SECONDS)
            
            st.session_state.track_history[track_id] = [
                p for p in st.session_state.track_history[track_id]
                if p['timestamp'] > cutoff_time
            ]
            
            # Cap length
            if len(st.session_state.track_history[track_id]) > TrajectoryTracker.MAX_HISTORY_POINTS:
                st.session_state.track_history[track_id] = \
                    st.session_state.track_history[track_id][-TrajectoryTracker.MAX_HISTORY_POINTS:]
        except Exception:
            # Fail silently - history update is non-critical
            pass
    
    @staticmethod
    def get_trajectory(track_id: str) -> Dict[str, Any]:
        """
        Get trajectory data for a track.
        
        Returns:
            Dictionary with:
            - history: List of historical points
            - predicted_path: List of predicted points
            - confidence: Prediction confidence (0.0-1.0)
        
        Advisory only - no weapon logic or engagement decisions.
        """
        try:
            if 'track_history' not in st.session_state:
                st.session_state.track_history = {}

            track_id = str(track_id)
            history = st.session_state.track_history.get(track_id, [])
            
            # Generate predicted path (10-30s horizon, advisory only)
            predicted_path = []
            confidence = 0.5  # Default confidence
            
            if history and len(history) >= 2:
                # Use recent history to predict
                recent = history[-min(5, len(history)):]
                
                # Calculate average velocity from recent points
                if len(recent) >= 2:
                    dt = (recent[-1]['timestamp'] - recent[0]['timestamp']).total_seconds()
                    if dt > 0:
                        dx = recent[-1]['x'] - recent[0]['x']
                        dy = recent[-1]['y'] - recent[0]['y']
                        dz = recent[-1]['altitude'] - recent[0]['altitude']
                        
                        vx = dx / dt
                        vy = dy / dt
                        vz = dz / dt
                        
                        # Prediction horizon: 10-30 seconds
                        prediction_horizon = 20.0  # 20 seconds default
                        current = recent[-1]
                        
                        # Generate prediction points
                        for t in [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]:
                            if t <= prediction_horizon:
                                predicted_path.append({
                                    'time_ahead': t,
                                    'x': current['x'] + vx * t,
                                    'y': current['y'] + vy * t,
                                    'altitude': current['altitude'] + vz * t
                                })
                        
                        # Confidence based on history consistency
                        if len(recent) >= 3:
                            # Check velocity consistency
                            speeds = [p['speed'] for p in recent]
                            speed_variance = max(speeds) - min(speeds) if speeds else 0.0
                            confidence = max(0.3, min(0.9, 1.0 - (speed_variance / 100.0)))
            
            return {
                'history': history,
                'predicted_path': predicted_path,
                'confidence': confidence,
                'advisory_note': 'Trajectory prediction is advisory only - no weapon logic or engagement decisions'
            }
        except Exception:
            # Fail-safe default
            return {
                'history': [],
                'predicted_path': [],
                'confidence': 0.0,
                'advisory_note': 'Trajectory data unavailable - monitoring only'
            }
    
    @staticmethod
    def create_trajectory_visualization(
        track: Dict[str, Any],
        history_points: Optional[List[Dict[str, Any]]] = None,
        prediction_seconds: float = 60.0,
        training_mode: bool = False
    ) -> go.Figure:
        """
        Create trajectory visualization with history and prediction.
        
        Args:
            track: Current track dictionary with position and velocity
            history_points: Optional list of historical position points
            prediction_seconds: Number of seconds to predict ahead
            training_mode: Whether training mode is enabled
            
        Returns:
            Plotly figure showing trajectory (empty figure on error)
        """
        try:
            fig = go.Figure()
            
            # Extract current position and velocity
            pos = track.get('position', {})
            vel = track.get('velocity', {})
            
            if not isinstance(pos, dict) or not isinstance(vel, dict):
                return go.Figure()
            
            current_x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
            current_y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
            current_z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
            
            vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
            vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
            vz = float(vel.get('vz', 0.0)) if isinstance(vel.get('vz'), (int, float)) else 0.0
            
            # Add trajectory history if available
            if history_points and len(history_points) > 0:
                TrajectoryTracker._add_history_trail(
                    fig, history_points, current_x, current_y, current_z
                )
            
            # Add predicted trajectory
            TrajectoryTracker._add_predicted_trajectory(
                fig, current_x, current_y, current_z, vx, vy, vz, prediction_seconds
            )
            
            # Add current position marker
            fig.add_trace(go.Scatter3d(
                x=[current_x],
                y=[current_y],
                z=[current_z],
                mode='markers',
                marker=dict(size=12, color='#FF4D4F', symbol='circle', line=dict(width=2, color='white')),
                name='Current Position',
                hovertemplate=f'<b>Current Position</b><br>Position: ({current_x:.0f}, {current_y:.0f}, {current_z:.0f}) m<extra></extra>',
                showlegend=True
            ))
            
            # Update layout
            fig.update_layout(
                title="Trajectory Tracking (Advisory Only)",
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
                height=480,
                showlegend=True,
                template='plotly_dark'
            )
            
            return fig
        except Exception:
            return go.Figure()
    
    @staticmethod
    def _add_history_trail(
        fig: go.Figure,
        history_points: List[Dict[str, Any]],
        current_x: float,
        current_y: float,
        current_z: float
    ):
        """Add trajectory history trail with fade effect."""
        try:
            # Sort history by timestamp (oldest first)
            sorted_history = sorted(
                history_points,
                key=lambda p: p.get('timestamp', ''),
                reverse=False
            )
            
            hist_x = []
            hist_y = []
            hist_z = []
            
            for point in sorted_history:
                pos = point.get('position', {})
                if isinstance(pos, dict):
                    x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
                    y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
                    z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
                    hist_x.append(x)
                    hist_y.append(y)
                    hist_z.append(z)
            
            # Add current position to end
            hist_x.append(current_x)
            hist_y.append(current_y)
            hist_z.append(current_z)
            
            # Add history trail with gradient opacity
            fig.add_trace(go.Scatter3d(
                x=hist_x,
                y=hist_y,
                z=hist_z,
                mode='lines',
                line=dict(color='rgba(74, 144, 226, 0.4)', width=3),
                name='Trajectory History',
                hovertemplate=None,
                hoverinfo='skip',
                showlegend=True
            ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_predicted_trajectory(
        fig: go.Figure,
        x0: float, y0: float, z0: float,
        vx: float, vy: float, vz: float,
        prediction_seconds: float
    ):
        """Add predicted trajectory based on current velocity."""
        try:
            # Generate prediction points
            dt = 1.0  # 1 second intervals
            num_points = int(prediction_seconds / dt)
            
            pred_x = []
            pred_y = []
            pred_z = []
            times = []
            
            for i in range(num_points + 1):
                t = i * dt
                times.append(t)
                pred_x.append(x0 + vx * t)
                pred_y.append(y0 + vy * t)
                pred_z.append(z0 + vz * t)
            
            # Add predicted trajectory
            fig.add_trace(go.Scatter3d(
                x=pred_x,
                y=pred_y,
                z=pred_z,
                mode='lines',
                line=dict(color='rgba(250, 173, 20, 0.6)', width=3, dash='dash'),
                name='Predicted Trajectory',
                hovertemplate=None,
                hoverinfo='skip',
                customdata=times,
                showlegend=True
            ))
        except Exception:
            pass  # Fail silently
