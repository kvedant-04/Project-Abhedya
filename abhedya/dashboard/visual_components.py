"""
Visual Components

Reusable visual components for the dashboard.

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import math

# Default Plotly rendering config used for Streamlit embeds
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'responsive': True,
    'scrollZoom': True
}


class SeverityThemeController:
    """
    Severity theme controller (UI only).
    
    Maps advisory outputs to visual themes.
    Theme changes do NOT trigger actions.
    """
    
    SEVERITY_COLORS = {
        'NORMAL': {
            'primary': '#4A90E2',      # Blue
            'secondary': '#E3F2FD',    # Light blue
            'text': '#1E3A5F'          # Dark blue
        },
        'ELEVATED': {
            'primary': '#FAAD14',      # Amber
            'secondary': '#FFF7E6',    # Light amber
            'text': '#8B6914'          # Dark amber
        },
        'HIGH': {
            'primary': '#FF7875',      # Red
            'secondary': '#FFE8E8',    # Light red
            'text': '#A8071A'          # Dark red
        },
        'CRITICAL': {
            'primary': '#F5222D',      # Dark red
            'secondary': '#FFE8E8',    # Light red
            'text': '#820014'          # Very dark red
        }
    }
    
    @staticmethod
    def get_theme(severity: str, training_mode: bool = False) -> Dict[str, str]:
        """
        Get theme for severity level.
        
        Args:
            severity: Severity level (NORMAL, ELEVATED, HIGH, CRITICAL)
            training_mode: Whether training mode is enabled
            
        Returns:
            Theme dictionary with colors (safe defaults on error)
        """
        # Input validation
        if not isinstance(severity, str) or not severity:
            severity = 'NORMAL'
        
        if not isinstance(training_mode, bool):
            training_mode = False
        
        try:
            severity_upper = str(severity).upper()
            
            # CRITICAL only allowed in training mode
            if severity_upper == 'CRITICAL' and not training_mode:
                severity_upper = 'HIGH'
            
            return SeverityThemeController.SEVERITY_COLORS.get(
                severity_upper,
                SeverityThemeController.SEVERITY_COLORS['NORMAL']
            )
        except Exception:
            # Safe default theme
            return SeverityThemeController.SEVERITY_COLORS['NORMAL']
    
    @staticmethod
    def render_severity_badge(severity: str, training_mode: bool = False):
        """
        Render severity badge.
        
        Args:
            severity: Severity level
            training_mode: Whether training mode is enabled
        """
        # Input validation
        if not isinstance(severity, str) or not severity:
            severity = 'NORMAL'
        
        if not isinstance(training_mode, bool):
            training_mode = False
        
        try:
            theme = SeverityThemeController.get_theme(severity, training_mode)
            
            # Escape HTML to prevent XSS
            safe_severity = str(severity).replace('<', '&lt;').replace('>', '&gt;')
            label = safe_severity
            if str(severity).upper() == 'CRITICAL' and training_mode:
                label = f"{safe_severity} (Simulated)"
            
            # Validate theme colors (prevent injection)
            safe_secondary = str(theme.get('secondary', '#E3F2FD'))[:7]
            safe_primary = str(theme.get('primary', '#4A90E2'))[:7]
            safe_text = str(theme.get('text', '#1E3A5F'))[:7]
            
            st.markdown(
                f"""
                <div style="background-color: {safe_secondary}; 
                            border-left: 4px solid {safe_primary}; 
                            padding: 10px; 
                            border-radius: 3px; 
                            margin: 10px 0;">
                    <strong style="color: {safe_text};">{label}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            # Fail silently - don't crash dashboard
            pass

    @staticmethod
    def render_fusion_breakdown(track: Optional[Dict[str, Any]], training_mode: bool = False):
        """
        Render the 'Multi-Sensor Fusion Breakdown (Advisory)' panel.

        STRICTLY VISUAL ONLY - does not modify track state or perform fusion.
        - Reads `track.get('fusion')` or `track.get('sensor_contributions')` if available.
        - If missing, generates a deterministic, synthetic advisory distribution that sums to 1.0.
        - Renders horizontal bars with fixed colors (no animations, no computations that affect state).
        """
        try:
            st.subheader("Multi-Sensor Fusion Breakdown (Advisory)")
            st.caption("Advisory-only visualization of sensor contribution")

            # Placeholder when no track selected
            if not isinstance(track, dict):
                st.info("Select or hover a track to view sensor fusion breakdown.")
                return

            # Prefer explicit 'fusion' key, fallback to older 'sensor_contributions'
            fusion_src = track.get("fusion") or track.get("sensor_contributions") or {}

            # If missing or empty, produce a deterministic synthetic advisory distribution
            if not isinstance(fusion_src, dict) or not fusion_src:
                # Deterministic synthetic distribution (training-friendly)
                fusion_src = {
                    "Surveillance Radar": 0.45,
                    "Precision Tracking Radar": 0.35,
                    "Passive / ESM": 0.20
                }

            # Normalize values for display only (do not write back to track)
            try:
                items = [(k, float(v)) for k, v in fusion_src.items()]
            except Exception:
                items = [ ("Surveillance Radar", 0.45), ("Precision Tracking Radar", 0.35), ("Passive / ESM", 0.20) ]

            total = sum(v for _, v in items) or 1.0
            normalized = [(k, max(0.0, float(v) / total)) for k, v in items]

            # Colors mandated by design
            color_map = {
                "Surveillance Radar": "#1890FF",  # Blue
                "Precision Tracking Radar": "#52C41A",  # Green
                "Passive / ESM": "#722ED1"  # Purple
            }

            names = [k for k, _ in normalized]
            values = [v * 100.0 for _, v in normalized]
            colors = [color_map.get(n, "#999999") for n in names]

            # Render a simple horizontal bar chart (static, advisory-only)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=values,
                y=names,
                orientation='h',
                marker=dict(color=colors),
                text=[f"{int(round(val))}%" for val in values],
                textposition='outside',
                hoverinfo='skip',
                showlegend=False
            ))
            fig.update_layout(
                height=40 * max(1, len(names)) + 40,
                margin=dict(l=4, r=8, t=6, b=6),
                xaxis=dict(range=[0, 100], showticklabels=False),
                yaxis=dict(autorange='reversed')
            )

            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

            # Fusion Quality (visual-only)
            quality = track.get("fusion_quality") or {}
            ew_degraded = quality.get("ew_degraded") if isinstance(quality, dict) else False
            confidence_trend = quality.get("confidence_trend") if isinstance(quality, dict) and "confidence_trend" in quality else "Stable"

            st.markdown("**Fusion Quality:**")
            st.write(f"• EW Degradation: {'Yes' if ew_degraded else 'None'}")
            st.write(f"• Confidence Trend: {confidence_trend}")

        except Exception:
            # Fail silently and non-intrusively — do not change state or raise
            st.info("Select or hover a track to view sensor fusion breakdown.")
            return


class AirspaceVisualization:
    """
    Airspace visualization component.
    """
    
    @staticmethod
    def create_2d_visualization(
        tracks: List[Dict[str, Any]],
        center_x: float = 0.0,
        center_y: float = 0.0,
        view_range: float = 50000.0,
        training_mode: bool = False,
        current_time: Optional[datetime] = None,
        show_confidence_rings: bool = True,
        show_protected_zones: bool = True,
        atmospheric_conditions: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create 2D airspace visualization with time-based interpolation.
        
        Args:
            tracks: List of track dictionaries
            center_x: Center X coordinate
            center_y: Center Y coordinate
            view_range: View range in meters
            training_mode: Whether training mode is enabled (for visual dynamics)
            current_time: Current time for interpolation (defaults to now)
            
        Returns:
            Plotly figure (empty figure on error)
        """
        # Input validation
        if not isinstance(tracks, list):
            tracks = []
        
        try:
            center_x = float(center_x) if isinstance(center_x, (int, float)) else 0.0
            center_y = float(center_y) if isinstance(center_y, (int, float)) else 0.0
            view_range = max(1000.0, min(1000000.0, float(view_range))) if isinstance(view_range, (int, float)) else 50000.0
            
            fig = go.Figure()

            # If there are no explicit tracks passed in but session-level
            # simulation_tracks exist (training mode), prefer them so the
            # visualization always reflects the persistent session source.
            try:
                if (not tracks or len(tracks) == 0) and training_mode:
                    session_tracks = None
                    try:
                        session_tracks = st.session_state.get('simulation_tracks', None)
                    except Exception:
                        session_tracks = None

                    if isinstance(session_tracks, list) and len(session_tracks) > 0:
                        tracks = session_tracks
            except Exception:
                pass
            
            # Add protected zones (if enabled)
            if show_protected_zones:
                AirspaceVisualization._add_protected_zones(fig, center_x, center_y)
            
            # Radar sweep is handled via animation frames in Training Mode (see below)
            # No static sweep trace needed - animation frames will handle it
            
            # Interpolate track positions based on time (Training Mode only)
            if training_mode and current_time is None:
                from datetime import datetime
                current_time = datetime.now()
            
            # Group tracks by type (validate each track)
            valid_tracks = []
            for t in tracks:
                if isinstance(t, dict):
                    # Interpolate position if in training mode
                    if training_mode and current_time:
                        t = AirspaceVisualization._interpolate_track_position(t, current_time)
                    valid_tracks.append(t)
            
            # Update trajectory history for all tracks (before grouping)
            try:
                from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
                for track in valid_tracks:
                    if isinstance(track, dict):
                        TrajectoryTracker.update_track_history(track)
            except Exception:
                pass  # Fail silently - trajectory history is non-critical
            
            aircraft_tracks = [t for t in valid_tracks if t.get('object_type') == 'AIRCRAFT']
            drone_tracks = [t for t in valid_tracks if t.get('object_type') == 'AERIAL_DRONE']
            unknown_tracks = [t for t in valid_tracks if t.get('object_type') == 'UNKNOWN_OBJECT']
            
            # Add tracks with trajectory visualization layers
            if aircraft_tracks:
                AirspaceVisualization._add_track_group(fig, aircraft_tracks, 'Aircraft', '✈', training_mode, show_confidence_rings, atmospheric_conditions)
            if drone_tracks:
                AirspaceVisualization._add_track_group(fig, drone_tracks, 'Unmanned Aerial Vehicle', '🚁', training_mode, show_confidence_rings, atmospheric_conditions)
            if unknown_tracks:
                AirspaceVisualization._add_track_group(fig, unknown_tracks, 'Unknown Object', '●', training_mode, show_confidence_rings, atmospheric_conditions)

            # In Training Mode: radar sweep handled via CSS overlay (see app.py)
            # Plotly chart remains static for better performance and full interaction controls
            if training_mode:
                import streamlit as st
                
                base_tracks = st.session_state.get('simulation_tracks', valid_tracks)
                
                # Build static marker lists from base_tracks (no animation frames)
                base_x = [float(t.get('position', {}).get('x', 0.0)) for t in base_tracks]
                base_y = [float(t.get('position', {}).get('y', 0.0)) for t in base_tracks]
                base_icons = ['✈' if t.get('object_type') == 'AIRCRAFT' else ('🚁' if t.get('object_type') == 'AERIAL_DRONE' else '●') for t in base_tracks]
                base_colors = [SeverityThemeController.get_theme(str(t.get('threat_level', 'NONE'))).get('primary', '#4A90E2') for t in base_tracks]

                # Add static marker trace (no animation frames, no radar sweep traces)
                if base_x and base_y:
                    hover_base = []
                    for t in base_tracks:
                        confidence_val = float(t.get('confidence', 0.0)) if isinstance(t.get('confidence'), (int, float)) else 0.0
                        confidence_val = max(0.0, min(1.0, confidence_val))
                        
                        # Extract velocity for speed and heading
                        vel_hover = t.get('velocity', {})
                        if not isinstance(vel_hover, dict):
                            vel_hover = {}
                        
                        vx_hover = float(vel_hover.get('vx', 0.0)) if isinstance(vel_hover.get('vx'), (int, float)) else 0.0
                        vy_hover = float(vel_hover.get('vy', 0.0)) if isinstance(vel_hover.get('vy'), (int, float)) else 0.0
                        speed_mps = math.sqrt(vx_hover**2 + vy_hover**2) if vx_hover or vy_hover else float(t.get('speed_meters_per_second', 0.0))
                        heading_hover = (math.degrees(math.atan2(vy_hover, vx_hover)) + 360.0) % 360.0 if speed_mps > 0.1 else 0.0
                        
                        altitude = float(t.get('position', {}).get('z', 0.0)) if isinstance(t.get('position', {}).get('z'), (int, float)) else 0.0
                        
                        # Get trajectory confidence
                        trajectory_confidence_hover = 0.0
                        try:
                            from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
                            track_id_hover = str(t.get('track_id', 'N/A'))
                            trajectory_data_hover = TrajectoryTracker.get_trajectory(track_id_hover)
                            trajectory_confidence_hover = trajectory_data_hover.get('confidence', 0.0)
                        except Exception:
                            pass
                        
                        # Calculate data freshness
                        timestamp_str_hover = t.get('timestamp', '')
                        data_freshness_hover = "N/A"
                        try:
                            if timestamp_str_hover:
                                if isinstance(timestamp_str_hover, str):
                                    track_time_hover = datetime.fromisoformat(timestamp_str_hover.replace('Z', '+00:00'))
                                else:
                                    track_time_hover = timestamp_str_hover
                                age_seconds_hover = (datetime.now() - track_time_hover).total_seconds()
                                data_freshness_hover = f"{int(age_seconds_hover)}s ago"
                        except Exception:
                            pass
                        
                        track_id_hover = str(t.get('track_id', 'N/A'))
                        obj_type_hover = str(t.get('object_type', 'N/A'))
                        is_simulation_hover = t.get('is_simulation', False) or t.get('simulation_label', '')
                        data_source_hover = "SIMULATION / TRAINING DATA" if is_simulation_hover else "Live Data"
                        
                        # Build multi-line hover text using <br> (Plotly's native format)
                        hover_base.append(
                            f"Track ID: {track_id_hover}<br>"
                            f"Classification: {obj_type_hover} ({confidence_val:.1%})<br>"
                            f"Speed: {speed_mps * 3.6:.0f} km/h<br>"
                            f"Altitude: {altitude:.0f} m<br>"
                            f"Heading: {heading_hover:.1f}°<br>"
                            f"Trajectory Confidence: {trajectory_confidence_hover:.1%}<br>"
                            f"Data Freshness: {data_freshness_hover}<br>"
                            f"Data Source: {data_source_hover}"
                        )

                    static_trace = go.Scatter(
                        x=base_x,
                        y=base_y,
                        mode='markers',
                        marker=dict(size=15, color=base_colors, symbol='circle', line=dict(width=2, color='white')),
                        name='Simulation Tracks',
                        hovertemplate='%{hovertext}<extra></extra>',
                        hovertext=hover_base,
                        showlegend=True
                    )
                    fig.add_trace(static_trace)
            # Update layout
            fig.update_layout(
                title=dict(text="Airspace Overview", x=0.5, xanchor='center', y=0.95, yanchor='top', pad={'t': 8}),
                xaxis_title="East (meters)",
                yaxis_title="North (meters)",
                xaxis=dict(
                    range=[center_x - view_range, center_x + view_range],
                    scaleanchor="y",
                    scaleratio=1,
                    automargin=True
                ),
                yaxis=dict(
                    range=[center_y - view_range, center_y + view_range],
                    automargin=True
                ),
                hovermode='closest',
                template='plotly_white',
                autosize=True,
                automargin=True,
                margin=dict(l=70, r=20, t=90, b=80),
                height=700,
                showlegend=True,
                legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01)
            )

            # Ensure axes labels don't get clipped
            try:
                fig.update_xaxes(automargin=True)
                fig.update_yaxes(automargin=True)
            except Exception:
                pass
            
            # If we made it here but no traces were added (empty axes), add
            # a lightweight informative annotation so the user sees why the
            # chart is empty rather than a large blank space.
            try:
                if not fig.data or len(fig.data) == 0:
                    fig.add_annotation(
                        text="No tracks available to display",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=14, color="#666666")
                    )
            except Exception:
                pass

            return fig
        except Exception:
            # Safe default: return empty figure
            return go.Figure()
    
    @staticmethod
    def _interpolate_track_position(track: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """
        Interpolate track position based on velocity and time.
        
        Args:
            track: Track dictionary
            current_time: Current time for interpolation
            
        Returns:
            Track dictionary with interpolated position
        """
        try:
            from datetime import datetime
            import streamlit as st
            
            # Get track timestamp
            track_timestamp_str = track.get('timestamp', '')
            if not track_timestamp_str:
                return track
            
            try:
                if isinstance(track_timestamp_str, str):
                    track_timestamp = datetime.fromisoformat(track_timestamp_str.replace('Z', '+00:00'))
                else:
                    track_timestamp = track_timestamp_str
            except:
                return track
            
            # Calculate time delta
            time_delta = (current_time - track_timestamp).total_seconds()
            
            # Get velocity
            velocity = track.get('velocity', {})
            if not isinstance(velocity, dict):
                return track
            
            vx = float(velocity.get('vx', 0.0)) if isinstance(velocity.get('vx'), (int, float)) else 0.0
            vy = float(velocity.get('vy', 0.0)) if isinstance(velocity.get('vy'), (int, float)) else 0.0
            vz = float(velocity.get('vz', 0.0)) if isinstance(velocity.get('vz'), (int, float)) else 0.0
            
            # Get current position
            position = track.get('position', {})
            if not isinstance(position, dict):
                return track
            
            x = float(position.get('x', 0.0)) if isinstance(position.get('x'), (int, float)) else 0.0
            y = float(position.get('y', 0.0)) if isinstance(position.get('y'), (int, float)) else 0.0
            z = float(position.get('z', 0.0)) if isinstance(position.get('z'), (int, float)) else 0.0
            
            # Interpolate position
            new_x = x + vx * time_delta
            new_y = y + vy * time_delta
            new_z = z + vz * time_delta
            
            # Create new track with interpolated position
            new_track = track.copy()
            new_track['position'] = {
                'x': new_x,
                'y': new_y,
                'z': new_z
            }
            new_track['timestamp'] = current_time.isoformat()
            
            return new_track
        except Exception:
            # Return original track on error
            return track
    
    @staticmethod
    def _add_protected_zones(fig: go.Figure, center_x: float, center_y: float):
        """Add protected airspace zones."""
        zones = [
            (10000.0, "Critical Protected Zone", "rgba(255, 77, 79, 0.1)", "rgba(255, 77, 79, 0.3)"),
            (25000.0, "Protected Zone", "rgba(250, 173, 20, 0.1)", "rgba(250, 173, 20, 0.3)"),
            (50000.0, "Extended Zone", "rgba(74, 144, 226, 0.1)", "rgba(74, 144, 226, 0.3)")
        ]
        
        for radius, name, fill_color, line_color in zones:
            theta = [i * 2 * math.pi / 100 for i in range(101)]
            x = [center_x + radius * math.cos(t) for t in theta]
            y = [center_y + radius * math.sin(t) for t in theta]
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                fill='toself',
                fillcolor=fill_color,
                line=dict(color=line_color, width=2),
                name=name,
                showlegend=True,
                hoverinfo='skip'
            ))
    
    @staticmethod
    def _add_radar_sweep(fig: go.Figure, center_x: float, center_y: float, view_range: float):
        """
        Add rotating radar sweep overlay (Training Mode only - visual only).
        Uses time-based rotation that updates on each redraw.
        Uses Plotly animation frames for smooth rotation without full reruns.
        
        Args:
            fig: Plotly figure
            center_x: Center X coordinate
            center_y: Center Y coordinate
            view_range: View range in meters
        """
        try:
            import streamlit as st
            from datetime import datetime
            
            # Get animation start time from session state
            if 'animation_start_time' not in st.session_state:
                st.session_state.animation_start_time = datetime.now()
            
            # Calculate elapsed time since animation start
            elapsed = (datetime.now() - st.session_state.animation_start_time).total_seconds()
            
            # Calculate current rotation angle (7 second rotation period)
            rotation_period = 7.0
            angle = (elapsed % rotation_period) / rotation_period * 2 * math.pi
            
            # Create sweep line (from center to edge)
            sweep_length = view_range * 0.95  # Slightly inside view range
            sweep_x = [center_x, center_x + sweep_length * math.cos(angle)]
            sweep_y = [center_y, center_y + sweep_length * math.sin(angle)]
            
            # Add sweep line with low opacity
            fig.add_trace(go.Scatter(
                x=sweep_x,
                y=sweep_y,
                mode='lines',
                line=dict(color='rgba(74, 144, 226, 0.08)', width=3),
                name='Radar Sweep (Visualization Only)',
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Add sweep arc (fade-out effect)
            arc_angle_range = math.pi / 6  # 30 degrees
            arc_points = 20
            arc_angles = [angle - arc_angle_range + (i / arc_points) * 2 * arc_angle_range 
                         for i in range(arc_points + 1)]
            
            arc_x = [center_x + sweep_length * 0.7 * math.cos(a) for a in arc_angles]
            arc_y = [center_y + sweep_length * 0.7 * math.sin(a) for a in arc_angles]
            
            fig.add_trace(go.Scatter(
                x=arc_x,
                y=arc_y,
                mode='lines',
                line=dict(color='rgba(74, 144, 226, 0.05)', width=2),
                fill='toself',
                fillcolor='rgba(74, 144, 226, 0.03)',
                name='Radar Sweep Arc (Visualization Only)',
                showlegend=False,
                hoverinfo='skip'
            ))
        except Exception:
            # Fail silently - radar sweep is visual only
            pass
    
    @staticmethod
    def _add_track_group(fig: go.Figure, tracks: List[Dict[str, Any]], group_name: str, icon: str, training_mode: bool = False, show_confidence_rings: bool = True):
        """
        Add a group of tracks with optional trails (Training Mode only).
        
        Args:
            fig: Plotly figure
            tracks: List of track dictionaries
            group_name: Name of the group
            icon: Icon character
            training_mode: Whether to show trails (Training Mode only)
        """
        # Input validation
        if not isinstance(tracks, list) or not tracks:
            return
        
        if not isinstance(fig, go.Figure):
            return
        
        try:
            x_coords = []
            y_coords = []
            hover_texts = []
            colors = []
            
            for track in tracks:
                if not isinstance(track, dict):
                    continue
                
                pos = track.get('position', {})
                if not isinstance(pos, dict):
                    pos = {}
                
                x_val = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
                y_val = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
                
                x_coords.append(x_val)
                y_coords.append(y_val)
                
                # Build multi-line hover text (FIX HTML LEAKAGE)
                track_id = str(track.get('track_id', 'N/A'))
                obj_type = str(track.get('object_type', 'N/A'))
                confidence_val = float(track.get('confidence', 0.0)) if isinstance(track.get('confidence'), (int, float)) else 0.0
                confidence_val = max(0.0, min(1.0, confidence_val))
                
                # Extract velocity for speed and heading
                vel = track.get('velocity', {})
                if not isinstance(vel, dict):
                    vel = {}
                
                vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
                vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
                speed_mps = math.sqrt(vx**2 + vy**2) if vx or vy else float(track.get('speed_meters_per_second', 0.0))
                heading = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0 if speed_mps > 0.1 else 0.0
                
                altitude = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
                
                # Get trajectory confidence
                trajectory_confidence = 0.0
                try:
                    from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
                    trajectory_data = TrajectoryTracker.get_trajectory(track_id)
                    trajectory_confidence = trajectory_data.get('confidence', 0.0)
                except Exception:
                    pass
                
                # Calculate data freshness
                timestamp_str = track.get('timestamp', '')
                data_freshness = "N/A"
                try:
                    if timestamp_str:
                        if isinstance(timestamp_str, str):
                            track_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            track_time = timestamp_str
                        age_seconds = (datetime.now() - track_time).total_seconds()
                        data_freshness = f"{int(age_seconds)}s ago"
                except Exception:
                    pass
                
                # Build structured multi-line hover tooltip
                # Readable, no overflow, no HTML leakage
                # Use Plotly's native <br> for line breaks only
                
                # Determine mode (Live / Simulation)
                is_simulation = track.get('is_simulation', False) or track.get('simulation_label', '')
                mode = "Simulation" if is_simulation else "Live"
                
                # Primary Radar (visual attribution - which radar is tracking this)
                primary_radar = track.get('primary_radar', track.get('sensor_id', 'Multi-Sensor'))
                if not primary_radar or primary_radar == 'N/A':
                    primary_radar = "Multi-Sensor"
                
                # Classification with confidence
                classification = str(track.get('classification', obj_type)).upper()
                if classification == 'UNKNOWN' or not classification:
                    classification = obj_type
                
                # Build structured tooltip
                hover_text = (
                    f"Track ID: {track_id}<br>"
                    f"Classification: {classification}<br>"
                    f"Altitude: {altitude:.0f} m<br>"
                    f"Speed: {speed_mps * 3.6:.0f} km/h<br>"
                    f"Heading: {heading:.1f}°<br>"
                    f"Confidence: {confidence_val:.1%}<br>"
                    f"Primary Radar: {primary_radar}<br>"
                    f"Mode: {mode}"
                )
                hover_texts.append(hover_text)
                
                # Get color based on threat level
                threat_level = str(track.get('threat_level', 'NONE'))
                theme = SeverityThemeController.get_theme(threat_level, False)
                colors.append(theme.get('primary', '#4A90E2'))
                
                # Add confidence ring only if the UI option is enabled
                if show_confidence_rings and confidence_val > 0:
                    # Get EW state for confidence ring degradation visualization
                    ew_state = None
                    try:
                        from abhedya.dashboard.state_manager import DashboardStateManager
                        ew_state = DashboardStateManager.get_ew_environment_state() if DashboardStateManager else None
                    except Exception:
                        pass
                    
                    AirspaceVisualization._add_confidence_ring(
                        fig,
                        (x_val, y_val),
                        confidence_val,
                        ew_state=ew_state
                    )
            
            # Add trajectory visualization layers (trail, velocity vector, prediction cone)
            for i, track in enumerate(tracks):
                if not isinstance(track, dict):
                    continue
                
                track_id = str(track.get('track_id', f'track_{i}'))
                pos = track.get('position', {})
                vel = track.get('velocity', {})
                
                if not isinstance(pos, dict) or not isinstance(vel, dict):
                    continue
                
                x = x_coords[i] if i < len(x_coords) else 0.0
                y = y_coords[i] if i < len(y_coords) else 0.0
                
                vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
                vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
                
                # Update trajectory history
                try:
                    from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
                    TrajectoryTracker.update_track_history(track)
                    
                    # Get trajectory data
                    trajectory_data = TrajectoryTracker.get_trajectory(track_id)
                    history = trajectory_data.get('history', [])
                    predicted_path = trajectory_data.get('predicted_path', [])
                    trajectory_confidence = trajectory_data.get('confidence', 0.5)
                    
                    # Add trajectory trail (thin lines behind moving targets, color-coded by classification)
                    if history and len(history) > 1:
                        from abhedya.dashboard.trajectory_visualization import TrajectoryVisualization
                        # Get color based on track classification (color-coded trails)
                        threat_level = str(track.get('threat_level', 'NONE'))
                        classification = str(track.get('classification', 'UNKNOWN')).upper()
                        
                        # Color-code by classification
                        if classification == 'HOSTILE':
                            trail_color = '#FF4D4F'  # Red for hostile
                        elif classification == 'FRIENDLY':
                            trail_color = '#52C41A'  # Green for friendly
                        elif classification == 'UNKNOWN':
                            trail_color = '#FAAD14'  # Amber for unknown
                        else:
                            # Fallback to threat level theme
                            theme = SeverityThemeController.get_theme(threat_level, training_mode)
                            trail_color = theme.get('primary', '#4A90E2')
                        
                        # Add trail with fixed-length window and gradual fade
                        TrajectoryVisualization.add_trajectory_trail(
                            fig, track_id, history, trail_color,
                            max_trail_points=60,  # Fixed-length trail window (60 points)
                            max_trail_age_seconds=120.0  # 2 minutes max age
                        )
                    
                    # Add velocity vector (current velocity arrow)
                    if training_mode or len(history) > 0:  # Show in training mode or if we have history
                        from abhedya.dashboard.trajectory_visualization import TrajectoryVisualization
                        TrajectoryVisualization.add_velocity_vector(
                            fig, x, y, vx, vy,
                            speed_scale=1.0,
                            color='rgba(74, 144, 226, 0.4)'  # Subtle opacity
                        )
                    
                    # Add prediction cone (uncertainty fan)
                    if predicted_path and len(predicted_path) > 0:
                        from abhedya.dashboard.trajectory_visualization import TrajectoryVisualization
                        TrajectoryVisualization.add_prediction_cone(
                            fig, x, y, vx, vy,
                            prediction_horizon=20.0,  # 20 seconds
                            uncertainty_angle=15.0,  # 15 degree spread
                            confidence=trajectory_confidence,
                            color='rgba(250, 173, 20, 0.15)',  # Semi-transparent amber
                            atmospheric_conditions=atmospheric_conditions
                        )
                except Exception:
                    # Fail silently - trajectory visualization is non-critical
                    pass
            
            # Add track markers (only if we have valid coordinates). Use markers
            # only (no inline text) to keep the radar uncluttered.
            if x_coords and y_coords:
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    marker=dict(
                        size=15,
                        color=colors if colors else ['#4A90E2'] * len(x_coords),
                        symbol='circle',
                        line=dict(width=2, color='white')
                    ),
                    name=str(group_name),
                    hovertemplate='%{hovertext}<extra></extra>',
                    hovertext=hover_texts if hover_texts else [''] * len(x_coords),
                    showlegend=True
                ))
        except Exception:
            # Fail silently - don't crash visualization
            pass
    
    @staticmethod
    def _add_confidence_ring(fig: go.Figure, center: Tuple[float, float], confidence: float, max_radius: float = 5000.0, ew_state: Optional[str] = None):
        """
        Add confidence ring around track with EW degradation visualization.
        
        ADVISORY ONLY — TRACK-LEVEL TRUST CUE
        - Confidence ring opacity reduced under EW
        - Tooltip: "Confidence reduced due to EW interference"
        - NO flashing, NO aggressive colors
        
        Args:
            fig: Plotly figure
            center: Center coordinates (x, y)
            confidence: Confidence value [0.0, 1.0]
            max_radius: Maximum radius in meters
            ew_state: EW environment state (optional)
        """
        # Input validation
        if not isinstance(fig, go.Figure):
            return
        
        try:
            if not isinstance(center, (tuple, list)) or len(center) < 2:
                return
            
            center_x = float(center[0]) if isinstance(center[0], (int, float)) else 0.0
            center_y = float(center[1]) if isinstance(center[1], (int, float)) else 0.0
            confidence = max(0.0, min(1.0, float(confidence))) if isinstance(confidence, (int, float)) else 0.0
            max_radius = max(100.0, min(100000.0, float(max_radius))) if isinstance(max_radius, (int, float)) else 5000.0
            
            # Apply EW degradation to confidence ring opacity
            ring_opacity = 0.3  # Base opacity
            hover_text = f"Confidence: {confidence:.1%}"
            
            if ew_state and ew_state.upper() not in ['NONE', 'NORMAL']:
                # Reduce opacity under EW (subtle visual cue)
                ew_state_upper = ew_state.upper()
                if ew_state_upper == 'LOW':
                    ring_opacity = 0.25
                elif ew_state_upper == 'MEDIUM':
                    ring_opacity = 0.20
                elif ew_state_upper == 'HIGH':
                    ring_opacity = 0.15
                
                hover_text = f"Confidence: {confidence:.1%} — Reduced due to EW interference (Advisory)"
            
            radius = confidence * max_radius
            theta = [i * 2 * math.pi / 100 for i in range(101)]
            x = [center_x + radius * math.cos(t) for t in theta]
            y = [center_y + radius * math.sin(t) for t in theta]
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                line=dict(color=f'rgba(74, 144, 226, {ring_opacity})', width=2, dash='dot'),
                name='Confidence Ring',
                showlegend=False,
                hoverinfo='text',
                text=hover_text
            ))
        except Exception:
            # Fail silently
            pass


class ConfidenceGauge:
    """Confidence gauge component."""
    
    @staticmethod
    def render(confidence: float, label: str = "Confidence"):
        """
        Render confidence gauge.
        
        Args:
            confidence: Confidence value [0.0, 1.0]
            label: Label for gauge
        """
        # Input validation
        try:
            confidence = max(0.0, min(1.0, float(confidence))) if isinstance(confidence, (int, float)) else 0.0
            label = str(label) if label else "Confidence"
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+percent",
                value=confidence * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': label},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#4A90E2"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=200, autosize=True, automargin=True, margin=dict(l=60, r=10, t=50, b=50))
            try:
                fig.update_xaxes(automargin=True)
                fig.update_yaxes(automargin=True)
            except Exception:
                pass
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        except Exception:
            # Fail silently - don't crash dashboard
            pass


class TrendPlot:
    """Trend plot component."""
    
    @staticmethod
    def render(data: List[Dict[str, Any]], x_key: str, y_key: str, title: str = "Trend"):
        """
        Render trend plot.
        
        Args:
            data: List of data points
            x_key: Key for X axis
            y_key: Key for Y axis
            title: Plot title
        """
        # Input validation
        if not isinstance(data, list):
            st.info("No data available for trend plot.")
            return
        
        if not isinstance(x_key, str) or not x_key:
            x_key = 'x'
        
        if not isinstance(y_key, str) or not y_key:
            y_key = 'y'
        
        if not data:
            st.info("No data available for trend plot.")
            return
        
        try:
            df_data = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                x_val = item.get(x_key, 0)
                y_val = item.get(y_key, 0)
                
                # Validate numeric values
                try:
                    x_val = float(x_val) if isinstance(x_val, (int, float)) else 0.0
                    y_val = float(y_val) if isinstance(y_val, (int, float)) else 0.0
                except (ValueError, TypeError):
                    continue
                
                df_data.append({
                    'x': x_val,
                    'y': y_val
                })
            
            if not df_data:
                st.info("No valid data available for trend plot.")
                return
            
            import pandas as pd
            df = pd.DataFrame(df_data)
            
            safe_title = str(title).replace('<', '&lt;').replace('>', '&gt;') if title else "Trend"
            fig = px.line(df, x='x', y='y', title=safe_title)
            fig.update_layout(height=220, autosize=True, automargin=True, margin=dict(l=60, r=10, t=60, b=60))
            try:
                fig.update_xaxes(automargin=True)
                fig.update_yaxes(automargin=True)
            except Exception:
                pass
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        except Exception:
            # Fail silently - don't crash dashboard
            st.info("Error rendering trend plot.")
            pass


class SensorContributionPanel:
    """
    Sensor Contribution & Confidence Breakdown Panel.
    
    ADVISORY ONLY — VISUAL SIMULATION
    - No fire / launch / engage commands
    - No ROE logic
    - No autonomy
    - No while True loops
    - No time.sleep
    - No uncontrolled reruns
    - No randomness per rerun
    
    ADVISORY ONLY — NO AUTONOMOUS ACTIONS
    - No buttons
    - No decisions
    - No recommendations
    - Visualization only
    """
    
    # Sensor color mapping (matches sensor_models.py)
    SENSOR_COLORS = {
        "Surveillance Radar": "#52C41A",  # Green
        "Precision Tracking Radar": "#1890FF",  # Blue
        "Passive RF / ESM": "#722ED1"  # Purple
    }
    
    @staticmethod
    def compute_fused_confidence(track: Dict[str, Any]) -> float:
        """
        Compute fused confidence as weighted sum of sensor contributions.
        
        ADVISORY ONLY — EXPLAINABLE, NOT DECISIONAL
        - Does NOT change existing confidence outputs
        - Only explains them visually
        - Weighted sum: sum(contribution * sensor_confidence)
        
        Args:
            track: Track dictionary with sensor_contributions and confidence
            
        Returns:
            Fused confidence value (0.0-1.0)
        """
        try:
            if not isinstance(track, dict):
                return 0.0
            
            # Get base confidence
            base_confidence = float(track.get("confidence", 0.0))
            base_confidence = max(0.0, min(1.0, base_confidence))
            
            # Get sensor contributions
            contributions = track.get("sensor_contributions", {})
            if not isinstance(contributions, dict) or not contributions:
                # No contributions available, return base confidence
                return base_confidence
            
            # Compute weighted sum (simplified: assume each sensor contributes proportionally)
            # In reality, this would be: sum(contribution * sensor_confidence)
            # For visualization, we use the base confidence weighted by contributions
            total_contribution = sum(float(v) for v in contributions.values() if isinstance(v, (int, float)))
            
            if total_contribution > 0:
                # Normalize contributions and compute weighted average
                # Simplified model: higher contribution = higher confidence weight
                weighted_sum = 0.0
                for sensor_name, contribution in contributions.items():
                    if isinstance(contribution, (int, float)):
                        # Assume sensor confidence scales with contribution
                        sensor_confidence = base_confidence * (0.8 + 0.2 * contribution)
                        weighted_sum += contribution * sensor_confidence
                
                fused = weighted_sum / total_contribution if total_contribution > 0 else base_confidence
                return max(0.0, min(1.0, fused))
            else:
                return base_confidence
        except Exception:
            # Fail-safe: return base confidence
            return float(track.get("confidence", 0.0)) if isinstance(track, dict) else 0.0
    
    @staticmethod
    def render_sensor_contribution_panel(track: Dict[str, Any], training_mode: bool = False, ew_state: Optional[str] = None):
        """
        Render sensor contribution panel for a track with EW reliability visualization.
        
        ADVISORY ONLY — NO AUTONOMOUS ACTIONS
        - No buttons
        - No decisions
        - No recommendations
        
        Args:
            track: Track dictionary with sensor_contributions
            training_mode: Whether training mode is enabled
            ew_state: EW environment state (NONE, LOW, MEDIUM, HIGH) - optional
        """
        try:
            if not isinstance(track, dict):
                st.info("No track data available.")
                return
            
            # Get sensor contributions
            contributions = track.get("sensor_contributions", {})
            if not isinstance(contributions, dict) or not contributions:
                # Live mode placeholder
                st.info("⚠️ Sensor contribution data not available (Live Mode — Placeholder)")
                st.caption("Advisory Only — No Autonomous Actions")
                return
            
            # Get EW state (default to NONE if not provided)
            if ew_state is None:
                try:
                    from abhedya.dashboard.state_manager import DashboardStateManager
                    ew_data = DashboardStateManager.get_ew_analysis_data() if DashboardStateManager else None
                    ew_state = ew_data.get("ew_state", "NONE") if ew_data else "NONE"
                except Exception:
                    ew_state = "NONE"
            
            # Safety disclaimer
            st.caption("⚠️ Advisory Only — No Autonomous Actions")
            
            # Training mode labeling
            if training_mode:
                st.markdown("**SIMULATION / TRAINING DATA**")
                st.caption("Synthetic sensor weighting — for visualization only")
            
            # Compute fused confidence
            fused_confidence = SensorContributionPanel.compute_fused_confidence(track)
            base_confidence = float(track.get("confidence", 0.0))
            
            # Compute EW-degraded confidence
            try:
                from abhedya.dashboard.visual_components import EWReliabilityModel
                ew_degraded_confidence = EWReliabilityModel.compute_ew_degraded_confidence(
                    base_confidence, contributions, ew_state, training_mode
                )
            except Exception:
                ew_degraded_confidence = fused_confidence
            
            # Display fused confidence (with EW degradation indicator if applicable)
            st.markdown("**Fused Confidence**")
            st.progress(fused_confidence)
            if ew_state != "NONE" and ew_state != "NORMAL":
                st.caption(f"{fused_confidence * 100:.1f}% (base) → {ew_degraded_confidence * 100:.1f}% (EW-adjusted)")
                st.caption("⚠️ Confidence reduced due to EW interference (Advisory)")
            else:
                st.caption(f"{fused_confidence * 100:.1f}% (weighted sum of sensor contributions)")
            
            # Display individual sensor contributions with reliability
            st.markdown("**Sensor Contributions & Reliability**")
            st.caption("Contribution reflects data quality & geometry — advisory only")
            
            # Render contribution bars with reliability indicators
            for sensor_name, contribution in sorted(contributions.items(), key=lambda x: x[1], reverse=True):
                if not isinstance(contribution, (int, float)):
                    continue
                
                contribution = max(0.0, min(1.0, float(contribution)))
                percent = contribution * 100.0
                
                # Get sensor color
                color = SensorContributionPanel.SENSOR_COLORS.get(sensor_name, "#666666")
                
                # Get sensor reliability
                try:
                    from abhedya.dashboard.visual_components import EWReliabilityModel
                    sensor_type = EWReliabilityModel.map_sensor_name_to_type(sensor_name)
                    reliability_data = EWReliabilityModel.get_sensor_reliability(sensor_type, ew_state, training_mode)
                    reliability_score = reliability_data.get("reliability_score", 1.0)
                    status = reliability_data.get("status", "NORMAL")
                    explanation = reliability_data.get("explanation", "")
                except Exception:
                    reliability_score = 1.0
                    status = "NORMAL"
                    explanation = ""
                
                # Determine visual styling based on reliability
                is_degraded = reliability_score < 0.80
                is_jammed = reliability_score < 0.50
                
                # Color-code by reliability
                if is_jammed:
                    bar_color = "#888888"  # Grey for jammed
                    opacity = 0.4
                elif is_degraded:
                    bar_color = "#FFA940"  # Orange for degraded
                    opacity = 0.7
                else:
                    bar_color = color  # Normal color
                    opacity = 1.0
                
                # Render bar
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(
                        f'<div style="background-color:{bar_color}; height:24px; width:{percent}%; '
                        f'border-radius:4px; margin-bottom:4px; opacity:{opacity};"></div>',
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(f"**{percent:.1f}%**")
                
                # Sensor name, reliability, and status
                reliability_percent = reliability_score * 100.0
                status_badge = ""
                if status == "JAMMED":
                    status_badge = " 🔴 JAMMED"
                elif status == "DEGRADED":
                    status_badge = " 🟠 DEGRADED"
                else:
                    status_badge = " 🟢 NORMAL"
                
                st.markdown(
                    f"<small><strong>{sensor_name}</strong>{status_badge} — Reliability: {reliability_percent:.0f}%</small>",
                    unsafe_allow_html=True
                )
                
                # Show explanation on hover (via tooltip text)
                if explanation and ew_state != "NONE" and ew_state != "NORMAL":
                    st.caption(f"ℹ️ {explanation}")
            
            # Tooltip text
            st.caption("ℹ️ Contribution reflects data quality & geometry — advisory only")
            
        except Exception:
            # Fail gracefully - don't crash dashboard
            st.info("Error rendering sensor contribution panel.")
            pass


class EWReliabilityModel:
    """
    Electronic Warfare Reliability Model (Display-Only).
    
    ADVISORY ONLY — VISUAL SIMULATION
    - No fire / launch / engage commands
    - NO control logic
    - NO autonomous decisions
    - NO while True loops
    - NO time.sleep
    - NO uncontrolled reruns
    - NO randomness per rerun
    
    STRICT CONSTRAINTS:
    - Deterministic, explainable behavior only
    - EW effects NEVER delete tracks or cause hard failures
    - EW only affects confidence, reliability, and visualization trust
    - Must work identically in LIVE and TRAINING / SIMULATION mode
    """
    
    # EW Environment States
    EW_STATE_NONE = "NONE"
    EW_STATE_LOW = "LOW"
    EW_STATE_MEDIUM = "MEDIUM"
    EW_STATE_HIGH = "HIGH"
    
    # Sensor Types
    SENSOR_RADAR = "Radar"
    SENSOR_EO_IR = "EO / IR"
    SENSOR_PASSIVE_RF = "Passive RF / ESM"
    
    # Sensor Status Labels
    STATUS_NORMAL = "NORMAL"
    STATUS_DEGRADED = "DEGRADED"
    STATUS_JAMMED = "JAMMED"
    
    @staticmethod
    def get_sensor_reliability(sensor_type: str, ew_state: str, training_mode: bool = False) -> Dict[str, Any]:
        """
        Compute sensor reliability based on EW environment state.
        
        ADVISORY ONLY — DISPLAY-ONLY
        - Deterministic mapping: EW state → reliability score
        - NO random behavior
        - Reliability depends only on EW state and sensor type
        
        Args:
            sensor_type: Sensor type (Radar, EO / IR, Passive RF / ESM)
            ew_state: EW environment state (NONE, LOW, MEDIUM, HIGH)
            training_mode: Whether training mode is enabled (for slightly exaggerated effects)
            
        Returns:
            Dictionary with:
            - reliability_score: float [0.0, 1.0]
            - status: str (NORMAL / DEGRADED / JAMMED)
            - explanation: str (human-readable)
        """
        try:
            # Normalize inputs
            ew_state = str(ew_state).upper() if ew_state else EWReliabilityModel.EW_STATE_NONE
            sensor_type = str(sensor_type) if sensor_type else EWReliabilityModel.SENSOR_RADAR
            
            # Default to NONE if invalid
            if ew_state not in [EWReliabilityModel.EW_STATE_NONE, EWReliabilityModel.EW_STATE_LOW,
                               EWReliabilityModel.EW_STATE_MEDIUM, EWReliabilityModel.EW_STATE_HIGH]:
                ew_state = EWReliabilityModel.EW_STATE_NONE
            
            # Base reliability scores by EW state and sensor type
            # Deterministic mapping (no randomness)
            reliability_map = {
                EWReliabilityModel.EW_STATE_NONE: {
                    EWReliabilityModel.SENSOR_RADAR: 1.0,
                    EWReliabilityModel.SENSOR_EO_IR: 1.0,
                    EWReliabilityModel.SENSOR_PASSIVE_RF: 1.0
                },
                EWReliabilityModel.EW_STATE_LOW: {
                    EWReliabilityModel.SENSOR_RADAR: 0.85,  # Radar slightly affected
                    EWReliabilityModel.SENSOR_EO_IR: 0.95,   # EO/IR mostly unaffected
                    EWReliabilityModel.SENSOR_PASSIVE_RF: 0.90  # Passive RF slightly affected
                },
                EWReliabilityModel.EW_STATE_MEDIUM: {
                    EWReliabilityModel.SENSOR_RADAR: 0.65,  # Radar moderately affected
                    EWReliabilityModel.SENSOR_EO_IR: 0.85,  # EO/IR partially compensates
                    EWReliabilityModel.SENSOR_PASSIVE_RF: 0.70  # Passive RF moderately affected
                },
                EWReliabilityModel.EW_STATE_HIGH: {
                    EWReliabilityModel.SENSOR_RADAR: 0.40,  # Radar significantly affected
                    EWReliabilityModel.SENSOR_EO_IR: 0.70,  # EO/IR partially compensates
                    EWReliabilityModel.SENSOR_PASSIVE_RF: 0.50  # Passive RF significantly affected
                }
            }
            
            # Get base reliability
            base_reliability = reliability_map.get(ew_state, {}).get(sensor_type, 1.0)
            
            # Slightly exaggerate effects in training mode for learning clarity
            if training_mode and ew_state != EWReliabilityModel.EW_STATE_NONE:
                # Reduce reliability by additional 5-10% in training mode
                exaggeration_factor = 0.05 if ew_state == EWReliabilityModel.EW_STATE_LOW else (
                    0.08 if ew_state == EWReliabilityModel.EW_STATE_MEDIUM else 0.10
                )
                base_reliability = max(0.0, base_reliability - exaggeration_factor)
            
            # Determine status label
            if base_reliability >= 0.80:
                status = EWReliabilityModel.STATUS_NORMAL
            elif base_reliability >= 0.50:
                status = EWReliabilityModel.STATUS_DEGRADED
            else:
                status = EWReliabilityModel.STATUS_JAMMED
            
            # Generate explanation text
            if ew_state == EWReliabilityModel.EW_STATE_NONE:
                explanation = f"{sensor_type} operating normally. No EW interference detected."
            elif sensor_type == EWReliabilityModel.SENSOR_RADAR:
                explanation = f"Radar reliability reduced due to {ew_state.lower()} EW environment. Active emissions may be jammed or spoofed."
            elif sensor_type == EWReliabilityModel.SENSOR_EO_IR:
                explanation = f"EO/IR sensor partially compensates for EW. Optical sensors less affected by RF interference."
            elif sensor_type == EWReliabilityModel.SENSOR_PASSIVE_RF:
                explanation = f"Passive RF/ESM reliability reduced due to {ew_state.lower()} EW environment. Signal discrimination may be degraded."
            else:
                explanation = f"Sensor reliability affected by {ew_state.lower()} EW environment."
            
            return {
                "reliability_score": max(0.0, min(1.0, base_reliability)),
                "status": status,
                "explanation": explanation
            }
        except Exception:
            # Fail-safe: return normal reliability
            return {
                "reliability_score": 1.0,
                "status": EWReliabilityModel.STATUS_NORMAL,
                "explanation": "Reliability data unavailable. Assuming normal operation."
            }
    
    @staticmethod
    def map_sensor_name_to_type(sensor_name: str) -> str:
        """
        Map sensor contribution name to sensor type.
        
        Args:
            sensor_name: Sensor name from contribution dictionary
            
        Returns:
            Sensor type string
        """
        sensor_name_lower = str(sensor_name).lower()
        if "radar" in sensor_name_lower and "passive" not in sensor_name_lower:
            return EWReliabilityModel.SENSOR_RADAR
        elif "passive" in sensor_name_lower or "esm" in sensor_name_lower:
            return EWReliabilityModel.SENSOR_PASSIVE_RF
        elif "eo" in sensor_name_lower or "ir" in sensor_name_lower or "optical" in sensor_name_lower:
            return EWReliabilityModel.SENSOR_EO_IR
        else:
            # Default to Radar for unknown sensors
            return EWReliabilityModel.SENSOR_RADAR
    
    @staticmethod
    def compute_ew_degraded_confidence(base_confidence: float, sensor_contributions: Dict[str, float], 
                                       ew_state: str, training_mode: bool = False) -> float:
        """
        Compute confidence degraded by EW effects.
        
        ADVISORY ONLY — DISPLAY-ONLY
        - Confidence NEVER snaps to zero
        - Smooth degradation based on sensor reliability
        - Track NEVER disappears due to EW alone
        
        Args:
            base_confidence: Base track confidence [0.0, 1.0]
            sensor_contributions: Dictionary of sensor name -> contribution weight
            ew_state: EW environment state
            training_mode: Whether training mode is enabled
            
        Returns:
            Degraded confidence value [0.0, 1.0] (never zero)
        """
        try:
            if not isinstance(sensor_contributions, dict) or not sensor_contributions:
                return base_confidence
            
            # Compute weighted average reliability
            total_weight = 0.0
            weighted_reliability = 0.0
            
            for sensor_name, contribution in sensor_contributions.items():
                if not isinstance(contribution, (int, float)):
                    continue
                
                contribution = max(0.0, min(1.0, float(contribution)))
                sensor_type = EWReliabilityModel.map_sensor_name_to_type(sensor_name)
                reliability_data = EWReliabilityModel.get_sensor_reliability(sensor_type, ew_state, training_mode)
                reliability_score = reliability_data.get("reliability_score", 1.0)
                
                weighted_reliability += contribution * reliability_score
                total_weight += contribution
            
            # Average reliability across all sensors
            avg_reliability = weighted_reliability / total_weight if total_weight > 0 else 1.0
            
            # Apply degradation: confidence = base_confidence * avg_reliability
            # But ensure it never goes below a minimum threshold (e.g., 0.1)
            degraded_confidence = base_confidence * avg_reliability
            degraded_confidence = max(0.1, degraded_confidence)  # Never below 10%
            
            return max(0.0, min(1.0, degraded_confidence))
        except Exception:
            # Fail-safe: return base confidence
            return base_confidence

