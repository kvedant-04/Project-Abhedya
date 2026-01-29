# Abhedya Air Defense System - Architecture Documentation

## System Overview

The Abhedya Air Defense System is a modular, production-grade software-only simulation and decision-intelligence platform. It is designed with ethical constraints, fail-safe defaults, and mandatory human-in-the-loop requirements.

## Architecture Principles

1. **Modularity**: Clear separation of concerns with well-defined interfaces
2. **Determinism**: Predictable, explainable behavior
3. **Safety**: Fail-safe defaults and mandatory human approval
4. **Auditability**: Complete traceability of all operations
5. **Extensibility**: Easy to add new sensors, assessors, and advisory engines

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AbhedyaSystem (Core)                      │
│                  - Orchestrates all components              │
│                  - Enforces safety constraints              │
│                  - Manages system state                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Sensors    │   │  Assessment  │   │   Advisory   │
│              │   │              │   │              │
│ - Radar      │   │ - Threat     │   │ - Decision   │
│ - IFF        │   │   Assessor   │   │   Support    │
│ - Optical    │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │   Human       │
                   │   Interface   │
                   │   (Mandatory) │
                   └──────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │    Audit     │
                   │    Logger    │
                   └──────────────┘
```

## Component Details

### 1. Core System (`abhedya/core/`)

#### Models (`models.py`)
- **Coordinates**: 3D spatial coordinates
- **Velocity**: Velocity vector
- **SensorReading**: Raw sensor detection
- **Track**: Fused track of detected entity
- **AdvisoryRecommendation**: Advisory recommendation (non-binding)
- **SystemState**: Current system state

#### Interfaces (`interfaces.py`)
- **ISensor**: Sensor simulation interface
- **IThreatAssessor**: Threat assessment interface
- **IAdvisoryEngine**: Advisory decision-support interface
- **IHumanInterface**: Human-in-the-loop interface
- **IAuditLogger**: Audit logging interface

#### System (`system.py`)
- **AbhedyaSystem**: Main orchestrator class
- Manages sensor updates
- Coordinates track fusion
- Generates and presents recommendations
- Enforces safety constraints

### 2. Sensors (`abhedya/sensors/`)

#### Base Sensor (`base.py`)
- Common sensor functionality
- Range and confidence filtering
- Rate limiting
- Signal strength calculation

#### Radar Sensor (`radar.py`)
- Primary radar simulation
- Position and velocity detection
- Measurement noise modeling
- Range: ~150 km typical

#### IFF Sensor (`iff.py`)
- Identification Friend or Foe simulation
- Friendly entity identification
- IFF code validation
- Range: ~200 km typical

### 3. Threat Assessment (`abhedya/assessment/`)

#### Threat Assessor (`assessor.py`)
- Entity classification (Friendly/Hostile/Unknown/Neutral/Civilian)
- Threat level assessment (None/Low/Medium/High/Critical)
- Behavior pattern analysis
- Proximity-based threat evaluation
- Explainable reasoning

### 4. Advisory Engine (`abhedya/advisory/`)

#### Advisory Engine (`engine.py`)
- Generates advisory recommendations
- Probabilistic threat assessment
- Action recommendation (Monitor/Investigate/Alert/Track)
- Detailed reasoning generation
- **IMPORTANT**: Advisory only, no execution

### 5. Human Interface (`abhedya/interface/`)

#### Human Interface (`human.py`)
- Presents recommendations to operators
- Manages approval workflow
- Enforces mandatory approval requirement
- Tracks approval status
- **CRITICAL**: Cannot be bypassed

### 6. Audit System (`abhedya/audit/`)

#### Audit Logger (`logger.py`)
- Logs all system events
- Maintains audit trail
- Provides explainability
- Supports export and query
- File-based and in-memory storage

### 7. Configuration (`abhedya/config/`)

#### Config Manager (`manager.py`)
- Manages system configuration
- Enforces fail-safe defaults
- Validates configuration values
- YAML-based configuration
- Safety constraint enforcement

## Data Flow

```
1. Sensors detect entities
   ↓
2. Sensor readings collected
   ↓
3. Tracks created/updated (fusion)
   ↓
4. Threat assessment performed
   ↓
5. Advisory recommendations generated
   ↓
6. Recommendations presented to human
   ↓
7. Human approval obtained (mandatory)
   ↓
8. All events logged to audit trail
```

## Safety Mechanisms

### 1. Mandatory Human Approval
- Enforced at model level (Pydantic validator)
- Enforced at system level (runtime checks)
- Cannot be disabled

### 2. Fail-Safe Defaults
- Default action: NO_ACTION
- Default threat level: NONE
- Default entity type: UNKNOWN
- System mode: MONITORING

### 3. No Execution Capability
- System has no interfaces to real control systems
- All outputs are informational
- No weapon control logic

### 4. Deterministic Behavior
- All algorithms are deterministic (with controlled randomness for simulation)
- All decisions are explainable
- Complete audit trail

## Extension Points

### Adding New Sensors
1. Inherit from `BaseSensor` or implement `ISensor`
2. Implement `_detect_entities()` method
3. Add to system via `add_sensor()`

### Adding New Assessment Methods
1. Implement `IThreatAssessor` interface
2. Implement `assess_track()` and `explain_assessment()`
3. Pass to `AbhedyaSystem` constructor

### Adding New Advisory Engines
1. Implement `IAdvisoryEngine` interface
2. Implement `generate_recommendation()` and `explain_recommendation()`
3. Pass to `AbhedyaSystem` constructor

## Performance Considerations

- **Track Limit**: Maximum 1000 tracks per update (configurable)
- **Recommendation Queue**: Maximum 100 pending recommendations
- **System Timeout**: 30 seconds per cycle (configurable)
- **Sensor Update Rate**: Configurable per sensor (default 1 Hz)

## Testing and Validation

- Unit tests for each component
- Integration tests for system workflows
- Safety constraint validation
- Ethical requirement verification

## Deployment Considerations

- **Offline-capable**: No cloud dependencies
- **Open-source**: No proprietary services
- **Portable**: Python-based, cross-platform
- **Configurable**: YAML-based configuration

## Future Enhancements

Potential extensions (while maintaining ethical constraints):
- Additional sensor types (optical, acoustic)
- Advanced track fusion algorithms
- Machine learning-based threat assessment (advisory only)
- Enhanced visualization interfaces
- Multi-operator support

---

**Version**: 1.0.0
**Last Updated**: 2024

