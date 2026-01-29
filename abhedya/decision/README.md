# Decision, Ethics, and Human-in-the-Loop Engine

## Overview

The Decision, Ethics, and Human-in-the-Loop Engine aggregates advisory outputs and enforces ethical and legal constraints. 

**CRITICAL**: This engine SHALL NOT output executable commands. It only outputs advisory system states.

## Responsibilities

### 1. Aggregate Advisory Outputs
- Collects and aggregates advisory recommendations from threat assessments
- Combines track information with threat assessments
- Creates unified advisory system state

### 2. Enforce Ethical and Legal Constraints
- Verifies mandatory human approval requirement
- Ensures human operator presence
- Enforces advisory-only mode
- Prohibits autonomous actions

### 3. Enforce Protected and Civilian Airspace Rules
- Monitors protected zone violations
- Monitors civilian airspace violations
- Reports violations (advisory only)

### 4. Require Explicit Human Review States
- Determines when human review is required
- Tracks human review state
- Ensures human oversight

### 5. Enforce NO_ACTION Default Under Uncertainty
- Activates fail-safe when uncertainty is high
- Defaults to NO_ACTION / MONITORING_ONLY
- Prevents actions under uncertainty

## System Modes

### 1. Advisory Recommendation Mode
- **Purpose**: Normal advisory operation
- **Conditions**: 
  - Human operator present
  - Uncertainty within acceptable limits
  - No critical threats
- **Output**: Advisory recommendations (no executable commands)

### 2. Human Approval Required Mode
- **Purpose**: High-priority advisory requiring human review
- **Conditions**:
  - Critical or high threat levels detected
  - Requires explicit human review
- **Output**: Advisory state indicating review required (no executable commands)

### 3. Monitoring Only Mode
- **Purpose**: Safe monitoring without recommendations
- **Conditions**:
  - High uncertainty
  - Low confidence data
  - Fail-safe activation
- **Output**: Monitoring state only (no executable commands)

### 4. Degraded Safe Mode
- **Purpose**: Safe degraded operation
- **Conditions**:
  - Human operator not present
  - System degradation detected
- **Output**: Safe degraded state (no executable commands)

## Usage Example

```python
from abhedya.decision import DecisionEngine
from abhedya.tracking.models import Track
from abhedya.analysis.threat_assessment.models import ThreatAssessmentResult

# Initialize engine
engine = DecisionEngine(human_operator_present=True)

# Process advisory outputs
result = engine.process_advisory_outputs(
    tracks=active_tracks,
    threat_assessments=threat_assessments
)

# Access advisory system state
print(f"System Mode: {result.system_state.system_mode.value}")
print(f"Human Review: {result.system_state.human_review_state.value}")
print(f"Default Action: {result.system_state.default_action}")
print(f"Fail-Safe: {result.fail_safe_activated}")
print(f"\n{result.advisory_statement}")
```

## Output Format

### AdvisorySystemState
- **system_mode**: Current system mode (advisory state)
- **human_review_state**: Human review requirement
- **default_action**: Always "NO_ACTION"
- **advisory_summary**: Summary of advisory outputs
- **ethical_constraints_active**: Status of ethical constraints
- **protected_airspace_violations**: List of violations (advisory)
- **civilian_airspace_violations**: List of violations (advisory)
- **uncertainty_flags**: Uncertainty indicators

### DecisionResult
- **system_state**: Complete advisory system state
- **aggregated_recommendations**: Advisory recommendations only
- **ethical_constraints_status**: Status of all ethical constraints
- **airspace_compliance_status**: Airspace compliance status
- **human_review_required**: Whether human review is required
- **uncertainty_level**: Overall uncertainty [0.0, 1.0]
- **fail_safe_activated**: Whether fail-safe is activated
- **advisory_statement**: Explicit statement that outputs are advisory only

## Fail-Safe Behavior

### Fail-Safe Activation Conditions
1. **High Uncertainty**: Uncertainty exceeds maximum acceptable threshold
2. **Low Confidence**: More than 50% of tracks have low confidence
3. **Stale Data**: Tracks with data older than maximum age

### Fail-Safe Defaults
- **Default Action**: NO_ACTION (always)
- **Default Mode**: MONITORING_ONLY
- **No Executable Commands**: All outputs are advisory states only

## Ethical Constraints Enforcement

The engine verifies:
- ✅ Mandatory human approval required
- ✅ Human operator required
- ✅ Advisory-only mode
- ✅ Autonomous actions prohibited

If any constraint is violated, the system enters DEGRADED_SAFE mode.

## Airspace Compliance

### Protected Zone Monitoring
- Tracks within Critical Zone (< 20 km)
- Tracks within Protected Zone (20-50 km)
- Violations are reported (advisory only)

### Civilian Airspace Monitoring
- Drones in protected zones
- Civilian aircraft in restricted areas
- Violations are reported (advisory only)

## Human Review Requirements

Human review is required when:
- System mode is HUMAN_APPROVAL_REQUIRED
- Critical or high threat levels detected
- Protected zone violations detected
- High uncertainty flags present

## Uncertainty Handling

### Uncertainty Calculation
- Based on track confidence
- Based on assessment uncertainty
- Combined weighted average

### NO_ACTION Default
- If uncertainty > maximum acceptable: NO_ACTION / MONITORING_ONLY
- If confidence insufficient: NO_ACTION / MONITORING_ONLY
- If data stale: NO_ACTION / MONITORING_ONLY

## Critical Constraints

### No Executable Commands
- ❌ This engine does NOT output executable commands
- ❌ This engine does NOT trigger any actions
- ❌ This engine does NOT authorize any operations
- ✅ This engine ONLY outputs advisory system states

### Advisory Only
- All outputs are advisory
- All recommendations are informational
- All states are descriptive
- No execution authority

## Configuration

The decision engine uses configuration from `abhedya.infrastructure.config.config`:
- `EthicalConstraints`: Ethical constraint requirements
- `ProtectedAirspaceConfiguration`: Zone definitions
- `ConfidenceThresholds`: Confidence requirements
- `UncertaintyLimits`: Uncertainty limits
- `FailSafeConfiguration`: Fail-safe behavior

---

**Last Updated**: 2024

