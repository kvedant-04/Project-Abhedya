import math
from datetime import datetime
import plotly.graph_objects as go
from typing import Tuple, Optional


def classify_air_object(track: dict, scenario: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Classify an air object according to authoritative rules.

    Priority (first-match wins):
      1) Scenario override: if scenario indicates Drone Swarm / Saturation Test / UAV Intrusion
         -> object_type = "UAV / Drone" and classification override = track.classification or 'HOSTILE'
      2) Sensor / track metadata override: platform_type, emitter_type, declared_type
         -> object_type = that value
      3) Kinematics fallback (only if no overrides):
         - speed >= 400 km/h and altitude >= 6000 m -> Fixed-Wing Aircraft
         - 150 <= speed < 400 and 2000 <= altitude < 6000 -> Helicopter
         - speed < 150 and altitude < 3000 -> UAV / Drone
         - else -> Unknown Air Object

    This function is pure and does not mutate `track`.
    Returns (object_type, classification_override_or_None)
    """
    # Safe numeric defaults (do not mutate track)
    try:
        alt = float(track.get('altitude_m', track.get('altitude', 10000.0)))
    except Exception:
        alt = 10000.0
    try:
        spd = float(track.get('speed_kmh', track.get('speed', 720.0)))
    except Exception:
        spd = 720.0

    scen = (scenario or '').strip().lower()
    # Scenario override: highest priority
    if scen:
        if ('drone' in scen and 'swarm' in scen) or ('saturation' in scen) or ('uav intrusion' in scen):
            cls_override = track.get('classification') or 'HOSTILE'
            return "UAV / Drone", cls_override

    # Sensor / track metadata override
    for key in ('platform_type', 'emitter_type', 'declared_type'):
        val = track.get(key)
        if val:
            return str(val), track.get('classification')

    # Kinematics fallback
    if spd >= 400.0 and alt >= 6000.0:
        return "Fixed-Wing Aircraft", track.get('classification')
    if 150.0 <= spd < 400.0 and 2000.0 <= alt < 6000.0:
        return "Helicopter", track.get('classification')
    if spd < 150.0 and alt < 3000.0:
        return "UAV / Drone", track.get('classification')

    return "Unknown Air Object", track.get('classification')


def render_airspace_radar_ppi(tracks, training_mode: bool, sweep_angle_deg: float = None, scenario: str = None):
    """Advisory-only 2D Radar / PPI visualization.
    No state mutation. No Streamlit here. Returns a Plotly Figure.

    Important constraints upheld:
    - Consumes provided `tracks` list (single source of truth shared with 3D)
    - Does NOT regenerate positions or create synthetic tracks
    - Uses `classify_air_object` for object-type classification
    - Pure rendering function (no session_state or I/O)
    """

    # Calculate max range from provided tracks (in km)
    max_range = 0.0
    for t in tracks or []:
        try:
            if not isinstance(t, dict):
                continue
            if 'x_km' in t and 'y_km' in t:
                tx = float(t.get('x_km'))
                ty = float(t.get('y_km'))
            elif 'x' in t and 'y' in t:
                tx = float(t.get('x'))
                ty = float(t.get('y'))
                # support meters in legacy tracks (very large values)
                if abs(tx) > 2000 or abs(ty) > 2000:
                    tx /= 1000.0
                    ty /= 1000.0
            else:
                pos = t.get('position') or {}
                if pos and pos.get('x') is not None and pos.get('y') is not None:
                    tx = float(pos.get('x'))
                    ty = float(pos.get('y'))
                    if abs(tx) > 2000 or abs(ty) > 2000:
                        tx /= 1000.0
                        ty /= 1000.0
                else:
                    continue
            r = math.hypot(tx, ty)
            if r > max_range:
                max_range = r
        except Exception:
            # sanity: skip malformed track entries
            continue

    # Auto-zoom per requirement: radar max range = max(max_range * 1.25, 30km)
    R_MAX = max(max_range * 1.25 if max_range > 0 else 0.0, 30.0)
    # Ensure minimum visible ring of 10km
    min_ring = 10.0

    fig = go.Figure()

    # Range rings (military-style, thin, low-contrast)
    ring_radii = [10, 25, 50, 75, 100]
    theta_steps = 180
    for r in ring_radii:
        if r > R_MAX:
            continue
        thetas = [i * (360.0 / theta_steps) for i in range(theta_steps + 1)]
        xs = [r * math.cos(math.radians(a)) for a in thetas]
        ys = [r * math.sin(math.radians(a)) for a in thetas]
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode='lines',
                line=dict(color='rgba(200,230,200,0.18)', width=1),
                hoverinfo='skip',
                showlegend=False,
            )
        )
        # ring label at top (slightly inward)
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[r - (R_MAX * 0.02)],
                mode='text',
                text=[f"{r} km"],
                textfont=dict(color='rgba(220,255,220,0.9)', size=11),
                hoverinfo='skip',
                showlegend=False,
            )
        )

    # Crosshair axes (subtle)
    fig.add_trace(go.Scatter(x=[-R_MAX, R_MAX], y=[0, 0], mode='lines', line=dict(color='rgba(200,230,200,0.18)', width=1), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=[0, 0], y=[-R_MAX, R_MAX], mode='lines', line=dict(color='rgba(200,230,200,0.18)', width=1), hoverinfo='skip', showlegend=False))

    # Radar sweep line (single rotating sweep)
    if sweep_angle_deg is None:
        try:
            now = datetime.utcnow().timestamp()
            rotation_period = 7.0
            angle_deg = ((now % rotation_period) / rotation_period) * 360.0
        except Exception:
            angle_deg = 0.0
    else:
        angle_deg = float(sweep_angle_deg) % 360.0
    angle_rad = math.radians(angle_deg)
    sweep_x = [0.0, R_MAX * math.cos(angle_rad)]
    sweep_y = [0.0, R_MAX * math.sin(angle_rad)]
    fig.add_trace(
        go.Scatter(
            x=sweep_x,
            y=sweep_y,
            mode='lines',
            line=dict(color='rgba(180,255,180,0.30)', width=2),
            hoverinfo='skip',
            showlegend=False,
            opacity=0.95,
        )
    )

    # Prepare traces arrays (no coordinate mutation)
    hit_x, hit_y, hover_texts = [], [], []
    vis_x, vis_y, vis_text, vis_color, vis_size = [], [], [], [], []

    for t in tracks or []:
        if not isinstance(t, dict):
            continue

        # Extract 2D position (km) from the same source used by 3D battlespace
        x = None
        y = None
        try:
            if 'x_km' in t and 'y_km' in t:
                x = float(t.get('x_km'))
                y = float(t.get('y_km'))
            elif 'x' in t and 'y' in t:
                x = float(t.get('x'))
                y = float(t.get('y'))
                if abs(x) > 2000 or abs(y) > 2000:
                    x /= 1000.0
                    y /= 1000.0
            else:
                pos = t.get('position') or {}
                if pos and pos.get('x') is not None and pos.get('y') is not None:
                    x = float(pos.get('x'))
                    y = float(pos.get('y'))
                    if abs(x) > 2000 or abs(y) > 2000:
                        x /= 1000.0
                        y /= 1000.0
        except Exception:
            continue

        if x is None or y is None:
            continue

        # Polar metrics
        rng = math.hypot(x, y)
        bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

        # Identity and sensor fields
        track_id = t.get('track_id') or t.get('id') or 'UNKNOWN'
        sensor = (t.get('sensor') or t.get('source') or 'Radar')

        # Safe numeric fallbacks
        try:
            altitude = float(t.get('altitude_m', t.get('altitude', 10000.0)))
        except Exception:
            altitude = 10000.0
        try:
            speed = float(t.get('speed_kmh', t.get('speed', 720.0)))
        except Exception:
            speed = 720.0
        try:
            heading = float(t.get('heading_deg', t.get('heading', 0.0)))
        except Exception:
            heading = 0.0

        # Classification and object type via shared helper (obeying scenario overrides)
        object_type, classification_override = classify_air_object(t, scenario)
        classification_display = (classification_override or t.get('classification') or 'Unknown')
        classification_display = str(classification_display).upper()

        # Color by classification (friendly/hostile/unknown)
        cls_upper = classification_display
        if 'FRIEND' in cls_upper:
            color = '#2ecc71'
        elif 'HOST' in cls_upper or 'ENEMY' in cls_upper or 'FOE' in cls_upper:
            color = '#e74c3c'
        else:
            color = '#f1c40f'

        # Visual decluttering policy: for dense drone-swarm scenarios, reduce marker size
        is_drone_swarm = isinstance(scenario, str) and ('drone' in scenario.strip().lower() and 'swarm' in scenario.strip().lower())
        marker_size = 8 if is_drone_swarm else 14

        # Build hover text per strict spec (no N/A/null; safe defaults)
        scenario_source = scenario or 'Operational'
        hover_lines = [
            f"Track ID: {track_id}",
            f"Object Type: {object_type}",
            f"Classification: {classification_display}",
            f"Scenario: {scenario_source}",
            f"Range: {rng:.1f} km",
            f"Bearing: {bearing:.1f}°",
            f"Speed: {speed:.1f} km/h",
            f"Altitude: {altitude:.0f} m",
            f"Heading: {heading:.1f}°",
            f"Sensor: {sensor}",
            f"Tracking Status: {t.get('status') or 'Monitoring'}",
        ]

        # On-chart label: keep minimal to avoid clutter (Track ID)
        vis_label = str(track_id)

        hit_x.append(x)
        hit_y.append(y)
        hover_texts.append('<br>'.join(hover_lines))

        vis_x.append(x)
        vis_y.append(y)
        vis_text.append(vis_label)
        vis_color.append(color)
        vis_size.append(marker_size)

    # Invisible hit buffer trace (larger markers for easier hover) - below visible markers
    if hit_x:
        fig.add_trace(
            go.Scatter(
                x=hit_x,
                y=hit_y,
                mode='markers',
                marker=dict(size=28, color='rgba(0,0,0,0)', opacity=0),
                hovertemplate='%{customdata}',
                customdata=hover_texts,
                showlegend=False,
            )
        )

    # Glow layer
    if vis_x:
        glow_sizes = [max(6, int(s * 1.4)) for s in vis_size]
        fig.add_trace(
            go.Scatter(
                x=vis_x,
                y=vis_y,
                mode='markers',
                marker=dict(size=glow_sizes, color=vis_color, opacity=0.18, line=dict(width=0)),
                hoverinfo='skip',
                showlegend=False,
            )
        )

    # Visible blips + minimal labels
    if vis_x:
        fig.add_trace(
            go.Scatter(
                x=vis_x,
                y=vis_y,
                mode='markers+text',
                marker=dict(size=vis_size, symbol='circle', color=vis_color, line=dict(width=1, color='rgba(0,0,0,0.3)'), opacity=1.0),
                text=vis_text,
                textposition='top right',
                textfont=dict(color='rgba(230,255,230,0.95)', size=11),
                hoverinfo='skip',
                showlegend=False,
            )
        )

    # Final layout — professional radar look
    fig.update_layout(
        template=None,
        showlegend=False,
        margin=dict(l=6, r=6, t=6, b=6),
        plot_bgcolor='#24332c',
        paper_bgcolor='#24332c',
        font=dict(color='rgba(230,255,230,0.95)'),
        xaxis=dict(range=[-R_MAX, R_MAX], visible=False, zeroline=False, showgrid=False),
        yaxis=dict(range=[-R_MAX, R_MAX], visible=False, zeroline=False, showgrid=False),
    )

    fig.update_yaxes(scaleanchor='x', scaleratio=1)

    return fig
