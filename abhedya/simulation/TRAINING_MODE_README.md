# Training & Simulation Mode

## Overview

Training & Simulation Mode is a fully functional, ethical, and clearly labeled feature that allows the Command and Control Dashboard to operate with realistic synthetic data while preserving the real-world operational pipeline.

**CRITICAL**: This is an ADDITION — NOT a replacement. The real-world operational mode remains intact and unchanged.

## Purpose

Training & Simulation Mode enables:

- **Demonstration**: Showcase system capabilities without requiring real sensor data
- **Training**: Operator training with realistic scenarios
- **Testing**: System validation and integration testing
- **Development**: UI/UX development and debugging

## Design Principles

### 1. Advisory-Only System

- All outputs remain informational
- No autonomous actions
- No weapon control
- No command authority
- Training mode does NOT bypass ethics, fail-safes, or human-in-the-loop

### 2. Clear Mode Separation

- **Real-World Mode** (default): Expects real or external data inputs
- **Training & Simulation Mode**: Injects synthetic data at input boundary
- Toggle controlled by ONE checkbox: "Enable Training & Simulation Mode"

### 3. Professional Terminology

- Uses "Training & Simulation Mode" (not "Training / Simulation Mode Enabled")
- All synthetic data clearly labeled: "SIMULATION / TRAINING DATA"

## Functional Behavior

### When Training & Simulation Mode is ENABLED

- Synthetic data is injected at the INPUT boundary
- Data flows through the FULL pipeline:
  - Simulation → Preprocessing → Tracking → Trajectory →
  - Threat Assessment → Intent Inference → Decision → Dashboard
- All panels populate with realistic synthetic data:
  - Airspace Overview (moving tracks)
  - Threat & Advisory Status
  - Early Warning System
  - Electronic Warfare Analysis
  - Cybersecurity & System Integrity
  - Intent Probability Interface
- Dashboard NEVER shows "Insufficient Data" while training mode is ON
- All data clearly labeled as "SIMULATION / TRAINING DATA"

### When Training & Simulation Mode is DISABLED

- NO synthetic data is injected
- System behaves exactly as before
- Dashboard expects real or external inputs
- Existing "Insufficient Data" messages remain valid

## Synthetic Data Characteristics

### Physically Plausible

- Valid speeds (100-140 m/s for aircraft)
- Realistic altitudes (5-7 km)
- Smooth trajectories (circular motion patterns)
- Consistent velocity vectors

### Statistically Consistent

- Confidence values evolve over time
- Severity escalation and de-escalation
- Intent probabilities change with behavior
- State transitions follow logical patterns

### Ethically Safe

- No false hostile intent spikes without reasoning
- Conservative probability estimates
- Clear simulation labeling
- No alarming language

### Deterministic

- Seed-based generation (seed=42)
- Reproducible scenarios
- Time-offset based animation
- Smooth state transitions

## Implementation Details

### Data Generator

Location: `abhedya/simulation/training_data_generator.py`

The `TrainingDataGenerator` class provides:

- `generate_tracking_data()`: Synthetic airspace tracks
- `generate_early_warning_data()`: Early warning states
- `generate_threat_assessment_data()`: Threat assessments
- `generate_intent_assessment_data()`: Intent probabilities
- `generate_ew_analysis_data()`: Electronic warfare analysis
- `generate_cybersecurity_data()`: Cybersecurity monitoring
- `generate_advisory_state()`: System advisory states

### Data Injection

Location: `abhedya/dashboard/state_manager.py`

All data fetching methods check `is_training_mode()`:

- If `True`: Generate and return synthetic data
- If `False`: Attempt to fetch real data (or return None)

### Dashboard Integration

Location: `abhedya/dashboard/app.py`

- Sidebar checkbox: "Enable Training & Simulation Mode" (ALWAYS VISIBLE)
- Navigation controls: Home/Back buttons (ALWAYS VISIBLE)
- Simulation labels: "SIMULATION / TRAINING DATA" banners
- Fallback handling: Graceful degradation if generator fails

## User Interface

### Sidebar Controls

- **Training & Simulation Mode Toggle**: Single checkbox, always visible
- **Audio Toggle**: Separate control for audio indicators
- **View Options**: Confidence rings, protected zones, auto-refresh

### Navigation

- **Home Button**: Returns to Airspace Overview
- **Back Button**: Returns to previous view
- Navigation works in all tabs and both modes

### Visual Indicators

- **Training Mode Banner**: Red-bordered banner when active
- **Simulation Labels**: Amber-bordered labels on all synthetic data
- **Advisory Disclaimers**: "Advisory Only" on all panels

## Ethical Safeguards

1. **No Bypass**: Training mode does NOT bypass ethical constraints
2. **Clear Labeling**: All synthetic data clearly marked
3. **Fail-Safe Defaults**: System defaults to MONITORING_ONLY on errors
4. **Human-in-the-Loop**: Mandatory human approval still required
5. **Advisory Only**: No execution authority in any mode

## Limitations

1. **Deterministic**: Scenarios are predictable (seed-based)
2. **Simplified**: Synthetic data is simplified compared to real-world complexity
3. **Training Only**: Not suitable for operational decision-making
4. **Offline**: No external data sources in training mode

## Future Enhancements

Potential future enhancements (subject to ethical constraints):

- Multiple scenario templates
- Custom scenario configuration
- Historical scenario replay
- Multi-object coordination patterns
- Advanced trajectory patterns

**Note**: All enhancements must maintain advisory-only operation and ethical constraints.

## Usage

### Enabling Training Mode

1. Open the Command and Control Dashboard
2. In the sidebar, check "Enable Training & Simulation Mode"
3. All panels will populate with synthetic data
4. Data will be clearly labeled as "SIMULATION / TRAINING DATA"

### Disabling Training Mode

1. Uncheck "Enable Training & Simulation Mode" in the sidebar
2. System returns to real-world mode
3. Dashboard expects real or external data inputs

## Technical Notes

- Generator uses deterministic seed (42) for reproducibility
- Time offset calculated from session start time
- State transitions cycle on configurable intervals
- All synthetic data includes `is_simulation: True` flag
- All synthetic data includes `simulation_label: "SIMULATION / TRAINING DATA"`

## Compliance

Training & Simulation Mode maintains:

- **Advisory-Only Operation**: No autonomous actions
- **Human-in-the-Loop**: Mandatory human approval
- **Fail-Safe Defaults**: Safe defaults on errors
- **Clear Labeling**: All synthetic data clearly marked
- **Ethical Constraints**: No bypass of safety mechanisms

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Status**: Production-Ready


