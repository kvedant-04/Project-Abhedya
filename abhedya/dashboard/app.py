"""
Abhedya Air Defense System - Command and Control Dashboard

Streamlit application for the Command and Control Dashboard.
Defence-console style professional interface.

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from abhedya.dashboard.radar_ppi import render_airspace_radar_ppi

# -------------------------------------------------------------------
# Streamlit Page Config (MUST be first Streamlit call)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Abhedya Air Defense System - Command and Control Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Safe Imports (Fail-Safe Architecture)
# -------------------------------------------------------------------
try:
    from abhedya.dashboard.state_manager import DashboardStateManager
    from abhedya.dashboard.layout import DashboardLayout
    from abhedya.dashboard.visual_components import (
        AirspaceVisualization,
        ConfidenceGauge,
        TrendPlot,
        SeverityThemeController,
        SensorContributionPanel
    )
    from abhedya.dashboard.battlespace_3d import Battlespace3D
    from abhedya.dashboard.engagement_visualization import EngagementVisualization
    from abhedya.dashboard.trajectory_tracking import TrajectoryTracker
    from abhedya.dashboard.atmospheric_modeling import AtmosphericModel
    from abhedya.dashboard.interception_window import (
        InterceptionWindowVisualization,
        InterceptionFeasibilityAnalyzer,
        InterceptionFeasibilityPanel
    )
    from abhedya.dashboard.effects_controller import EffectsController
except Exception as e:
    st.error(f"Dashboard initialization error: {e}")
    DashboardStateManager = None
    DashboardLayout = None
    AirspaceVisualization = None
    ConfidenceGauge = None
    TrendPlot = None
    SeverityThemeController = None
    SensorContributionPanel = None
    EffectsController = None
    Battlespace3D = None
    EngagementVisualization = None
    TrajectoryTracker = None
    AtmosphericModel = None
    InterceptionWindowVisualization = None
    InterceptionFeasibilityAnalyzer = None
    InterceptionFeasibilityPanel = None

# Ensure DashboardLayout is available; if import failed, attempt direct module import.
if DashboardLayout is None:
    try:
        import importlib
        layout_mod = importlib.import_module('abhedya.dashboard.layout')
        if hasattr(layout_mod, 'DashboardLayout'):
            DashboardLayout = getattr(layout_mod, 'DashboardLayout')
    except Exception:
        DashboardLayout = None

# If DashboardLayout still unavailable, warn and stop execution early to avoid repeated crashes.
if DashboardLayout is None:
    try:
        st.warning("Dashboard layout failed to initialize — running in degraded mode. Some UI panels disabled.")
        # Stop further execution to avoid any render_* calls on None. Streamlit will display the warning.
        st.stop()
    except Exception:
        # If Streamlit unavailable, raise the original import error silently.
        pass

# Safe caller for DashboardLayout methods to avoid AttributeErrors when layout is unavailable
def _safe_dashboard_call(method_name: str, *args, **kwargs):
    try:
        if DashboardLayout and hasattr(DashboardLayout, method_name):
            return getattr(DashboardLayout, method_name)(*args, **kwargs)
    except Exception:
        try:
            st.warning(f"Dashboard method {method_name} unavailable")
        except Exception:
            pass
    return None


def apply_tactical_camera(fig):
    """
    Camera-only reset. Does NOT touch data, traces, or scenario state.
    Safe to call even if the figure looks empty.
    """
    try:
        fig.update_layout(
            scene=dict(
                camera=dict(
                    eye=dict(x=1.25, y=1.25, z=0.9),
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0)
                )
            )
        )
    except Exception:
        pass

def ensure_scene_alive(fig: "go.Figure"):
    """Rebinds Plotly 3D scene after trace mutation.

    This is safe and does not touch data. It ensures internal Plotly
    scene references are present so the 3D canvas does not go blank.
    """
    try:
        if not hasattr(fig.layout, "scene") or fig.layout.scene is None:
            fig.update_layout(scene={})

        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title="East (km)",
                    showgrid=True,
                    zeroline=False,
                    backgroundcolor="rgba(0,0,0,0)"
                ),
                yaxis=dict(
                    title="North (km)",
                    showgrid=True,
                    zeroline=False,
                    backgroundcolor="rgba(0,0,0,0)"
                ),
                zaxis=dict(
                    title="Altitude (meters)",
                    showgrid=True,
                    zeroline=False,
                    backgroundcolor="rgba(0,0,0,0)"
                ),
                aspectmode="cube",
            )
        )
    except Exception:
        # Best-effort, do not raise from visualization helper
        pass


def is_figure_healthy(fig):
    """Lightweight health check for the battlespace figure.

    Returns False when figure is missing layout.scene or has no data.
    """
    try:
        if fig is None:
            return False
        if not getattr(fig, 'data', None):
            return False
        if not hasattr(fig.layout, 'scene'):
            return False
        return True
    except Exception:
        return False

def recover_plotly_scene(fig):
    """
    One-shot, idempotent scene recovery.
    Must work even if scene is visually blank.
    Does NOT recreate the figure or touch fig.data.
    """
    try:
        fig.update_layout(
            scene=dict(
                camera=dict(
                    eye=dict(x=1.25, y=1.25, z=1.25),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
                xaxis=dict(visible=True),
                yaxis=dict(visible=True),
                zaxis=dict(visible=True),
            ),
            margin=dict(l=0, r=0, t=40, b=0),
        )
    except Exception:
        # Best-effort; do not raise from visualization helper
        pass

# (moved earlier to ensure it's the first Streamlit call)

# -------------------------------------------------------------------
# Session State Initialization (STRICT)
# -------------------------------------------------------------------
if "training_mode" not in st.session_state:
    st.session_state.training_mode = False

if "shadow_mode" not in st.session_state:
    st.session_state.shadow_mode = False

if "audio_enabled" not in st.session_state:
    st.session_state.audio_enabled = False

if "acknowledged_items" not in st.session_state:
    st.session_state.acknowledged_items = set()

# Initialize last update time for timestamp tracking
if "last_update_time" not in st.session_state:
    from datetime import datetime
    st.session_state.last_update_time = datetime.now()

# -------------------------------------------------------------------
# Additional strict session state defaults (MUST be set before widgets)
# -------------------------------------------------------------------
if "show_atmospheric_overlay" not in st.session_state:
    st.session_state.show_atmospheric_overlay = False

if "atmospheric_preset" not in st.session_state:
    st.session_state.atmospheric_preset = "None"

if "atmospheric_conditions" not in st.session_state:
    st.session_state.atmospheric_conditions = None

if "ew_environment_state" not in st.session_state:
    st.session_state.ew_environment_state = "NONE"

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 5.0

# uirevision counter used to allow safe scene rebuilds on scenario change
if "uirevision_counter" not in st.session_state:
    st.session_state["uirevision_counter"] = 0

if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = "civil_air_traffic"

if "simulation_initialized" not in st.session_state:
    st.session_state.simulation_initialized = False

if "simulation_tracks" not in st.session_state:
    st.session_state.simulation_tracks = []

if "training_mode_toggle_prev" not in st.session_state:
    st.session_state.training_mode_toggle_prev = st.session_state.get("training_mode", False)

# Let state manager extend state if available
if DashboardStateManager:
    try:
        DashboardStateManager.initialize_session_state()
    except Exception:
        pass

# -------------------------------------------------------------------
# CSS (with Training Mode visual dynamics)
# -------------------------------------------------------------------
training_mode_active = st.session_state.get("training_mode", False)

css_dynamics = """
    /* Subtle professional UI transitions */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @keyframes smoothValueUpdate {
        0% { transform: scale(1); }
        50% { transform: scale(1.01); }
        100% { transform: scale(1); }
    }
    .stExpander {
        transition: all 0.15s ease-out;
    }
    .stExpander[data-state="open"] {
        animation: slideInDown 0.15s ease-out;
    }
    /* Smooth panel transitions (compact) */
    .element-container {
        animation: fadeIn 0.18s ease-out;
        padding: 6px !important;
        margin-bottom: 6px !important;
    }
    /* Smooth metric value transitions */
    [data-testid="stMetricValue"] {
        transition: all 0.4s ease-in-out;
    }
    /* Status card highlight on state change */
    .status-card {
        transition: background-color 0.3s ease-out, border-color 0.3s ease-out;
    }
    """

st.markdown(f"""
<style>
    .main-header {{
    background: linear-gradient(90deg, #1e3a5f 0%, #2c5282 100%);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 10px;
    font-size: 18px;
}}
{css_dynamics}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Persistent Banner (Guarded)
# -------------------------------------------------------------------
if DashboardLayout is not None and hasattr(DashboardLayout, 'render_persistent_banner'):
    DashboardLayout.render_persistent_banner()
else:
    st.warning("Persistent banner unavailable (layout not initialized)")

# -------------------------------------------------------------------
# Navigation Controls (ALWAYS VISIBLE)
# -------------------------------------------------------------------
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 8])
with nav_col1:
    if st.button("🏠 Home", key="nav_home", help="Return to Airspace Overview"):
        st.session_state.current_tab = "Airspace Overview"
        st.rerun()
with nav_col2:
    if st.button("← Back", key="nav_back", help="Return to previous view"):
        # Simple back navigation - could be enhanced with history stack
        st.rerun()

# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>Abhedya Air Defense System</h1>
    <p>Command and Control Dashboard</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Sidebar Controls (ALL KEYS UNIQUE - ALWAYS VISIBLE)
# -------------------------------------------------------------------
with st.sidebar:
    st.header("Dashboard Controls")
    # Training & Simulation Mode Toggle (ALWAYS VISIBLE)
    st.checkbox(
        "Enable Training & Simulation Mode",
        value=st.session_state.get("training_mode", False),
        key="training_mode",
        help="Enables synthetic data for training and simulation. All data clearly labeled as SIMULATION / TRAINING DATA."
    )

    # Read training mode after rendering its widget
    training_mode = st.session_state.get("training_mode", False)

    # Atmospheric Controls (Training Mode only for editable presets)
    with st.container():
        st.subheader("Atmospheric Conditions")
        try:
            from abhedya.dashboard.atmospheric_modeling import AtmosphericModel, AtmosphericPreset

            # Atmospheric preset selector (widget-bound key: atmospheric_preset)
            preset_options = [p.value for p in AtmosphericPreset]
            selected_preset_str = st.selectbox(
                "Atmospheric Preset",
                options=["None"] + preset_options,
                index=0,
                key="atmospheric_preset",
                help="Select atmospheric preset for training scenarios"
            )

            if selected_preset_str != "None":
                selected_preset = AtmosphericPreset(selected_preset_str)
                atmospheric_conditions = AtmosphericModel.get_conditions(preset=selected_preset)
            else:
                atmospheric_conditions = AtmosphericModel.get_conditions()

            # Store conditions (non-widget key) — safe to update
            st.session_state["atmospheric_conditions"] = atmospheric_conditions

            # Atmospheric overlay toggle — widget writes directly to session state
            st.checkbox(
                "Show Atmospheric Overlay",
                value=st.session_state.get("show_atmospheric_overlay", False),
                key="show_atmospheric_overlay",
                help="Display atmospheric layers in 3D battlespace"
            )

            # Display current conditions summary and label simulation data when active
            if atmospheric_conditions:
                summary = AtmosphericModel.get_environmental_state_summary(atmospheric_conditions)
                st.caption(f"🌦️ {summary}")
                if training_mode:
                    st.caption("**SIMULATION / TRAINING DATA**")
        except Exception:
            atmospheric_conditions = None
            st.session_state["atmospheric_conditions"] = None
    
    if st.session_state.get("training_mode", False):
        st.info("⚠️ Training & Simulation Mode Active — Synthetic data enabled")
        
        # Scenario Selector (Training Mode only)
        try:
            from abhedya.dashboard.scenario_presets import ScenarioPresets
            
            scenario_list = ScenarioPresets.get_scenario_list()
            scenario_options = {item["name"]: item["key"] for item in scenario_list}
            
            # Scenario selector dropdown (widget writes to key 'scenario_selector')
            selected_scenario_name = st.selectbox(
                "Scenario",
                options=list(scenario_options.keys()),
                index=list(scenario_options.values()).index(st.session_state.selected_scenario) if st.session_state.selected_scenario in scenario_options.values() else 0,
                key="scenario_selector",
                help="Select a deterministic scenario preset. All scenarios are completely deterministic - same geometry on every reload."
            )

            # Check if scenario changed and update simulation state accordingly
            previous_scenario = st.session_state.get("selected_scenario", "civil_air_traffic")
            new_scenario = scenario_options[selected_scenario_name]
            if previous_scenario != new_scenario:
                st.session_state.selected_scenario = new_scenario
            
            # Reset simulation if scenario changed and trigger immediate reinitialization
            if previous_scenario != new_scenario:
                # Reset simulation state to force reinitialization
                if 'simulation_initialized' in st.session_state:
                    st.session_state.simulation_initialized = False
                if 'simulation_start_time' in st.session_state:
                    del st.session_state.simulation_start_time
                if 'simulation_tracks' in st.session_state:
                    st.session_state.simulation_tracks = []

                # Immediately initialize simulation tracks for the new scenario
                try:
                    if DashboardStateManager:
                        DashboardStateManager._initialize_simulation_tracks()
                except Exception:
                    # Fail silently; subsequent calls will attempt initialization
                    pass
            
            # Show scenario description
            scenario_data = ScenarioPresets.get_scenario(st.session_state.selected_scenario)
            st.caption(f"📋 {scenario_data['description']}")
            
        except Exception as e:
            st.warning(f"Scenario selector unavailable: {e}")
            if "selected_scenario" not in st.session_state:
                st.session_state.selected_scenario = "civil_air_traffic"

    # Audio Toggle (ALWAYS VISIBLE)
    st.checkbox(
        "Enable Audio Indicators",
        value=st.session_state.get("audio_enabled", False),
        key="audio_enabled",
        help="Audio indicators are advisory and for simulation/training visualization only."
    )

    st.markdown("---")
    st.subheader("View Options")
    
    # EW Environment State Selector (Training Mode only)
    if training_mode:
        st.subheader("Electronic Warfare Environment (Training Mode)")
        ew_state_options = ["NONE", "LOW", "MEDIUM", "HIGH"]
        current_ew_state = st.session_state.get('ew_environment_state', 'NONE')

        selected_ew_state = st.selectbox(
            "EW Environment State",
            ew_state_options,
            index=ew_state_options.index(current_ew_state) if current_ew_state in ew_state_options else 0,
            key="ew_environment_state_selector",
            help="Select EW environment state for training scenarios. ADVISORY ONLY — affects confidence visualization only."
        )

        # Mirror selector value into canonical session key (widget uses selector key)
        st.session_state["ew_environment_state"] = selected_ew_state

        if selected_ew_state != 'NONE':
            st.caption(f"⚠️ EW Environment: {selected_ew_state} — Sensor trust visualization adjusted (SIMULATION / TRAINING DATA)")
    
    st.subheader("View Options")

    show_confidence_rings = st.checkbox(
        "Show Confidence Rings",
        value=st.session_state.get('show_confidence_rings', True),
        key="show_confidence_rings",
        help="Toggle display of confidence rings around tracks (advisory only)"
    )


    show_protected_zones = st.checkbox(
        "Show Protected Zones",
        value=st.session_state.get('show_protected_zones', True),
        key="show_protected_zones",
        help="Toggle display of protected airspace zones (advisory only)"
    )


    auto_refresh = st.checkbox(
        "Auto-refresh",
        value=st.session_state.get("auto_refresh", True),
        key="auto_refresh",
        help="Automatically refresh dashboard for animations (Training Mode only)"
    )

    if auto_refresh:
        # Faster refresh for smooth animations in Training Mode
        default_interval = 0.5 if st.session_state.get("training_mode", False) else 5.0
        refresh_interval = st.slider(
            "Refresh Interval (seconds)",
            0.1, 10.0, default_interval,
            key="refresh_interval_slider",
            help="Lower values = smoother animations (Training Mode)"
        )
        
        # Reset simulation when training mode is toggled
        if 'training_mode_toggle_prev' not in st.session_state:
            st.session_state.training_mode_toggle_prev = st.session_state.get("training_mode", False)
        
        if st.session_state.get("training_mode", False) != st.session_state.training_mode_toggle_prev:
            # Training mode changed
            new_val = st.session_state.get("training_mode", False)
            if new_val:
                # Initialize simulation immediately to avoid empty tabs
                try:
                    if DashboardStateManager:
                        DashboardStateManager._initialize_simulation_tracks()
                except Exception:
                    # Fail silently - dashboard will show Monitoring Only if necessary
                    pass
            else:
                # Disable simulation state
                st.session_state.simulation_initialized = False
                st.session_state.simulation_tracks = []
            st.session_state.training_mode_toggle_prev = new_val

    # Auto-refresh implementation (browser-side reload). Uses JS to reload
    # after the selected interval. This is a minimal, non-invasive approach
    # to trigger updates without server-side loops.
    try:
        if st.session_state.get('auto_refresh', False):
            interval = float(st.session_state.get('refresh_interval', 5.0))
            # Bound interval to reasonable range
            interval = max(0.1, min(60.0, interval))
            js = f"<script>setTimeout(function(){{window.location.reload();}}, {int(interval*1000)});</script>"
            st.markdown(js, unsafe_allow_html=True)
    except Exception:
        pass

# -------------------------------------------------------------------
# Mode Awareness Banner (Always Visible)
# -------------------------------------------------------------------
if DashboardLayout is not None and hasattr(DashboardLayout, 'render_mode_awareness_banner'):
    DashboardLayout.render_mode_awareness_banner()
else:
    st.warning("Mode awareness banner unavailable (layout not initialized)")

# -------------------------------------------------------------------
# Tabs
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Airspace Overview",
    "Threat & Advisory Status",
    "Early Warning System",
    "Electronic Warfare Analysis",
    "Cybersecurity & System Integrity",
    "SAM C2 Visualization"
])

# -------------------------------------------------------------------
# TAB 1 — Airspace Overview
# -------------------------------------------------------------------
with tab1:
    st.header("Airspace Overview")
    # Global data freshness indicator (UI-only)
    if DashboardLayout:
        # Mark this tab as active; if the user just switched to this tab,
        # reset its per-tab refresh timestamp so the indicator reads "just now".
        tab_name = "Airspace Overview"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        if DashboardLayout is not None and hasattr(DashboardLayout, 'render_data_freshness'):
            DashboardLayout.render_data_freshness(st.session_state.get("training_mode", False))
        else:
            st.warning("Data freshness unavailable (layout not initialized)")

    data = DashboardStateManager.get_tracking_data() if DashboardStateManager else None
    training_mode = st.session_state.get("training_mode", False)
    is_simulation = data and isinstance(data, list) and len(data) > 0 and data[0].get("is_simulation", False) if data else False
    
    # Operational Context Panel
    if data and isinstance(data, list) and len(data) > 0:
        num_tracks = len(data)
        summary = f"Monitoring {num_tracks} active track{'s' if num_tracks != 1 else ''} in airspace. Traffic density: {'moderate' if num_tracks <= 3 else 'elevated'}."
    else:
        summary = "No active tracks detected. Airspace monitoring in progress."
    
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_operational_context'):
        DashboardLayout.render_operational_context(
            "Airspace Overview",
            summary,
            training_mode,
            is_simulation
        )
    else:
        st.warning("Operational context unavailable (layout not initialized)")
    
    # Intelligence Narrative
    if data and isinstance(data, list) and len(data) > 0:
        num_tracks = len(data)
        zone_proximity = "within protected zones" if any(
            abs(float(t.get('position', {}).get('x', 0.0))) < 25000 or 
            abs(float(t.get('position', {}).get('y', 0.0))) < 25000 
            for t in data if isinstance(t, dict)
        ) else "outside protected zones"
        
        narrative = f"Current airspace shows {num_tracks} tracked object{'s' if num_tracks != 1 else ''} with stable trajectories. Objects are {zone_proximity}. Trajectory patterns indicate {'consistent motion' if num_tracks > 0 else 'no active traffic'}. Trend stability: {'stable' if num_tracks > 0 else 'monitoring'}."
        
        # Do not render the large confidence metric on the Airspace Overview
        # to avoid duplicating confidence information on the radar visualization.
        if DashboardLayout is not None and hasattr(DashboardLayout, 'render_intelligence_narrative'):
            DashboardLayout.render_intelligence_narrative(narrative, None)
        else:
            st.warning("Intelligence narrative unavailable (layout not initialized)")
    
    if not data:
        if training_mode:
            st.info("ℹ️ Training data generator initializing — Monitoring Only")
        else:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_insufficient_data_message'):
                DashboardLayout.render_insufficient_data_message("Tracking data unavailable")
            else:
                st.warning("Tracking data unavailable (layout not initialized)")
    else:
        # Create visualization with time-based interpolation
        from datetime import datetime
        current_time = datetime.now()
        
        # Get atmospheric conditions from session state
        atmospheric_conditions = st.session_state.get("atmospheric_conditions")
        
        # Ensure simulation tracks are initialized and synchronized with the
        # data variable for Training Mode to avoid empty visualizations.
        if training_mode:
            try:
                if DashboardStateManager and not st.session_state.get('simulation_initialized', False):
                    DashboardStateManager._initialize_simulation_tracks()
            except Exception:
                # Initialization may fail transiently; proceed to visualization
                pass

            # If session-level simulation_tracks are empty but the unified
            # data provider returned tracks, mirror them into session state so
            # the visualization has a consistent source of truth.
            try:
                if (not st.session_state.get('simulation_tracks')) and data:
                    st.session_state.simulation_tracks = data
            except Exception:
                pass

            # maintain radar sweep angle in session state and increment per rerun
            if 'radar_sweep_angle_deg' not in st.session_state:
                st.session_state.radar_sweep_angle_deg = 0.0
            # small incremental step per rerun for smooth rotation
            st.session_state.radar_sweep_angle_deg = (st.session_state.radar_sweep_angle_deg + 5.0) % 360.0

        # Render single Airspace Radar PPI and remove old 2D placeholder
        st.subheader("Airspace Overview — Radar PPI (Advisory)")
        ppi_fig = render_airspace_radar_ppi(
            data,
            training_mode,
            sweep_angle_deg=st.session_state.get('radar_sweep_angle_deg', 0.0),
            scenario=st.session_state.get('selected_scenario', None)
        )
        st.plotly_chart(ppi_fig, use_container_width=True, height=650, key="airspace_radar_ppi_main")
        
        # Update last_update_time only when the underlying track data changes.
        # This prevents frequent auto-refresh/re-runs from resetting the
        # client-side freshness timer. We create a lightweight fingerprint
        # based on track IDs and timestamps.
        try:
            from datetime import datetime
            # Use a stable fingerprint based on the set of track IDs only.
            # This prevents frequent small positional/timestamp updates from
            # resetting the freshness timer during auto-refresh animation.
            try:
                ids = sorted([str(t.get('track_id')) for t in data if isinstance(t, dict) and t.get('track_id') is not None])
            except Exception:
                ids = []

            fingerprint = tuple(ids)
            if st.session_state.get('last_data_fingerprint') != fingerprint:
                st.session_state.last_data_fingerprint = fingerprint
                st.session_state.last_update_time = datetime.now()
        except Exception:
            try:
                st.session_state.last_update_time = datetime.now()
            except Exception:
                pass
# -------------------------------------------------------------------
with tab2:
    st.header("Threat & Advisory Status")
    tab_name = "Threat & Advisory Status"
    prev = st.session_state.get('_last_active_tab')
    if prev != tab_name:
        st.session_state['_last_active_tab'] = tab_name
        st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
    st.session_state['_active_tab_name'] = tab_name
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_data_freshness'):
        DashboardLayout.render_data_freshness(st.session_state.get("training_mode", False))
    else:
        st.warning("Data freshness unavailable (layout not initialized)")

    advisory = DashboardStateManager.get_advisory_state() if DashboardStateManager else None
    threat = DashboardStateManager.get_threat_assessment_data() if DashboardStateManager else None
    intent = DashboardStateManager.get_intent_assessment_data() if DashboardStateManager else None
    training_mode = st.session_state.get("training_mode", False)
    
    # Determine overall posture
    advisory_state = advisory.get("system_mode", "MONITORING_ONLY") if advisory else "MONITORING_ONLY"
    threat_level = threat.get("threat_level", "NONE") if threat else "NONE"
    
    # Operational Context Panel
    if advisory_state == "MONITORING_ONLY":
        summary = "System operating in monitoring posture. No elevated threats detected. Advisory state: stable."
    elif threat_level in ["HIGH", "CRITICAL"]:
        summary = f"Elevated threat assessment: {threat_level}. System posture: {advisory_state}. Continuous monitoring active."
    else:
        summary = f"System posture: {advisory_state}. Threat level: {threat_level}. Monitoring ongoing."
    
    is_simulation = (advisory and advisory.get("is_simulation", False)) or (threat and threat.get("is_simulation", False))
    
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_operational_context'):
        DashboardLayout.render_operational_context(
            "Threat & Advisory Status",
            summary,
            training_mode,
            is_simulation
        )
    else:
        st.warning("Operational context unavailable (layout not initialized)")
    
    # Intelligence Narrative
    posture_trend = "stable" if advisory_state == "MONITORING_ONLY" and threat_level in ["NONE", "LOW"] else "elevated" if threat_level in ["MEDIUM", "HIGH"] else "monitoring"
    narrative = f"Overall system posture trend: {posture_trend}. Threat assessment indicates {threat_level.lower()} level activity. Advisory state reflects {advisory_state.lower().replace('_', ' ')}. No immediate action required — informational assessment only."
    
    overall_confidence = advisory.get("confidence", 0.0) if advisory else (threat.get("confidence", 0.0) if threat else 0.0)
    # Guard rendering of intelligence narrative to avoid crashes in degraded mode
    try:
        if DashboardLayout is not None and hasattr(DashboardLayout, "render_intelligence_narrative"):
            DashboardLayout.render_intelligence_narrative(narrative, overall_confidence if overall_confidence > 0 else None)
        else:
            try:
                import streamlit as _st
                _st.warning("Intelligence narrative unavailable in degraded mode")
            except Exception:
                pass
    except Exception:
        try:
            import streamlit as _st
            _st.warning("Intelligence narrative unavailable due to rendering error")
        except Exception:
            pass

        if not advisory and not threat and not intent:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_insufficient_data_message'):
                DashboardLayout.render_insufficient_data_message("Advisory data unavailable")
            else:
                st.warning("Advisory data unavailable (layout not initialized)")
    else:
        if advisory:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_advisory_panel'):
                DashboardLayout.render_advisory_panel(
                    "System Advisory State",
                    advisory.get("system_mode", "MONITORING_ONLY"),
                    advisory.get("confidence", 0.0),
                    advisory.get("reasoning", ""),
                    training_mode,
                    advisory.get("is_simulation", False)
                )
            else:
                st.warning("Advisory panel unavailable (layout not initialized)")

        if threat:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_advisory_panel'):
                DashboardLayout.render_advisory_panel(
                    "Threat Assessment",
                    threat.get("threat_level", "NONE"),
                    threat.get("confidence", 0.0),
                    threat.get("reasoning", ""),
                    training_mode,
                    threat.get("is_simulation", False)
                )
            else:
                st.warning("Threat advisory panel unavailable (layout not initialized)")
        
        # Intent Assessment Panel (below Threat Assessment, above Human Acknowledgment)
        if intent:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_intent_assessment_panel'):
                DashboardLayout.render_intent_assessment_panel(
                    intent,
                    training_mode
                )
            else:
                st.warning("Intent assessment panel unavailable (layout not initialized)")
        elif training_mode:
            # Show simulation data indicator in training mode
            st.info("ℹ️ Intent data unavailable — Monitoring Only")
        
        # Interception Feasibility Panel
        if InterceptionFeasibilityAnalyzer and InterceptionFeasibilityPanel:
            try:
                # Get tracking data for feasibility analysis
                tracking_data = DashboardStateManager.get_tracking_data() if DashboardStateManager else None
                
                if tracking_data and len(tracking_data) > 0:
                    # Analyze first track (or selected track)
                    selected_track = tracking_data[0]
                    
                    # Update trajectory history for the track
                    if TrajectoryTracker:
                        TrajectoryTracker.update_track_history(selected_track)
                    
                    # Compute feasibility
                    feasibility_result = InterceptionFeasibilityAnalyzer.compute_feasibility(
                        selected_track,
                        defender_position={'x': 0.0, 'y': 0.0, 'z': 0.0},  # Default defender at origin
                        is_training_mode=training_mode
                    )
                    
                    # Render panel
                    # Get atmospheric conditions from session state
                    atmospheric_conditions = st.session_state.get("atmospheric_conditions")
                    
                    InterceptionFeasibilityPanel.render_panel(
                        feasibility_result,
                        track=selected_track,
                        atmospheric_conditions=atmospheric_conditions
                    )
                else:
                    st.info("ℹ️ Monitoring Only — Insufficient Data (No tracks available for interception feasibility analysis)")
            except Exception:
                st.info("ℹ️ Monitoring Only — Insufficient Data")
        
        # Update last update time
        from datetime import datetime
        st.session_state.last_update_time = datetime.now()

# -------------------------------------------------------------------
# TAB 3 — Early Warning System
# -------------------------------------------------------------------
with tab3:
    st.header("Early Warning System")
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_data_freshness'):
        tab_name = "Early Warning System"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        DashboardLayout.render_data_freshness(st.session_state.get("training_mode", False))
    else:
        tab_name = "Early Warning System"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        st.warning("Data freshness unavailable (layout not initialized)")

    ew = DashboardStateManager.get_early_warning_data() if DashboardStateManager else None
    training_mode = st.session_state.get("training_mode", False)
    
    # Operational Context Panel
    warning_state = ew.get("warning_state", "NORMAL") if ew else "NORMAL"
    if warning_state == "NORMAL":
        summary = "Early warning system operating normally. No anomalies detected. Baseline patterns stable."
    elif warning_state == "ELEVATED":
        summary = "Early warning system indicates elevated activity. Anomalies detected. Monitoring intensified."
    else:
        summary = f"Early warning system state: {warning_state}. Anomaly detection active. Continuous assessment ongoing."
    
    is_simulation = ew.get("is_simulation", False) if ew else False
    
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_operational_context'):
        DashboardLayout.render_operational_context(
            "Early Warning System",
            summary,
            training_mode,
            is_simulation
        )
    else:
        st.warning("Operational context unavailable (layout not initialized)")
    
    # Intelligence Narrative
    anomaly_status = "no anomalies present" if warning_state == "NORMAL" else "anomalies detected"
    narrative = f"Early warning analysis shows {anomaly_status}. Statistical baselines remain {'within normal parameters' if warning_state == 'NORMAL' else 'showing deviation'}. Trend analysis indicates {'stable patterns' if warning_state == 'NORMAL' else 'elevated activity requiring continued monitoring'}."
    
    ew_confidence = ew.get("confidence", 0.0) if ew else None
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_intelligence_narrative'):
        DashboardLayout.render_intelligence_narrative(narrative, ew_confidence)
    else:
        st.warning("Intelligence narrative unavailable (layout not initialized)")

    if not ew:
        if not training_mode:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_insufficient_data_message'):
                DashboardLayout.render_insufficient_data_message("Early warning unavailable")
            else:
                st.warning("Early warning unavailable (layout not initialized)")
        else:
            st.info("ℹ️ Training data generator initializing — Monitoring Only")
    else:
        if DashboardLayout is not None and hasattr(DashboardLayout, 'render_advisory_panel'):
            DashboardLayout.render_advisory_panel(
                "Early Warning State",
                ew.get("warning_state", "NORMAL"),
                ew.get("confidence", 0.0),
                "\n".join(ew.get("reasoning", [])) if isinstance(ew.get("reasoning"), list) else ew.get("reasoning", ""),
                training_mode,
                ew.get("is_simulation", False)
            )
        else:
            st.warning("Early warning advisory panel unavailable (layout not initialized)")

        if EffectsController:
            EffectsController.render_audio_indicator(ew.get("warning_state", "NORMAL"))
        
        # Update last update time
        from datetime import datetime
        st.session_state.last_update_time = datetime.now()

# -------------------------------------------------------------------
# TAB 4 — Electronic Warfare
# -------------------------------------------------------------------
with tab4:
    st.header("Electronic Warfare Analysis")
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_data_freshness'):
        tab_name = "Electronic Warfare Analysis"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        DashboardLayout.render_data_freshness(st.session_state.get("training_mode", False))
    else:
        tab_name = "Electronic Warfare Analysis"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        st.warning("Data freshness unavailable (layout not initialized)")

    ew_data = DashboardStateManager.get_ew_analysis_data() if DashboardStateManager else None
    training_mode = st.session_state.get("training_mode", False)
    
    # Operational Context Panel
    ew_state = ew_data.get("ew_state", "NORMAL") if ew_data else "NORMAL"
    if ew_state == "NORMAL":
        summary = "RF spectrum analysis indicates normal operation. Noise floor stable. No anomalous emissions detected."
    else:
        summary = f"RF spectrum analysis shows {ew_state.lower()} state. Anomalous patterns detected. Spectrum monitoring active."
    
    is_simulation = ew_data.get("is_simulation", False) if ew_data else False
    
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_operational_context'):
        DashboardLayout.render_operational_context(
            "Electronic Warfare Analysis",
            summary,
            training_mode,
            is_simulation
        )
    else:
        st.warning("Operational context unavailable (layout not initialized)")
    
    # Intelligence Narrative
    spectrum_status = "stable" if ew_state == "NORMAL" else "showing deviations"
    narrative = f"Spectrum analysis indicates {spectrum_status}. Noise floor measurements are {'within baseline parameters' if ew_state == 'NORMAL' else 'elevated above baseline'}. Signal-to-noise ratios {'remain normal' if ew_state == 'NORMAL' else 'show variation'}. Bandwidth utilization: {'normal' if ew_state == 'NORMAL' else 'anomalous patterns observed'}."
    
    ew_confidence = ew_data.get("confidence", 0.0) if ew_data else None
    if DashboardLayout is not None and hasattr(DashboardLayout, 'render_intelligence_narrative'):
        DashboardLayout.render_intelligence_narrative(narrative, ew_confidence)
    else:
        st.warning("Intelligence narrative unavailable (layout not initialized)")

    if not ew_data:
        if not training_mode:
            if DashboardLayout is not None and hasattr(DashboardLayout, 'render_insufficient_data_message'):
                DashboardLayout.render_insufficient_data_message("EW data unavailable")
            else:
                st.warning("EW data unavailable (layout not initialized)")
        else:
            st.info("ℹ️ Training data generator initializing — Monitoring Only")
    else:
        if DashboardLayout is not None and hasattr(DashboardLayout, 'render_advisory_panel'):
            DashboardLayout.render_advisory_panel(
                "Electronic Warfare State",
                ew_data.get("ew_state", "NORMAL"),
                ew_data.get("confidence", 0.0),
                "\n".join(ew_data.get("reasoning", [])) if isinstance(ew_data.get("reasoning"), list) else ew_data.get("reasoning", ""),
                training_mode,
                ew_data.get("is_simulation", False)
            )
        else:
            st.warning("EW advisory panel unavailable (layout not initialized)")
        
        # Update last update time
        from datetime import datetime
        st.session_state.last_update_time = datetime.now()

# -------------------------------------------------------------------
# TAB 5 — Cybersecurity
# -------------------------------------------------------------------
with tab5:
    st.header("Cybersecurity & System Integrity")
    if DashboardLayout:
        tab_name = "Cybersecurity & System Integrity"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        DashboardLayout.render_data_freshness(st.session_state.get("training_mode", False))

    cyber = DashboardStateManager.get_cybersecurity_data() if DashboardStateManager else None
    training_mode = st.session_state.get("training_mode", False)
    
    # Operational Context Panel
    cyber_state = cyber.get("cybersecurity_state", "NORMAL") if cyber else "NORMAL"
    if cyber_state == "NORMAL":
        summary = "System integrity monitoring normal. No suspicious activity detected. Access patterns within baseline."
    elif cyber_state == "SUSPICIOUS":
        summary = "System integrity monitoring indicates suspicious activity. Anomalous patterns detected. Investigation recommended."
    else:
        summary = f"System integrity monitoring: {cyber_state}. Alert condition active. Immediate review recommended."
    
    is_simulation = cyber.get("is_simulation", False) if cyber else False
    
    if DashboardLayout:
        DashboardLayout.render_operational_context(
            "Cybersecurity & System Integrity",
            summary,
            training_mode,
            is_simulation
        )
    
    # Intelligence Narrative
    integrity_status = "maintained" if cyber_state == "NORMAL" else "requires attention"
    narrative = f"System integrity posture: {integrity_status}. Log access patterns {'within normal parameters' if cyber_state == 'NORMAL' else 'show deviations'}. Configuration consistency: {'verified' if cyber_state == 'NORMAL' else 'under review'}. No unauthorized access {'detected' if cyber_state == 'NORMAL' else 'patterns observed'}."
    
    cyber_confidence = cyber.get("confidence", 0.0) if cyber else None
    DashboardLayout.render_intelligence_narrative(narrative, cyber_confidence)

    if not cyber:
        if not training_mode:
            DashboardLayout.render_insufficient_data_message("Cybersecurity data unavailable")
        else:
            st.info("ℹ️ Training data generator initializing — Monitoring Only")
    else:
        DashboardLayout.render_advisory_panel(
            "Cybersecurity State",
            cyber.get("cybersecurity_state", "NORMAL"),
            cyber.get("confidence", 0.0),
            "\n".join(cyber.get("reasoning", [])) if isinstance(cyber.get("reasoning"), list) else cyber.get("reasoning", ""),
            training_mode,
            cyber.get("is_simulation", False)
        )
        
        # Update last update time
        from datetime import datetime
        st.session_state.last_update_time = datetime.now()

# -------------------------------------------------------------------
# TAB 6 — SAM C2 Visualization
# -------------------------------------------------------------------
with tab6:
    st.header("SAM C2 Visualization")
    if DashboardLayout:
        tab_name = "SAM C2 Visualization"
        prev = st.session_state.get('_last_active_tab')
        if prev != tab_name:
            st.session_state['_last_active_tab'] = tab_name
            st.session_state[f'last_refresh_ts::{tab_name}'] = datetime.now()
        st.session_state['_active_tab_name'] = tab_name
        DashboardLayout.render_data_freshness(st.session_state.get("training_mode", False))
    
    training_mode = st.session_state.get("training_mode", False)
    
    # Operational Context Panel
    summary = "SAM C2 visualization provides 3D battlespace, engagement sequences, and interception feasibility analysis. All visualizations are advisory only - mathematical simulations for operator awareness."
    is_simulation = training_mode  # Always simulation in this tab
    if DashboardLayout:
        DashboardLayout.render_operational_context(
            "SAM C2 Visualization",
            summary,
            training_mode,
            is_simulation
        )
    
    # Intelligence Narrative
    narrative = "SAM C2 visualization provides comprehensive 3D battlespace awareness, engagement sequence simulation, and interception feasibility assessment. All outputs are mathematical simulations and feasibility assessments only. No actual engagement or control logic is executed."
    DashboardLayout.render_intelligence_narrative(narrative, None)
    
    # Get tracking data
    data = DashboardStateManager.get_tracking_data() if DashboardStateManager else None
    
    if not data or len(data) == 0:
        if not training_mode:
            if DashboardLayout:
                DashboardLayout.render_insufficient_data_message("Tracking data unavailable for SAM C2 visualization")
        else:
            st.info("ℹ️ Training data generator initializing — Monitoring Only")
    else:
        # Visualization mode selector
        viz_mode = st.radio(
            "Visualization Mode",
            ["3D Battlespace", "Engagement Sequence", "Trajectory Tracking", "Interception Window"],
            horizontal=True,
            key="sam_c2_viz_mode"
        )
        
        # Default defender position (origin)
        defender_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Select target track for detailed visualization
        if len(data) > 0:
            track_options = [f"Track {t.get('track_id', 'UNKNOWN')} ({t.get('object_type', 'UNKNOWN')})" for t in data if isinstance(t, dict)]
            if track_options:
                selected_track_idx = st.selectbox(
                    "Select Track for Detailed Visualization",
                    range(len(track_options)),
                    format_func=lambda x: track_options[x],
                    key="sam_c2_track_select"
                )
                selected_track = data[selected_track_idx] if selected_track_idx < len(data) else data[0]
            else:
                selected_track = data[0]
        else:
            selected_track = None
        
        # Render selected visualization
        if selected_track and Battlespace3D:
            try:
                if viz_mode == "3D Battlespace":
                    # 3D Battlespace Visualization
                    if training_mode:
                        st.info("ℹ️ **SIMULATION / TRAINING DATA** — All displayed data is synthetic. Advisory-only system.")
                    
                    # Get atmospheric conditions from session state
                    atmospheric_conditions = st.session_state.get("atmospheric_conditions")
                    show_atmospheric_overlay = st.session_state.get("show_atmospheric_overlay", False)
                    
                    # Sensor Layer Controls (visual only, defence-grade UI)
                    # ADVISORY ONLY — SENSOR VISUALIZATION. NO CONTROL OR DECISION LOGIC.
                    st.subheader("Sensor Layer Controls")
                    
                    # Initialize sensor layer controls in session state (default ON)
                    if "sensor_show_surveillance" not in st.session_state:
                        st.session_state.sensor_show_surveillance = True
                    if "sensor_show_fire_control" not in st.session_state:
                        st.session_state.sensor_show_fire_control = True
                    if "sensor_show_passive" not in st.session_state:
                        st.session_state.sensor_show_passive = True
                    if "sensor_global_opacity" not in st.session_state:
                        st.session_state.sensor_global_opacity = None
                    
                    left_col, right_col = st.columns([1, 1])

                    with left_col:
                        st.markdown("### Radar Sensors")
                        show_surveillance = st.checkbox(
                            "Surveillance Radar",
                            value=st.session_state.sensor_show_surveillance,
                            key="sensor_toggle_surveillance",
                            help="Toggle Long-Range Surveillance Radar visualization"
                        )
                        st.session_state.sensor_show_surveillance = show_surveillance

                        show_fire_control = st.checkbox(
                            "Precision Tracking Radar",
                            value=st.session_state.sensor_show_fire_control,
                            key="sensor_toggle_fire_control",
                            help="Toggle Precision Tracking Radar visualization (ADVISORY ONLY)"
                        )
                        st.session_state.sensor_show_fire_control = show_fire_control

                        st.markdown("### Passive Sensors")
                        show_passive = st.checkbox(
                            "Passive / ESM Sensor",
                            value=st.session_state.sensor_show_passive,
                            key="sensor_toggle_passive",
                            help="Toggle Passive / ESM Sensor visualization"
                        )
                        st.session_state.sensor_show_passive = show_passive

                    with right_col:
                        st.markdown("### Visual Aids")
                        if "show_sensor_track_hints" not in st.session_state:
                            st.session_state["show_sensor_track_hints"] = True
                        show_sensor_hints = st.checkbox(
                            "Show Sensor-Track Coverage Hints",
                            value=st.session_state["show_sensor_track_hints"],
                            key="show_sensor_track_hints",
                            help="Display faint dotted lines showing tracks within sensor coverage volumes (geometric check only, no detection logic)"
                        )
                        use_custom_opacity = st.checkbox(
                            "Adjust Coverage Opacity",
                            value=st.session_state.sensor_global_opacity is not None,
                            key="sensor_use_custom_opacity",
                            help="Override default sensor coverage volume opacity"
                        )
                        global_opacity = None
                        if use_custom_opacity:
                            if st.session_state.sensor_global_opacity is None:
                                st.session_state.sensor_global_opacity = 0.12
                            global_opacity = st.slider(
                                "Coverage Volume Opacity",
                                min_value=0.05,
                                max_value=0.25,
                                value=st.session_state.sensor_global_opacity,
                                step=0.01,
                                key="sensor_opacity_slider",
                                help="Adjust opacity of all sensor coverage volumes (0.05 = very faint, 0.25 = more visible)"
                            )
                            st.session_state.sensor_global_opacity = global_opacity
                        else:
                            st.session_state.sensor_global_opacity = None
                    
                    sensor_layer_controls = {
                        "show_surveillance": show_surveillance,
                        "show_fire_control": show_fire_control,
                        "show_passive": show_passive,
                        "global_opacity": global_opacity
                    }
                    
                    # --- Simulation Time Control (RESTORED) ---
                    SIM_DURATION = 120.0
                    if "sim_time" not in st.session_state:
                        st.session_state["sim_time"] = 0.0
                    
                    sim_time = st.slider(
                        "Simulation Time (seconds)",
                        min_value=0.0,
                        max_value=float(SIM_DURATION),
                        step=1.0,
                        key="sim_time"
                    )
                    st.caption("Drag to scrub through the simulated timeline")

                    # (Track History Replay removed) - Simulation Time is the only time control
                    # Threat Density (visibility only; scenario-aware default)
                    current_scenario = str(st.session_state.get("selected_scenario", "civil_air_traffic") or "civil_air_traffic")
                    show_density_default = bool(training_mode) or (current_scenario in ("drone_swarm", "saturation_test"))
                    if "show_threat_density" not in st.session_state:
                        st.session_state["show_threat_density"] = show_density_default
                    show_threat_density = st.checkbox(
                        "Show Threat Density",
                        value=st.session_state["show_threat_density"],
                        key="show_threat_density",
                        help="Advisory only. Highlights track density; does not affect positions or logic."
                    )
                    st.caption("Threat Density (Advisory): Low = Blue, Medium = Yellow, High = Orange/Red.")
                    st.caption("Urgency Levels (TTC): LOW — >180 s | MEDIUM — 60–180 s | HIGH — <60 s")
                    
                    # SCENARIO CHANGE: Destroy and rebuild (correct Plotly 3D lifecycle)
                    current_scenario = str(st.session_state.get("selected_scenario", "civil_air_traffic") or "civil_air_traffic")
                    previous_scenario = st.session_state.get("_last_rendered_scenario")
                    
                    if previous_scenario != current_scenario:
                        # Scenario changed: destroy old figure, force full rebuild
                        st.session_state["battlespace_fig"] = None
                        st.session_state["_last_rendered_scenario"] = current_scenario
                        st.session_state["_scenario_just_changed"] = True
                    
                    # Create figure once per scenario (destroy on scenario change)
                    if "battlespace_fig" not in st.session_state or st.session_state["battlespace_fig"] is None:
                        try:
                            fig_3d = Battlespace3D.create_3d_visualization(
                                tracks=data,
                                defender_position=defender_position,
                                view_range=50000.0,
                                training_mode=training_mode,
                                show_trajectories=True,
                                show_interception_windows=False,
                                atmospheric_conditions=atmospheric_conditions,
                                show_atmospheric_overlay=show_atmospheric_overlay,
                                show_sensor_track_hints=show_sensor_hints,
                                sensor_layer_controls=sensor_layer_controls,
                                show_protected_zones=show_protected_zones,
                                highlight_track_id=str(selected_track.get('track_id', '')) if selected_track else None,
                                sim_time=0.0
                            )
                            st.session_state["battlespace_fig"] = fig_3d
                            if "_last_rendered_scenario" not in st.session_state:
                                st.session_state["_last_rendered_scenario"] = current_scenario
                        except Exception as e:
                            st.error(f"Battlespace initialization failed: {str(e)}")
                            st.stop()
                    else:
                        fig_3d = st.session_state["battlespace_fig"]
                    
                    # If scenario just changed, update uirevision to force Plotly re-render
                    try:
                        if st.session_state.get("_scenario_just_changed"):
                            import time
                            fig_3d.layout.uirevision = f"battlespace_rebuild_{int(time.time() * 1000)}"
                            st.session_state["_scenario_just_changed"] = False
                    except Exception:
                        pass
                    
                    # Camera preserved via unique uirevision on rebuild.
                    # Figure rebuilt on scenario change (correct Plotly 3D lifecycle).
                    # Time slider and sensor toggles use in-place mutations (no rebuild).

                    # Sensor layer toggles: visibility-only, in-place mutations only.
                    try:
                        surveillance_on = sensor_layer_controls.get("show_surveillance", True) if isinstance(sensor_layer_controls, dict) else True
                        tracking_on = sensor_layer_controls.get("show_fire_control", True) if isinstance(sensor_layer_controls, dict) else True
                        esm_on = sensor_layer_controls.get("show_passive", True) if isinstance(sensor_layer_controls, dict) else True

                        for tr in fig_3d.data:
                            meta = getattr(tr, 'meta', None)
                            # HARD GUARD: Never touch track traces
                            if meta and meta.get('type') == 'track':
                                continue
                            # Visibility-only mutations for sensor and infrastructure traces
                            if meta and meta.get('is_sensor'):
                                stype = str(meta.get('sensor_type', '')).upper()
                                if 'LONG_RANGE' in stype or 'SURVEILLANCE' in stype:
                                    tr.visible = surveillance_on
                                elif 'FIRE' in stype or 'TRACK' in stype:
                                    tr.visible = tracking_on
                                elif 'PASSIVE' in stype or 'ESM' in stype:
                                    tr.visible = esm_on
                            elif meta and meta.get('type') in ('sensor_volume', 'density', 'sensor_hint'):
                                # Infrastructure visibility follows sensor toggles
                                if meta.get('type') == 'density':
                                    tr.visible = show_threat_density
                                elif 'sensor_type' in meta:
                                    stype = str(meta.get('sensor_type', '')).upper()
                                    if 'SURVEILLANCE' in stype:
                                        tr.visible = surveillance_on
                                    elif 'TRACK' in stype or 'FIRE' in stype:
                                        tr.visible = tracking_on
                                    elif 'ESM' in stype or 'PASSIVE' in stype:
                                        tr.visible = esm_on
                    except Exception:
                        pass

                    # Verify tracks still exist (sanity check only)
                    try:
                        has_tracks = any((getattr(t, 'meta', None) and t.meta.get('type') == 'track') for t in fig_3d.data)
                    except Exception:
                        has_tracks = False
                    
                    # Update track positions in-place (no figure rebuild, no trace addition/removal).
                    try:
                        from abhedya.dashboard.battlespace_3d import update_track_positions
                        effective_time = float(st.session_state.get("sim_time", 0.0))
                        update_track_positions(fig_3d, data, float(effective_time))
                    except Exception:
                        pass
                    # Note: Track history / replay feature removed. No per-track history persisted in session_state.
                    
                    # Threat Density layer (visual only; add or update trace, never recreate figure)
                    try:
                        from abhedya.dashboard.battlespace_3d import compute_threat_density_points
                        import plotly.graph_objects as go
                        import math as _math
                        density_points = compute_threat_density_points(data)
                        xs = [p[0] for p in density_points]
                        ys = [p[1] for p in density_points]
                        zs = [p[2] for p in density_points]
                        # Only update existing density trace. Do NOT add new traces after figure init.
                        density_trace = None
                        for tr in fig_3d.data:
                            if getattr(tr, "name", None) == "Threat Density (Advisory)":
                                density_trace = tr
                                break
                        if density_trace is not None:
                            density_trace.x = xs
                            density_trace.y = ys
                            density_trace.z = zs
                            density_trace.visible = show_threat_density
                        else:
                            # Do not create density trace here; it must be created during figure initialization
                            pass
                        # Saturation cluster hint: soft halo ring at centroid when dense (visual only)
                        halo_trace = None
                        for tr in fig_3d.data:
                            if getattr(tr, "name", None) == "Density Halo (Advisory)":
                                halo_trace = tr
                                break
                        n_pts = len(density_points)
                        show_halo = show_threat_density and n_pts >= 5
                        if n_pts >= 5:
                            cx = sum(xs) / n_pts
                            cy = sum(ys) / n_pts
                            cz = sum(zs) / n_pts
                            radius_km = 2.0
                            steps = 32
                            halo_x = [cx + radius_km * _math.cos(2 * _math.pi * i / steps) for i in range(steps + 1)]
                            halo_y = [cy + radius_km * _math.sin(2 * _math.pi * i / steps) for i in range(steps + 1)]
                            halo_z = [cz] * (steps + 1)
                            if halo_trace is not None:
                                halo_trace.x = halo_x
                                halo_trace.y = halo_y
                                halo_trace.z = halo_z
                                halo_trace.visible = show_halo
                            else:
                                # Do not create halo trace after init; skip to preserve persistent figure
                                pass
                        elif halo_trace is not None:
                            halo_trace.visible = False
                    except Exception:
                        pass
                    
                    # Inject Plotly-native updatemenus overlay for in-figure recovery
                    healthy = is_figure_healthy(fig_3d)

                    # Professional button styling (health-aware opacity fade)
                    btn_opacity = 0.35 if healthy else 0.95
                    tooltip_opacity = 0.0 if healthy else 0.85

                    fig_3d.update_layout(
                        updatemenus=[
                            dict(
                                type="buttons",
                                direction="left",
                                x=0.5,
                                y=0.003,
                                xanchor="center",
                                yanchor="bottom",
                                showactive=False,
                                visible=True,
                                bgcolor=f"rgba(37,99,235,{btn_opacity})",
                                bordercolor="#1E40AF",
                                borderwidth=1,
                                font=dict(color="white", size=12, family="Inter, Segoe UI, sans-serif"),
                                pad=dict(l=10, r=10, t=6, b=6),
                                buttons=[
                                    dict(
                                        label="Reacquire Tactical View",
                                        method="relayout",
                                        args=[
                                            {
                                                "scene.camera.eye.x": 1.25,
                                                "scene.camera.eye.y": 1.25,
                                                "scene.camera.eye.z": 1.25,
                                                "scene.camera.center.x": 0,
                                                "scene.camera.center.y": 0,
                                                "scene.camera.center.z": 0,
                                                "scene.xaxis.visible": True,
                                                "scene.yaxis.visible": True,
                                                "scene.zaxis.visible": True,
                                            }
                                        ],
                                    )
                                ],
                            )
                        ],
                        annotations=[
                            dict(
                                x=0.5,
                                y=0.11,
                                xref="paper",
                                yref="paper",
                                text=("ⓘ Reacquire Tactical View resets camera & redraws the battlespace if the view becomes occluded."),
                                showarrow=False,
                                font=dict(size=11, color="#C7D2FE", family="Inter, Segoe UI, sans-serif"),
                                align="center",
                                bgcolor="rgba(15,23,42,0.85)",
                                bordercolor="#334155",
                                borderwidth=1,
                                borderpad=6,
                                xanchor="center",
                                yanchor="bottom",
                                opacity=tooltip_opacity,
                            )
                        ]
                    )

                    # Add invisible hover trace for tooltip support
                    import plotly.graph_objects as go
                    fig_3d.add_trace(
                        go.Scatter3d(
                            x=[0],
                            y=[0],
                            z=[0],
                            mode="markers",
                            marker=dict(size=1, opacity=0),
                            hoverinfo="text",
                            text=(
                                "ⓘ Reacquire Tactical View & redraws the battlespace if the view becomes occluded."
                            ),
                            showlegend=False,
                        )
                    )

                    with st.container():
                        st.plotly_chart(
                            fig_3d,
                            use_container_width=True,
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "responsive": True,
                                "scrollZoom": True,
                            },
                        )
                    
                    # Sensor Legend Panel (below 3D visualization)
                    try:
                        from abhedya.dashboard.sensor_models import SensorModels
                        
                        st.subheader("Sensor Coverage Legend (Advisory)")
                        
                        # Get all sensor definitions from sensor_models.py
                        sensor_definitions = SensorModels.get_all_sensor_definitions()
                        
                        if sensor_definitions and len(sensor_definitions) >= 3:
                            # Display sensor legend with color → sensor type mapping
                            st.markdown("**Color → Sensor Type Mapping:**")
                            
                            # Create columns for legend entries
                            cols = st.columns(min(3, len(sensor_definitions)))
                            
                            for idx, sensor_def in enumerate(sensor_definitions):
                                metadata = sensor_def.get("metadata")
                                geometry = sensor_def.get("geometry")
                                
                                if not metadata or not geometry:
                                    continue
                                
                                col_idx = idx % len(cols)
                                with cols[col_idx]:
                                    # Color swatch + sensor info
                                    st.markdown(
                                        f"<div style='padding:10px; border-left:4px solid {metadata.color}; margin-bottom:10px; background-color:rgba(255,255,255,0.02); border-radius:4px;'>"
                                        f"<div style='display:flex; align-items:center; margin-bottom:6px;'>"
                                        f"<div style='width:20px; height:20px; background-color:{metadata.color}; border-radius:3px; margin-right:8px;'></div>"
                                        f"<strong>{metadata.icon} {metadata.name}</strong>"
                                        f"</div>"
                                        f"<div style='margin-left:28px;'>"
                                        f"<small><strong>Type:</strong> {metadata.sensor_type.value}</small><br>"
                                        f"<small><strong>Role:</strong> {metadata.role}</small><br>"
                                        f"<small><strong>Range:</strong> {geometry.coverage_range_km:.0f} km</small>"
                                        f"</div>"
                                        f"</div>",
                                        unsafe_allow_html=True
                                    )
                            
                            # Multiple sensors indicator
                            st.info(f"📡 **{len(sensor_definitions)} sensors visible simultaneously** | Coverage volumes may overlap visually")
                            
                            # Critical disclaimer
                            st.warning(
                                "⚠️ **Visual coverage ≠ detection guarantee**\n\n"
                                "Coverage volume overlap does NOT imply:\n"
                                "- Sensor fusion\n"
                                "- Detection logic\n"
                                "- Priority or dominance\n"
                                "- Engagement authorization\n\n"
                                "All sensor visuals are advisory only — visualization purposes."
                            )
                            
                            st.caption("**Advisory Only** — Sensor visualization does not imply firing or authorization. All sensor visuals are informational only.")
                        else:
                            st.info("ℹ️ Sensor information unavailable — Monitoring Only")
                    except Exception:
                        pass  # Fail silently - sensor panel is non-critical

                    # --- Multi-Sensor Fusion Breakdown (Advisory) ---
                    # MUST render immediately after Sensor Coverage Legend (display-only)
                    def get_synthetic_fusion(track_id: str):
                        base = abs(hash(track_id)) % 100
                        surv = 45 + (base % 10)
                        track_v = 25 + ((base // 2) % 10)
                        esm = 100 - surv - track_v
                        return {
                            "Surveillance Radar": int(surv),
                            "Precision Tracking Radar": int(track_v),
                            "Passive RF / ESM": int(esm)
                        }

                    # Select track id (use synthetic CIV_001 when none selected)
                    if isinstance(selected_track, dict):
                        fusion_track_id = str(selected_track.get("track_id", "CIV_001"))
                        classification = selected_track.get('object_type', 'UNKNOWN')
                    else:
                        fusion_track_id = "CIV_001"
                        classification = "FRIENDLY"

                    fusion = get_synthetic_fusion(fusion_track_id)

                    # Render UI exactly as specified (unconditional)
                    st.subheader("Multi-Sensor Fusion Breakdown (Advisory)")
                    st.caption("Advisory-only. Synthetic training data.")
                    st.write(f"Track: {fusion_track_id} | Classification: {classification}")

                    # Render contribution bars with percent text; values sum to 100
                    for sensor_name, value in fusion.items():
                        pct = int(value)
                        cols = st.columns([3, 4, 1])
                        with cols[0]:
                            st.write(sensor_name)
                        with cols[1]:
                            st.progress(pct)
                        with cols[2]:
                            st.write(f"{pct}%")

                    st.markdown("**Fusion Quality:**")
                    st.write("• EW Degradation: None")
                    st.write("• Confidence Trend: Stable")
                elif viz_mode == "Engagement Sequence" and EngagementVisualization:
                    # Engagement Sequence Visualization
                    # Calculate interception feasibility if available
                    interception_data = None
                    try:
                        from abhedya.interception_simulation import InterceptionFeasibilityAnalyzer
                        from abhedya.domain.value_objects import Coordinates, Velocity
                        
                        target_pos = selected_track.get('position', {})
                        target_vel = selected_track.get('velocity', {})
                        
                        if isinstance(target_pos, dict) and isinstance(target_vel, dict):
                            analyzer = InterceptionFeasibilityAnalyzer()
                            result = analyzer.assess_feasibility(
                                defender_position=Coordinates(
                                    x=defender_position['x'],
                                    y=defender_position['y'],
                                    z=defender_position['z']
                                ),
                                defender_velocity=Velocity(vx=0.0, vy=0.0, vz=0.0),
                                target_position=Coordinates(
                                    x=float(target_pos.get('x', 0.0)),
                                    y=float(target_pos.get('y', 0.0)),
                                    z=float(target_pos.get('z', 0.0))
                                ),
                                target_velocity=Velocity(
                                    vx=float(target_vel.get('vx', 0.0)),
                                    vy=float(target_vel.get('vy', 0.0)),
                                    vz=float(target_vel.get('vz', 0.0))
                                )
                            )
                            
                            interception_data = {
                                'feasibility_level': result.feasibility_level.value,
                                'time_to_intercept': result.closest_approach.time_to_closest_approach_seconds,
                                'closest_approach_distance': result.closest_approach.closest_approach_distance_meters
                            }
                    except Exception:
                        pass  # Fail silently - interception analysis optional
                    
                    # Get atmospheric conditions from session state
                    atmospheric_conditions = st.session_state.get("atmospheric_conditions")
                    
                    fig_engagement = EngagementVisualization.create_engagement_sequence(
                        target_track=selected_track,
                        defender_position=defender_position,
                        interception_result=interception_data,
                        time_steps=50,
                        training_mode=training_mode,
                        atmospheric_conditions=atmospheric_conditions
                    )
                    st.plotly_chart(fig_engagement, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'responsive': True, 'scrollZoom': True})
                    
                    # Interception Feasibility Panel (below visualization)
                    if InterceptionFeasibilityAnalyzer and InterceptionFeasibilityPanel:
                        try:
                            # Update trajectory history
                            if TrajectoryTracker:
                                TrajectoryTracker.update_track_history(selected_track)
                            
                            # Compute feasibility using new analyzer
                            feasibility_result = InterceptionFeasibilityAnalyzer.compute_feasibility(
                                selected_track,
                                defender_position=defender_position,
                                is_training_mode=training_mode
                            )
                            
                            # Render panel
                            InterceptionFeasibilityPanel.render_panel(
                                feasibility_result,
                                track=selected_track
                            )
                        except Exception:
                            pass  # Fail silently
                    
                elif viz_mode == "Trajectory Tracking" and TrajectoryTracker:
                    # Trajectory Tracking Visualization
                    # Get trajectory history from session state if available
                    history_points = st.session_state.get('track_history', {}).get(
                        str(selected_track.get('track_id', '')), []
                    )
                    
                    fig_trajectory = TrajectoryTracker.create_trajectory_visualization(
                        track=selected_track,
                        history_points=history_points,
                        prediction_seconds=60.0,
                        training_mode=training_mode
                    )
                    st.plotly_chart(fig_trajectory, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'responsive': True, 'scrollZoom': True})
                    
                elif viz_mode == "Interception Window" and InterceptionWindowVisualization:
                    # Interception Window Visualization
                    interception_result_data = None
                    try:
                        from abhedya.interception_simulation import InterceptionFeasibilityAnalyzer
                        from abhedya.domain.value_objects import Coordinates, Velocity
                        
                        target_pos = selected_track.get('position', {})
                        target_vel = selected_track.get('velocity', {})
                        
                        if isinstance(target_pos, dict) and isinstance(target_vel, dict):
                            analyzer = InterceptionFeasibilityAnalyzer()
                            result = analyzer.assess_feasibility(
                                defender_position=Coordinates(
                                    x=defender_position['x'],
                                    y=defender_position['y'],
                                    z=defender_position['z']
                                ),
                                defender_velocity=Velocity(vx=0.0, vy=0.0, vz=0.0),
                                target_position=Coordinates(
                                    x=float(target_pos.get('x', 0.0)),
                                    y=float(target_pos.get('y', 0.0)),
                                    z=float(target_pos.get('z', 0.0))
                                ),
                                target_velocity=Velocity(
                                    vx=float(target_vel.get('vx', 0.0)),
                                    vy=float(target_vel.get('vy', 0.0)),
                                    vz=float(target_vel.get('vz', 0.0))
                                )
                            )
                            
                            interception_result_data = {
                                'feasibility_level': result.feasibility_level.value,
                                'time_to_intercept': result.closest_approach.time_to_closest_approach_seconds,
                                'closest_approach_distance': result.closest_approach.closest_approach_distance_meters,
                                'window_start_time': max(0.0, result.closest_approach.time_to_closest_approach_seconds - 10.0),
                                'window_end_time': result.closest_approach.time_to_closest_approach_seconds + 10.0
                            }
                    except Exception:
                        pass  # Fail silently
                    
                    if interception_result_data:
                        fig_window = InterceptionWindowVisualization.create_interception_window_visualization(
                            target_track=selected_track,
                            defender_position=defender_position,
                            interception_result=interception_result_data,
                            view_range=50000.0
                        )
                        st.plotly_chart(fig_window, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'responsive': True, 'scrollZoom': True})
                    else:
                        st.info("ℹ️ Interception feasibility analysis unavailable. Enable Training & Simulation Mode for full functionality.")
                
            except Exception as e:
                st.error(f"Visualization error: {str(e)}")
                st.info("ℹ️ Visualization failed. This is a non-critical advisory feature.")
        
        # Atmospheric effects panel (if available)
        if selected_track and AtmosphericModel:
            with st.expander("Atmospheric Effects (Advisory Only)"):
                pos = selected_track.get('position', {})
                vel = selected_track.get('velocity', {})
                
                if isinstance(pos, dict) and isinstance(vel, dict):
                    altitude = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0
                    speed = math.sqrt(
                        (float(vel.get('vx', 0.0)) ** 2) +
                        (float(vel.get('vy', 0.0)) ** 2) +
                        (float(vel.get('vz', 0.0)) ** 2)
                    )
                    
                    atmospheric_effects = AtmosphericModel.calculate_atmospheric_effects(
                        altitude_meters=altitude,
                        velocity_ms=speed
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Air Density", f"{atmospheric_effects['air_density_kg_per_m3']:.3f} kg/m³")
                        st.metric("Pressure", f"{atmospheric_effects['pressure_pa']/1000:.1f} kPa")
                    with col2:
                        st.metric("Temperature", f"{atmospheric_effects['temperature_k']:.1f} K")
                        st.metric("Drag Coefficient", f"{atmospheric_effects['drag_coefficient']:.3f}")
                    with col3:
                        st.metric("Wind Effect Factor", f"{atmospheric_effects['wind_effect_factor']:.2f}")
                    
                    st.caption("⚠️ Atmospheric effects are advisory only - mathematical modeling for visualization purposes")
        
        # Sensor Contribution & Confidence Breakdown Panel
        if selected_track and SensorContributionPanel:
            with st.expander("Sensor Contribution & Confidence Breakdown (Advisory Only)"):
                try:
                    SensorContributionPanel.render_sensor_contribution_panel(
                        selected_track,
                        training_mode=training_mode
                    )
                except Exception:
                    st.info("ℹ️ Sensor contribution data unavailable — Advisory Only")
        
        # Update last update time
        from datetime import datetime
        st.session_state.last_update_time = datetime.now()

# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; padding:15px;">
    <p><strong>Abhedya Air Defense System</strong></p>
    <p>Decision Support System — Advisory Only</p>
    <p>Human operator review required</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Compatibility Entry Point removed to avoid accidental imports
# -------------------------------------------------------------------
