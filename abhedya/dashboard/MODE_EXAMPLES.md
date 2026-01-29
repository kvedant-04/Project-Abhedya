# Training, Simulation, and Shadow Mode - Implementation Examples

## Session State Keys

```python
# In app.py session state initialization
if "training_mode" not in st.session_state:
    st.session_state.training_mode = False

if "shadow_mode" not in st.session_state:
    st.session_state.shadow_mode = False

# Additional mode-related state
if "audio_enabled" not in st.session_state:
    st.session_state.audio_enabled = False

# Simulation state (managed by state_manager)
if "simulation_tracks" not in st.session_state:
    st.session_state.simulation_tracks = []
if "simulation_initialized" not in st.session_state:
    st.session_state.simulation_initialized = False
```

## Example UI Banner

```python
# In layout.py
@staticmethod
def render_mode_awareness_banner():
    """
    Always-visible Mode Awareness Banner.
    
    Shows current operational mode (Live, Training, or Shadow).
    Must be visible at all times to ensure operator awareness.
    """
    training_mode = st.session_state.get("training_mode", False)
    shadow_mode = st.session_state.get("shadow_mode", False)
    
    if training_mode:
        # Training/Simulation Mode - Red banner
        st.markdown(
            """
            <div style="
                background:#FFF1F0;
                border-left:5px solid #F5222D;
                padding:12px;
                margin-bottom:14px;
                border-radius:4px;
                position:sticky;
                top:0;
                z-index:1000;
            ">
                <strong>⚠️ TRAINING & SIMULATION MODE ACTIVE</strong><br>
                <small>
                    <strong>SIMULATION / TRAINING DATA</strong> — All displayed data is synthetic.<br>
                    Advisory-only system. No autonomous actions. Confidence values are advisory only.
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif shadow_mode:
        # Shadow Mode - Amber banner
        st.markdown(
            """
            <div style="
                background:#FFF7E6;
                border-left:5px solid #FAAD14;
                padding:12px;
                margin-bottom:14px;
                border-radius:4px;
                position:sticky;
                top:0;
                z-index:1000;
            ">
                <strong>🔍 SHADOW MODE ACTIVE</strong><br>
                <small>
                    Live data with simulation overlay for comparison.<br>
                    Advisory-only system. No autonomous actions. Confidence values are advisory only.
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Live Mode - Blue banner
        st.markdown(
            """
            <div style="
                background:#E6F7FF;
                border-left:5px solid #4A90E2;
                padding:12px;
                margin-bottom:14px;
                border-radius:4px;
                position:sticky;
                top:0;
                z-index:1000;
            ">
                <strong>📡 LIVE MODE</strong><br>
                <small>
                    Operating with live data sources.<br>
                    Advisory-only system. No autonomous actions. Confidence values are advisory only.
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )
```

## Example Mode Switch Logic

```python
# In app.py sidebar
with st.sidebar:
    st.subheader("Operational Mode")
    
    # Training & Simulation Mode Toggle
    training_mode = st.checkbox(
        "Enable Training & Simulation Mode",
        value=st.session_state.get("training_mode", False),
        key="training_mode",
        help="Enables synthetic data for training and simulation. All data clearly labeled as SIMULATION / TRAINING DATA."
    )
    
    # Shadow Mode Toggle (only if training mode is off)
    if not training_mode:
        shadow_mode = st.checkbox(
            "Enable Shadow Mode",
            value=st.session_state.get("shadow_mode", False),
            key="shadow_mode",
            help="Mirrors live logic using synthetic inputs. Shows live data with simulation overlay for comparison."
        )
    else:
        # Training mode takes precedence - disable shadow mode
        if st.session_state.get("shadow_mode", False):
            st.session_state.shadow_mode = False
        shadow_mode = False
    
    # Mode conflict prevention
    if training_mode and shadow_mode:
        st.session_state.shadow_mode = False
        shadow_mode = False
    
    # Mode status display
    if training_mode:
        st.info("⚠️ Training & Simulation Mode Active — Synthetic data enabled")
    elif shadow_mode:
        st.info("🔍 Shadow Mode Active — Live data with simulation overlay")
    else:
        st.info("📡 Live Mode — Operating with live data sources")
```

## Example Unified Data Provider Usage

```python
# In state_manager.py - BEFORE (with branching duplication):
def get_tracking_data():
    if DashboardStateManager.is_training_mode():
        # Generate simulation data
        from abhedya.simulation.training_data_generator import get_training_generator
        generator = get_training_generator()
        return generator.generate_tracking_data(...)
    else:
        # Get live data
        from abhedya.dashboard.live_stub_provider import LiveStubProvider
        return LiveStubProvider.get_tracking_data()

# In state_manager.py - AFTER (unified, no duplication):
def get_tracking_data():
    from abhedya.dashboard.data_provider import UnifiedDataProvider
    return UnifiedDataProvider.get_tracking_data()
    # UnifiedDataProvider handles all mode detection internally
```

## Example Data Provider Implementation

```python
# In data_provider.py
class UnifiedDataProvider:
    @staticmethod
    def get_tracking_data() -> List[Dict[str, Any]]:
        """
        Get tracking data from appropriate source based on mode.
        
        NO branching logic duplication - single method handles all modes.
        """
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            # Pure simulation mode
            return UnifiedDataProvider._get_simulation_tracking_data()
        elif shadow_mode:
            # Shadow mode: merge live + simulation
            return UnifiedDataProvider._get_shadow_tracking_data()
        else:
            # Live mode: use live stub provider
            return UnifiedDataProvider._get_live_tracking_data()
    
    @staticmethod
    def _get_simulation_tracking_data() -> List[Dict[str, Any]]:
        """Get tracking data from simulation engine."""
        from abhedya.simulation.training_data_generator import get_training_generator
        generator = get_training_generator()
        time_offset = generator.get_time_offset()
        return generator.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset)
    
    @staticmethod
    def _get_shadow_tracking_data() -> List[Dict[str, Any]]:
        """Get shadow mode tracking data (live + simulation overlay)."""
        from abhedya.dashboard.live_stub_provider import LiveStubProvider
        from abhedya.simulation.training_data_generator import get_training_generator
        
        # Get live data
        live_data = LiveStubProvider.get_tracking_data()
        
        # Get simulation data
        generator = get_training_generator()
        time_offset = generator.get_time_offset()
        sim_data = generator.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset)
        
        # Merge: live data first, then simulation overlay
        merged = list(live_data) if live_data else []
        
        # Add simulation tracks with shadow label
        for track in sim_data:
            if isinstance(track, dict):
                track = track.copy()
                track['is_shadow'] = True
                track['shadow_label'] = 'SHADOW MODE — Simulation Overlay'
                merged.append(track)
        
        return merged
    
    @staticmethod
    def _get_live_tracking_data() -> List[Dict[str, Any]]:
        """Get live tracking data."""
        from abhedya.dashboard.live_stub_provider import LiveStubProvider
        return LiveStubProvider.get_tracking_data()
```

## Example: Using Unified Provider in State Manager

```python
# In state_manager.py
@staticmethod
def get_early_warning_data() -> Optional[Dict[str, Any]]:
    """
    Get early warning system data.
    
    Uses unified data provider to eliminate branching logic duplication.
    """
    try:
        from abhedya.dashboard.data_provider import UnifiedDataProvider
        return UnifiedDataProvider.get_early_warning_data()
    except Exception:
        # Fail-safe default
        return {
            'warning_state': 'NORMAL',
            'confidence': 0.0,
            'reasoning': [],
            'is_simulation': False,
            'simulation_label': 'MONITORING ONLY'
        }
```

## Example: Mode-Aware UI Rendering

```python
# In app.py tab rendering
with tab1:
    # Get data (mode-aware routing handled internally)
    data = DashboardStateManager.get_tracking_data()
    
    # Render mode awareness banner (always visible)
    DashboardLayout.render_mode_awareness_banner()
    
    # Render operational context (mode-aware)
    training_mode = st.session_state.get("training_mode", False)
    shadow_mode = st.session_state.get("shadow_mode", False)
    is_simulation = training_mode or shadow_mode
    
    DashboardLayout.render_operational_context(
        "Airspace Overview",
        "Monitoring airspace for track activity.",
        training_mode,
        is_simulation
    )
    
    # Render visualization (mode-aware)
    fig = AirspaceVisualization.create_2d_visualization(
        data,
        training_mode=training_mode,
        ...
    )
    st.plotly_chart(fig)
```

## Key Implementation Points

### 1. No Branching Logic Duplication
- **Before**: Each data fetching method had `if training_mode: ... else: ...`
- **After**: Single `UnifiedDataProvider` handles all mode routing
- **Benefit**: Changes to mode logic only need to be made in one place

### 2. Same Processing Pipeline
- All modes use the same visualization components
- All modes use the same UI helpers
- Only data source changes, not processing logic

### 3. Always-Visible Mode Banner
- Banner appears at top of every tab
- Color-coded by mode (Red=Training, Amber=Shadow, Blue=Live)
- Sticky positioning ensures visibility

### 4. Clear Labeling
- All simulation data includes `is_simulation=True`
- All simulation data includes `simulation_label` field
- UI components check these flags for visual indicators

### 5. Mode Conflict Prevention
- Training mode takes precedence over shadow mode
- If training_mode enabled, shadow_mode automatically disabled
- UI prevents enabling both simultaneously

---

**Last Updated**: 2024  
**Version**: 1.0.0
