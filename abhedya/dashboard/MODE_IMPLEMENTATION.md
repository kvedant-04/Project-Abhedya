# Training, Simulation, and Shadow Mode Implementation

## Overview

Unified mode system with no branching logic duplication. All modes use the same processing pipeline with mode-aware data providers.

## Modes

### 1. Live Mode (Default)
- **Flag**: `training_mode = False`, `shadow_mode = False`
- **Data Source**: `LiveStubProvider` (safe placeholder)
- **Behavior**: Returns empty/minimal data structures
- **Labeling**: No simulation labels

### 2. Training & Simulation Mode
- **Flag**: `training_mode = True`
- **Data Source**: `simulation_engine` (synthetic data)
- **Behavior**: Generates realistic synthetic data
- **Labeling**: All data labeled as "SIMULATION / TRAINING DATA"

### 3. Shadow Mode
- **Flag**: `shadow_mode = True` (training_mode must be False)
- **Data Source**: Merged live + simulation data
- **Behavior**: Mirrors live logic using synthetic inputs as overlay
- **Labeling**: Live data + "SHADOW MODE — Simulation Overlay" labels

## Session State Keys

```python
# Mode Flags
st.session_state.training_mode = False      # Training & Simulation Mode
st.session_state.shadow_mode = False        # Shadow Mode (overlay simulation on live)

# Mode Conflict Prevention
# - If training_mode = True, shadow_mode is automatically False
# - If shadow_mode = True, training_mode must be False
```

## Unified Data Provider Pattern

### Architecture
```
app.py
  └─> state_manager.py.get_tracking_data()
      └─> UnifiedDataProvider.get_tracking_data()
          ├─> Checks training_mode
          ├─> Checks shadow_mode
          └─> Routes to appropriate source:
              ├─> Training: simulation_engine
              ├─> Shadow: merge(live_stub_provider + simulation_engine)
              └─> Live: live_stub_provider
```

### Example: Mode Switch Logic

```python
# In app.py sidebar
training_mode = st.checkbox("Enable Training & Simulation Mode", ...)
shadow_mode = st.checkbox("Enable Shadow Mode", ...) if not training_mode else False

# Mode conflict prevention
if training_mode and shadow_mode:
    st.session_state.shadow_mode = False
    shadow_mode = False
```

### Example: Data Fetching (No Branching Duplication)

```python
# In state_manager.py - BEFORE (with duplication):
def get_tracking_data():
    if training_mode:
        return simulation_engine.generate_tracking_data()
    else:
        return live_provider.get_tracking_data()

# In state_manager.py - AFTER (unified):
def get_tracking_data():
    from abhedya.dashboard.data_provider import UnifiedDataProvider
    return UnifiedDataProvider.get_tracking_data()
    # UnifiedDataProvider handles all mode detection internally
```

## UI Requirements

### Always-Visible Mode Awareness Banner

```python
# In layout.py
@staticmethod
def render_mode_awareness_banner():
    training_mode = st.session_state.get("training_mode", False)
    shadow_mode = st.session_state.get("shadow_mode", False)
    
    if training_mode:
        # Red banner: "TRAINING & SIMULATION MODE ACTIVE"
        # Shows: "SIMULATION / TRAINING DATA — All displayed data is synthetic"
    elif shadow_mode:
        # Amber banner: "SHADOW MODE ACTIVE"
        # Shows: "Live data with simulation overlay for comparison"
    else:
        # Blue banner: "LIVE MODE"
        # Shows: "Operating with live data sources"
```

### Clear Simulation Labeling

All data from simulation/shadow modes includes:
- `is_simulation: True` flag
- `simulation_label: "SIMULATION / TRAINING DATA"` or `"SHADOW MODE — Simulation Overlay"`
- Visual indicators in UI (banners, labels, badges)

### Confidence Values (Advisory Only)

All confidence values displayed with disclaimer:
- "Confidence values are advisory only"
- No autonomous decisions based on confidence
- Human-in-the-loop required

## Implementation Files

### `live_stub_provider.py`
- Safe placeholder for live data
- Returns empty/minimal data structures
- No external connections
- Fail-safe defaults

### `data_provider.py`
- Unified data provider interface
- Mode detection and routing
- Eliminates branching logic duplication
- Single source of truth for data fetching

### `state_manager.py`
- Updated to use `UnifiedDataProvider`
- All data fetching methods route through unified provider
- No mode-specific branching in public methods

### `layout.py`
- `render_mode_awareness_banner()` - Always-visible mode indicator
- Mode-aware UI rendering
- Clear simulation labeling

### `app.py`
- Mode toggle controls in sidebar
- Mode conflict prevention
- Calls `render_mode_awareness_banner()`

## Data Flow Examples

### Training Mode Flow
```
User enables training_mode
  └─> app.py: st.session_state.training_mode = True
      └─> state_manager.get_tracking_data()
          └─> UnifiedDataProvider.get_tracking_data()
              └─> Detects training_mode = True
                  └─> Calls simulation_engine.generate_tracking_data()
                      └─> Returns synthetic tracks with is_simulation=True
                          └─> app.py renders with "SIMULATION" labels
```

### Shadow Mode Flow
```
User enables shadow_mode (training_mode = False)
  └─> app.py: st.session_state.shadow_mode = True
      └─> state_manager.get_tracking_data()
          └─> UnifiedDataProvider.get_tracking_data()
              └─> Detects shadow_mode = True
                  ├─> Calls live_stub_provider.get_tracking_data() (live)
                  └─> Calls simulation_engine.generate_tracking_data() (overlay)
                      └─> Merges both with shadow labels
                          └─> app.py renders with "SHADOW MODE" indicators
```

### Live Mode Flow
```
Default state (training_mode = False, shadow_mode = False)
  └─> app.py: No mode flags set
      └─> state_manager.get_tracking_data()
          └─> UnifiedDataProvider.get_tracking_data()
              └─> Detects both modes = False
                  └─> Calls live_stub_provider.get_tracking_data()
                      └─> Returns empty/minimal data
                          └─> app.py shows "Insufficient Data" message
```

## Safety Guarantees

### NO Autonomous Decisions
- All modes are advisory only
- No control logic in any mode
- Human-in-the-loop required

### NO Background Threads
- All processing in main Streamlit thread
- No async operations
- Synchronous data fetching only

### NO JS Timers
- No client-side JavaScript timers
- No auto-refresh via JS
- All updates via Streamlit reruns (if auto-refresh enabled)

### Mode Isolation
- Training mode: Pure simulation, clearly labeled
- Shadow mode: Live + simulation overlay, clearly labeled
- Live mode: Real data only, no simulation artifacts

## Testing

### Mode Switching
1. Enable training_mode → Verify simulation data appears
2. Disable training_mode → Verify returns to live mode
3. Enable shadow_mode → Verify merged data appears
4. Enable training_mode while shadow_mode active → Verify shadow_mode disabled

### Data Labeling
1. Training mode → All data has `is_simulation=True`
2. Shadow mode → Live data has `is_shadow=False`, simulation has `is_shadow=True`
3. Live mode → No simulation labels

### UI Banners
1. Training mode → Red banner visible
2. Shadow mode → Amber banner visible
3. Live mode → Blue banner visible

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Status**: Implementation Complete
