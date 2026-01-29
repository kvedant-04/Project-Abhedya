# Quick Start Guide - Abhedya Air Defense System

## Installation

1. **Install Python 3.9+**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install the package (optional, for development):**
```bash
pip install -e .
```

## Running the Demo

The easiest way to see the system in action:

```bash
python examples/demo.py
```

This will run a demonstration scenario showing:
- Sensor detection (Radar and IFF)
- Track creation and fusion
- Threat assessment
- Advisory recommendation generation
- Human approval workflow
- Audit trail logging

## Basic Usage Example

```python
from abhedya import AbhedyaSystem
from abhedya.sensors import RadarSensor, IFFSensor
from abhedya.assessment import ThreatAssessor
from abhedya.advisory import AdvisoryEngine
from abhedya.interface import HumanInterface
from abhedya.audit import AuditLogger
from abhedya.core.models import Coordinates, Velocity

# 1. Create sensors
radar = RadarSensor(
    sensor_id="RADAR_001",
    position=Coordinates(x=0.0, y=0.0, z=0.0),
    range_meters=150000.0
)

iff = IFFSensor(
    sensor_id="IFF_001",
    position=Coordinates(x=0.0, y=0.0, z=0.0),
    range_meters=200000.0
)

# 2. Create system components
threat_assessor = ThreatAssessor()
advisory_engine = AdvisoryEngine()
human_interface = HumanInterface()
audit_logger = AuditLogger(log_directory="logs")

# 3. Initialize system
system = AbhedyaSystem(
    sensors=[radar, iff],
    threat_assessor=threat_assessor,
    advisory_engine=advisory_engine,
    human_interface=human_interface,
    audit_logger=audit_logger
)

# 4. Add simulated entities (for demonstration)
radar.add_simulated_entity(
    position=Coordinates(x=50000.0, y=60000.0, z=5000.0),
    velocity=Velocity(vx=-100.0, vy=-80.0, vz=0.0),
    entity_id="ENTITY_001"
)

# 5. Run system cycles
for i in range(10):
    system.run_cycle()
    
    # Check for recommendations
    state = system.get_state()
    if state.pending_recommendations:
        for rec in state.pending_recommendations:
            print(f"Recommendation: {rec.action.value}")
            print(f"Threat Level: {rec.threat_level.value}")
            print(f"Reasoning:\n{rec.reasoning}")
            
            # Simulate human approval
            human_interface.simulate_human_approval(
                rec.recommendation_id,
                approved=True
            )
```

## Key Concepts

### 1. Sensors
- **RadarSensor**: Simulates primary radar detection
- **IFFSensor**: Simulates Identification Friend or Foe interrogation
- Sensors generate `SensorReading` objects with position, velocity, and confidence

### 2. Tracks
- Sensor readings are fused into `Track` objects
- Tracks represent detected entities over time
- Tracks include entity classification and threat assessment

### 3. Threat Assessment
- `ThreatAssessor` classifies entities (Friendly/Hostile/Unknown/etc.)
- Assesses threat levels (None/Low/Medium/High/Critical)
- Provides explainable reasoning

### 4. Advisory Recommendations
- `AdvisoryEngine` generates recommendations (advisory only)
- Recommendations include action, threat level, confidence, and reasoning
- **IMPORTANT**: All recommendations require human approval

### 5. Human Interface
- `HumanInterface` presents recommendations to operators
- Manages approval workflow
- **CRITICAL**: Cannot be bypassed

### 6. Audit Trail
- `AuditLogger` logs all system events
- Provides complete traceability
- Supports explainability queries

## Important Reminders

⚠️ **This system is SOFTWARE-ONLY and ADVISORY**
- No real-world actions are executed
- All outputs require human approval
- Designed for simulation and demonstration only

⚠️ **Ethical Constraints**
- Mandatory human approval (cannot be disabled)
- Fail-safe defaults (NO_ACTION by default)
- Complete audit trail
- Explainable decisions

## Next Steps

1. Read `ARCHITECTURE.md` for detailed system design
2. Read `ETHICS.md` for ethical considerations
3. Explore the codebase in `abhedya/` directory
4. Modify `examples/demo.py` to create your own scenarios

## Troubleshooting

**Import errors?**
- Make sure you're in the project root directory
- Install dependencies: `pip install -r requirements.txt`

**No recommendations generated?**
- Check that entities are within sensor range
- Verify threat assessor and advisory engine are configured
- Check minimum confidence thresholds

**Questions?**
- Review the documentation in `README.md`, `ARCHITECTURE.md`, and `ETHICS.md`
- Check code comments for implementation details

