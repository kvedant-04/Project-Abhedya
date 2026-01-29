# Command and Control Dashboard

## Overview

The Command and Control Dashboard provides a defence-console style professional interface for the Abhedya Air Defense System.

**ADVISORY ONLY** - No autonomous actions. All outputs are advisory and require human operator review.

## Features

### Dashboard Tabs

1. **Airspace Overview**
   - 2D airspace visualization
   - Aircraft and unmanned aerial vehicle icons
   - Velocity vectors and confidence rings
   - Timeline replay (read-only)

2. **Threat & Advisory Status**
   - Advisory state display
   - Confidence indicators
   - Human acknowledgment panel (non-binding)

3. **Early Warning System**
   - State: NORMAL / ELEVATED / HIGH
   - Confidence gauge
   - Trend deviation plots
   - Reasoning panel

4. **Electronic Warfare Analysis**
   - RF spectrum visualization
   - Noise floor and entropy plots
   - Detected anomalies list

5. **Cybersecurity & System Integrity**
   - Cyber state: NORMAL / SUSPICIOUS / ALERT
   - Affected subsystem
   - Integrity status

### Visual Severity Theming

The dashboard implements a severity theme controller that maps advisory outputs to visual themes:

- **NORMAL** → Neutral (blue/grey)
- **ELEVATED** → Amber
- **HIGH** → Red
- **CRITICAL** → Dark Red (Training Mode only)

**Important**: Theme changes are UI-only and do NOT trigger any actions.

### Audio Effects (Optional)

Audio alerts are:
- Disabled by default
- Require explicit user toggle
- Use local audio files only
- Non-militaristic tones
- Stop immediately when severity lowers

Audio mapping:
- **ELEVATED** → Single soft chime
- **HIGH** → Periodic alert tone
- **CRITICAL** → Repeating training alert (Training Mode only)

All audio displays: "Audio indicators are advisory and for simulation/training visualization only."

### Training / Simulation Mode

A global toggle enables Training / Simulation Mode:

- CRITICAL severity visuals/audio only allowed when enabled
- Extreme scenarios labeled as "Simulated"
- Toggle state visible at all times

## Safety Guarantees

### What the Dashboard DOES:
- ✅ Displays advisory information
- ✅ Provides visualization of system state
- ✅ Shows confidence and uncertainty indicators
- ✅ Provides human acknowledgment controls (non-binding)
- ✅ Optional audio/visual effects (advisory indicators only)

### What the Dashboard DOES NOT Do:
- ❌ Execute autonomous actions
- ❌ Trigger weapon or engagement logic
- ❌ Provide execution authority
- ❌ Bypass human-in-the-loop requirements
- ❌ Make decisions

## UI Safety & Language Rules

- No weapon names
- No nation names
- No war language
- Uses only:
  - "High-consequence simulated threat"
  - "Strategic-level anomaly (simulation)"
- Persistent banner on all pages:
  - "Decision Support System — Advisory Only — No Autonomous Actions"

## Error Handling

- Dashboard never crashes
- Missing data → shows "Insufficient Data — Monitoring Only"
- All backend calls wrapped in try/except
- No blocking loops
- No recomputation

## Usage

### Running the Dashboard

```bash
streamlit run abhedya/dashboard/app.py
```

### Configuration

The dashboard reads data from:
- `abhedya.early_warning` - Early Warning System
- `abhedya.ew_analysis` - Electronic Warfare Analysis
- `abhedya.cybersecurity` - Cybersecurity & Intrusion Detection
- `abhedya.tracking` - Tracking module
- `abhedya.decision` - Decision engine

### Dependencies

- `streamlit` - Web application framework
- `plotly` - Interactive visualization
- `pandas` - Data manipulation

## Architecture

### Components

- **app.py**: Main Streamlit application
- **layout.py**: Layout components and persistent elements
- **state_manager.py**: State management and data fetching
- **visual_components.py**: Visualization components
- **effects_controller.py**: Audio/visual effects controller

### Data Flow

1. Dashboard requests data from backend modules
2. Backend modules return advisory data
3. Dashboard visualizes data with appropriate themes
4. User interactions (acknowledgments) are non-binding
5. All effects are advisory indicators only

## Limitations

1. **Read-Only**: Dashboard is read-only and does not modify system state
2. **Advisory Only**: All outputs are advisory and require human review
3. **No Actions**: No autonomous actions are performed
4. **Simulation**: Audio/visual effects are for simulation/training only

---

**Last Updated**: 2024

