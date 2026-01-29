# SAM C2 Dashboard Architecture

## Overview

Professional, defence-grade SAM Command & Control dashboard with tiered feature implementation. All features are **ADVISORY ONLY** - visualization and simulation only, no control logic or autonomous actions.

## Tier System

### Tier 1: FULL SYSTEM (All Factors Enabled)
- Complete feature set
- All visualization modes
- Full simulation engine
- Comprehensive tracking
- Full UI/HMI polish
- Logging and replay
- Confidence visualization

### Tier 2: Core Visualization
- Engagement Sequence Visualization
- Training/Simulation/Shadow Mode
- Basic 3D battlespace
- Track visualization

### Tier 3: Advanced Visualization
- Full 3D Battlespace Visualization
- Atmospheric Modeling
- Trajectory prediction
- Interception windows

### Tier 4: UI/HMI & Analytics
- Full UI/HMI polish
- Logging and audit
- Replay functionality
- Confidence visualization
- Operational context panels

## Folder Structure

```
abhedya/dashboard/
├── __init__.py                    # Module exports
├── app.py                         # Main Streamlit app (tab orchestration)
├── layout.py                      # ALL UI helpers (single source of truth)
├── visual_components.py           # Plots, radar, 3D scenes
├── simulation_engine.py           # Synthetic data generation
├── tracking_engine.py             # Trajectory & prediction
├── state_manager.py               # Session state & data fetching
├── effects_controller.py          # Audio/visual effects
├── battlespace_3d.py              # 3D battlespace visualization
├── engagement_visualization.py    # Engagement sequence visualization
├── trajectory_tracking.py         # Trajectory history & prediction
├── interception_window.py         # Interception window visualization
├── atmospheric_modeling.py        # Atmospheric effects modeling
├── README.md                      # Dashboard documentation
├── ARCHITECTURE.md                # This file
└── SAM_C2_IMPLEMENTATION.md       # SAM C2 feature documentation
```

## File Responsibilities

### `app.py` - Main Application (Tab Orchestration)
**Purpose**: Entry point and tab orchestration only. No UI rendering logic.

**Responsibilities**:
- Streamlit page configuration
- Session state initialization
- Tab creation and routing
- Import orchestration (fail-safe)
- Mode flag management (`training_mode`, `shadow_mode`, etc.)
- Tab-to-component routing

**Dependencies**:
- `layout.py` (UI helpers)
- `state_manager.py` (data fetching)
- `visual_components.py` (visualizations)
- `simulation_engine.py` (synthetic data)
- `tracking_engine.py` (trajectory)

**Key Patterns**:
```python
# Tab structure
with tab1:
    data = DashboardStateManager.get_tracking_data()
    DashboardLayout.render_operational_context(...)
    fig = AirspaceVisualization.create_2d_visualization(...)
    st.plotly_chart(fig)
```

**NO**:
- Direct UI rendering (use `layout.py`)
- Data processing (use `state_manager.py`)
- Visualization creation (use `visual_components.py`)

---

### `layout.py` - UI Helpers (Single Source of Truth)
**Purpose**: ALL UI rendering helpers. Single source of truth for UI components.

**Responsibilities**:
- Operational context panels
- Intelligence narrative blocks
- Advisory panels
- Training mode indicators
- Data freshness indicators
- Insufficient data messages
- Banner rendering
- Metric displays
- Status cards
- All Streamlit UI primitives

**Key Methods**:
```python
class DashboardLayout:
    @staticmethod
    def render_operational_context(headline, message, training_mode, is_simulation)
    @staticmethod
    def render_intelligence_narrative(narrative_text, confidence)
    @staticmethod
    def render_advisory_panel(title, state, confidence, reasoning, training_mode, is_simulation)
    @staticmethod
    def render_training_mode_indicator()
    @staticmethod
    def render_data_freshness(training_mode)
    @staticmethod
    def render_insufficient_data_message(context)
```

**Dependencies**:
- `streamlit` only
- No business logic
- No data processing

**NO**:
- Business logic
- Data processing
- Visualization creation
- State management

---

### `visual_components.py` - Visualization Components
**Purpose**: All visualization creation (2D, 3D, radar, plots).

**Responsibilities**:
- 2D airspace visualization
- 3D battlespace visualization (or delegates to `battlespace_3d.py`)
- Radar sweep visualization
- Confidence gauges
- Trend plots
- Severity theme controller
- Chart configuration

**Key Classes**:
```python
class AirspaceVisualization:
    @staticmethod
    def create_2d_visualization(tracks, ...) -> go.Figure

class SeverityThemeController:
    @staticmethod
    def get_theme(severity, training_mode) -> Dict[str, str]

class ConfidenceGauge:
    @staticmethod
    def render(value, label, ...)

class TrendPlot:
    @staticmethod
    def create_plot(data, ...) -> go.Figure
```

**Dependencies**:
- `plotly.graph_objects`
- `plotly.express`
- `streamlit` (for session state access only)
- `battlespace_3d.py` (for 3D scenes)

**NO**:
- UI layout (use `layout.py`)
- Data fetching (use `state_manager.py`)
- Business logic

---

### `simulation_engine.py` - Synthetic Data Generation
**Purpose**: Generate realistic synthetic data for training/simulation/shadow modes.

**Responsibilities**:
- Track generation (position, velocity, classification)
- Early warning data generation
- EW analysis data generation
- Cybersecurity data generation
- Threat assessment data generation
- Intent inference data generation
- Advisory state generation
- Deterministic seed-based generation

**Key Methods**:
```python
class SimulationEngine:
    @staticmethod
    def generate_tracking_data(num_tracks, seed, time_offset) -> List[Dict]
    @staticmethod
    def generate_early_warning_data(tracks, seed) -> Dict
    @staticmethod
    def generate_ew_analysis_data(seed) -> Dict
    @staticmethod
    def generate_cybersecurity_data(seed) -> Dict
    @staticmethod
    def update_tracks(tracks, time_delta) -> List[Dict]
```

**Dependencies**:
- `datetime`
- `random` (with seed control)
- `math`
- Domain models (Coordinates, Velocity, etc.)

**NO**:
- UI rendering
- State management
- Visualization

---

### `tracking_engine.py` - Trajectory & Prediction
**Purpose**: Trajectory analysis, prediction, and history management.

**Responsibilities**:
- Trajectory prediction (constant velocity, constant acceleration models)
- Trajectory history storage
- Position interpolation
- Velocity estimation
- Time-to-intercept calculation
- Closest approach calculation
- Trajectory smoothing

**Key Methods**:
```python
class TrackingEngine:
    @staticmethod
    def predict_trajectory(track, time_horizon_seconds) -> List[Dict]
    @staticmethod
    def interpolate_position(track, target_time) -> Dict
    @staticmethod
    def calculate_time_to_intercept(track, defender_position) -> float
    @staticmethod
    def calculate_closest_approach(track, defender_position) -> Dict
    @staticmethod
    def update_trajectory_history(track_id, position, timestamp)
```

**Dependencies**:
- `datetime`
- `math`
- Domain models
- `interception_simulation` (for feasibility)

**NO**:
- UI rendering
- Data generation
- State management

---

### `state_manager.py` - Session State & Data Fetching
**Purpose**: Centralized state management and data fetching with mode-aware routing.

**Responsibilities**:
- Session state initialization
- Mode flag management (`training_mode`, `shadow_mode`)
- Data fetching with mode-aware routing
- Simulation state persistence
- Track history management
- Last update time tracking

**Key Methods**:
```python
class DashboardStateManager:
    @staticmethod
    def initialize_session_state()
    @staticmethod
    def get_tracking_data() -> Optional[List[Dict]]
    @staticmethod
    def get_early_warning_data() -> Optional[Dict]
    @staticmethod
    def get_ew_analysis_data() -> Optional[Dict]
    @staticmethod
    def get_cybersecurity_data() -> Optional[Dict]
    @staticmethod
    def get_threat_assessment_data() -> Optional[Dict]
    @staticmethod
    def get_advisory_state() -> Optional[Dict]
    @staticmethod
    def is_training_mode() -> bool
    @staticmethod
    def is_shadow_mode() -> bool
```

**Data Flow Logic**:
```python
def get_tracking_data():
    if is_training_mode():
        return simulation_engine.generate_tracking_data(...)
    elif is_shadow_mode():
        # Shadow mode: use real data but overlay simulation
        real_data = fetch_real_tracking_data()
        sim_data = simulation_engine.generate_tracking_data(...)
        return merge_shadow_data(real_data, sim_data)
    else:
        return fetch_real_tracking_data()
```

**Dependencies**:
- `streamlit` (session state)
- `simulation_engine.py`
- `tracking_engine.py`
- Backend modules (early_warning, ew_analysis, etc.)

**NO**:
- UI rendering
- Visualization creation
- Business logic

---

### `effects_controller.py` - Audio/Visual Effects
**Purpose**: Audio and visual effects controller (advisory only).

**Responsibilities**:
- Audio alert management
- Visual severity theming
- Effect state management
- User preference handling

**Key Methods**:
```python
class EffectsController:
    @staticmethod
    def play_audio_alert(severity, training_mode)
    @staticmethod
    def apply_visual_theme(severity, training_mode)
    @staticmethod
    def is_audio_enabled() -> bool
```

**Dependencies**:
- `streamlit` (session state)
- `layout.py` (for theme application)

**NO**:
- Data processing
- Visualization creation

---

### Specialized Visualization Modules

#### `battlespace_3d.py`
**Purpose**: 3D battlespace visualization.

**Dependencies**: `plotly.graph_objects`, `visual_components.py` (for theme)

#### `engagement_visualization.py`
**Purpose**: Engagement sequence visualization.

**Dependencies**: `plotly.graph_objects`, `interception_simulation`

#### `trajectory_tracking.py`
**Purpose**: Trajectory history and prediction visualization.

**Dependencies**: `plotly.graph_objects`, `tracking_engine.py`

#### `interception_window.py`
**Purpose**: Interception window visualization.

**Dependencies**: `plotly.graph_objects`, `interception_simulation`

#### `atmospheric_modeling.py`
**Purpose**: Atmospheric effects modeling.

**Dependencies**: `math`, domain models

## Data Flow

### Standard Flow (Real-World Mode)
```
1. app.py
   └─> Calls DashboardStateManager.get_tracking_data()
       └─> Fetches from backend modules (tracking, early_warning, etc.)
           └─> Returns data to app.py
               └─> app.py calls visual_components.py
                   └─> Creates Plotly figure
                       └─> app.py calls layout.py for UI helpers
                           └─> Renders complete tab
```

### Training/Simulation Mode Flow
```
1. app.py
   └─> Checks st.session_state.training_mode
       └─> Calls DashboardStateManager.get_tracking_data()
           └─> Detects training_mode = True
               └─> Calls simulation_engine.py.generate_tracking_data()
                   └─> Returns synthetic data
                       └─> app.py calls visual_components.py
                           └─> Creates Plotly figure with simulation data
                               └─> app.py calls layout.py
                                   └─> Renders with "SIMULATION" labels
```

### Shadow Mode Flow
```
1. app.py
   └─> Checks st.session_state.shadow_mode
       └─> Calls DashboardStateManager.get_tracking_data()
           └─> Detects shadow_mode = True
               └─> Fetches real data AND generates simulation data
                   └─> Merges both (real + overlay simulation)
                       └─> Returns merged data
                           └─> app.py renders with shadow indicators
```

### Trajectory Prediction Flow
```
1. app.py
   └─> Gets track data
       └─> Calls tracking_engine.py.predict_trajectory()
           └─> Returns predicted positions
               └─> app.py calls trajectory_tracking.py
                   └─> Creates visualization with history + prediction
```

## Mode Control via Session State

### Mode Flags
```python
# In app.py session state initialization
st.session_state.training_mode = False      # Tier 2+
st.session_state.shadow_mode = False        # Tier 2+
st.session_state.audio_enabled = False      # Tier 4
st.session_state.show_confidence_rings = True  # Tier 4
st.session_state.show_protected_zones = True   # Tier 4
st.session_state.auto_refresh = True        # Tier 4
```

### Mode-Aware Data Fetching
```python
# In state_manager.py
def get_tracking_data():
    if st.session_state.get('training_mode', False):
        return simulation_engine.generate_tracking_data(...)
    elif st.session_state.get('shadow_mode', False):
        real_data = fetch_real_data()
        sim_data = simulation_engine.generate_tracking_data(...)
        return merge_shadow(real_data, sim_data)
    else:
        return fetch_real_data()
```

### Mode-Aware Visualization
```python
# In visual_components.py
def create_2d_visualization(tracks, training_mode=False, ...):
    if training_mode:
        # Add simulation-specific visuals (radar sweep, trails)
        add_radar_sweep(fig)
        add_trajectory_trails(fig, tracks)
    # Common visualization
    add_tracks(fig, tracks)
```

## Import Structure (No Circular Dependencies)

### Import Hierarchy
```
app.py
├── layout.py (UI helpers only)
├── state_manager.py
│   ├── simulation_engine.py
│   └── tracking_engine.py
└── visual_components.py
    ├── battlespace_3d.py
    ├── engagement_visualization.py
    ├── trajectory_tracking.py
    ├── interception_window.py
    └── atmospheric_modeling.py
```

### Import Rules
1. **app.py** imports everything (orchestrator)
2. **layout.py** imports only `streamlit` (UI only)
3. **visual_components.py** imports `plotly` and specialized modules
4. **state_manager.py** imports `simulation_engine.py` and `tracking_engine.py`
5. **simulation_engine.py** imports domain models only
6. **tracking_engine.py** imports domain models and `interception_simulation`

### Avoiding Circular Imports
- **layout.py** never imports `app.py` or `state_manager.py`
- **visual_components.py** never imports `app.py` or `state_manager.py`
- **simulation_engine.py** never imports dashboard modules
- **tracking_engine.py** never imports dashboard modules
- All modules import from `abhedya.*` backend modules, not dashboard modules

## Tier Implementation Mapping

### Tier 1: FULL SYSTEM
- ✅ All files implemented
- ✅ All visualization modes
- ✅ Full simulation engine
- ✅ Complete tracking engine
- ✅ Full UI/HMI polish
- ✅ Logging and replay
- ✅ Confidence visualization

### Tier 2: Core Visualization
**Required Files**:
- `app.py` (basic tabs)
- `layout.py` (basic UI helpers)
- `visual_components.py` (2D visualization only)
- `simulation_engine.py` (basic track generation)
- `state_manager.py` (mode-aware routing)

**Features**:
- Engagement Sequence Visualization (basic)
- Training/Simulation Mode
- Basic 3D battlespace
- Track visualization

### Tier 3: Advanced Visualization
**Additional Files**:
- `battlespace_3d.py`
- `engagement_visualization.py`
- `trajectory_tracking.py`
- `interception_window.py`
- `atmospheric_modeling.py`
- `tracking_engine.py` (full implementation)

**Features**:
- Full 3D Battlespace Visualization
- Atmospheric Modeling
- Trajectory prediction
- Interception windows

### Tier 4: UI/HMI & Analytics
**Additional Features**:
- Full `layout.py` implementation (all UI helpers)
- `effects_controller.py` (audio/visual effects)
- Logging integration
- Replay functionality
- Confidence visualization
- Operational context panels

## Error Handling Strategy

### Fail-Safe Pattern
```python
# In app.py
try:
    from abhedya.dashboard.layout import DashboardLayout
except Exception as e:
    st.error(f"Dashboard initialization error: {e}")
    DashboardLayout = None

# Usage
if DashboardLayout:
    DashboardLayout.render_operational_context(...)
else:
    st.info("UI components unavailable")
```

### Defensive UI Helpers
```python
# In layout.py
@staticmethod
def render_operational_context(...):
    try:
        # UI rendering
    except Exception:
        # Best-effort fallback
        st.write("Operational context unavailable")
```

## Testing Strategy

### Unit Tests
- `simulation_engine.py`: Test data generation
- `tracking_engine.py`: Test trajectory calculations
- `atmospheric_modeling.py`: Test atmospheric calculations

### Integration Tests
- `state_manager.py`: Test mode-aware routing
- `visual_components.py`: Test visualization creation

### UI Tests
- `layout.py`: Test UI helper rendering
- `app.py`: Test tab orchestration

## Performance Considerations

### Lazy Loading
- Import modules only when needed
- Generate visualization data on-demand
- Cache simulation data in session state

### Session State Management
- Store large data structures in session state
- Update incrementally (don't regenerate entire state)
- Clear state on mode toggle

### Visualization Optimization
- Use Plotly's client-side animations
- Minimize server-side reruns
- Cache figure objects when possible

## Security & Safety

### Advisory-Only Guarantees
- All modules include advisory disclaimers
- No control logic in any module
- All outputs are informational only
- Human-in-the-loop enforced at UI level

### Mode Isolation
- Training mode clearly labeled
- Shadow mode clearly labeled
- Real-world mode has no simulation artifacts
- Mode flags checked at every data fetch

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Status**: Architecture Design Complete
