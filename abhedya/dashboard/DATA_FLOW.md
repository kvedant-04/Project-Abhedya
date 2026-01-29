# SAM C2 Dashboard Data Flow

## Visual Data Flow Diagrams

### Standard Flow (Real-World Mode)

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
│  (Tab Orchestration, Session State Management)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────────────────────┐
                 │                                     │
                 ▼                                     ▼
    ┌──────────────────────┐          ┌──────────────────────┐
    │   state_manager.py    │          │    layout.py          │
    │  (Data Fetching)     │          │  (UI Helpers)         │
    └───────────┬───────────┘          └──────────────────────┘
                │
                │ Fetches from backend
                │
                ▼
    ┌───────────────────────────────────────────┐
    │  Backend Modules                          │
    │  - tracking                               │
    │  - early_warning                          │
    │  - ew_analysis                            │
    │  - cybersecurity                          │
    │  - threat_assessment                      │
    └───────────────────────────────────────────┘
                │
                │ Returns data
                │
                ▼
    ┌──────────────────────┐
    │ visual_components.py │
    │  (Visualization)     │
    └───────────┬──────────┘
                │
                │ Creates Plotly figure
                │
                ▼
    ┌──────────────────────┐
    │    layout.py         │
    │  (UI Rendering)      │
    └──────────────────────┘
                │
                ▼
         Streamlit UI
```

### Training/Simulation Mode Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
│  st.session_state.training_mode = True                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
    ┌──────────────────────┐
    │   state_manager.py    │
    │  Detects training_mode│
    └───────────┬───────────┘
                │
                ▼
    ┌──────────────────────┐
    │ simulation_engine.py │
    │  (Synthetic Data)    │
    └───────────┬───────────┘
                │
                │ Generates synthetic tracks
                │
                ▼
    ┌──────────────────────┐
    │ visual_components.py │
    │  (With simulation    │
    │   visuals: sweep,    │
    │   trails, etc.)      │
    └───────────┬──────────┘
                │
                ▼
    ┌──────────────────────┐
    │    layout.py         │
    │  (Adds "SIMULATION"  │
    │   labels)           │
    └──────────────────────┘
                │
                ▼
         Streamlit UI
         (Labeled as Simulation)
```

### Shadow Mode Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
│  st.session_state.shadow_mode = True                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
    ┌──────────────────────┐
    │   state_manager.py   │
    │  Detects shadow_mode │
    └───────────┬───────────┘
                │
                ├──────────────────────┐
                │                      │
                ▼                      ▼
    ┌──────────────────┐    ┌──────────────────────┐
    │  Real Data       │    │ simulation_engine.py│
    │  (Backend)       │    │  (Synthetic Data)    │
    └─────────┬────────┘    └──────────┬───────────┘
              │                        │
              │                        │
              └──────────┬─────────────┘
                         │
                         │ Merge (real + simulation overlay)
                         │
                         ▼
              ┌──────────────────────┐
              │ visual_components.py  │
              │  (Shows both)        │
              └───────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │    layout.py          │
              │  (Adds "SHADOW"       │
              │   indicators)        │
              └──────────────────────┘
                         │
                         ▼
                  Streamlit UI
                  (Real + Shadow Overlay)
```

### Trajectory Prediction Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
│  Gets track data from state_manager                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
    ┌──────────────────────┐
    │  tracking_engine.py  │
    │  (Trajectory Logic)  │
    └───────────┬───────────┘
                │
                ├──────────────────────────────┐
                │                              │
                ▼                              ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │ predict_trajectory()  │    │ interpolate_position│
    │  (Future positions)   │    │  (Time-based)       │
    └───────────┬───────────┘    └──────────────────────┘
                │
                │ Returns predicted positions
                │
                ▼
    ┌──────────────────────┐
    │trajectory_tracking.py│
    │  (Visualization)     │
    └───────────┬───────────┘
                │
                │ Creates Plotly figure
                │ (History + Prediction)
                │
                ▼
         Streamlit UI
```

### Engagement Sequence Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
│  Selects track for engagement visualization                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──────────────────────┐
                 │                      │
                 ▼                      ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │  Track Data          │  │interception_simulation│
    │  (From state_manager)│  │  (Feasibility)       │
    └───────────┬──────────┘  └──────────┬───────────┘
                │                        │
                │                        │
                └──────────┬─────────────┘
                           │
                           ▼
              ┌──────────────────────┐
              │engagement_visualization│
              │  (Creates sequence)  │
              └───────────┬───────────┘
                         │
                         │ Creates Plotly 3D figure
                         │ (Target + Interceptor trajectories)
                         │
                         ▼
                  Streamlit UI
```

## Module Interaction Matrix

| Module | Imports From | Used By |
|--------|-------------|---------|
| `app.py` | All dashboard modules | Entry point |
| `layout.py` | `streamlit` only | `app.py` |
| `state_manager.py` | `simulation_engine.py`, `tracking_engine.py`, backend modules | `app.py` |
| `visual_components.py` | `plotly`, specialized visualization modules | `app.py` |
| `simulation_engine.py` | Domain models, `math`, `datetime` | `state_manager.py` |
| `tracking_engine.py` | Domain models, `interception_simulation` | `state_manager.py`, visualization modules |
| `battlespace_3d.py` | `plotly`, `visual_components.py` (theme) | `app.py` |
| `engagement_visualization.py` | `plotly`, `interception_simulation` | `app.py` |
| `trajectory_tracking.py` | `plotly`, `tracking_engine.py` | `app.py` |
| `interception_window.py` | `plotly`, `interception_simulation` | `app.py` |
| `atmospheric_modeling.py` | `math`, domain models | `app.py` |

## Session State Structure

```python
# Mode Flags
st.session_state.training_mode = False      # Tier 2+
st.session_state.shadow_mode = False        # Tier 2+
st.session_state.audio_enabled = False      # Tier 4

# UI Preferences
st.session_state.show_confidence_rings = True   # Tier 4
st.session_state.show_protected_zones = True    # Tier 4
st.session_state.auto_refresh = True            # Tier 4
st.session_state.refresh_interval = 0.5         # Tier 4

# Simulation State (Training Mode)
st.session_state.simulation_tracks = []          # Tier 2+
st.session_state.simulation_initialized = False  # Tier 2+
st.session_state.simulation_last_update = None   # Tier 2+

# Tracking State
st.session_state.track_history = {}             # Tier 3+
st.session_state.last_update_time = None         # Tier 4

# Animation State
st.session_state.animation_start_time = None     # Tier 4
st.session_state.previous_confidence_values = {} # Tier 4
```

## Data Structure Flow

### Track Data Structure
```python
{
    'track_id': str,
    'object_type': 'AIRCRAFT' | 'AERIAL_DRONE' | 'UNKNOWN_OBJECT',
    'position': {'x': float, 'y': float, 'z': float},
    'velocity': {'vx': float, 'vy': float, 'vz': float},
    'confidence': float,
    'threat_level': 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH',
    'timestamp': datetime,
    'is_simulation': bool,  # Added by simulation_engine
    'simulation_label': str  # Added by simulation_engine
}
```

### Flow Through Modules
```
simulation_engine.py
    └─> Generates track dict
        └─> state_manager.py
            └─> Stores in session_state.simulation_tracks
                └─> Returns to app.py
                    └─> Passes to visual_components.py
                        └─> Creates Plotly figure
                            └─> Returns to app.py
                                └─> Renders with layout.py helpers
```

## Mode Detection Logic

### In state_manager.py
```python
def get_tracking_data():
    training_mode = st.session_state.get('training_mode', False)
    shadow_mode = st.session_state.get('shadow_mode', False)
    
    if training_mode:
        # Pure simulation
        return simulation_engine.generate_tracking_data(...)
    elif shadow_mode:
        # Real + simulation overlay
        real_data = fetch_real_data()
        sim_data = simulation_engine.generate_tracking_data(...)
        return merge_shadow_data(real_data, sim_data)
    else:
        # Real-world mode
        return fetch_real_data()
```

### In visual_components.py
```python
def create_2d_visualization(tracks, training_mode=False, ...):
    # Common visualization
    add_tracks(fig, tracks)
    
    if training_mode:
        # Add simulation-specific visuals
        add_radar_sweep(fig)
        add_trajectory_trails(fig, tracks)
        add_simulation_labels(fig)
```

### In layout.py
```python
def render_operational_context(..., training_mode=False, is_simulation=False):
    # Common UI
    st.markdown(f"### {headline}")
    st.markdown(message)
    
    if training_mode or is_simulation:
        # Add simulation label
        st.info("SIMULATION / TRAINING DATA — Advisory Only")
```

---

**Last Updated**: 2024  
**Version**: 1.0.0
