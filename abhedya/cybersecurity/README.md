# Cybersecurity & Intrusion Detection Module

## Overview

The Cybersecurity & Intrusion Detection module protects the Abhedya software system itself. This is **NOT** offensive cyber capability.

**ADVISORY ONLY** - Alert and visibility only. No automated blocking, no shutdown logic, no retaliation.

## Features

### 1. System Behavior Monitoring
- **Log Access Patterns**: Tracks access patterns across subsystems
- **Configuration Access Frequency**: Monitors configuration access rates
- **Module Interaction Rates**: Tracks module interaction frequencies
- **Statistical Baselines**: Establishes normal behavior baselines

### 2. Anomaly Detection
- **Statistical Baselines**: Z-score deviation from baseline
- **Z-score Deviation**: Statistical anomaly detection
- **Sequence Irregularities**: Detects unusual event sequences
- **Rate-limit Violations**: Detects excessive access rates

### 3. Integrity Monitoring
- **Configuration Consistency**: Checks configuration integrity
- **Unexpected Changes**: Detects unexpected configuration changes
- **Suspicious Access Sequences**: Identifies suspicious event sequences
- **Hash-based Verification**: Configuration hash verification

### 4. Advisory Outputs
- **Cybersecurity State**: `NORMAL`, `SUSPICIOUS`, or `ALERT` (advisory only)
- **Confidence Score**: [0.0, 1.0]
- **Uncertainty**: [0.0, 1.0]
- **Affected Subsystem**: Identifies affected subsystem
- **Advisory Message**: Human-readable message for operator

## Components

### 1. Log Analyzer (`log_analyzer.py`)
Analyzes system logs:
- Access pattern extraction
- Baseline statistics calculation
- Sequence irregularity detection
- Event history management

### 2. Intrusion Detector (`intrusion_detector.py`)
Detects anomalies:
- Statistical deviation (Z-score)
- Rate limit violation detection
- Sequence irregularity detection
- Baseline comparison

### 3. Integrity Monitor (`integrity_monitor.py`)
Monitors system integrity:
- Configuration consistency checks
- Unexpected change detection
- Suspicious sequence detection
- Hash-based verification

### 4. Cybersecurity Engine (`cybersecurity_engine.py`)
Main engine that:
- Orchestrates log analysis, intrusion detection, and integrity monitoring
- Aggregates results
- Determines cybersecurity state
- Generates advisory outputs

## Usage Example

```python
from abhedya.cybersecurity import CybersecurityEngine, SystemEvent, EventType, AccessType
from datetime import datetime

# Initialize engine
engine = CybersecurityEngine(
    enable_log_analysis=True,
    enable_intrusion_detection=True,
    enable_integrity_monitoring=True
)

# Create system events
events = [
    SystemEvent(
        event_id="event_1",
        timestamp=datetime.now(),
        event_type=EventType.CONFIG_ACCESS,
        access_type=AccessType.READ,
        subsystem="config",
        resource="config.yaml",
        user_id="operator_1"
    ),
    SystemEvent(
        event_id="event_2",
        timestamp=datetime.now(),
        event_type=EventType.MODULE_ACCESS,
        access_type=AccessType.EXECUTE,
        subsystem="tracking",
        resource="tracker.py",
        user_id="operator_1"
    ),
    # ... more events
]

# Analyze
result = engine.analyze(events)

# Access results
print(f"Cybersecurity State: {result.cybersecurity_state.value} (ADVISORY ONLY)")
print(f"Confidence: {result.confidence:.2%}")
print(f"Uncertainty: {result.uncertainty:.2%}")
print(f"Affected Subsystem: {result.affected_subsystem}")
print(f"Advisory Message: {result.advisory_message}")

# Print reasoning
for reason in result.reasoning:
    print(f"  {reason}")

# Access access patterns
if result.access_patterns:
    for pattern in result.access_patterns:
        print(f"\nSubsystem: {pattern.subsystem}")
        print(f"  Access Count: {pattern.access_count}")
        print(f"  Access Rate: {pattern.access_rate:.2f} accesses/s")

# Access anomaly detection
if result.anomaly_detection:
    print(f"\nAnomaly Detected: {result.anomaly_detection.is_anomalous}")
    print(f"Anomaly Score: {result.anomaly_detection.anomaly_score:.2%}")
    if result.anomaly_detection.rate_limit_violations:
        print("Rate Limit Violations:")
        for violation in result.anomaly_detection.rate_limit_violations:
            print(f"  - {violation}")

# Access integrity check
if result.integrity_check:
    print(f"\nIntegrity Consistent: {result.integrity_check.is_consistent}")
    if result.integrity_check.unexpected_changes:
        print("Unexpected Changes:")
        for change in result.integrity_check.unexpected_changes:
            print(f"  - {change}")

print(f"\n{result.advisory_statement}")
```

## Detection Methods

### Statistical Deviation
Uses Z-score to detect deviations from baseline:
```
Z = |value - baseline_mean| / baseline_std
```
Anomaly if Z > threshold (default: 2.0σ)

### Rate Limit Violations
Detects excessive access rates:
```
rate_limit = baseline_rate * multiplier (default: 3.0x)
```
Violation if current_rate > rate_limit

### Sequence Irregularities
Detects unusual event sequences:
- Rapid repeated access (< 100ms interval)
- Rapid subsystem switching (< 1s interval)
- Unusual access patterns

### Configuration Integrity
Uses hash-based verification:
- Calculates SHA-256 hash of configuration values
- Compares to expected hashes
- Flags inconsistencies

## Cybersecurity States

### NORMAL
- No significant anomalies detected
- System behavior within expected parameters
- Integrity checks pass

### SUSPICIOUS
- Some anomalies detected
- Statistical deviations present
- Minor integrity issues

### ALERT
- High-priority concerns detected
- Multiple anomalies
- Significant integrity issues

**IMPORTANT**: These states are **ADVISORY ONLY** and do not trigger automated actions.

## Safety Guarantees

### What This Module DOES:
- ✅ System behavior monitoring
- ✅ Anomaly detection
- ✅ Integrity monitoring
- ✅ Advisory outputs
- ✅ Alert and visibility

### What This Module DOES NOT Do:
- ❌ Automated blocking
- ❌ Shutdown logic
- ❌ Retaliation
- ❌ Automated responses
- ❌ Network scanning
- ❌ External API calls

## Configuration

The cybersecurity module uses configurable parameters:

### Log Analyzer
- `time_window_seconds`: Time window for pattern analysis (default: 3600s = 1 hour)
- `minimum_samples_for_baseline`: Minimum samples for baseline (default: 10)

### Intrusion Detector
- `z_score_threshold`: Z-score threshold (default: 2.0)
- `rate_limit_multiplier`: Rate limit multiplier (default: 3.0x)
- `minimum_samples_for_baseline`: Minimum samples for baseline (default: 10)

### Integrity Monitor
- `expected_config_hashes`: Expected configuration hashes (optional)
- `suspicious_sequences`: Suspicious event sequences (optional)

## Limitations

1. **Simplified Models**: Uses simplified statistical models
2. **No Real-time Processing**: Batch processing of events
3. **No Network Monitoring**: Only internal system monitoring
4. **Baseline Requirements**: Requires minimum samples for baseline
5. **Hash-based Only**: Configuration verification uses hashes only

## Example Output

```python
CybersecurityResult(
    result_id="...",
    timestamp=datetime.now(),
    cybersecurity_state=CybersecurityState.SUSPICIOUS,
    confidence=0.75,
    uncertainty=0.25,
    affected_subsystem="config",
    advisory_message="SUSPICIOUS: Unusual system behavior detected | Affected subsystem: config | Anomaly score: 65.00% | Human operator review recommended",
    access_patterns=[
        AccessPattern(
            subsystem="config",
            access_count=25,
            access_rate=0.007,
            unique_resources=3,
            ...
        )
    ],
    anomaly_detection=AnomalyDetectionResult(
        is_anomalous=True,
        anomaly_score=0.65,
        statistical_deviation=2.3,
        rate_limit_violations=[
            "config: 0.007 accesses/s (limit: 0.005, baseline: 0.002)"
        ],
        ...
    ),
    integrity_check=IntegrityCheckResult(
        is_consistent=True,
        unexpected_changes=[],
        ...
    ),
    reasoning=[
        "Cybersecurity State: SUSPICIOUS (ADVISORY ONLY)",
        "Anomaly Detection:",
        "  - Statistical deviation from baseline: 2.30σ",
        "  - Rate limit violation in config: 0.007 accesses/s exceeds limit",
        ...
    ],
    advisory_statement="ADVISORY ONLY - Alert and visibility only..."
)
```

## Integration

### Inputs
- **SystemEvent**: System events to analyze
- **Optional**: Baseline events for comparison
- **Optional**: Current configuration for integrity checks

### Outputs
- **CybersecurityResult**: Advisory result object
- **No Execution Logic**: Outputs are advisory only
- **No Actions**: No actions are taken

### No Coupling
- Does not modify existing modules
- Does not execute any actions
- Pure monitoring and analysis

## Event Types

### CONFIG_ACCESS
Configuration access events

### MODULE_ACCESS
Module access events

### DATA_ACCESS
Data access events

### SYSTEM_ACCESS
System-level access events

### UNKNOWN
Unknown event types

## Access Types

### READ
Read access

### WRITE
Write access

### EXECUTE
Execute access

### MODIFY
Modify access

## Best Practices

1. **Regular Baseline Updates**: Update baseline regularly with normal operation data
2. **Configuration Hashes**: Maintain expected configuration hashes
3. **Suspicious Sequences**: Define known suspicious sequences
4. **Event Logging**: Ensure comprehensive event logging
5. **Human Review**: Always require human operator review for alerts

---

**Last Updated**: 2024

