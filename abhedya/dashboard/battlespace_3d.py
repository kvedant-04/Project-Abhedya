"""
3D Battlespace Visualization Module

Provides 3D visualization of airspace, tracks, and interception sequences.
ADVISORY ONLY — SENSOR VISUALIZATION. NO CONTROL OR DECISION LOGIC.

ADVISORY ONLY - Visualization and simulation only, no control logic.

STRICT CONSTRAINTS:
- Visualization only, no autonomous actions
- No weapon control or interception logic
- All outputs are advisory and informational
- Human-in-the-loop required for all interpretations
- Visual indication only — geometric overlap within coverage volumes
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import math
import hashlib

# Import streamlit only for session state access (no UI rendering in this module)
try:
    import streamlit as st
except ImportError:
    st = None

# Threat classification → marker color (VISUAL ONLY, advisory). Markers only; trajectories unchanged.
CLASSIFICATION_COLOR_MAP = {
    "Friendly": "#2ECC71",
    "Civil": "#2ECC71",
    "Unknown": "#F1C40F",
    "Hostile": "#E74C3C",
}

# Critical zone radius (m) for TTC — must match zone definition. Advisory only.
TTC_CRITICAL_RADIUS_M = 5000.0


def compute_ttc_seconds(track: Dict[str, Any], asset_pos: Dict[str, float], critical_radius_m: float) -> Optional[float]:
    """
    Advisory TTC (time to critical zone boundary) assuming straight-line motion.
    Does NOT mutate anything; does NOT use sim_time or prediction. Deterministic.
    Returns None if not applicable.
    """
    try:
        pos = track.get("position") if isinstance(track.get("position"), dict) else {}
        tx = float(pos.get("x", 0.0))
        ty = float(pos.get("y", 0.0))
        ax = float(asset_pos.get("x", 0.0))
        ay = float(asset_pos.get("y", 0.0))
        dx = ax - tx
        dy = ay - ty
        distance = (dx * dx + dy * dy) ** 0.5
        speed = track.get("speed_mps")
        if speed is None or not isinstance(speed, (int, float)):
            vel = track.get("velocity") if isinstance(track.get("velocity"), dict) else {}
            vx = float(vel.get("vx", 0.0))
            vy = float(vel.get("vy", 0.0))
            vz = float(vel.get("vz", 0.0))
            speed = (vx * vx + vy * vy + vz * vz) ** 0.5
        if not speed or speed <= 0:
            return None
        remaining = distance - critical_radius_m
        if remaining <= 0:
            return 0.0
        return remaining / speed
    except Exception:
        return None


def get_urgency_level(ttc_seconds: Optional[float]) -> Optional[str]:
    """Urgency from TTC (locked): TTC > 180 → LOW, 60 < TTC ≤ 180 → MEDIUM, TTC ≤ 60 → HIGH."""
    if ttc_seconds is None:
        return None
    if ttc_seconds > 180.0:
        return "LOW"
    if ttc_seconds > 60.0:
        return "MEDIUM"
    return "HIGH"


class Battlespace3D:
    """
    3D battlespace visualization component.
    
    ADVISORY ONLY - Provides visualization of airspace, tracks, and
    engagement sequences. No control logic or autonomous actions.
    """
    
    @staticmethod
    def create_3d_visualization(
        tracks: List[Dict[str, Any]],
        defender_position: Optional[Dict[str, float]] = None,
        view_range: float = 50000.0,
        training_mode: bool = False,
        show_trajectories: bool = True,
        show_interception_windows: bool = False,
        interception_data: Optional[List[Dict[str, Any]]] = None,
        atmospheric_conditions: Optional[Dict[str, Any]] = None,
        show_atmospheric_overlay: bool = False,
        show_sensor_track_hints: bool = False,
        sensor_layer_controls: Optional[Dict[str, Any]] = None,
        show_protected_zones: bool = True,
        highlight_track_id: Optional[str] = None,
        sim_time: float = 0.0,
    ) -> go.Figure:
        """
        Create 3D battlespace visualization.
        
        Args:
            tracks: List of track dictionaries with position (x, y, z) and velocity
            defender_position: Defender position dict with x, y, z (defaults to origin)
            view_range: View range in meters
            training_mode: Whether training mode is enabled
            show_trajectories: Whether to show trajectory history/prediction
            show_interception_windows: Whether to show interception feasibility windows
            interception_data: Optional interception feasibility data for visualization
            
        Returns:
            Plotly 3D figure (empty figure on error)
        """
        # ===== BEGIN FIXED BLOCK =====

        # CRITICAL STEP 1: Guarantee track flow - ensure tracks are always a list
        if not isinstance(tracks, list):
            tracks = []

        assert isinstance(tracks, list), "tracks must be a list"

        # Training-mode fallback for simulation tracks
        if training_mode and (not tracks or len(tracks) == 0):
            try:
                import streamlit as st
                simulation_tracks = st.session_state.get("simulation_tracks", [])
                if isinstance(simulation_tracks, list) and simulation_tracks:
                    tracks = simulation_tracks
            except Exception:
                pass

        # Default defender position
        if defender_position is None:
            defender_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        view_range = (
            max(1000.0, min(1000000.0, float(view_range)))
            if isinstance(view_range, (int, float))
            else 50000.0
        )

        fig = go.Figure()

        # Initialize scene
        try:
            Battlespace3D._initialize_scene(fig, defender_position, view_range)
        except Exception:
            fig.add_trace(
                go.Scatter3d(
                    x=[0.0], y=[0.0], z=[0.0],
                    mode="markers",
                    marker=dict(size=1, color="rgba(0,0,0,0)"),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # Enforce single top-level hovermode for reliable hover selection
        fig.update_layout(hovermode="closest", scene=dict(hovermode="closest"))

        # CRITICAL: Set uirevision to unique value per rebuild.
        # Each scenario rebuild gets a new uirevision so Plotly re-renders instead of caching.
        import hashlib
        import time
        unique_seed = hashlib.md5(f"{time.time()}:{view_range}:{len(tracks or [])}".encode()).hexdigest()[:8]
        fig.layout.uirevision = f"battlespace_{unique_seed}"

        # Create empty placeholder traces for threat density and halo (for in-place mutation later)
        try:
            fig.add_trace(
                go.Scatter3d(
                    x=[], y=[], z=[],
                    mode='markers',
                    marker=dict(size=40, color='orange', opacity=0.25),
                    name='Threat Density (Advisory)',
                    showlegend=True,
                    hoverinfo='skip',
                    meta={'type': 'threat_density'}
                )
            )
            fig.add_trace(
                go.Scatter3d(
                    x=[], y=[], z=[],
                    mode='lines',
                    line=dict(color='rgba(255,200,100,0.5)', width=2),
                    name='Density Halo (Advisory)',
                    showlegend=True,
                    hoverinfo='skip',
                    meta={'type': 'density_halo'}
                )
            )
        except Exception:
            pass

        # Protected zones
        if show_protected_zones:
            Battlespace3D._add_protected_zones_3d(fig, defender_position, view_range)

        # ===== END FIXED BLOCK =====

            # Simulation time control (visual-only). This adds a Streamlit slider if Streamlit is available.
            try:
                if st is not None:
                    # Initialize sim_time in session state
                    if 'sim_time' not in st.session_state:
                        st.session_state['sim_time'] = 0.0
                    # Default max sim time (seconds) - align with trajectory prediction window used elsewhere
                    default_max = st.session_state.get('sim_time_max', 90.0)
                    sim_min = 0.0
                    sim_max = float(default_max)
                    # Render a slider UI element in the Streamlit app; changing it updates session_state['sim_time']
                    try:
                        sim_val = st.slider('Simulation Time (s)', min_value=sim_min, max_value=sim_max, value=float(st.session_state.get('sim_time', 0.0)), step=1.0, key='sim_time')
                        st.session_state['sim_time'] = float(sim_val)
                    except Exception:
                        # Fallback: ensure sim_time exists
                        st.session_state['sim_time'] = float(st.session_state.get('sim_time', 0.0))

                    # Note: Replay UI is provided by the main app; visualization honors `st.session_state['replay_time']` if present.
            except Exception:
                pass
            
            # Add comprehensive multi-radar sensor visualization (visual only, advisory)
            # Uses sensor_models.py for static sensor definitions
            # Get scenario key from session state if in training mode
            scenario_key = None
            if training_mode:
                try:
                    import streamlit as st
                    scenario_key = st.session_state.get("selected_scenario")
                except Exception:
                    scenario_key = None
            
            # Determine global opacity override from provided sensor_layer_controls (if any)
            global_opacity_override = None
            try:
                if isinstance(sensor_layer_controls, dict):
                    global_opacity_override = sensor_layer_controls.get('global_opacity')
            except Exception:
                global_opacity_override = None

            # CRITICAL STEP 3: Sensor volumes MUST render when toggles are ON
            # Sensors are core SAM C2 visualization elements - never skip
            # Pass sensor_layer_controls to ensure toggles are respected
            Battlespace3D._add_sensor_visualization_3d(
                fig, defender_position, view_range,
                scenario_key=scenario_key,
                training_mode=training_mode,
                sensor_layer_controls=sensor_layer_controls,  # CRITICAL: Pass controls to respect toggles
                global_opacity_override=global_opacity_override,
                tracks=tracks
            )
            
            # CRITICAL: Always add atmospheric layers when enabled - never skip
            # Atmospheric layers MUST render when toggle is ON and conditions exist
            if show_atmospheric_overlay and atmospheric_conditions:
                Battlespace3D._add_atmospheric_layers_3d(
                    fig, defender_position, view_range, atmospheric_conditions, training_mode=training_mode
                )
            # If atmospheric overlay is enabled but conditions are missing, try to get from session state
            elif show_atmospheric_overlay and training_mode:
                try:
                    import streamlit as st
                    fallback_conditions = st.session_state.get("atmospheric_conditions")
                    if fallback_conditions:
                        Battlespace3D._add_atmospheric_layers_3d(
                            fig, defender_position, view_range, fallback_conditions, training_mode=training_mode
                        )
                except Exception:
                    pass  # Fail silently if atmospheric rendering unavailable
            
            # CRITICAL STEP 1: Guarantee track flow - MANDATORY CHECK
            # Tracks MUST render when data exists - this is the PRIMARY rendering function
            highlight_center = None
            tracks_to_render = tracks  # Use tracks parameter directly
            
            # MANDATORY CHECK: Assert tracks_to_render is a list
            assert isinstance(tracks_to_render, list), "tracks_to_render must be a list"
            
            # CRITICAL: YOU MUST CALL _add_tracks_3d() IF TRACKS EXIST
            # If this function is not called → NOTHING WILL RENDER
            if len(tracks_to_render) > 0:
                highlight_center = Battlespace3D._add_tracks_3d(
                    fig, tracks_to_render, defender_position,
                    show_trajectories=show_trajectories,
                    training_mode=training_mode,
                    highlight_track_id=highlight_track_id
                )
                # After tracks added, ensure a single legend entry for objects and trajectories
                try:
                    # Representative legend entry for objects
                    # Representative legend entry for trajectories (single semantic entry)
                    if any([d for d in fig.data if getattr(d, 'legendgroup', None) == 'trajectories']):
                        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='rgba(200,200,200,0.9)', width=4), name='Object Trajectories', legendgroup='trajectories', showlegend=True, hoverinfo='skip'))
                except Exception:
                    pass
                # DEBUG: Verify traces were added (can be removed after verification)
                # trace_count_after_tracks = len(fig.data)
                # print(f"DEBUG: Added tracks, trace count: {trace_count_after_tracks}")
            
            # If there are no tracks, do not add in-plot annotations (visuals should remain clean).
            # Upstream callers (Streamlit UI) may display warnings outside the plot.
            if not tracks_to_render or len(tracks_to_render) == 0:
                # No in-plot annotation to avoid clutter; keep scene minimal.
                pass
            
            # Add optional sensor-track visual hints (faint, dotted lines)
            # CRITICAL: Use tracks_to_render for consistency
            if show_sensor_track_hints and tracks_to_render and len(tracks_to_render) > 0:
                Battlespace3D._add_sensor_track_hints_3d(
                    fig, tracks_to_render, defender_position, view_range
                )
            
            # Add interception windows if requested
            if show_interception_windows and interception_data:
                Battlespace3D._add_interception_windows_3d(
                    fig, interception_data, defender_position
                )
            
            # CRITICAL: Compute actual extents from tracks for balanced axis ranges
            # This prevents the "vertical line collapse" issue and ensures cube mode works
            x_min, x_max = -view_range / 1000.0, view_range / 1000.0  # km
            y_min, y_max = -view_range / 1000.0, view_range / 1000.0  # km
            z_min, z_max = 0.0, view_range * 0.5  # meters
            
            # Compute scene center for camera positioning
            scene_center_x_km = 0.0
            scene_center_y_km = 0.0
            scene_center_z_m = view_range * 0.25  # Default to quarter altitude
            
            if tracks_to_render and len(tracks_to_render) > 0:
                # Compute actual track extents
                track_x_km = []
                track_y_km = []
                track_z_m = []
                
                for track in tracks_to_render:
                    if not isinstance(track, dict):
                        continue
                    pos = track.get('position', {})
                    if not isinstance(pos, dict):
                        continue
                    
                    x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
                    y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
                    z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
                    
                    track_x_km.append(x / 1000.0)
                    track_y_km.append(y / 1000.0)
                    track_z_m.append(z)
                
                if track_x_km and track_y_km and track_z_m:
                    # Compute centers
                    x_center = (max(track_x_km) + min(track_x_km)) / 2.0
                    y_center = (max(track_y_km) + min(track_y_km)) / 2.0
                    z_center = (max(track_z_m) + min(track_z_m)) / 2.0 if track_z_m else 5000.0
                    
                    # Compute ranges with padding (30% margin for visibility)
                    x_range = max(track_x_km) - min(track_x_km)
                    y_range = max(track_y_km) - min(track_y_km)
                    z_range = max(track_z_m) - min(track_z_m) if track_z_m else 10000.0
                    
                    # Ensure minimum ranges for proper cube visualization
                    x_range = max(x_range, 20.0)  # At least 20 km
                    y_range = max(y_range, 20.0)
                    z_range = max(z_range, 10000.0)  # At least 10 km altitude
                    
                    # Set ranges with padding
                    x_min = x_center - x_range * 0.65
                    x_max = x_center + x_range * 0.65
                    y_min = y_center - y_range * 0.65
                    y_max = y_center + y_range * 0.65
                    z_min = max(0.0, z_center - z_range * 0.65)
                    z_max = z_center + z_range * 0.65
                    
                    # Update scene center for camera
                    scene_center_x_km = x_center
                    scene_center_y_km = y_center
                    scene_center_z_m = z_center
            
            # Convert view_range to km for display
            view_range_km = view_range / 1000.0
            
            # Update layout for 3D - Light Tactical Command Theme
            title_text = "3D Battlespace Visualization (Advisory Only)"
            if training_mode:
                title_text += " — SIMULATION / TRAINING DATA"
            
            # Deep blue-grey background (#111827 = rgb(17, 24, 39))
            tactical_bg_color = 'rgb(17, 24, 39)'  # #111827
            
            # CRITICAL: Compute camera position to show full battlespace on initial render
            # Camera center should be at the scene center (computed from data or default)
            if highlight_center:
                try:
                    cx_km, cy_km, cz_m = highlight_center
                    camera_center = dict(x=cx_km, y=cy_km, z=cz_m)
                except Exception:
                    # Fallback to scene center
                    camera_center = dict(x=scene_center_x_km, y=scene_center_y_km, z=scene_center_z_m)
            else:
                # Use computed scene center (from tracks or default)
                camera_center = dict(x=scene_center_x_km, y=scene_center_y_km, z=scene_center_z_m)
            
            # CRITICAL: Compute camera eye position to show full battlespace cube
            # Calculate distance needed to see the full extent
            x_span = x_max - x_min
            y_span = y_max - y_min
            z_span = z_max - z_min
            
            # Find the maximum span (in equivalent units for cube mode)
            # For cube mode, we need to normalize Z to km scale
            z_span_km = z_span / 1000.0  # Convert meters to km for comparison
            max_span = max(x_span, y_span, z_span_km)
            
            # Camera distance: 1.5x the maximum span to show full cube with margin
            camera_distance = max_span * 1.5
            
            # Isometric view: equal angles for X, Y, Z visibility
            # Eye position: offset from center at isometric angle
            camera_eye_x = camera_center['x'] + camera_distance * 0.707  # cos(45°)
            camera_eye_y = camera_center['y'] + camera_distance * 0.707  # sin(45°)
            # NOTE: X/Y are in kilometers, Z is in meters. Convert camera_distance (km)
            # to meters before adding to the Z coordinate to avoid mixing units.
            # Ensure camera has a natural tilted angle (not top-down).
            camera_eye_z = camera_center['z'] + max(2000.0, (camera_distance * 1000.0) * 0.45)

            # Compute manual aspect ratio to avoid Z dominating due to unit differences
            try:
                # x_span and y_span are in km, z_span is in meters; convert z to km for ratio math
                x_span_km = max(0.0001, float(x_span))
                y_span_km = max(0.0001, float(y_span))
                z_span_km = max(0.0001, float(z_span) / 1000.0)

                # Normalize spans relative to the largest span
                norm_max = max(x_span_km, y_span_km, z_span_km, 1.0)
                rx = x_span_km / norm_max
                ry = y_span_km / norm_max
                rz = z_span_km / norm_max

                # Compress altitude influence so Z does not visually overpower X/Y.
                # Use a mild power <1 to reduce dominance of very large altitude ranges
                try:
                    rz_compressed = float(rz) ** 0.6
                except Exception:
                    rz_compressed = rz

                # Clamp ratios to avoid extreme pillar or pancake shapes
                min_xy_ratio = 0.20
                max_xy_ratio = 1.0
                min_z_ratio = 0.20
                max_z_ratio = 0.80

                aspect_x = max(min_xy_ratio, min(max_xy_ratio, float(rx)))
                aspect_y = max(min_xy_ratio, min(max_xy_ratio, float(ry)))
                aspect_z = max(min_z_ratio, min(max_z_ratio, float(rz_compressed)))

                # Normalize the final aspect ratios so they are relative proportions
                s = aspect_x + aspect_y + aspect_z
                if s > 0:
                    aspect_x /= s
                    aspect_y /= s
                    aspect_z /= s
            except Exception:
                # Fallback balanced aspect
                aspect_x = 1.0
                aspect_y = 1.0
                aspect_z = 0.5

            # Compute a stable relative camera eye (Plotly expects eye values as relative vectors)
            # Use conservative isometric-like eye values so the whole cube is visible on initial load.
            camera_eye_rel_x = 1.8
            camera_eye_rel_y = 1.8
            camera_eye_rel_z = 1.2

            # Determine if this is the first render for the battlespace scene.
            is_first_load = True
            try:
                if st is not None:
                    is_first_load = not bool(st.session_state.get('_battlespace3d_initialized'))
            except Exception:
                is_first_load = True

            # On first load, force a clear, balanced camera and aspectratio so the cube/grid
            # are visible immediately. Subsequent renders preserve user camera via uirevision.
            if is_first_load:
                # Mark initialized so future renders keep the user's interactions
                try:
                    if st is not None:
                        st.session_state['_battlespace3d_initialized'] = True
                except Exception:
                    pass

            fig.update_layout(
                title=dict(
                    text=title_text,
                    font=dict(color='rgba(255, 255, 255, 0.9)', size=16)
                ),
                scene=dict(
                    xaxis=dict(
                        visible=True,
                        title=dict(
                            text="East (km)",
                            font=dict(color='rgba(255, 255, 255, 0.98)', size=18)
                        ),
                        range=[x_min, x_max],  # Use computed extents
                        tickformat='.1f',
                        tickfont=dict(color='rgba(220, 230, 240, 0.95)', size=13),
                        tickcolor='rgba(255,255,255,0.75)',
                        ticklen=6,
                        gridcolor='rgba(255, 255, 255, 0.10)',  # Reduced grid opacity for less noise
                        backgroundcolor='rgba(0, 0, 0, 0)',
                        showbackground=False,  # Remove background boxes for cleaner look
                        showgrid=True,
                        showline=True,
                        linecolor='rgba(255, 255, 255, 0.3)',  # Subtle axis lines
                        zeroline=False  # Remove zero lines for cleaner appearance
                    ),
                    yaxis=dict(
                        visible=True,
                        title=dict(
                            text="North (km)",
                            font=dict(color='rgba(255, 255, 255, 0.98)', size=18)
                        ),
                        range=[y_min, y_max],  # Use computed extents
                        tickformat='.1f',
                        tickfont=dict(color='rgba(220, 230, 240, 0.95)', size=13),
                        tickcolor='rgba(255,255,255,0.75)',
                        ticklen=6,
                        gridcolor='rgba(255, 255, 255, 0.10)',  # Reduced grid opacity for less noise
                        backgroundcolor='rgba(0, 0, 0, 0)',
                        showbackground=False,  # Remove background boxes for cleaner look
                        showgrid=True,
                        showline=True,
                        linecolor='rgba(255, 255, 255, 0.3)',  # Subtle axis lines
                        zeroline=False  # Remove zero lines for cleaner appearance
                    ),
                    zaxis=dict(
                        visible=True,
                        title=dict(
                            text="Altitude (meters)",
                            font=dict(color='rgba(255, 255, 255, 0.98)', size=18)
                        ),
                        range=[z_min, z_max],  # Use computed extents
                        tickformat='.0f',
                        tickfont=dict(color='rgba(220, 230, 240, 0.95)', size=13),
                        tickcolor='rgba(255,255,255,0.75)',
                        ticklen=6,
                        gridcolor='rgba(255, 255, 255, 0.10)',  # Reduced grid opacity for less noise
                        backgroundcolor='rgba(0, 0, 0, 0)',
                        showbackground=False,  # Remove background boxes for cleaner look
                        showgrid=True,
                        showline=True,
                        linecolor='rgba(255, 255, 255, 0.3)',  # Subtle axis lines
                        zeroline=False  # Remove zero lines for cleaner appearance
                    ),
                    # Use cube aspect mode so axes scale equally and the cube is visible
                    aspectmode='cube',
                    aspectratio=dict(x=aspect_x, y=aspect_y, z=aspect_z),
                    # CRITICAL: Explicit camera initialization for immediate visibility
                    # Camera center is set to the computed scene center (data units).
                    # The camera eye is chosen differently on first load vs subsequent updates.
                    camera=(dict(
                        center=dict(x=scene_center_x_km, y=scene_center_y_km, z=scene_center_z_m),
                        up=dict(x=0, y=0, z=1)
                    )),
                    bgcolor=tactical_bg_color,  # Deep blue-grey tactical background
                    # Ensure axes are visible and gridlines are enabled so the cube is apparent
                    xaxis_showspikes=False,
                    yaxis_showspikes=False,
                    zaxis_showspikes=False,
                ),
                height=700,  # Increased height to fill viewport better
                showlegend=True,
                legend=dict(
                    font=dict(size=14, color='rgba(255, 255, 255, 0.95)'),
                    bgcolor='rgba(17, 24, 39, 0.75)',
                    bordercolor='rgba(255, 255, 255, 0.12)',
                    borderwidth=1,
                    traceorder='grouped',
                    itemsizing='constant',
                    x=0.99,
                    y=0.98,
                    xanchor='right',
                    yanchor='top',
                    tracegroupgap=8,
                    orientation='v'
                ),
                plot_bgcolor=tactical_bg_color,
                paper_bgcolor=tactical_bg_color,
                font=dict(color='rgba(255, 255, 255, 0.9)', size=14),
                hovermode='closest',
                autosize=True
            )

            # Interaction & camera usability tweaks
            try:
                # For 3D scenes, prefer perspective projection for natural zoom feel
                if 'scene' not in fig.layout:
                    fig.layout['scene'] = {}
                fig.layout.scene.camera.projection = dict(type='perspective')

                # Use 'orbit' dragmode for intuitive left-click rotation (free 3D rotation)
                fig.layout.scene.dragmode = 'orbit'
                fig.layout.dragmode = 'orbit'

                # Preserve camera between updates only when the underlying scene data is unchanged.
                try:
                    tracks_fingerprint = f"tracks={len(tracks_to_render)}|vr={int(view_range)}"
                except Exception:
                    tracks_fingerprint = f"tracks=0|vr={int(view_range)}"

                if is_first_load:
                    # On initial load set an explicit eye and center so the cube/grid are visible.
                    try:
                        fig.layout.scene.camera.eye = dict(x=1.8, y=1.8, z=1.2)
                        fig.layout.scene.camera.center = dict(x=0.0, y=0.0, z=0.0)
                    except Exception:
                        # best-effort fallback
                        try:
                            fig.layout.scene.camera.eye = dict(x=camera_eye_rel_x, y=camera_eye_rel_y, z=camera_eye_rel_z)
                        except Exception:
                            pass
                    # Ensure cube aspect so axes are equally scaled on first load
                    try:
                        fig.layout.scene.aspectmode = 'cube'
                    except Exception:
                        pass
            except Exception:
                pass
            # Do not forcibly reassign `scene.camera` here to avoid overwriting
            # user interactions (zoom/rotate/pan) on subsequent renders.
            
            # CRITICAL STEP 8: Debug visually - MANDATORY CHECK
            # Verify that traces were added to the figure
            trace_count = len(fig.data) if fig.data else 0
            
            # NEVER RETURN EMPTY FIGURES - this is forbidden
            # If no traces exist, at minimum grid and zones should be present
            if trace_count == 0:
                # This indicates a critical failure - grid should always be present
                # Re-add grid as fallback
                try:
                    Battlespace3D._add_coordinate_grid(fig, view_range)
                    Battlespace3D._add_protected_zones_3d(fig, defender_position, view_range)
                except Exception:
                    pass
            
            # Final trace count verification
            final_trace_count = len(fig.data) if fig.data else 0
            # DEBUG: Print trace count (can be removed after verification)
            # print(f"DEBUG: Final trace count: {final_trace_count}, tracks passed: {len(tracks_to_render)}")
            
            return fig
    
    @staticmethod
    def _add_coordinate_grid(fig: go.Figure, view_range: float):
        """
        Add coordinate system grid for reference.
        
        Grid is displayed in km for X, Y axes (horizontal plane).
        """
        try:
            # Convert to km for grid spacing
            view_range_km = view_range / 1000.0
            grid_spacing_km = max(5.0, view_range_km / 10)  # Grid spacing in km
            grid_points = int(view_range_km / grid_spacing_km)

            # Basic horizontal X/Y grid at ground level (z=0)
            for i in range(-grid_points, grid_points + 1):
                x_km = i * grid_spacing_km
                fig.add_trace(go.Scatter3d(
                    x=[x_km, x_km],
                    y=[-view_range_km, view_range_km],
                    z=[0, 0],
                    mode='lines',
                    line=dict(color='rgba(255, 255, 255, 0.12)', width=1.0),  # Subtle grid lines
                    showlegend=False,
                    hoverinfo='skip'
                ))

            for i in range(-grid_points, grid_points + 1):
                y_km = i * grid_spacing_km
                fig.add_trace(go.Scatter3d(
                    x=[-view_range_km, view_range_km],
                    y=[y_km, y_km],
                    z=[0, 0],
                    mode='lines',
                    line=dict(color='rgba(255, 255, 255, 0.12)', width=1.0),  # Subtle grid lines
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Add subtle vertical grid and altitude bands to create a 3D lattice
            z_max_m = max(1000.0, view_range * 0.5)  # maximum altitude to visualize (meters)
            altitude_line_color = 'rgba(255, 255, 255, 0.04)'

            # Vertical lines at X-grid positions along three representative Y lines (edge, center, opposite edge)
            y_positions = [-view_range_km, 0.0, view_range_km]
            for i in range(-grid_points, grid_points + 1):
                x_km = i * grid_spacing_km
                for y_pos in y_positions:
                    fig.add_trace(go.Scatter3d(
                        x=[x_km, x_km],
                        y=[y_pos, y_pos],
                        z=[0, z_max_m],
                        mode='lines',
                        line=dict(color=altitude_line_color, width=1),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

            # Vertical lines at Y-grid positions along three representative X lines
            x_positions = [-view_range_km, 0.0, view_range_km]
            for i in range(-grid_points, grid_points + 1):
                y_km = i * grid_spacing_km
                for x_pos in x_positions:
                    fig.add_trace(go.Scatter3d(
                        x=[x_pos, x_pos],
                        y=[y_km, y_km],
                        z=[0, z_max_m],
                        mode='lines',
                        line=dict(color=altitude_line_color, width=1),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

            # Horizontal altitude rectangles (subtle) to help anchor vertical position
            z_levels = [0.0, z_max_m * 0.25, z_max_m * 0.5, z_max_m * 0.75, z_max_m]
            rect_color = 'rgba(255, 255, 255, 0.04)'
            for z_level in z_levels:
                rect_x = [-view_range_km, view_range_km, view_range_km, -view_range_km, -view_range_km]
                rect_y = [-view_range_km, -view_range_km, view_range_km, view_range_km, -view_range_km]
                rect_z = [z_level] * len(rect_x)
                fig.add_trace(go.Scatter3d(
                    x=rect_x,
                    y=rect_y,
                    z=rect_z,
                    mode='lines',
                    line=dict(color=rect_color, width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Ground/base plane at z=0 (two triangles forming a quad) for spatial reference
            try:
                # Define four corner vertices (km, km, meters)
                v0 = (-view_range_km, -view_range_km, 0.0)
                v1 = ( view_range_km, -view_range_km, 0.0)
                v2 = ( view_range_km,  view_range_km, 0.0)
                v3 = (-view_range_km,  view_range_km, 0.0)

                gx = [v0[0], v1[0], v2[0], v3[0]]
                gy = [v0[1], v1[1], v2[1], v3[1]]
                gz = [v0[2], v1[2], v2[2], v3[2]]
                # Two triangular faces: (0,1,2) and (0,2,3)
                # Make ground plane subtly darker than background so objects feel anchored
                try:
                    fig.add_trace(go.Mesh3d(
                        x=gx,
                        y=gy,
                        z=gz,
                        i=[0, 0],
                        j=[1, 2],
                        k=[2, 3],
                        color='rgb(12,18,26)',
                        opacity=0.22,
                        ambient=0.6,
                        flatshading=True,
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                except Exception:
                    # Fallback to a faint plane if Mesh3d params unsupported
                    try:
                        fig.add_trace(go.Mesh3d(
                            x=gx,
                            y=gy,
                            z=gz,
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color='rgba(255,255,255,0.02)',
                            opacity=0.35,
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                    except Exception:
                        pass

                # Add a subtle border around the ground plane for spatial reference
                try:
                    border_color = 'rgba(255, 255, 255, 0.14)'
                    fig.add_trace(go.Scatter3d(
                        x=[gx[0], gx[1], gx[2], gx[3], gx[0]],
                        y=[gy[0], gy[1], gy[2], gy[3], gy[0]],
                        z=[0, 0, 0, 0, 0],
                        mode='lines',
                        line=dict(color=border_color, width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                except Exception:
                    pass

                # Add a small origin marker (0,0,0) with label to make origin explicit
                try:
                    fig.add_trace(go.Scatter3d(
                        x=[0.0],
                        y=[0.0],
                        z=[0.0],
                        mode='markers+text',
                        marker=dict(size=6, color='rgba(255,255,255,0.95)', symbol='cross'),
                        text=['Origin'],
                        textposition='top center',
                        textfont=dict(color='rgba(255,255,255,0.9)', size=12),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass  # Fail silently

    @staticmethod
    def _initialize_scene(fig: go.Figure, defender_position: Dict[str, float], view_range: float):
        """
        Initialize base 3D scene: axes, aspect, camera defaults, grid and ground plane.
        This is always run at the start of `create_3d_visualization` so the cube
        and grid exist before any tracks, zones or sensors are added.
        """
        try:
            # Basic scene extents (km for X/Y, meters for Z)
            view_range_km = view_range / 1000.0
            x_min, x_max = -view_range_km, view_range_km
            y_min, y_max = -view_range_km, view_range_km
            z_min, z_max = 0.0, max(1000.0, view_range * 0.5)

            # Conservative camera centered on defender_position
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)

            # Set a deterministic initial layout.scene so next traces attach correctly
            try:
                fig.update_layout(
                    scene=dict(
                        xaxis=dict(visible=True, title=dict(text="East (km)"), range=[x_min, x_max], showgrid=True),
                        yaxis=dict(visible=True, title=dict(text="North (km)"), range=[y_min, y_max], showgrid=True),
                        zaxis=dict(visible=True, title=dict(text="Altitude (meters)"), range=[z_min, z_max], showgrid=True),
                        aspectmode='cube',
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    showlegend=True
                )
            except Exception:
                pass

            # Add an invisible anchor point to force scene instantiation
            try:
                fig.add_trace(go.Scatter3d(x=[def_x_km], y=[def_y_km], z=[def_z], mode='markers', marker=dict(size=1, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
            except Exception:
                pass

            # Add coordinate grid and base plane (ground) so scene is visually grounded
            try:
                Battlespace3D._add_coordinate_grid(fig, view_range)
            except Exception:
                pass

            # Ensure a minimal camera is present so the cube renders predictably
            try:
                if 'scene' in fig.layout:
                    fig.layout.scene.camera = dict(eye=dict(x=1.6, y=1.6, z=1.1), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1))
            except Exception:
                pass
        except Exception:
            pass
    
    @staticmethod
    def _get_or_create_trajectory(track: Dict[str, Any], prediction_seconds: float = 90.0, num_points: int = 36):
        """
        Deterministic parametric trajectory generator with session-state caching.
        Returns list of (x_km, y_km, z_m) points.
        """
        try:
            # Basic track info
            tid = str(track.get('track_id', 'unknown'))
            pos = track.get('position', {}) if isinstance(track.get('position'), dict) else {}
            x0 = float(pos.get('x', 0.0))
            y0 = float(pos.get('y', 0.0))
            z0 = float(pos.get('z', 0.0))

            vel = track.get('velocity', {}) if isinstance(track.get('velocity'), dict) else {}
            vx = float(vel.get('vx', 0.0))
            vy = float(vel.get('vy', 0.0))
            vz = float(vel.get('vz', 0.0))

            # Fingerprint to detect scenario changes for this track
            # Include an optional track timestamp if provided so updates from upstream
            # result in cache refresh only when the track truly changed for this simulation step.
            ts = track.get('timestamp') or track.get('last_update') or track.get('time') or track.get('updated_at')
            ts_str = str(ts) if ts is not None else 'notime'
            fp = f"{tid}|{x0:.2f},{y0:.2f},{z0:.1f}|{vx:.3f},{vy:.3f},{vz:.3f}|{int(prediction_seconds)}|{int(num_points)}|{ts_str}"

            # Use Streamlit session_state for caching if available
            cache = None
            try:
                if st is not None:
                    cache = st.session_state.setdefault('_trajectory_cache', {})
            except Exception:
                cache = None

            if cache is not None and tid in cache and cache[tid].get('fp') == fp:
                return cache[tid].get('points', [])

            # Deterministic seed from track id
            hv = int(hashlib.md5(tid.encode('utf-8')).hexdigest()[:8], 16)

            # Parameterize amplitudes (meters for Z, km for lateral offsets)
            Ax_km = 0.02 + ((hv & 0xFF) / 255.0) * 0.12  # 0.02..0.14 km lateral
            Ay_km = 0.02 + (((hv >> 8) & 0xFF) / 255.0) * 0.10
            Az_m = 20.0 + (((hv >> 16) & 0xFF) / 255.0) * 300.0  # 20..320 meters altitude variation

            # Frequencies (radians per second) - ensure variety per track
            omega_x = 0.015 + (((hv >> 24) & 0xFF) / 255.0) * 0.045
            omega_y = 0.012 + (((hv >> 4) & 0xFF) / 255.0) * 0.038
            omega_z = 0.008 + (((hv >> 12) & 0xFF) / 255.0) * 0.030

            # Phase offsets
            phi_x = ((hv >> 2) & 0x7F) / 127.0 * math.pi * 2.0
            phi_y = ((hv >> 10) & 0x7F) / 127.0 * math.pi * 2.0
            phi_z = ((hv >> 18) & 0x7F) / 127.0 * math.pi * 2.0

            # Build points (t in seconds). Use 0..prediction_seconds inclusive
            pts = []
            for i in range(num_points + 1):
                t = (i / float(num_points)) * float(prediction_seconds)
                # Linear baseline displacement (meters)
                bx = x0 + vx * t
                by = y0 + vy * t
                bz = z0 + vz * t

                # Oscillatory lateral deviations (convert km to meters when applying)
                dx_km = Ax_km * math.sin(omega_x * t + phi_x)
                dy_km = Ay_km * math.cos(omega_y * t + phi_y)

                # Compute world coordinates: x,y in km for plotting, z in meters
                x_km = (bx / 1000.0) + dx_km
                y_km = (by / 1000.0) + dy_km
                z_m = bz + Az_m * math.sin(omega_z * t + phi_z)

                pts.append((x_km, y_km, z_m))

            # Smoothen using Catmull-Rom chain for visual quality
            try:
                smooth = Battlespace3D._catmull_rom_chain(pts, segments=12)
                if smooth and len(smooth) > 2:
                    pts = smooth
            except Exception:
                pass

            # Cache
            if cache is not None:
                try:
                    cache[tid] = {'fp': fp, 'points': pts}
                except Exception:
                    pass

            return pts
        except Exception:
            return []
        except Exception as e:
            try:
                import streamlit as _st
                import traceback
                _st.error("3D Visualization failed to render")
                _st.text(str(e))
                _st.text(traceback.format_exc())
            except Exception:
                pass

    @staticmethod
    def _add_protected_zones_3d(
        fig: go.Figure, 
        defender_position: Dict[str, float],
        view_range: float
    ):
        """
        Add 3D protected zones as semi-transparent spheres.
        
        ADVISORY ONLY - Visual reference only, no control logic.
        """
        try:
            # Convert defender position to km for X, Y
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            # CRITICAL: Zones must have distinct, meaningful colors for visual hierarchy
            # Use saturated hues and slightly increased opacity so volumes read as 3D
            # Define a single shared center for all zones (concentric requirement)
            # ZONE_CENTER: (x_km, y_km, z_m)
            # Use defender_position converted to km/m as the center point
            center_x_km = def_x_km
            center_y_km = def_y_km
            center_z_m = def_z
            ZONE_CENTER = (center_x_km, center_y_km, center_z_m)

            # Define explicit radii in km and ensure ordering: critical < protected < extended
            critical_radius = 5.0
            protected_radius = 15.0
            extended_radius = 30.0

            # Build zones list (radius_km, name, color)
            zones = [
                (critical_radius, "Critical Protected Zone", "#FF3B30"),
                (protected_radius, "Protected Zone", "#FF9500"),
                (extended_radius, "Extended Zone", "#007AFF")
            ]
            
            view_range_km = view_range / 1000.0
            
            # Use a single shared center for all zones (concentric requirement)
            center_x_km = def_x_km
            center_y_km = def_y_km
            center_z_m = def_z

            # Draw largest zones first so smaller, higher-priority zones render on top.
            zones_sorted = sorted(zones, key=lambda rnc: rnc[0], reverse=True)
            for radius_km, name, color in zones_sorted:
                if radius_km > view_range_km:
                    continue
                
                # Create a spherical cap (dome) clipped at ground using per-zone altitude ceilings.
                # Theta spans 0..2pi, phi spans 0..phi_max where phi_max corresponds to cap height.
                n_theta = 64
                n_phi = 32

                radius_m = radius_km * 1000.0

                # Per-zone altitude ceilings (meters) - realistic ceilings per request
                if 'Critical' in name:
                    ceiling_m = center_z_m + 7000.0  # ~7 km
                elif 'Protected' in name:
                    ceiling_m = center_z_m + 11000.0  # ~11 km
                else:
                    ceiling_m = center_z_m + 17000.0  # ~17 km

                # Cap height h measured from top of sphere down to cap base: h = min(radius_m, ceiling_m - center_z_m)
                h = max(0.0, min(radius_m, ceiling_m - center_z_m))
                if h <= 0.0:
                    # Nothing to draw if ceiling is at or below center
                    x_sphere, y_sphere, z_sphere, tri_i, tri_j, tri_k = [], [], [], [], [], []
                else:
                    # phi_max derived from spherical cap height: cos(phi_max) = 1 - h / radius
                    try:
                        cos_phi_max = max(-1.0, min(1.0, 1.0 - (h / radius_m)))
                        phi_max = math.acos(cos_phi_max)
                    except Exception:
                        phi_max = math.pi / 2.0

                    theta_vals = [2.0 * math.pi * i / n_theta for i in range(n_theta)]
                    phi_vals = [phi_max * j / (n_phi - 1) for j in range(n_phi)]

                    x_sphere = []
                    y_sphere = []
                    z_sphere = []

                    for it in range(n_theta):
                        th = theta_vals[it]
                        for ip in range(n_phi):
                            ph = phi_vals[ip]
                            x_km = center_x_km + (radius_m * math.sin(ph) * math.cos(th)) / 1000.0
                            y_km = center_y_km + (radius_m * math.sin(ph) * math.sin(th)) / 1000.0
                            z = center_z_m + radius_m * math.cos(ph)
                            # Clip at ground plane (no geometry below center_z_m)
                            if z < center_z_m:
                                z = center_z_m
                            x_sphere.append(x_km)
                            y_sphere.append(y_km)
                            z_sphere.append(z)

                    # Build triangle indices with theta wrap-around
                    nu = n_theta
                    nv = n_phi
                    tri_i = []
                    tri_j = []
                    tri_k = []
                    try:
                        for iu in range(nu):
                            iu_next = (iu + 1) % nu
                            for iv in range(nv - 1):
                                a = iu * nv + iv
                                b = iu_next * nv + iv
                                c = iu_next * nv + (iv + 1)
                                d = iu * nv + (iv + 1)
                                tri_i.append(a)
                                tri_j.append(b)
                                tri_k.append(c)
                                tri_i.append(a)
                                tri_j.append(c)
                                tri_k.append(d)
                    except Exception:
                        tri_i, tri_j, tri_k = [], [], []

                # Add as mesh3d for sphere visualization (with explicit triangles)
                # Enforce exact opacity mapping per specification (inner zones more visible)
                if radius_km == critical_radius:
                    mesh_opacity = 0.40
                elif radius_km == protected_radius:
                    mesh_opacity = 0.25
                else:
                    mesh_opacity = 0.15

                # Zones are concentric around defender_position (def_x_km, def_y_km).
                # Provide explicit hovertemplate per zone so meaning is clear.
                if 'zones_legend_added' not in locals():
                    zones_legend_added = False

                purpose = 'Immediate asset defense' if 'Critical' in name else ('Active defense region' if 'Protected' in name else 'Early detection / awareness')
                hover_template_zone = (
                    f"Zone: {name}<br>"
                    f"Radius: {int(radius_km)} km<br>"
                    f"Purpose: {purpose}<extra></extra>"
                )

                mesh_kwargs = dict(
                    x=x_sphere,
                    y=y_sphere,
                    z=z_sphere,
                    opacity=mesh_opacity,
                    color=color,
                    lighting=dict(ambient=0.6, diffuse=0.7, specular=0.25, roughness=0.6),
                    flatshading=False,
                    legendgroup='zones',
                    showlegend=True,
                    name=name,
                    hovertemplate=None,
                    hoverinfo='skip'
                )
                if tri_i and tri_j and tri_k:
                    mesh_kwargs.update(dict(i=tri_i, j=tri_j, k=tri_k))

                fig.add_trace(go.Mesh3d(**mesh_kwargs))
                # Temporary debug assertion to confirm critical zone added
                try:
                    if name and 'Critical' in name:
                        print(f"DEBUG: Added zone {name} radius_km={radius_km} center={ZONE_CENTER} opacity={mesh_opacity} tris={len(tri_i)}")
                except Exception:
                    pass
                if not zones_legend_added:
                    zones_legend_added = True
                try:
                    # Add a subtle boundary outline (equatorial ring) to make the zone edge readable.
                    circ_x = []
                    circ_y = []
                    circ_z = []
                    steps = 64
                    for s in range(steps + 1):
                        ang = 2.0 * math.pi * s / steps
                        cx = center_x_km + radius_km * math.cos(ang)
                        cy = center_y_km + radius_km * math.sin(ang)
                        cz = center_z_m + 0.0  # equatorial ring at defender altitude for reference
                        circ_x.append(cx)
                        circ_y.append(cy)
                        circ_z.append(cz)
                    fig.add_trace(go.Scatter3d(
                        x=circ_x,
                        y=circ_y,
                        z=circ_z,
                        mode='lines',
                        line=dict(color='rgba(0,0,0,0.35)', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                except Exception:
                    pass
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_tracks_3d(
        fig: go.Figure,
        tracks: List[Dict[str, Any]],
        defender_position: Dict[str, float],
        show_trajectories: bool = True,
        training_mode: bool = False
        , highlight_track_id: Optional[str] = None
    ) -> Optional[Tuple[float, float, float]]:
        """
        Add 3D track visualization with trajectory history and prediction.
        
        ADVISORY ONLY - Visualization only, no control logic.
        """
        try:
            # CRITICAL: Verify tracks is a non-empty list
            if not isinstance(tracks, list) or len(tracks) == 0:
                return None
            
            # Import TrajectoryTracker for trajectory data
            try:
                from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
            except Exception:
                TrajectoryTracker = None
            
            highlight_center = None
            tracks_added_count = 0  # DEBUG: Count tracks that produce traces
            tracks_legend_added = False

            # Generate a distinct color palette for the number of tracks to ensure
            # each track is visually distinct and legend bullets match marker colors.
            def _hsl_to_hex(h, s, l):
                # h: 0-360, s,l: 0-1
                c = (1 - abs(2 * l - 1)) * s
                x = c * (1 - abs((h / 60.0) % 2 - 1))
                m = l - c/2
                if h < 60:
                    r1, g1, b1 = c, x, 0
                elif h < 120:
                    r1, g1, b1 = x, c, 0
                elif h < 180:
                    r1, g1, b1 = 0, c, x
                elif h < 240:
                    r1, g1, b1 = 0, x, c
                elif h < 300:
                    r1, g1, b1 = x, 0, c
                else:
                    r1, g1, b1 = c, 0, x
                r = int((r1 + m) * 255)
                g = int((g1 + m) * 255)
                b = int((b1 + m) * 255)
                return f"#{r:02X}{g:02X}{b:02X}"

            num_tracks = max(1, len(tracks))
            palette = []
            for i in range(num_tracks):
                hue = (i * 360.0 / num_tracks) % 360.0
                # Use high saturation and medium lightness for vivid, distinct colors
                palette.append(_hsl_to_hex(hue, 0.76, 0.52))

            def _hex_to_rgba(hex_color, alpha=1.0):
                try:
                    h = hex_color.lstrip('#')
                    r = int(h[0:2], 16)
                    g = int(h[2:4], 16)
                    b = int(h[4:6], 16)
                    return f'rgba({r}, {g}, {b}, {alpha})'
                except Exception:
                    return f'rgba(157,209,255, {alpha})'

                def _generate_parametric_path(track_obj, prediction_seconds: float = 60.0, num_points: int = 40):
                    """
                    Generate a deterministic curved parametric trajectory for a track.
                    Returns list of (x_km, y_km, z_m) points.
                    """
                    try:
                        tid = str(track_obj.get('track_id', 'unknown'))
                        # Stable hash from track id
                        h = hashlib.md5(tid.encode('utf-8')).hexdigest()
                        hv = int(h[:8], 16)

                        pos = track_obj.get('position', {}) if isinstance(track_obj.get('position'), dict) else {}
                        x0 = float(pos.get('x', 0.0))
                        y0 = float(pos.get('y', 0.0))
                        z0 = float(pos.get('z', 0.0))

                        vel = track_obj.get('velocity', {}) if isinstance(track_obj.get('velocity'), dict) else {}
                        vx = float(vel.get('vx', 0.0))
                        vy = float(vel.get('vy', 0.0))
                        vz = float(vel.get('vz', 0.0))

                        # Prediction endpoint using current velocity
                        dx = vx * prediction_seconds
                        dy = vy * prediction_seconds
                        # Convert to km for X/Y
                        x0_km = x0 / 1000.0
                        y0_km = y0 / 1000.0
                        end_x_km = x0_km + dx / 1000.0
                        end_y_km = y0_km + dy / 1000.0

                        # Determine lateral curvature strength (km) deterministically from hash
                        # Range: 0.2 km (tight) to 6.0 km (wide) scaled by predicted distance
                        base_dist_km = max(0.1, math.hypot(end_x_km - x0_km, end_y_km - y0_km))
                        curve_factor = ((hv % 1000) / 1000.0)
                        curve_strength_km = 0.2 + curve_factor * max(1.0, base_dist_km * 0.6)

                        # Lateral direction: perpendicular to velocity, fallback to hash-derived angle
                        if abs(vx) < 1e-3 and abs(vy) < 1e-3:
                            angle_deg = (hv % 360)
                            angle = math.radians(angle_deg)
                            lat_x = math.cos(angle)
                            lat_y = math.sin(angle)
                        else:
                            # Perp vector (-vy, vx)
                            lat_x = -vy
                            lat_y = vx
                            norm = math.hypot(lat_x, lat_y)
                            if norm > 1e-6:
                                lat_x /= norm
                                lat_y /= norm
                            else:
                                lat_x, lat_y = 1.0, 0.0

                        # Altitude profile parameters from hash
                        climb_factor = ((hv >> 8) % 100) / 100.0  # 0..0.99
                        # climb between -200 m (descend) and +1500 m
                        climb_m = -200.0 + climb_factor * 1700.0
                        # descent quadratic coefficient small
                        descent_m = (50.0 + ((hv >> 16) % 200)) / max(1.0, prediction_seconds)

                        pts = []
                        for i in range(num_points + 1):
                            t = i / float(num_points)
                            # Linear baseline
                            bx = x0_km + (end_x_km - x0_km) * t
                            by = y0_km + (end_y_km - y0_km) * t

                            # Add single-hump sinusoidal lateral deviation
                            lateral = math.sin(math.pi * t) * curve_strength_km
                            cx = bx + lat_x * lateral
                            cy = by + lat_y * lateral

                            # Altitude profile: gradual climb to mid, slight descent towards end
                            zt = z0 + climb_m * t - descent_m * (t ** 2) * prediction_seconds
                            # Small cruise oscillation for realism (deterministic)
                            osc = math.sin(2.0 * math.pi * t * (1 + ((hv >> 24) % 3))) * (5.0 + (hv % 10))
                            zt += osc

                            pts.append((cx, cy, zt))
                        return pts
                    except Exception:
                        return []

            # Determine scenario context (if available in Streamlit session state)
            scenario_name = None
            try:
                import streamlit as _st
                scenario_name = _st.session_state.get('selected_scenario') or _st.session_state.get('scenario')
            except Exception:
                scenario_name = None

            # Pre-select exactly one Hostile track for the special Mixed Airspace scenario
            selected_hostile_track_id = None
            try:
                if scenario_name and isinstance(scenario_name, str) and scenario_name.strip().lower() == 'mixed airspace (1 hostile)':
                    # Build lightweight metadata for selection without altering tracks
                    metas = []
                    for t in tracks:
                        try:
                            tid = str(t.get('track_id', ''))
                            # quick classification normalization
                            ot = str(t.get('object_type') or t.get('entity_type') or '').lower()
                            if any(k in ot for k in ['civil', 'civ', 'passeng', 'airliner', 'commercial']):
                                cls = 'CIVILIAN'
                            elif any(k in ot for k in ['friend', 'ally', 'blue', 'own', 'friendly']):
                                cls = 'FRIENDLY'
                            elif any(k in ot for k in ['hostile', 'enemy', 'bogey']):
                                cls = 'HOSTILE'
                            else:
                                cls = 'UNKNOWN'
                            # declared hostile flag
                            declared = bool(t.get('declared_hostile') or t.get('is_hostile') or t.get('hostile'))
                            # speed estimate
                            vv = t.get('velocity') or {}
                            vx = float(vv.get('vx', 0.0)) if isinstance(vv.get('vx', 0.0), (int, float)) else 0.0
                            vy = float(vv.get('vy', 0.0)) if isinstance(vv.get('vy', 0.0), (int, float)) else 0.0
                            speed = math.hypot(vx, vy)
                            # deviation detection (basic)
                            dev = False
                            for dk in ['is_deviating', 'deviation', 'off_route', 'course_deviation', 'altitude_deviation', 'diverting', 'loitering', 'suspect']:
                                dv = t.get(dk)
                                if isinstance(dv, bool) and dv:
                                    dev = True
                                    break
                                if isinstance(dv, (int, float)) and dv > 0:
                                    dev = True
                                    break
                                if isinstance(dv, str) and dv.strip():
                                    dev = True
                                    break
                            # distance to defender (if position available)
                            pos = t.get('position') or {}
                            tx = float(pos.get('x', 0.0)) if isinstance(pos.get('x', 0.0), (int, float)) else 0.0
                            ty = float(pos.get('y', 0.0)) if isinstance(pos.get('y', 0.0), (int, float)) else 0.0
                            dx = (tx - defender_position.get('x', 0.0))
                            dy = (ty - defender_position.get('y', 0.0))
                            dist = math.hypot(dx, dy)
                            metas.append({'track_id': tid, 'classification': cls, 'declared': declared, 'speed': speed, 'deviation': dev, 'distance': dist})
                        except Exception:
                            continue

                    # Priority a) pick any declared/CLASSIFIED HOSTILE
                    hostiles = [m for m in metas if m.get('declared') or m.get('classification') == 'HOSTILE']
                    if hostiles:
                        selected_hostile_track_id = hostiles[0].get('track_id')
                    else:
                        # b) pick UNKNOWN with deviation first
                        unknowns = [m for m in metas if m.get('classification') == 'UNKNOWN']
                        deviators = [u for u in unknowns if u.get('deviation')]
                        if deviators:
                            # choose the deviator with highest speed as tie-break
                            deviators.sort(key=lambda x: (-x.get('speed', 0.0), x.get('distance', 1e12)))
                            selected_hostile_track_id = deviators[0].get('track_id')
                        elif unknowns:
                            # choose highest speed among unknowns, tie-breaker: closest distance
                            unknowns.sort(key=lambda x: (-x.get('speed', 0.0), x.get('distance', 1e12)))
                            selected_hostile_track_id = unknowns[0].get('track_id')
                        else:
                            selected_hostile_track_id = None
            except Exception:
                selected_hostile_track_id = None

            # Legend: classification color key (invisible dummy traces, once)
            if tracks and len(tracks) > 0:
                try:
                    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='markers', marker=dict(size=8, color=CLASSIFICATION_COLOR_MAP["Friendly"], symbol='circle'), name='Friendly / Civil', legendgroup='classification', showlegend=True))
                    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='markers', marker=dict(size=8, color=CLASSIFICATION_COLOR_MAP["Unknown"], symbol='circle'), name='Unknown / Suspect', legendgroup='classification', showlegend=True))
                    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='markers', marker=dict(size=8, color=CLASSIFICATION_COLOR_MAP["Hostile"], symbol='circle'), name='Hostile', legendgroup='classification', showlegend=True))
                except Exception:
                    pass

            # Draw order: trajectories first, then aircraft markers LAST so hover works
            marker_list = []
            for idx, track in enumerate(tracks):
                # Render every track possible; if structure is unexpected, fall back to defaults
                if not isinstance(track, dict):
                    track = {}

                # Ensure classification exists (default Unknown); no inference, no randomness
                if "classification" not in track:
                    track["classification"] = "Unknown"

                pos = track.get('position') if isinstance(track.get('position'), dict) else {}

                x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
                y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
                z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
                
                track_id = str(track.get('track_id', 'UNKNOWN'))
                obj_type = str(track.get('object_type', track.get('entity_type', 'UNKNOWN')))
                confidence = float(track.get('confidence', 0.5)) if isinstance(track.get('confidence'), (int, float)) else 0.5
                confidence = max(0.0, min(1.0, confidence))
                
                # Extract velocity for speed calculation
                vel = track.get('velocity', {})
                if not isinstance(vel, dict):
                    vel = {}
                
                vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
                vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
                vz = float(vel.get('vz', 0.0)) if isinstance(vel.get('vz'), (int, float)) else 0.0
                speed_mps = math.sqrt(vx**2 + vy**2 + vz**2)
                speed_kmh = speed_mps * 3.6

                # -----------------------------
                # Track history storage (audit-only, non-destructive)
                try:
                    if 'history' not in track or not isinstance(track.get('history'), list):
                        track['history'] = []
                    # Append current position once per sim_time (avoid duplicate timestamps)
                    try:
                        hist_last_t = track['history'][-1]['t'] if track['history'] else None
                    except Exception:
                        hist_last_t = None
                    try:
                        cur_t = float(sim_time)
                    except Exception:
                        cur_t = None
                    if cur_t is not None and (hist_last_t is None or float(hist_last_t) != float(cur_t)):
                        track['history'].append({'x': x, 'y': y, 'z': z, 't': cur_t})
                except Exception:
                    pass
                # -----------------------------
                
                # Assign a distinct color from the palette per track index so no two tracks
                # reuse the same color and legend bullets match the trace color.
                try:
                    color = palette[idx]
                except Exception:
                    color = '#9DD1FF'

                # Simulation time for visual-only interpolation (seconds)
                try:
                    sim_time = float(st.session_state.get('sim_time', 0.0)) if st is not None else 0.0
                except Exception:
                    sim_time = 0.0
                
                # Marker size: use a consistent, operator-appropriate size (10-14)
                # Per spec: keep markers serious, not toy-like. Selected tracks will be slightly larger.
                marker_base_size = 12  # base size in recommended range (10-14)
                
                # Modulate track brightness/opacity using fused confidence with EW degradation
                # ADVISORY ONLY — SUBTLE VISUAL EFFECT
                # Do NOT animate, no blinking, smooth static visual weighting only
                try:
                    from abhedya.dashboard.visual_components import SensorContributionPanel, EWReliabilityModel
                    from abhedya.dashboard.state_manager import DashboardStateManager
                    
                    # Get EW state
                    ew_state = None
                    try:
                        ew_state = DashboardStateManager.get_ew_environment_state() if DashboardStateManager else None
                    except Exception:
                        pass
                    
                    # Compute fused confidence
                    fused_confidence = SensorContributionPanel.compute_fused_confidence(track)
                    
                    # Apply EW degradation if applicable
                    if ew_state and ew_state.upper() not in ['NONE', 'NORMAL']:
                        contributions = track.get("sensor_contributions", {})
                        if contributions:
                            ew_degraded_confidence = EWReliabilityModel.compute_ew_degraded_confidence(
                                fused_confidence, contributions, ew_state, training_mode
                            )
                            fused_confidence = ew_degraded_confidence
                    
                    # Opacity scales with fused confidence (0.6 to 1.0 range for visibility)
                    track_opacity = 0.6 + (fused_confidence * 0.4)
                    track_opacity = max(0.6, min(1.0, track_opacity))
                except Exception:
                    # Fail-safe: use base confidence
                    track_opacity = 0.6 + (confidence * 0.4)
                    track_opacity = max(0.6, min(1.0, track_opacity))
                
                # Update trajectory history if TrajectoryTracker is available
                if TrajectoryTracker:
                    try:
                        TrajectoryTracker.update_track_history(track)
                    except Exception:
                        pass  # Fail silently
                
                # Get trajectory data for history and prediction
                trajectory_data = None
                if TrajectoryTracker:
                    try:
                        trajectory_data = TrajectoryTracker.get_trajectory(track_id)
                    except Exception:
                        trajectory_data = None
                
                # Add past trajectory (faded line) — prefer explicit `track['history']`, fallback to TrajectoryTracker
                if show_trajectories:
                    history = None
                    if isinstance(track.get('history'), list) and len(track.get('history')) > 1:
                        history = track.get('history')
                    elif trajectory_data:
                        history = trajectory_data.get('history', [])

                    if history and len(history) > 1:
                        pts = []
                        for point in history:
                            px = float(point.get('x', x))
                            py = float(point.get('y', y))
                            pz = float(point.get('altitude', z)) if point.get('altitude') is not None else float(point.get('z', z))
                            pts.append((px / 1000.0, py / 1000.0, pz))

                        # Append current position for continuity
                        pts.append((x / 1000.0, y / 1000.0, z))

                        smoothed = Battlespace3D._catmull_rom_chain(pts, segments=24)
                        if smoothed and len(smoothed) > 1:
                            hist_x_km = [p[0] for p in smoothed]
                            hist_y_km = [p[1] for p in smoothed]
                            hist_z = [p[2] for p in smoothed]
                            # History is intentionally faded but visible; use same hue as track
                            hist_color = _hex_to_rgba(color, 0.6)
                            fig.add_trace(go.Scatter3d(
                                x=hist_x_km,
                                y=hist_y_km,
                                z=hist_z,
                                mode='lines',
                                line=dict(
                                    color=hist_color,
                                    width=3
                                ),
                                name=f"History {track_id}",
                                showlegend=False,
                                hoverinfo='skip',
                                meta={'type': 'trajectory', 'layer': 'scenario', 'subtype': 'history'}
                            ))
                        # Additional audit-history trace (raw history, thin dashed, low opacity)
                        try:
                            raw_hist = track.get('history') if isinstance(track.get('history'), list) else None
                            if raw_hist and len(raw_hist) > 1:
                                hx = [float(p.get('x', x)) / 1000.0 for p in raw_hist]
                                hy = [float(p.get('y', y)) / 1000.0 for p in raw_hist]
                                hz = [float(p.get('z', z)) for p in raw_hist]
                                # Determine classification-based color from existing field
                                try:
                                    cls_raw = str(track.get('classification', '') or '').lower()
                                    if any(k in cls_raw for k in ['friend', 'ally', 'blue', 'own', 'friendly']):
                                        hist_color2 = CLASSIFICATION_COLOR_MAP.get('Friendly')
                                    elif any(k in cls_raw for k in ['civil', 'civ', 'passeng', 'airliner', 'commercial']):
                                        hist_color2 = CLASSIFICATION_COLOR_MAP.get('Civil')
                                    elif any(k in cls_raw for k in ['hostile', 'enemy', 'bogey']):
                                        hist_color2 = CLASSIFICATION_COLOR_MAP.get('Hostile')
                                    else:
                                        hist_color2 = CLASSIFICATION_COLOR_MAP.get('Unknown')
                                except Exception:
                                    hist_color2 = CLASSIFICATION_COLOR_MAP.get('Unknown')
                                fig.add_trace(go.Scatter3d(
                                    x=hx,
                                    y=hy,
                                    z=hz,
                                    mode='lines',
                                    line=dict(color=hist_color2, width=2, dash='dot'),
                                    opacity=0.35,
                                    name=f"{track_id} History",
                                    showlegend=False,
                                    hoverinfo='skip',
                                    meta={'type': 'trajectory', 'layer': 'scenario', 'subtype': 'raw_history'}
                                ))
                        except Exception:
                            pass
                
                # Add predicted trajectory (dashed advisory projection)
                if show_trajectories:
                    # Build a robust multi-point curved predicted path for every track.
                    path_pts = []
                    traj_pts = []  # Initialize for scoping; will be set in trajectory generation block

                    # 1) Use explicit predicted_path from trajectory_data if available
                    if trajectory_data and isinstance(trajectory_data.get('predicted_path', None), list) and len(trajectory_data.get('predicted_path')) > 1:
                        try:
                            pts = []
                            # start from current position for continuity
                            pts.append((x / 1000.0, y / 1000.0, z))
                            for point in trajectory_data.get('predicted_path', []):
                                px = float(point.get('x', x)) if point.get('x') is not None else x
                                py = float(point.get('y', y)) if point.get('y') is not None else y
                                pz = float(point.get('altitude', z)) if point.get('altitude') is not None else float(point.get('z', z) if point.get('z') is not None else z)
                                pts.append((px / 1000.0, py / 1000.0, pz))
                            # Smooth and ensure multi-point
                            sm_pred = Battlespace3D._catmull_rom_chain(pts, segments=18)
                            if sm_pred and len(sm_pred) > 2:
                                path_pts = sm_pred
                        except Exception:
                            path_pts = []

                    # 2) If no explicit prediction, generate deterministic curved parametric path
                    if not path_pts:
                        try:
                            param_pts = _generate_parametric_path(track, prediction_seconds=90.0, num_points=36)
                            if param_pts and len(param_pts) > 2:
                                path_pts = param_pts
                        except Exception:
                            path_pts = []

                    # 3) Safety: if still too few points, synthesize a smooth multi-point arc
                    if not path_pts or len(path_pts) < 3:
                        try:
                            # Create a gentle curved arc from current heading
                            base_pts = []
                            # Determine a small forward displacement for endpoints
                            forward_m = max(200.0, math.hypot(vx, vy) * 60.0)  # meters over 60s
                            end_x_m = x + (vx if abs(vx) > 1e-6 else 100.0) * 30.0
                            end_y_m = y + (vy if abs(vy) > 1e-6 else 100.0) * 30.0
                            # create 24 points between start and end with a sinusoidal lateral offset
                            num_pts = 24
                            for i in range(num_pts + 1):
                                t = i / float(num_pts)
                                bx = (x + (end_x_m - x) * t) / 1000.0
                                by = (y + (end_y_m - y) * t) / 1000.0
                                # lateral sinusoid scaled by small factor
                                lateral_km = 0.02 + ((hashlib.md5(track_id.encode()).digest()[0] % 8) / 100.0)
                                lat = math.sin(math.pi * t) * lateral_km * (1.0 + ((hashlib.md5(track_id.encode()).digest()[1] % 5) / 5.0))
                                # apply a perpendicular vector based on heading
                                heading_angle = math.atan2(vy, vx) if (abs(vx) > 1e-6 or abs(vy) > 1e-6) else math.radians((hashlib.md5(track_id.encode()).digest()[2] % 360))
                                perp_x = -math.sin(heading_angle)
                                perp_y = math.cos(heading_angle)
                                cx = bx + perp_x * lat
                                cy = by + perp_y * lat
                                # small altitude variation
                                base_alt = z
                                alt_variation = (10.0 + (hashlib.md5(track_id.encode()).digest()[3] % 50)) * math.sin(2.0 * math.pi * (t + 0.2))
                                cz = base_alt + alt_variation
                                base_pts.append((cx, cy, cz))
                            path_pts = base_pts
                        except Exception:
                            path_pts = [(x / 1000.0, y / 1000.0, z), ((x + 100.0) / 1000.0, (y + 100.0) / 1000.0, z + 50.0)]

                    # 4) Ensure path_pts is multi-point and smooth
                    try:
                        if path_pts and len(path_pts) >= 2:
                            # If too coarse, interpolate with Catmull-Rom for smoothness
                            smooth_pts = Battlespace3D._catmull_rom_chain(path_pts, segments=18)
                            if smooth_pts and len(smooth_pts) > 2:
                                path_pts = smooth_pts
                    except Exception:
                        pass

                    # 5) Finally, add the visible prediction/path trace BEFORE the marker so markers render on top
                    try:
                        # Use deterministic parametric generator with caching to produce persistent trajectories
                        try:
                            # Generate or retrieve deterministic cached trajectory
                            prediction_seconds_local = 90.0
                            traj_pts = Battlespace3D._get_or_create_trajectory(track, prediction_seconds=prediction_seconds_local, num_points=40)
                            if traj_pts and len(traj_pts) > 1:
                                path_x = [p[0] for p in traj_pts]
                                path_y = [p[1] for p in traj_pts]
                                path_z = [p[2] for p in traj_pts]

                            # Build per-point customdata for hover: [Track ID, Altitude (m), Speed (km/h), Heading (deg), Classification]
                            cds = []
                            npts = len(traj_pts)
                                # approximate time per segment
                            dt = float(prediction_seconds_local) / max(1, (npts - 1))
                            # fallback heading from current velocity
                            try:
                                fallback_heading = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0
                            except Exception:
                                fallback_heading = 0.0

                            for i_pt in range(npts):
                                x_i, y_i, z_i = traj_pts[i_pt]
                                # choose neighbor for tangent (prefer next, fallback to prev)
                                if i_pt + 1 < npts:
                                    nx, ny, nz = traj_pts[i_pt + 1]
                                elif i_pt - 1 >= 0:
                                    nx, ny, nz = traj_pts[i_pt - 1]
                                else:
                                    nx, ny, nz = x_i, y_i, z_i

                                dx_m = (nx - x_i) * 1000.0
                                dy_m = (ny - y_i) * 1000.0
                                dz_m = (nz - z_i)
                                dist_m = math.hypot(math.hypot(dx_m, dy_m), dz_m)
                                speed_mps = dist_m / dt if dt > 0 and dist_m > 0 else 0.0
                                speed_kmh_pt = speed_mps * 3.6
                                if abs(dx_m) > 1e-6 or abs(dy_m) > 1e-6:
                                    heading_pt = (math.degrees(math.atan2(dy_m, dx_m)) + 360.0) % 360.0
                                else:
                                    heading_pt = fallback_heading

                                cds.append([track_id, float(z_i), float(speed_kmh_pt), float(heading_pt), obj_type])

                            hovertemplate_traj = (
                                "Track ID: %{customdata[0]}<br>"
                                "Altitude: %{customdata[1]:.0f} m<br>"
                                "Speed: %{customdata[2]:.0f} km/h<br>"
                                "Heading: %{customdata[3]:.0f}\u00B0<extra></extra>"
                            )

                            # Trajectory lines are decorative only for legend semantics.
                            # Per strict scope, do NOT attach hover to trajectory lines.
                            fig.add_trace(go.Scatter3d(
                                x=path_x,
                                y=path_y,
                                z=path_z,
                                mode='lines',
                                line=dict(color=color, width=4),
                                opacity=0.92,
                                name=f'Trajectory_{track_id}',
                                legendgroup='trajectories',
                                showlegend=False,
                                hoverinfo='skip',
                                meta={'type': 'trajectory', 'layer': 'scenario', 'subtype': 'prediction'}
                            ))
                        except Exception:
                            pass
                    except Exception:
                        pass

                # Build deterministic heading and attach track metadata
                try:
                    heading_deg = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0
                except Exception:
                    heading_deg = 0.0

                # Explicitly initialize classification using scenario and object_type
                raw_class = (track.get('classification') or obj_type or '').strip()
                rc = raw_class.lower()

                # Scenario overrides
                scenario_lc = (scenario_name or '').lower() if 'scenario_name' in locals() else (scenario_name or '')
                if scenario_lc and 'civil air traffic' in scenario_lc:
                    classification_enum = 'CIVILIAN'
                elif scenario_lc and 'friendly' in scenario_lc:
                    classification_enum = 'FRIENDLY'
                elif scenario_lc and 'mixed airspace' in scenario_lc:
                    # In Mixed Airspace, prefer explicit object_type hints; otherwise UNKNOWN for deviating/unidentified
                    if any(k in rc for k in ['civil', 'civ', 'passeng', 'airliner', 'commercial']):
                        classification_enum = 'CIVILIAN'
                    elif any(k in rc for k in ['friend', 'ally', 'blue', 'own', 'friendly']):
                        classification_enum = 'FRIENDLY'
                    elif any(k in rc for k in ['hostile', 'enemy', 'bogey']):
                        classification_enum = 'HOSTILE'
                    else:
                        classification_enum = 'UNKNOWN'
                else:
                    # Default mapping from object_type if present
                    if any(k in rc for k in ['civil', 'civ', 'passeng', 'airliner', 'commercial']):
                        classification_enum = 'CIVILIAN'
                    elif any(k in rc for k in ['friend', 'ally', 'blue', 'own', 'friendly']):
                        classification_enum = 'FRIENDLY'
                    elif any(k in rc for k in ['hostile', 'enemy', 'bogey']):
                        classification_enum = 'HOSTILE'
                    else:
                        # No explicit classification provided; log error and set UNKNOWN (caller must ensure data completeness)
                        classification_enum = 'UNKNOWN'
                        try:
                            print(f"ERROR: Track {track_id} missing explicit classification; set to UNKNOWN. Provide classification in track source.")
                        except Exception:
                            pass

                # Scenario-aware override: Mixed Airspace single hostile selection
                try:
                    if selected_hostile_track_id and str(selected_hostile_track_id) == str(track_id):
                        classification_enum = 'HOSTILE'
                except Exception:
                    pass

                # Persist classification back into track metadata
                try:
                    track['classification'] = classification_enum
                except Exception:
                    pass

                # Marker color from classification only (trajectories keep palette color)
                _cls_key = "Civil" if classification_enum == "CIVILIAN" else ("Friendly" if classification_enum == "FRIENDLY" else ("Hostile" if classification_enum == "HOSTILE" else "Unknown"))
                marker_color = CLASSIFICATION_COLOR_MAP.get(_cls_key, "#F1C40F")

                # Derive Threat State directly from classification (strict mapping)
                if classification_enum == 'CIVILIAN' or classification_enum == 'FRIENDLY':
                    threat_state_display = 'Friendly'
                elif classification_enum == 'HOSTILE':
                    threat_state_display = 'Hostile'
                else:
                    # UNKNOWN
                    # In Mixed Airspace scenario, UNKNOWN should be Potential Threat
                    if scenario_lc and 'mixed airspace' in scenario_lc:
                        threat_state_display = 'Potential Threat'
                    else:
                        # Default behavior per spec: UNKNOWN -> Potential Threat
                        threat_state_display = 'Potential Threat'

                # Assign tracking status strictly from threat state
                if threat_state_display == 'Friendly':
                    tracking_status_display = 'Monitoring'
                elif threat_state_display == 'Hostile':
                    tracking_status_display = 'Intercepting'
                else:
                    tracking_status_display = 'Tracking'

                # Persist threat and tracking status into track metadata
                try:
                    track['threat_state'] = threat_state_display
                    track['tracking_status'] = tracking_status_display
                except Exception:
                    pass

                # -----------------------------
                # Kill Chain Funnel (EXPLAINABILITY ONLY)
                # Ensure a deterministic, read-only `kill_chain_stage` exists for every track.
                # Allowed values: DETECTED, TRACKED, IDENTIFIED, EVALUATED, ASSIGNED, MONITORING
                try:
                    allowed_stages = ["DETECTED", "TRACKED", "IDENTIFIED", "EVALUATED", "ASSIGNED", "MONITORING"]
                    kcs = track.get('kill_chain_stage')
                    if not isinstance(kcs, str) or kcs.strip().upper() not in allowed_stages:
                        # Default placeholder
                        track['kill_chain_stage'] = "DETECTED"
                    else:
                        track['kill_chain_stage'] = kcs.strip().upper()

                    # Training-mode deterministic placeholders (visual only)
                    if training_mode:
                        try:
                            # If classification is known (not UNKNOWN), mark IDENTIFIED
                            cls_val = str(track.get('classification', '') or '').strip()
                            if cls_val and cls_val.upper() != 'UNKNOWN':
                                track['kill_chain_stage'] = 'IDENTIFIED'

                            # Threat-state driven overrides (training mode only)
                            ts = str(track.get('threat_state', '') or '').strip()
                            if ts == 'Potential Threat':
                                track['kill_chain_stage'] = 'EVALUATED'
                            if ts == 'Hostile':
                                track['kill_chain_stage'] = 'MONITORING'
                        except Exception:
                            pass
                except Exception:
                    try:
                        track['kill_chain_stage'] = 'DETECTED'
                    except Exception:
                        pass
                # -----------------------------

                # TTC & urgency (advisory only; no mutation, deterministic)
                ttc_seconds = compute_ttc_seconds(track, defender_position, TTC_CRITICAL_RADIUS_M)
                urgency_level = get_urgency_level(ttc_seconds)
                ttc_display = f"{int(round(ttc_seconds))} s" if ttc_seconds is not None else "N/A"
                urgency_display = urgency_level if urgency_level else "N/A"

                # Attach mandatory metadata to the plotted object via `customdata`
                # Order: [..., Detected By, Time to Criticality, Urgency Level, Kill Chain Stage]
                _sensor_names = ["Long-Range Surveillance Radar", "Precision Tracking Radar", "Passive / ESM Sensor"]
                try:
                    _h = hashlib.md5(str(track_id).encode("utf-8")).hexdigest()
                    _idx = int(_h[:4], 16) % 3
                    _idx2 = (int(_h[4:8], 16) % 3)
                    if _idx == _idx2:
                        detected_by_str = _sensor_names[_idx]
                    else:
                        detected_by_str = ", ".join(sorted([_sensor_names[_idx], _sensor_names[_idx2]]))
                except Exception:
                    detected_by_str = "Surveillance Radar"
                if not detected_by_str or str(detected_by_str).strip() == "" or str(detected_by_str) == "None":
                    detected_by_str = "Surveillance Radar (Synthetic)"
                # Append kill chain stage into customdata for hover (index 10)
                kcs_val = str(track.get('kill_chain_stage', 'DETECTED'))

                # Build hover customdata without history fields (history removed)
                customdata_point = [
                    track_id,
                    classification_enum,
                    threat_state_display,
                    float(z),
                    float(speed_kmh),
                    float(heading_deg),
                    tracking_status_display,
                    detected_by_str,
                    ttc_display,
                    urgency_display,
                    kcs_val
                ]

                # Hovertemplate — only allowed fields (history fields removed)
                hovertemplate = (
                    "Track ID: %{customdata[0]}<br>"
                    "Classification: %{customdata[1]}<br>"
                    "Altitude: %{customdata[3]:,.0f} m<br>"
                    "Speed: %{customdata[4]:.0f} km/h<br>"
                    "Heading: %{customdata[5]:.0f}\u00B0<br>"
                    "Threat State: %{customdata[2]}<br>"
                    "Tracking Status: %{customdata[6]}<br>"
                    "Detected By: %{customdata[7]}<br>"
                    "Time to Criticality: %{customdata[8]}<br>"
                    "Urgency Level: %{customdata[9]}<br>"
                    "Kill Chain Stage: %{customdata[10]}<extra></extra>"
                )
                
                # Interpolate marker position along precomputed trajectory at `sim_time` if available.
                try:
                    interp_used = False
                    if 'traj_pts' in locals() and traj_pts and len(traj_pts) > 1:
                        npts = len(traj_pts)
                        max_t = prediction_seconds_local
                        # Build uniform time array from 0..max_t across trajectory points
                        dt = float(max_t) / max(1, (npts - 1))
                        # Clamp sim_time into [0, max_t]
                        t = max(0.0, min(sim_time, max_t))
                        # locate interval
                        idx_low = int(min(npts - 2, max(0, int(math.floor(t / dt)))))
                        t0 = idx_low * dt
                        t1 = (idx_low + 1) * dt
                        if t1 - t0 <= 0.0:
                            alpha = 0.0
                        else:
                            alpha = (t - t0) / (t1 - t0)
                        x0_km, y0_km, z0_m = traj_pts[idx_low]
                        x1_km, y1_km, z1_m = traj_pts[min(idx_low + 1, npts - 1)]
                        x_km = x0_km + alpha * (x1_km - x0_km)
                        y_km = y0_km + alpha * (y1_km - y0_km)
                        display_z = z0_m + alpha * (z1_m - z0_m)
                        interp_used = True
                    else:
                        x_km = x / 1000.0
                        y_km = y / 1000.0
                except Exception:
                    x_km = x / 1000.0
                    y_km = y / 1000.0
                
                # Add current position marker; emphasize if this is the highlighted track
                is_highlight = (highlight_track_id is not None and str(highlight_track_id) == track_id)
                # Track markers MUST be clearly visible - increased line width for contrast
                # CRITICAL: Track markers MUST be clearly visible and render ABOVE zones
                # Tracks are the PRIMARY content - they must never be hidden
                # Slightly raise markers above ground plane for visibility (only set if not interpolated)
                if 'interp_used' not in locals() or not interp_used:
                    display_z = z if z and z > 1.0 else 1.0

                final_marker_size = marker_base_size + (3 if is_highlight else 0)
                if is_highlight:
                    outline_color = '#FFFF7F'
                    outline_width = 5
                else:
                    # Urgency-based outline (advisory only): LOW thin grey/blue, MEDIUM amber thicker, HIGH red thicker
                    if urgency_level == "HIGH":
                        outline_color = "#E74C3C"
                        outline_width = 4
                    elif urgency_level == "MEDIUM":
                        outline_color = "#F1C40F"
                        outline_width = 3
                    else:
                        outline_color = "#95A5A6"
                        outline_width = 2

                marker_props = dict(
                    size=final_marker_size,
                    color=marker_color,
                    symbol='circle',
                    line=dict(width=outline_width, color=outline_color),
                    opacity=1.0  # Solid, non-transparent markers for professional appearance
                )

                # Marker will be positioned by the update routine; append marker info unchanged

                # Defer marker add so all markers are drawn LAST (after trajectories)
                show_track_legend = not tracks_legend_added
                marker_list.append((x_km, y_km, display_z, marker_props, customdata_point, hovertemplate, track_id, show_track_legend))

                # Direction indicator: short projected movement vector for clarity
                try:
                    # Short horizon for direction indicator (seconds)
                    dir_seconds = 5.0
                    end_x_m = x + vx * dir_seconds
                    end_y_m = y + vy * dir_seconds
                    end_z_m = z + vz * dir_seconds

                    end_x_km = end_x_m / 1000.0
                    end_y_km = end_y_m / 1000.0

                    fig.add_trace(go.Scatter3d(
                        x=[x_km, end_x_km],
                        y=[y_km, end_y_km],
                        z=[z, end_z_m],
                        mode='lines',
                        line=dict(color=color, width=4),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                except Exception:
                    pass

                # Record highlight center for camera centering (km, km, meters)
                if is_highlight:
                    try:
                        highlight_center = (x_km, y_km, z)
                    except Exception:
                        highlight_center = None
                # CRITICAL: If no track is highlighted, use first track's center for camera
                elif highlight_center is None:
                    try:
                        highlight_center = (x_km, y_km, z)
                    except Exception:
                        pass

            # Add all aircraft markers LAST so they capture hover (draw order)
            # Add markers and subtle kill-chain badge (badge is a secondary, non-interactive marker)
            stage_color_map = {
                'DETECTED': '#95A5A6',  # Grey
                'TRACKED': '#1890FF',   # Blue
                'IDENTIFIED': '#17BCD9',# Cyan
                'EVALUATED': '#FFBF00', # Amber
                'ASSIGNED': '#FFA500',  # Orange
                'MONITORING': '#E74C3C' # Red
            }

            # Collect buffer traces to add AFTER visible markers so tracks win hover priority
            buffer_list = []
            for (x_km, y_km, display_z, marker_props, customdata_point, hovertemplate, track_id, show_track_legend) in marker_list:
                fig.add_trace(go.Scatter3d(
                    x=[x_km],
                    y=[y_km],
                    z=[display_z],
                    mode='markers',
                    marker=marker_props,
                    name=f"Track_{track_id}",
                    customdata=[customdata_point],
                    hovertemplate=hovertemplate,
                    hoverinfo='text',
                    hoverlabel=dict(namelength=-1),
                    showlegend=show_track_legend,
                    meta={'type': 'track', 'layer': 'scenario', 'track_id': track_id}
                ))
                # Defer creation of an invisible buffer trace until after all visible markers
                try:
                    buf_symbol = marker_props.get('symbol', 'circle')
                    buf_size = int(marker_props.get('size', 12) * 3)
                except Exception:
                    buf_symbol = 'circle'
                    buf_size = 36
                buffer_list.append((x_km, y_km, display_z, customdata_point, hovertemplate, buf_symbol, buf_size))

                # Add a small, non-interactive badge above the marker indicating kill-chain stage
                try:
                    kcs_val = str(customdata_point[10]) if len(customdata_point) > 10 else 'DETECTED'
                    badge_color = stage_color_map.get(kcs_val, '#95A5A6')
                    # Slight vertical offset so badge does not overlap the marker
                    badge_z = display_z + max(5.0, 0.01 * (display_z if isinstance(display_z, (int, float)) else 10.0))
                    fig.add_trace(go.Scatter3d(
                        x=[x_km],
                        y=[y_km],
                        z=[badge_z],
                        mode='markers',
                        marker=dict(size=6, color=badge_color, symbol='circle'),
                        showlegend=False,
                        hoverinfo='skip',
                        meta={'type': 'track', 'layer': 'scenario', 'subtype': 'badge'}
                    ))
                except Exception:
                    pass

                if show_track_legend:
                    tracks_legend_added = True
            
            # After all visible markers and badges are added, append invisible buffer traces
            try:
                for (bx, by, bz, bcd, bhover, bsymbol, bsize) in buffer_list:
                    try:
                        fig.add_trace(go.Scatter3d(
                            x=[bx], y=[by], z=[bz],
                            mode='markers',
                            marker=dict(size=bsize, color='rgba(0,0,0,0)', symbol=bsymbol, line=dict(width=0)),
                            customdata=[bcd],
                            hovertemplate=bhover,
                            hoverinfo='text',
                            hoverlabel=dict(namelength=-1),
                            showlegend=False,
                            meta={'type': 'track', 'layer': 'scenario', 'subtype': 'buffer'}
                        ))
                    except Exception:
                        pass
            except Exception:
                pass

            # CRITICAL: Return highlight center (or first track center) - never return None when tracks exist
            return highlight_center
        except Exception as e:
            # CRITICAL: Log exception but don't fail silently - return None only if truly no tracks
            # If tracks exist but rendering failed, this is a bug that should be visible
            return None

    @staticmethod
    def _catmull_rom_chain(points, segments=16):
        """
        Generate a Catmull-Rom spline chain for a list of 3D points.
        Returns a list of interpolated (x,y,z) points. Pure Python implementation.
        """
        try:
            if not points or len(points) < 2:
                return points

            def catmull_rom(p0, p1, p2, p3, t):
                t2 = t * t
                t3 = t2 * t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 + (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 + (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
                z = 0.5 * ((2 * p1[2]) + (-p0[2] + p2[2]) * t + (2*p0[2] - 5*p1[2] + 4*p2[2] - p3[2]) * t2 + (-p0[2] + 3*p1[2] - 3*p2[2] + p3[2]) * t3)
                return (x, y, z)

            # Pad endpoints to handle boundaries
            extended = [points[0]] + points + [points[-1]]
            result = []
            for i in range(1, len(extended)-2):
                p0 = extended[i-1]
                p1 = extended[i]
                p2 = extended[i+1]
                p3 = extended[i+2]
                for s in range(segments):
                    t = s / float(segments)
                    result.append(catmull_rom(p0, p1, p2, p3, t))
            result.append(points[-1])
            return result
        except Exception:
            return points
    
    @staticmethod
    def _add_atmospheric_layers_3d(
        fig: go.Figure,
        defender_position: Dict[str, float],
        view_range: float,
        atmospheric_conditions: Dict[str, Any],
        training_mode: bool = False
    ): 
        """
        Add atmospheric layers visualization (ground haze, weather volume).
        
        ADVISORY ONLY — Visual representation only, no engagement logic changes.
        
        Args:
            fig: Plotly figure
            defender_position: Defender position dict
            view_range: View range in meters
            atmospheric_conditions: Atmospheric conditions dictionary
        """
        try:
            from abhedya.dashboard.atmospheric_modeling import AtmosphericModel
            
            visibility = atmospheric_conditions.get("visibility")
            if not visibility:
                return

            # Get atmospheric layer color (may be hex or rgba)
            layer_color = AtmosphericModel.get_atmospheric_layer_color(visibility)

            # Determine severity and opacities from visibility if provided
            severity = getattr(visibility, 'severity', None)
            vis_name = getattr(visibility, 'name', None) if not isinstance(visibility, str) else visibility
            vis_str = str(vis_name).lower() if vis_name else str(visibility).lower()
            
            # Convert defender position to km for X, Y
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            view_range_km = view_range / 1000.0
            
            # 1. Ground haze layer -- visible but subtle; increase opacity slightly under adverse conditions
            haze_altitude_max = 500.0  # meters
            grid_size = 20  # Grid resolution

            haze_x = []
            haze_y = []
            haze_z = []

            for i in range(grid_size + 1):
                for j in range(grid_size + 1):
                    x_offset = (i / grid_size - 0.5) * view_range_km * 0.8
                    y_offset = (j / grid_size - 0.5) * view_range_km * 0.8
                    haze_x.append(def_x_km + x_offset)
                    haze_y.append(def_y_km + y_offset)
                    haze_z.append(def_z + haze_altitude_max * (0.3 + 0.7 * (i + j) / (2 * grid_size)))  # Slight variation

            # Determine haze opacity based on visibility severity and training mode
            base_haze_opacity = 0.14
            if 'fog' in vis_str or 'haze' in vis_str:
                base_haze_opacity = 0.26
            elif 'rain' in vis_str or 'storm' in vis_str:
                base_haze_opacity = 0.22

            if training_mode:
                base_haze_opacity = min(0.45, base_haze_opacity * 1.25)

                fig.add_trace(go.Mesh3d(
                    x=haze_x,
                    y=haze_y,
                    z=haze_z,
                    color=(layer_color if layer_color else '#BFD7FF'),
                    opacity=base_haze_opacity,
                    lighting=dict(ambient=0.45, diffuse=0.5, specular=0.1, roughness=0.9),
                    showlegend=True,
                    name="Atmospheric Layer (Advisory)",
                    hovertemplate=None,
                    hoverinfo='skip'
                ))

            # Add a subtle large ground tint plane to influence scene mood (low opacity)
            try:
                tint_alpha = 0.06 if base_haze_opacity < 0.2 else 0.10
                tint_alpha = min(0.22, tint_alpha * (1.5 if 'storm' in vis_str else 1.0))
                # Convert hex layer_color to rgba if needed
                def _hex_to_rgba(hex_color, alpha):
                    try:
                        h = hex_color.lstrip('#')
                        lv = len(h)
                        r = int(h[0:2], 16)
                        g = int(h[2:4], 16)
                        b = int(h[4:6], 16)
                        return f'rgba({r}, {g}, {b}, {alpha})'
                    except Exception:
                        return f'rgba(191, 215, 255, {alpha})'

                tint_color = _hex_to_rgba(layer_color if layer_color else '#BFD7FF', tint_alpha)
                gx = [-view_range_km, view_range_km, view_range_km, -view_range_km]
                gy = [-view_range_km, -view_range_km, view_range_km, view_range_km]
                gz = [def_z + 1.0] * 4
                fig.add_trace(go.Mesh3d(
                    x=gx,
                    y=gy,
                    z=gz,
                    i=[0], j=[1], k=[2],
                    color=tint_color,
                    opacity=tint_alpha,
                    showlegend=False,
                    hoverinfo='skip'
                ))
            except Exception:
                pass
            
            # 2. Weather volume (optional translucent cuboid for storm conditions)
            if 'rain' in vis_str or 'storm' in vis_str:
                weather_height = 3000.0  # meters
                weather_x = []
                weather_y = []
                weather_z = []

                # Create cuboid vertices
                half_range_km = view_range_km * 0.4
                vertices = [
                    (def_x_km - half_range_km, def_y_km - half_range_km, def_z),
                    (def_x_km + half_range_km, def_y_km - half_range_km, def_z),
                    (def_x_km + half_range_km, def_y_km + half_range_km, def_z),
                    (def_x_km - half_range_km, def_y_km + half_range_km, def_z),
                    (def_x_km - half_range_km, def_y_km - half_range_km, def_z + weather_height),
                    (def_x_km + half_range_km, def_y_km - half_range_km, def_z + weather_height),
                    (def_x_km + half_range_km, def_y_km + half_range_km, def_z + weather_height),
                    (def_x_km - half_range_km, def_y_km + half_range_km, def_z + weather_height),
                ]

                for vx, vy, vz in vertices:
                    weather_x.append(vx)
                    weather_y.append(vy)
                    weather_z.append(vz)

                # Add weather volume as mesh with slightly stronger opacity for visibility
                weather_opacity = 0.14 if base_haze_opacity < 0.2 else 0.20
                if training_mode:
                    weather_opacity = min(0.36, weather_opacity * 1.4)

                fig.add_trace(go.Mesh3d(
                    x=weather_x,
                    y=weather_y,
                    z=weather_z,
                    color=(layer_color if layer_color else '#BFD7FF'),
                    opacity=weather_opacity,
                    showlegend=True,
                    name="Weather Volume (Advisory)",
                    hovertemplate=None,
                    hoverinfo='skip'
                ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_interception_windows_3d(
        fig: go.Figure,
        interception_data: List[Dict[str, Any]],
        defender_position: Dict[str, float]
    ):
        """
        Add interception feasibility windows visualization.
        
        ADVISORY ONLY - Visualizes mathematical feasibility assessment only.
        No control logic or engagement commands.
        """
        try:
            for data in interception_data:
                if not isinstance(data, dict):
                    continue
                
                # Extract interception window data
                feasibility = data.get('feasibility_level', 'NOT_FEASIBLE')
                target_pos = data.get('target_position', {})
                window_start = data.get('window_start_time', None)
                window_end = data.get('window_end_time', None)
                
                if not isinstance(target_pos, dict):
                    continue
                
                target_x = float(target_pos.get('x', 0.0)) if isinstance(target_pos.get('x'), (int, float)) else 0.0
                target_y = float(target_pos.get('y', 0.0)) if isinstance(target_pos.get('y'), (int, float)) else 0.0
                target_z = float(target_pos.get('z', 0.0)) if isinstance(target_pos.get('z'), (int, float)) else 0.0
                
                # Color based on feasibility
                if feasibility == 'HIGHLY_FEASIBLE':
                    color = 'rgba(255, 77, 79, 0.3)'
                elif feasibility == 'FEASIBLE':
                    color = 'rgba(250, 173, 20, 0.3)'
                elif feasibility == 'MARGINALLY_FEASIBLE':
                    color = 'rgba(74, 144, 226, 0.3)'
                else:
                    color = 'rgba(100, 100, 100, 0.2)'
                
                # Draw line from defender to target
                fig.add_trace(go.Scatter3d(
                    x=[defender_position['x'], target_x],
                    y=[defender_position['y'], target_y],
                    z=[defender_position['z'], target_z],
                    mode='lines',
                    line=dict(color=color, width=3),
                    name=f"Interception Window ({feasibility})",
                    showlegend=True,
                    hovertemplate=None,
                    hoverinfo='skip'
                ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_sensor_visualization_3d(
        fig: go.Figure,
        defender_position: Dict[str, float],
        view_range: float,
        scenario_key: Optional[str] = None,
        training_mode: bool = False,
        sensor_layer_controls: Optional[Dict[str, Any]] = None,
        global_opacity_override: Optional[float] = None,
        tracks: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Add sensor visualization using sensor_models.py definitions.
        
        ADVISORY ONLY - Visual representation only, no sensing or engagement logic.
        Sensor visuals do NOT imply firing or authorization.
        
        Sensor Types (from sensor_models.py):
        1) Long-Range Surveillance Radar (Green translucent dome)
        2) Precision Tracking Radar (Blue focused cone)
        3) Passive / ESM Sensor (Purple dashed arc)
        
        ADVISORY ONLY — SENSOR VISUALIZATION. NO CONTROL OR DECISION LOGIC.
        
        Rendering Rules:
        - Fixed positions (no movement)
        - Coverage volumes (cone or dome based on type)
        - Color-coded by type
        - Semi-transparent (opacity 0.05–0.15)
        - No animation loops
        - Geometry derived from fixed angles + radius
        """
        try:
            from abhedya.dashboard.sensor_models import SensorModels, SensorType
            
            # Get scenario-specific sensor layout
            if scenario_key:
                sensor_types_to_show = SensorModels.get_scenario_sensor_layout(scenario_key)
                # Filter sensor definitions to only include those in the scenario layout
                all_definitions = SensorModels.get_all_sensor_definitions()
                sensor_definitions = []
                for s in all_definitions:
                    metadata = s.get("metadata")
                    if metadata and metadata.sensor_type in sensor_types_to_show:
                        sensor_definitions.append(s)
            else:
                # Default: show all sensors
                sensor_definitions = SensorModels.get_all_sensor_definitions()
            
            # Apply sensor layer controls (toggles and opacity)
            global_opacity = None
            if sensor_layer_controls:
                # Filter by toggles (default: all ON)
                show_surveillance = sensor_layer_controls.get("show_surveillance", True)
                show_fire_control = sensor_layer_controls.get("show_fire_control", True)
                show_passive = sensor_layer_controls.get("show_passive", True)
                
                # Filter sensor definitions based on toggles
                filtered_definitions = []
                for sensor_def in sensor_definitions:
                    metadata = sensor_def.get("metadata")
                    if not metadata:
                        continue
                    sensor_type = metadata.sensor_type
                    if sensor_type == SensorType.LONG_RANGE_SURVEILLANCE and not show_surveillance:
                        continue
                    if sensor_type == SensorType.FIRE_CONTROL and not show_fire_control:
                        continue
                    if sensor_type == SensorType.PASSIVE_ESM and not show_passive:
                        continue
                    filtered_definitions.append(sensor_def)
                
                sensor_definitions = filtered_definitions
                
                # Get global opacity override (if provided)
                global_opacity = sensor_layer_controls.get("global_opacity")

            # If a direct override was provided (from caller), prefer it
            if global_opacity_override is not None:
                try:
                    global_opacity = float(global_opacity_override)
                except Exception:
                    pass

            # Add a visible training watermark and legend note when in training_mode
            try:
                if training_mode:
                    fig.add_annotation(
                        text="SIMULATION / TRAINING MODE",
                        xref='paper', yref='paper',
                        x=0.02, y=0.98,
                        showarrow=False,
                        font=dict(size=12, color='rgba(255,255,255,0.85)', family='Arial', bold=True),
                        bgcolor='rgba(255,255,255,0.02)'
                    )
                    # Slightly enhance overall atmospheric tint when training to make it intentional
                    try:
                        fig.layout.plot_bgcolor = 'rgba(12,16,25,1)'
                    except Exception:
                        pass
            except Exception:
                pass
            
            # CRITICAL STEP 3: Sensor volumes MUST render when toggles are ON
            # Verify multiple sensors exist (at least 3 required for full visualization)
            # Note: After filtering, we may have fewer than 3, which is acceptable
            # BUT: If sensor_layer_controls indicate sensors should be shown, we MUST render them
            if len(sensor_definitions) == 0:
                # Check if sensors were filtered out but toggles are ON
                # If toggles are ON, we should still render default sensors
                if sensor_layer_controls:
                    show_surveillance = sensor_layer_controls.get("show_surveillance", True)
                    show_fire_control = sensor_layer_controls.get("show_fire_control", True)
                    show_passive = sensor_layer_controls.get("show_passive", True)
                    # If any toggle is ON but no sensors found, try to get default sensors
                    if show_surveillance or show_fire_control or show_passive:
                        try:
                            from abhedya.dashboard.sensor_models import SensorModels
                            sensor_definitions = SensorModels.get_all_sensor_definitions()
                            # Re-apply filtering
                            filtered_definitions = []
                            for sensor_def in sensor_definitions:
                                metadata = sensor_def.get("metadata")
                                if not metadata:
                                    continue
                                sensor_type = metadata.sensor_type
                                if sensor_type == SensorType.LONG_RANGE_SURVEILLANCE and not show_surveillance:
                                    continue
                                if sensor_type == SensorType.FIRE_CONTROL and not show_fire_control:
                                    continue
                                if sensor_type == SensorType.PASSIVE_ESM and not show_passive:
                                    continue
                                filtered_definitions.append(sensor_def)
                            sensor_definitions = filtered_definitions
                        except Exception:
                            pass  # Fail silently if sensor models unavailable
                
                # If still no sensors after fallback, return (all toggles OFF)
                if len(sensor_definitions) == 0:
                    return
            
            # Convert defender position to km for X, Y
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            view_range_km = view_range / 1000.0
            
            # Render all sensors simultaneously (coverage volumes may overlap visually)
            # Overlap does NOT imply fusion or logic - purely visual
            # Track which sensor-type legend entries have been added
            sensor_type_shown = {}
            for sensor_def in sensor_definitions:
                geometry = sensor_def.get("geometry")
                metadata = sensor_def.get("metadata")
                
                if not geometry or not metadata:
                    continue
                
                # Calculate absolute position (relative to defender)
                pos_x_km = def_x_km + geometry.position_x_km
                pos_y_km = def_y_km + geometry.position_y_km
                pos_z = def_z + geometry.position_z_m
                
                # Skip if sensor is outside view range
                distance_from_center_km = math.sqrt(
                    (pos_x_km - def_x_km)**2 + (pos_y_km - def_y_km)**2
                )
                if distance_from_center_km > view_range_km * 1.2:
                    continue
                
                # Extract sensor properties
                sensor_name = metadata.name
                sensor_type = metadata.sensor_type.value
                role = metadata.role
                color = metadata.color
                coverage_color = metadata.coverage_color
                
                # Append "SIMULATION / TRAINING DATA" in training mode
                display_name = sensor_name
                if training_mode:
                    display_name = f"{sensor_name} — SIMULATION / TRAINING DATA"
                
                # Create hover text (MUST include: name, type, role, "Advisory Only — Visualization")
                hover_text = (
                    f"<b>{display_name}</b><br>"
                    f"Type: {sensor_type}<br>"
                    f"Role: {role}<br>"
                    f"<br>Advisory Only — Visualization"
                )
                
                # 1. Sensor position marker (ground anchor)
                # Slightly increase opacity in training mode for teaching clarity
                marker_opacity = 1.0 if not training_mode else 1.0  # Keep full opacity for markers
                # Map sensor type to a canonical legend label
                # Consolidate sensor legend under a single 'Surveillance Sensors' entry
                show_legend_now = not bool(sensor_type_shown.get('Surveillance Sensors', False))

                # Prepare sensor hover customdata and hovertemplate per spec
                # Sensor Name, Type, State (always Active), Visible Tracks (never None in training)
                sensor_id = metadata.name if getattr(metadata, 'name', None) else (sensor_name or 'N/A')
                sensor_type_label = sensor_type if sensor_type else 'N/A'
                # Range: prefer geometry.coverage_range_km, fallback to metadata info
                try:
                    range_km_val = float(geometry.coverage_range_km) if getattr(geometry, 'coverage_range_km', None) is not None else None
                except Exception:
                    range_km_val = None

                range_str = f"{int(range_km_val)} km" if range_km_val is not None else 'N/A'
                # State MUST be Active (never N/A, None, Unknown)
                state_display = "Active"
                # Visible Tracks: never None; deterministic list from current scene tracks
                try:
                    track_list = list(tracks) if isinstance(tracks, list) else []
                    visible_ids = sorted([str(t.get("track_id", "")) for t in track_list if isinstance(t, dict) and t.get("track_id") is not None])
                    if visible_ids:
                        visible_tracks_str = "<br>".join([f"- {tid}" for tid in visible_ids])
                    else:
                        visible_tracks_str = "- (No tracks in scene)"
                except Exception:
                    visible_tracks_str = "- (No tracks in scene)"

                sensor_custom = [sensor_id, sensor_type_label, range_str, state_display, visible_tracks_str]
                sensor_hovertemplate = (
                    "Sensor: %{customdata[0]}<br>"
                    "Type: %{customdata[1]}<br>"
                    "Range: %{customdata[2]}<br>"
                    "State: %{customdata[3]}<br>"
                    "Visible Tracks:<br>%{customdata[4]}<extra></extra>"
                )

                fig.add_trace(go.Scatter3d(
                    x=[pos_x_km],
                    y=[pos_y_km],
                    z=[pos_z],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=(color if color else ('#22C55E' if metadata.sensor_type == SensorType.LONG_RANGE_SURVEILLANCE else ('#3B82F6' if metadata.sensor_type == SensorType.FIRE_CONTROL else '#8B5CF6'))),
                        symbol='circle',
                        line=dict(width=2, color='white'),
                        opacity=marker_opacity
                    ),
                    name='Surveillance Sensors',
                    legendgroup='sensors',
                    showlegend=show_legend_now,
                    customdata=[sensor_custom],
                    hovertemplate=None,
                    hoverinfo='skip',
                    meta={'is_sensor': True, 'sensor_type': getattr(metadata.sensor_type, 'name', sensor_type_label)}
                ))
                if show_legend_now:
                    sensor_type_shown['Surveillance Sensors'] = True
                
                # 2. Render coverage volume based on sensor type
                # Multiple sensors render simultaneously - coverage volumes may overlap visually
                # Overlap does NOT imply: fusion, detection logic, priority, or dominance
                # Sensor volumes MUST be visible but NOT hide tracks
                # Sensors render BEFORE tracks, so opacity must be moderate
                base_opacity = 0.26 if metadata.sensor_type == SensorType.LONG_RANGE_SURVEILLANCE else (0.28 if metadata.sensor_type == SensorType.FIRE_CONTROL else 0.22)
                training_opacity = min(0.40, base_opacity * 1.15) if training_mode else base_opacity
                
                # Apply global opacity override if provided (from UI slider)
                final_opacity = global_opacity if global_opacity is not None else training_opacity
                # Ensure coverage volumes are visible: allow a slightly larger range but keep them semi-transparent
                final_opacity = max(0.16, min(0.40, final_opacity))

                # Propagate EW environment state into sensor coverage visuals (display-only).
                # Reduce coverage opacity slightly based on sensor reliability under EW,
                # using the existing EWReliabilityModel (ADVISORY ONLY - visual cue).
                try:
                    from abhedya.dashboard.visual_components import EWReliabilityModel
                    from abhedya.dashboard.state_manager import DashboardStateManager

                    ew_state = None
                    try:
                        ew_state = DashboardStateManager.get_ew_environment_state() if DashboardStateManager else None
                    except Exception:
                        ew_state = None

                    if ew_state and ew_state.upper() not in ['NONE', 'NORMAL']:
                        # Map sensor name to type and get reliability score
                        try:
                            sensor_type_mapped = EWReliabilityModel.map_sensor_name_to_type(sensor_name)
                            reliability_data = EWReliabilityModel.get_sensor_reliability(sensor_type_mapped, ew_state, training_mode)
                            reliability_score = float(reliability_data.get('reliability_score', 1.0)) if isinstance(reliability_data, dict) else 1.0
                            # Reduce opacity proportionally to reliability (visual-only)
                            # But keep minimum visibility - operator must see degraded sensors
                            final_opacity = final_opacity * max(0.50, min(1.0, reliability_score))
                            final_opacity = max(0.12, min(0.30, final_opacity))  # Keep visible even when degraded
                            # Annotate hover text with EW advisory note
                            hover_text = hover_text + f"<br>EW Environment: {str(ew_state).upper()} (Advisory)"
                        except Exception:
                            pass
                except Exception:
                    # If visual components unavailable, skip EW visual propagation
                    pass
                
                if metadata.sensor_type == SensorType.LONG_RANGE_SURVEILLANCE:
                    # Green translucent dome (omnidirectional)
                    Battlespace3D._render_coverage_dome(
                            fig, pos_x_km, pos_y_km, pos_z,
                            geometry.coverage_range_km,
                            geometry.coverage_altitude_ceiling_m,
                            (coverage_color if coverage_color else '#22C55E'),
                            hover_text,
                            opacity=final_opacity,
                            sensor_type=getattr(metadata.sensor_type, 'name', 'LONG_RANGE_SURVEILLANCE')
                        )
                
                elif metadata.sensor_type == SensorType.FIRE_CONTROL:
                    # Blue focused cone (directional)
                    Battlespace3D._render_coverage_cone(
                            fig, pos_x_km, pos_y_km, pos_z,
                            geometry.coverage_range_km,
                            geometry.coverage_altitude_ceiling_m,
                            geometry.beam_width_deg,
                            geometry.beam_elevation_deg,
                            (coverage_color if coverage_color else '#3B82F6'),
                            hover_text,
                            opacity=final_opacity,
                            sensor_type=getattr(metadata.sensor_type, 'name', 'FIRE_CONTROL')
                        )
                
                elif metadata.sensor_type == SensorType.PASSIVE_ESM:
                    # Purple dashed arc (directional, passive)
                    Battlespace3D._render_coverage_arc(
                            fig, pos_x_km, pos_y_km, pos_z,
                            geometry.coverage_range_km,
                            geometry.coverage_altitude_ceiling_m,
                            geometry.beam_width_deg,
                            geometry.beam_elevation_deg,
                            (coverage_color if coverage_color else '#8B5CF6'),
                            hover_text,
                            opacity=final_opacity,
                            sensor_type=getattr(metadata.sensor_type, 'name', 'PASSIVE_ESM')
                        )
        except Exception:
            # Fallback to legacy implementation if sensor_models unavailable
            try:
                Battlespace3D._add_multi_radar_sensors_3d(fig, defender_position, view_range)
            except Exception:
                Battlespace3D._add_ground_radars_3d(fig, defender_position, view_range)
    
    @staticmethod
    def _render_coverage_dome(
        fig: go.Figure,
        center_x_km: float,
        center_y_km: float,
        center_z_m: float,
        range_km: float,
        altitude_ceiling_m: float,
        color: str,
        hover_text: str,
        opacity: float = 0.22,
        sensor_type: str = 'LONG_RANGE_SURVEILLANCE'
    ):
        """
        Render omnidirectional coverage dome (for Surveillance Radar).
        
        VISUALIZATION ONLY - Geometry derived from fixed angles + radius.
        """
        try:
            # Create hemisphere dome (omnidirectional coverage)
            segments = 24
            theta_segments = 12  # Half sphere only
            
            dome_x = []
            dome_y = []
            dome_z = []
            
            for i in range(theta_segments + 1):
                theta = math.pi * i / theta_segments  # 0 to pi (half sphere)
                for j in range(segments + 1):
                    phi = 2 * math.pi * j / segments
                    x = center_x_km + range_km * math.sin(theta) * math.cos(phi)
                    y = center_y_km + range_km * math.sin(theta) * math.sin(phi)
                    z = center_z_m + range_km * 1000.0 * math.cos(theta)  # Convert to meters
                    # Clamp to altitude ceiling
                    z = min(z, center_z_m + altitude_ceiling_m)
                    dome_x.append(x)
                    dome_y.append(y)
                    dome_z.append(z)
            
            # Add dome mesh (semi-transparent) with lighting for depth perception
            fig.add_trace(go.Mesh3d(
                x=dome_x,
                y=dome_y,
                z=dome_z,
                color=color,
                opacity=opacity,  # Semi-transparent (adjustable for training mode)
                lighting=dict(ambient=0.6, diffuse=0.6, specular=0.2, roughness=0.9),
                showlegend=False,
                hovertemplate=None,
                hoverinfo='skip',
                meta={'is_sensor': True, 'sensor_type': sensor_type}
            ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _render_coverage_cone(
        fig: go.Figure,
        center_x_km: float,
        center_y_km: float,
        center_z_m: float,
        range_km: float,
        altitude_ceiling_m: float,
        beam_width_deg: float,
        beam_elevation_deg: float,
        color: str,
        hover_text: str,
        opacity: float = 0.24,
        sensor_type: str = 'FIRE_CONTROL'
    ):
        """
        Render directional coverage cone (for Precision Tracking Radar).
        
        VISUALIZATION ONLY - Geometry derived from fixed angles + radius.
        """
        try:
            # Convert angles to radians
            beam_width_rad = math.radians(beam_width_deg)
            beam_elevation_rad = math.radians(beam_elevation_deg)
            
            # Create cone geometry (focused beam)
            cone_segments = 16
            range_steps = 8
            
            cone_x = []
            cone_y = []
            cone_z = []
            
            # Base of cone (at sensor position)
            cone_x.append(center_x_km)
            cone_y.append(center_y_km)
            cone_z.append(center_z_m)
            
            # Generate cone surface points
            for r_step in range(1, range_steps + 1):
                r = (r_step / range_steps) * range_km
                altitude = r * 1000.0 * math.sin(beam_elevation_rad)
                altitude = min(altitude, altitude_ceiling_m)
                
                for i in range(cone_segments + 1):
                    angle = 2 * math.pi * i / cone_segments
                    # Cone expands with distance
                    radius_at_r = r * math.tan(beam_width_rad / 2.0)
                    
                    x = center_x_km + radius_at_r * math.cos(angle)
                    y = center_y_km + radius_at_r * math.sin(angle)
                    z = center_z_m + altitude
                    
                    cone_x.append(x)
                    cone_y.append(y)
                    cone_z.append(z)
            
            # Add cone mesh (semi-transparent) with lighting for clearer depth
            fig.add_trace(go.Mesh3d(
                x=cone_x,
                y=cone_y,
                z=cone_z,
                color=color,
                opacity=opacity,  # Semi-transparent (adjustable for training mode)
                lighting=dict(ambient=0.6, diffuse=0.65, specular=0.2, roughness=0.8),
                showlegend=False,
                hovertemplate=None,
                hoverinfo='skip',
                meta={'is_sensor': True, 'sensor_type': sensor_type}
            ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _render_coverage_arc(
        fig: go.Figure,
        center_x_km: float,
        center_y_km: float,
        center_z_m: float,
        range_km: float,
        altitude_ceiling_m: float,
        beam_width_deg: float,
        beam_elevation_deg: float,
        color: str,
        hover_text: str,
        opacity: float = 0.18,
        sensor_type: str = 'PASSIVE_ESM'
    ):
        """
        Render directional coverage arc (for Passive / ESM Sensor).
        
        VISUALIZATION ONLY - Geometry derived from fixed angles + radius.
        Uses dashed line style to indicate passive nature.
        """
        try:
            # Convert angles to radians
            beam_width_rad = math.radians(beam_width_deg)
            beam_elevation_rad = math.radians(beam_elevation_deg)
            
            # Create arc geometry (directional, passive)
            range_steps = 10
            
            # Generate arc outline points (dashed appearance via sparse points)
            arc_x = []
            arc_y = []
            arc_z = []
            
            # Left edge of arc
            for r_step in range(0, range_steps + 1, 2):  # Step by 2 for dashed effect
                r = (r_step / range_steps) * range_km
                altitude = r * 1000.0 * math.sin(beam_elevation_rad)
                altitude = min(altitude, altitude_ceiling_m)
                
                angle = -beam_width_rad / 2.0
                radius_at_r = r * math.tan(beam_width_rad / 2.0)
                
                x = center_x_km + radius_at_r * math.cos(angle)
                y = center_y_km + radius_at_r * math.sin(angle)
                z = center_z_m + altitude
                
                arc_x.append(x)
                arc_y.append(y)
                arc_z.append(z)
            
            # Right edge of arc (reverse order)
            for r_step in range(range_steps, -1, -2):  # Step by 2 for dashed effect
                r = (r_step / range_steps) * range_km
                altitude = r * 1000.0 * math.sin(beam_elevation_rad)
                altitude = min(altitude, altitude_ceiling_m)
                
                angle = beam_width_rad / 2.0
                radius_at_r = r * math.tan(beam_width_rad / 2.0)
                
                x = center_x_km + radius_at_r * math.cos(angle)
                y = center_y_km + radius_at_r * math.sin(angle)
                z = center_z_m + altitude
                
                arc_x.append(x)
                arc_y.append(y)
                arc_z.append(z)
            
            # Add arc as line trace (dashed appearance)
            fig.add_trace(go.Scatter3d(
                x=arc_x,
                y=arc_y,
                z=arc_z,
                mode='lines',
                line=dict(
                    color=color,
                    width=3,
                    dash='dash'  # Dashed line for passive sensor
                ),
                name="Passive Sensor Arc",
                showlegend=False,
                hovertemplate=None,
                hoverinfo='skip',
                meta={'is_sensor': True, 'sensor_type': sensor_type}
            ))
            
            # Add semi-transparent arc fill with subtle lighting for depth
            if len(arc_x) > 2:
                fig.add_trace(go.Mesh3d(
                    x=arc_x,
                    y=arc_y,
                    z=arc_z,
                    color=color,
                    opacity=opacity,  # Semi-transparent for passive sensor
                    lighting=dict(ambient=0.55, diffuse=0.6, specular=0.15, roughness=0.9),
                    showlegend=False,
                    hovertemplate=None,
                    hoverinfo='skip',
                    meta={'is_sensor': True, 'sensor_type': sensor_type}
                ))
        except Exception:
            pass  # Fail silently
    
    @staticmethod
    def _add_multi_radar_sensors_3d(
        fig: go.Figure,
        defender_position: Dict[str, float],
        view_range: float
    ):
        """
        Add comprehensive multi-radar sensor visualization layer.
        
        ADVISORY ONLY - Visual representation only, no sensing or engagement logic.
        Sensor visuals do NOT imply firing or authorization.
        
        Radar Types:
        1) Long-Range Surveillance Radar (Green, tall mast + wide dome, large coverage)
        2) Precision Tracking Radar (Blue, medium mast + focused dome, medium coverage)
        3) Low-Altitude / Counter-UAS Radar (Amber, short mast + shallow dome, small coverage)
        4) Early Warning Radar (Purple, very tall mast + wide dome, extended range)
        
        ADVISORY ONLY — SENSOR VISUALIZATION. NO CONTROL OR DECISION LOGIC.
        5) Tracking Radar (Cyan, medium mast + focused dome, precision tracking)
        """
        try:
            from abhedya.dashboard.sensor_visualization import SensorVisualization
            
            # Get comprehensive sensor configurations
            sensor_configs = SensorVisualization.get_sensor_configurations(
                defender_position=defender_position,
                view_range=view_range,
                include_all_types=True
            )
            
            # Convert defender position to km for X, Y
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            view_range_km = view_range / 1000.0
            
            for sensor_config in sensor_configs:
                # single legend entry for sensors
                if 'sensors_legend_added' not in locals():
                    sensors_legend_added = False
                pos_x_km = sensor_config['position_km']['x']
                pos_y_km = sensor_config['position_km']['y']
                pos_z = sensor_config['position_km']['z']
                
                # Skip if sensor is outside view range
                distance_from_center_km = math.sqrt(
                    (pos_x_km - def_x_km)**2 + (pos_y_km - def_y_km)**2
                )
                if distance_from_center_km > view_range_km * 1.2:  # Slightly beyond view for coverage
                    continue
                
                mast_height = sensor_config['mast_height_m']
                dome_radius = sensor_config['dome_radius_m']
                coverage_radius_km = sensor_config['range_km']
                color = sensor_config['color']
                coverage_color = sensor_config['coverage_color']
                sensor_name = sensor_config['name']
                hover_text = SensorVisualization.get_sensor_hover_text(sensor_config)
                
                # 1. Ground anchor point (small marker at base)
                # Map sensor name/type to canonical legend label for multi-radar fallback
                try:
                    lname = sensor_name.lower()
                    if 'surveil' in lname or 'long' in lname:
                        sensor_legend_label = 'Long-Range Surveillance Radar'
                    elif 'precision' in lname or 'fire' in lname:
                        sensor_legend_label = 'Precision Tracking Radar'
                    elif 'passive' in lname or 'esm' in lname:
                        sensor_legend_label = 'Passive / ESM Sensor'
                    else:
                        sensor_legend_label = sensor_name
                except Exception:
                    sensor_legend_label = sensor_name

                show_sensor_legend = not bool(locals().get('sensors_legend_added', False)) and True
                # Anchor point for sensor (visual only) — do not capture hover to avoid stealing track hover
                fig.add_trace(go.Scatter3d(
                    x=[pos_x_km],
                    y=[pos_y_km],
                    z=[pos_z],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=color,
                        symbol='circle',
                        line=dict(width=2, color='white')
                    ),
                    name=sensor_legend_label,
                    legendgroup=sensor_legend_label,
                    showlegend=show_sensor_legend,
                    hovertemplate=None,
                    hoverinfo='skip'
                ))
                # mark that at least one sensor legend entry was added (fallback path)
                sensors_legend_added = True
                
                # 2. 3D Mast (cylinder)
                mast_segments = 16
                mast_radius = 0.5  # meters, converted to km for X, Y
                mast_radius_km = mast_radius / 1000.0
                
                for i in range(mast_segments):
                    angle = 2 * math.pi * i / mast_segments
                    next_angle = 2 * math.pi * (i + 1) / mast_segments
                    
                    # Create cylinder side faces
                    x_cyl = [
                        pos_x_km + mast_radius_km * math.cos(angle),
                        pos_x_km + mast_radius_km * math.cos(next_angle),
                        pos_x_km + mast_radius_km * math.cos(next_angle),
                        pos_x_km + mast_radius_km * math.cos(angle)
                    ]
                    y_cyl = [
                        pos_y_km + mast_radius_km * math.sin(angle),
                        pos_y_km + mast_radius_km * math.sin(next_angle),
                        pos_y_km + mast_radius_km * math.sin(next_angle),
                        pos_y_km + mast_radius_km * math.sin(angle)
                    ]
                    z_cyl = [pos_z, pos_z, pos_z + mast_height, pos_z + mast_height]
                    
                    fig.add_trace(go.Mesh3d(
                        x=x_cyl,
                        y=y_cyl,
                        z=z_cyl,
                        color=color,
                        opacity=0.8,
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                
                # 3. Dome (semi-sphere on top of mast)
                dome_top_z = pos_z + mast_height
                dome_segments = 16
                dome_theta_segments = 8  # Half sphere only
                
                dome_x = []
                dome_y = []
                dome_z = []
                
                for i in range(dome_theta_segments + 1):
                    theta = math.pi * i / dome_theta_segments  # 0 to pi (half sphere)
                    for j in range(dome_segments + 1):
                        phi = 2 * math.pi * j / dome_segments
                        x_dome = pos_x_km + (dome_radius / 1000.0) * math.sin(theta) * math.cos(phi)
                        y_dome = pos_y_km + (dome_radius / 1000.0) * math.sin(theta) * math.sin(phi)
                        z_dome = dome_top_z + dome_radius * math.cos(theta)
                        dome_x.append(x_dome)
                        dome_y.append(y_dome)
                        dome_z.append(z_dome)
                
                # Create dome mesh
                fig.add_trace(go.Mesh3d(
                    x=dome_x,
                    y=dome_y,
                    z=dome_z,
                    color=color,
                    opacity=0.7,
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # 4. Coverage hemisphere (semi-transparent)
                coverage_segments = 24
                coverage_theta_segments = 12  # Half sphere only
                
                coverage_x = []
                coverage_y = []
                coverage_z = []
                
                for i in range(coverage_theta_segments + 1):
                    theta = math.pi * i / coverage_theta_segments  # 0 to pi (half sphere)
                    for j in range(coverage_segments + 1):
                        phi = 2 * math.pi * j / coverage_segments
                        x_cov = pos_x_km + coverage_radius_km * math.sin(theta) * math.cos(phi)
                        y_cov = pos_y_km + coverage_radius_km * math.sin(theta) * math.sin(phi)
                        z_cov = pos_z + coverage_radius_km * 1000.0 * math.cos(theta)  # Convert to meters
                        coverage_x.append(x_cov)
                        coverage_y.append(y_cov)
                        coverage_z.append(z_cov)
                
                # Create coverage hemisphere mesh
                fig.add_trace(go.Mesh3d(
                    x=coverage_x,
                    y=coverage_y,
                    z=coverage_z,
                    color=coverage_color,
                    opacity=0.08,
                    showlegend=False,
                    hovertemplate=None,
                    hoverinfo='skip'
                ))
        except Exception:
            # Fallback to original 3-radar implementation if sensor visualization module unavailable
            Battlespace3D._add_ground_radars_3d(fig, defender_position, view_range)
    
    @staticmethod
    def _is_track_in_sensor_coverage(
        track_pos: Dict[str, float],
        sensor_pos_km: Tuple[float, float, float],
        sensor_range_km: float,
        sensor_altitude_ceiling_m: float,
        sensor_type: str,
        sensor_beam_width_deg: float,
        sensor_beam_elevation_deg: float
    ) -> bool:
        """
        Check if track is within sensor coverage volume (geometric check only).
        
        VISUALIZATION ONLY - Pure geometry check, no detection or tracking logic.
        Visual indication only — geometric overlap within coverage volumes.
        No probability, no tracking state, no authorization implied.
        
        Args:
            track_pos: Track position dict with x, y, z (in meters)
            sensor_pos_km: Sensor position tuple (x_km, y_km, z_m)
            sensor_range_km: Sensor coverage range in km
            sensor_altitude_ceiling_m: Sensor altitude ceiling in meters
            sensor_type: Sensor type string
            sensor_beam_width_deg: Beam width in degrees (for directional sensors)
            sensor_beam_elevation_deg: Beam elevation in degrees
        
        Returns:
            True if track is geometrically within coverage, False otherwise
        """
        try:
            # Convert track position to km for X, Y
            track_x_km = track_pos.get('x', 0.0) / 1000.0
            track_y_km = track_pos.get('y', 0.0) / 1000.0
            track_z_m = track_pos.get('z', 0.0)
            
            sensor_x_km, sensor_y_km, sensor_z_m = sensor_pos_km
            
            # Calculate horizontal distance
            dx_km = track_x_km - sensor_x_km
            dy_km = track_y_km - sensor_y_km
            horizontal_distance_km = math.sqrt(dx_km**2 + dy_km**2)
            
            # Check range (horizontal distance must be within sensor range)
            if horizontal_distance_km > sensor_range_km:
                return False
            
            # Check altitude ceiling
            if track_z_m > sensor_z_m + sensor_altitude_ceiling_m:
                return False
            
            # For omnidirectional sensors (360° beam width), that's all we need
            if sensor_beam_width_deg >= 360.0:
                return True
            
            # For directional sensors, check if track is within beam angle
            # Calculate angle from sensor to track
            track_angle_rad = math.atan2(dy_km, dx_km)
            track_angle_deg = math.degrees(track_angle_rad)
            
            # For simplicity, assume beam is centered at 0° (north)
            # In a real system, this would use the sensor's actual pointing angle
            beam_half_width_deg = sensor_beam_width_deg / 2.0
            # Normalize angle to 0-360
            track_angle_deg = (track_angle_deg + 360.0) % 360.0
            
            # Check if within beam (simplified - assumes beam centered at 0°)
            # For visualization, we'll use a generous check
            if sensor_beam_width_deg < 360.0:
                # Check if track is within beam arc
                # Simplified: check if angle is within ±beam_half_width from 0° or 180°
                angle_from_center = min(
                    abs(track_angle_deg),
                    abs(track_angle_deg - 360.0),
                    abs(track_angle_deg - 180.0)
                )
                if angle_from_center > beam_half_width_deg:
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def _add_sensor_track_hints_3d(
        fig: go.Figure,
        tracks: List[Dict[str, Any]],
        defender_position: Dict[str, float],
        view_range: float
    ):
        """
        Add optional visual hints (faint, dotted lines) between sensors and tracks within coverage.
        
        ADVISORY ONLY - Lines show "within coverage" only (geometric check).
        Visual indication only — geometric overlap within coverage volumes.
        No probability, no tracking state, no authorization implied.
        Lines are derived purely from geometry.
        
        Rules:
        - Lines must be faint, dotted, and advisory
        - Lines show "within coverage" only
        - Visual indication only — geometric overlap
        - No probability, no tracking state, no authorization implied
        - Lines are derived purely from geometry
        """
        try:
            from abhedya.dashboard.sensor_models import SensorModels, SensorType
            
            # Default: show all sensors (scenario_key not in signature, removed UI wiring)
            sensor_definitions = SensorModels.get_all_sensor_definitions()
            
            if not sensor_definitions or len(sensor_definitions) == 0:
                return
            
            # Convert defender position to km for X, Y
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            # For each sensor, check which tracks are within coverage
            for sensor_def in sensor_definitions:
                geometry = sensor_def.get("geometry")
                metadata = sensor_def.get("metadata")
                
                if not geometry or not metadata:
                    continue
                
                # Calculate sensor absolute position
                sensor_x_km = def_x_km + geometry.position_x_km
                sensor_y_km = def_y_km + geometry.position_y_km
                sensor_z_m = def_z + geometry.position_z_m
                sensor_pos_km = (sensor_x_km, sensor_y_km, sensor_z_m)
                
                # Check each track
                for track in tracks:
                    if not isinstance(track, dict):
                        continue
                    
                    track_pos = track.get('position', {})
                    if not isinstance(track_pos, dict):
                        continue
                    
                    # Geometric check: is track within sensor coverage?
                    is_in_coverage = Battlespace3D._is_track_in_sensor_coverage(
                        track_pos=track_pos,
                        sensor_pos_km=sensor_pos_km,
                        sensor_range_km=geometry.coverage_range_km,
                        sensor_altitude_ceiling_m=geometry.coverage_altitude_ceiling_m,
                        sensor_type=metadata.sensor_type.value,
                        sensor_beam_width_deg=geometry.beam_width_deg,
                        sensor_beam_elevation_deg=geometry.beam_elevation_deg
                    )
                    
                    if is_in_coverage:
                        # Draw faint, dotted line from sensor to track
                        track_x_km = track_pos.get('x', 0.0) / 1000.0
                        track_y_km = track_pos.get('y', 0.0) / 1000.0
                        track_z_m = track_pos.get('z', 0.0)
                        
                        # Use sensor color but very faint
                        line_color = metadata.color
                        # Convert hex to rgba with low opacity
                        if line_color.startswith('#'):
                            # Extract RGB
                            r = int(line_color[1:3], 16)
                            g = int(line_color[3:5], 16)
                            b = int(line_color[5:7], 16)
                            line_color_rgba = f'rgba({r}, {g}, {b}, 0.15)'  # Very faint
                        else:
                            line_color_rgba = line_color
                        
                        # Add faint, dotted line
                        fig.add_trace(go.Scatter3d(
                            x=[sensor_x_km, track_x_km],
                            y=[sensor_y_km, track_y_km],
                            z=[sensor_z_m, track_z_m],
                            mode='lines',
                            line=dict(
                                color=line_color_rgba,
                                width=1,
                                dash='dot'  # Dotted line
                            ),
                            name=f"{metadata.name} → Track",
                            showlegend=False,
                            hovertemplate=None,
                            hoverinfo='skip'
                        ))
        except Exception:
            pass  # Fail silently - visual hints are non-critical
    
    @staticmethod
    def _add_ground_radars_3d(
        fig: go.Figure,
        defender_position: Dict[str, float],
        view_range: float
    ):
        """
        Add multiple ground radars as 3D visual objects.
        
        ADVISORY ONLY - Visual representation only, no sensing or engagement logic.
        
        Radar Types:
        1) Long-Range Surveillance Radar (Green, tall mast + wide dome, large coverage)
        2) Precision Tracking Radar (Blue, medium mast + focused dome, medium coverage)
        3) Low-Altitude / Counter-UAS Radar (Amber, short mast + shallow dome, small coverage)
        
        ADVISORY ONLY — SENSOR VISUALIZATION. NO CONTROL OR DECISION LOGIC.
        """
        try:
            # Convert defender position to km for X, Y
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            view_range_km = view_range / 1000.0
            
            # Define radar positions (relative to defender, in km for X, Y, meters for Z)
            radar_configs = [
                {
                    'type': 'Long-Range Surveillance',
                    'position_km': {'x': def_x_km - 5.0, 'y': def_y_km - 5.0, 'z': def_z},
                    'mast_height_m': 40.0,  # Tall mast
                    'dome_radius_m': 8.0,  # Wide dome
                    'coverage_radius_km': 100.0,  # Large coverage
                    'color': '#52C41A',  # Green
                    'coverage_color': 'rgba(82, 196, 26, 0.12)'  # Semi-transparent green
                },
                {
                    'type': 'Precision Tracking',
                    'position_km': {'x': def_x_km + 5.0, 'y': def_y_km - 5.0, 'z': def_z},
                    'mast_height_m': 25.0,  # Medium mast
                    'dome_radius_m': 5.0,  # Focused dome
                    'coverage_radius_km': 50.0,  # Medium coverage
                    'color': '#1890FF',  # Blue
                    'coverage_color': 'rgba(24, 144, 255, 0.12)'  # Semi-transparent blue
                },
                {
                    'type': 'Low-Altitude / Counter-UAS',
                    'position_km': {'x': def_x_km, 'y': def_y_km + 8.0, 'z': def_z},
                    'mast_height_m': 12.0,  # Short mast
                    'dome_radius_m': 3.0,  # Shallow dome
                    'coverage_radius_km': 20.0,  # Small coverage
                    'color': '#FAAD14',  # Amber
                    'coverage_color': 'rgba(250, 173, 20, 0.12)'  # Semi-transparent amber
                }
            ]
            
            for radar in radar_configs:
                pos_x_km = radar['position_km']['x']
                pos_y_km = radar['position_km']['y']
                pos_z = radar['position_km']['z']
                
                # Skip if radar is outside view range
                distance_from_center_km = math.sqrt(
                    (pos_x_km - def_x_km)**2 + (pos_y_km - def_y_km)**2
                )
                if distance_from_center_km > view_range_km:
                    continue
                
                mast_height = radar['mast_height_m']
                dome_radius = radar['dome_radius_m']
                coverage_radius_km = radar['coverage_radius_km']
                color = radar['color']
                coverage_color = radar['coverage_color']
                
                # 1. Ground anchor point (small marker at base)
                fig.add_trace(go.Scatter3d(
                    x=[pos_x_km],
                    y=[pos_y_km],
                    z=[pos_z],
                    mode='markers',
                    marker=dict(
                        size=6,
                        color=color,
                        symbol='circle',
                        line=dict(width=1, color='white')
                    ),
                    name=f"{radar['type']} Radar",
                    showlegend=True,
                    hovertemplate=None,
                    hoverinfo='skip'
                ))
                
                # 2. 3D Mast (cylinder)
                mast_segments = 16
                mast_radius = 0.5  # meters, converted to km for X, Y
                mast_radius_km = mast_radius / 1000.0
                
                for i in range(mast_segments):
                    angle = 2 * math.pi * i / mast_segments
                    next_angle = 2 * math.pi * (i + 1) / mast_segments
                    
                    # Create cylinder side faces
                    x_cyl = [
                        pos_x_km + mast_radius_km * math.cos(angle),
                        pos_x_km + mast_radius_km * math.cos(next_angle),
                        pos_x_km + mast_radius_km * math.cos(next_angle),
                        pos_x_km + mast_radius_km * math.cos(angle)
                    ]
                    y_cyl = [
                        pos_y_km + mast_radius_km * math.sin(angle),
                        pos_y_km + mast_radius_km * math.sin(next_angle),
                        pos_y_km + mast_radius_km * math.sin(next_angle),
                        pos_y_km + mast_radius_km * math.sin(angle)
                    ]
                    z_cyl = [pos_z, pos_z, pos_z + mast_height, pos_z + mast_height]
                    
                    fig.add_trace(go.Mesh3d(
                        x=x_cyl,
                        y=y_cyl,
                        z=z_cyl,
                        color=color,
                        opacity=0.8,
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                
                # 3. Dome (semi-sphere on top of mast)
                dome_top_z = pos_z + mast_height
                dome_segments = 16
                dome_theta_segments = 8  # Half sphere only
                
                dome_x = []
                dome_y = []
                dome_z = []
                
                for i in range(dome_theta_segments + 1):
                    theta = math.pi * i / dome_theta_segments  # 0 to pi (half sphere)
                    for j in range(dome_segments + 1):
                        phi = 2 * math.pi * j / dome_segments
                        x_dome = pos_x_km + (dome_radius / 1000.0) * math.sin(theta) * math.cos(phi)
                        y_dome = pos_y_km + (dome_radius / 1000.0) * math.sin(theta) * math.sin(phi)
                        z_dome = dome_top_z + dome_radius * math.cos(theta)
                        dome_x.append(x_dome)
                        dome_y.append(y_dome)
                        dome_z.append(z_dome)
                
                # Create dome mesh
                fig.add_trace(go.Mesh3d(
                    x=dome_x,
                    y=dome_y,
                    z=dome_z,
                    color=color,
                    opacity=0.7,
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # 4. Coverage hemisphere (semi-transparent)
                coverage_segments = 20
                coverage_theta_segments = 10  # Half sphere only
                
                coverage_x = []
                coverage_y = []
                coverage_z = []
                
                for i in range(coverage_theta_segments + 1):
                    theta = math.pi * i / coverage_theta_segments  # 0 to pi (half sphere)
                    for j in range(coverage_segments + 1):
                        phi = 2 * math.pi * j / coverage_segments
                        x_cov = pos_x_km + coverage_radius_km * math.sin(theta) * math.cos(phi)
                        y_cov = pos_y_km + coverage_radius_km * math.sin(theta) * math.sin(phi)
                        z_cov = pos_z + coverage_radius_km * 1000.0 * math.cos(theta)  # Convert to meters
                        coverage_x.append(x_cov)
                        coverage_y.append(y_cov)
                        coverage_z.append(z_cov)
                
                # Create coverage hemisphere mesh
                fig.add_trace(go.Mesh3d(
                    x=coverage_x,
                    y=coverage_y,
                    z=coverage_z,
                    color=coverage_color,
                    opacity=0.15,
                    showlegend=False,
                    hoverinfo='skip'
                ))
        except Exception:
            pass  # Fail silently


def compute_threat_density_points(tracks: List[Dict[str, Any]]) -> List[Tuple[float, float, float]]:
    """
    Derive (x_km, y_km, z_m) points from existing track positions only.
    VISUAL ONLY — does not modify tracks. Coordinate system matches battlespace (x,y km, z m).
    """
    out = []
    if not isinstance(tracks, list):
        return out
    for t in tracks:
        if not isinstance(t, dict):
            continue
        pos = t.get("position") if isinstance(t.get("position"), dict) else {}
        x = pos.get("x") if "x" in pos else None
        y = pos.get("y") if "y" in pos else None
        if x is None or y is None:
            continue
        try:
            x_km = float(x) / 1000.0
            y_km = float(y) / 1000.0
            z_m = float(pos.get("z", 0))
        except (TypeError, ValueError):
            continue
        out.append((x_km, y_km, z_m))
    return out


def update_track_positions(
    fig: go.Figure,
    tracks: List[Dict[str, Any]],
    sim_time: float,
    replay_time: Optional[float] = None,
) -> None:
    """
    Update only the x/y/z of existing track marker traces for the given sim_time.
    NEVER add/remove traces, touch layout, or clear data.
    On failure for a trace, silently keep last valid state.
    """
    if fig is None or not hasattr(fig, "data") or not isinstance(tracks, list):
        return
    sim_time = float(sim_time)
    track_by_id = {str(t.get("track_id", "")): t for t in tracks if isinstance(t, dict) and t.get("track_id") is not None}
    prediction_seconds = 90.0
    num_points = 40
    max_t = prediction_seconds
    for trace in fig.data:
        try:
            name = getattr(trace, "name", None)
            meta = getattr(trace, 'meta', None)
            # Identify track traces by meta or by naming convention
            is_track = False
            if meta and meta.get('type') == 'track':
                is_track = True
            elif name and str(name).startswith("Track_"):
                is_track = True
            if not is_track:
                continue

            # Resolve track id
            track_id = None
            if meta and meta.get('track_id'):
                track_id = str(meta.get('track_id'))
            elif name and str(name).startswith("Track_"):
                track_id = str(name)[6:]
            if not track_id:
                continue

            track = track_by_id.get(track_id)
            if not track:
                continue

            traj_pts = Battlespace3D._get_or_create_trajectory(track, prediction_seconds=prediction_seconds, num_points=num_points)
            if not traj_pts or len(traj_pts) < 2:
                pos = track.get("position") or {}
                x = float(pos.get("x", 0.0)) / 1000.0
                y = float(pos.get("y", 0.0)) / 1000.0
                z = float(pos.get("z", 1.0))
                trace.x = [x]
                trace.y = [y]
                trace.z = [z]
                continue

            npts = len(traj_pts)
            dt = float(max_t) / max(1, npts - 1)
            t = max(0.0, min(sim_time, max_t))
            idx_low = int(min(npts - 2, max(0, int(math.floor(t / dt)))))
            t0 = idx_low * dt
            t1 = (idx_low + 1) * dt
            alpha = (t - t0) / (t1 - t0) if (t1 - t0) > 0.0 else 0.0
            x0_km, y0_km, z0_m = traj_pts[idx_low]
            x1_km, y1_km, z1_m = traj_pts[min(idx_low + 1, npts - 1)]
            x_km = x0_km + alpha * (x1_km - x0_km)
            y_km = y0_km + alpha * (y1_km - y0_km)
            display_z = z0_m + alpha * (z1_m - z0_m)
            trace.x = [x_km]
            trace.y = [y_km]
            trace.z = [display_z]
        except Exception:
            continue