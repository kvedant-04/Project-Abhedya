# Logging and Audit Module

## Overview

The Logging and Audit module provides comprehensive, immutable logging and audit trail functionality for the Abhedya Air Defense System.

**Key Features:**
- Immutable logs (append-only)
- Timestamped advisory states
- Human acknowledgment tracking
- Replay support
- SQLite storage with structured JSON logs

## Architecture

### Database Schema

The module uses SQLite with three main tables:

#### 1. `advisory_logs`
Stores advisory outputs from system modules.

**Columns:**
- `id` (INTEGER PRIMARY KEY) - Auto-incrementing log entry ID
- `timestamp` (TEXT) - ISO format timestamp
- `module_name` (TEXT) - Name of the module (e.g., "early_warning", "ew_analysis")
- `advisory_state` (TEXT) - Advisory state (e.g., "NORMAL", "ELEVATED", "HIGH")
- `confidence` (REAL) - Confidence value [0.0, 1.0]
- `data_json` (TEXT) - JSON-encoded advisory data
- `metadata_json` (TEXT) - Optional JSON-encoded metadata
- `created_at` (TEXT) - Database insertion timestamp

**Indexes:**
- `idx_advisory_logs_timestamp` - On `timestamp` for efficient time-based queries
- `idx_advisory_logs_module` - On `module_name` for module filtering
- `idx_advisory_logs_state` - On `advisory_state` for state filtering

#### 2. `acknowledgments`
Stores human acknowledgment actions.

**Columns:**
- `id` (INTEGER PRIMARY KEY) - Auto-incrementing log entry ID
- `timestamp` (TEXT) - ISO format timestamp
- `item_id` (TEXT) - ID of the acknowledged item
- `item_type` (TEXT) - Type of the item
- `acknowledged_by` (TEXT) - Optional identifier of who acknowledged
- `metadata_json` (TEXT) - Optional JSON-encoded metadata
- `created_at` (TEXT) - Database insertion timestamp

**Indexes:**
- `idx_acknowledgments_timestamp` - On `timestamp` for efficient time-based queries
- `idx_acknowledgments_item_id` - On `item_id` for item lookup

#### 3. `system_events`
Stores system events (startup, shutdown, errors, etc.).

**Columns:**
- `id` (INTEGER PRIMARY KEY) - Auto-incrementing log entry ID
- `timestamp` (TEXT) - ISO format timestamp
- `event_type` (TEXT) - Type of event (e.g., "system_startup", "advisory_state_change")
- `event_data_json` (TEXT) - JSON-encoded event data
- `metadata_json` (TEXT) - Optional JSON-encoded metadata
- `created_at` (TEXT) - Database insertion timestamp

**Indexes:**
- `idx_system_events_timestamp` - On `timestamp` for efficient time-based queries
- `idx_system_events_type` - On `event_type` for event type filtering

## Usage

### Basic Logging

```python
from abhedya.logging_and_audit import AdvisoryLogger

# Initialize logger
logger = AdvisoryLogger(db_path="abhedya_audit.db")

# Log early warning advisory
log_id = logger.log_early_warning(
    warning_state="ELEVATED",
    confidence=0.75,
    reasoning=["Track density increased", "Velocity anomaly detected"],
    trend_analysis={"track_density": 5.2, "baseline": 3.1}
)

# Log EW analysis advisory
log_id = logger.log_ew_analysis(
    ew_state="ANOMALOUS",
    confidence=0.82,
    spectral_features={"snr": 12.5, "entropy": 0.65},
    anomaly_detection={"is_anomalous": True, "pattern": "Unknown emission"}
)

# Log cybersecurity advisory
log_id = logger.log_cybersecurity(
    cybersecurity_state="SUSPICIOUS",
    confidence=0.68,
    affected_subsystem="configuration",
    integrity_check={"is_consistent": False}
)

# Log dashboard acknowledgment
log_id = logger.log_dashboard_acknowledgment(
    item_id="advisory_123",
    item_type="threat_assessment",
    acknowledged_by="operator_1"
)
```

### Querying Logs

```python
from datetime import datetime, timedelta

# Query advisory logs
logs = logger.query_advisory_logs(
    module_name="early_warning",
    advisory_state="ELEVATED",
    start_timestamp=datetime.utcnow() - timedelta(hours=24),
    limit=100
)

# Query acknowledgments
acks = logger.query_acknowledgments(
    item_type="threat_assessment",
    start_timestamp=datetime.utcnow() - timedelta(hours=24)
)
```

### Replay Functionality

```python
from abhedya.logging_and_audit import LogReplay

# Initialize replay
replay = LogReplay(db_path="abhedya_audit.db")

# Replay advisory logs
for log_entry in replay.replay_advisory_logs(
    module_name="early_warning",
    start_timestamp=datetime.utcnow() - timedelta(hours=24)
):
    print(f"{log_entry['timestamp']}: {log_entry['advisory_state']}")

# Replay all logs in chronological order
for entry, entry_type in replay.replay_all(
    start_timestamp=datetime.utcnow() - timedelta(hours=24)
):
    print(f"{entry_type}: {entry['timestamp']}")
```

### Database Statistics

```python
stats = logger.get_database_stats()
print(f"Total advisory logs: {stats['advisory_logs_count']}")
print(f"Total acknowledgments: {stats['acknowledgments_count']}")
print(f"Total system events: {stats['system_events_count']}")
```

## Module Integration

### Early Warning System

```python
from abhedya.logging_and_audit import AdvisoryLogger

logger = AdvisoryLogger()

# After early warning analysis
logger.log_early_warning(
    warning_state=result.warning_state,
    confidence=result.confidence,
    reasoning=result.reasoning,
    trend_analysis=result.trend_analysis
)
```

### Electronic Warfare Analysis

```python
# After EW analysis
logger.log_ew_analysis(
    ew_state=result.ew_state,
    confidence=result.confidence,
    spectral_features=result.spectral_features,
    anomaly_detection=result.anomaly_detection,
    reasoning=result.reasoning
)
```

### Cybersecurity

```python
# After cybersecurity analysis
logger.log_cybersecurity(
    cybersecurity_state=result.cybersecurity_state,
    confidence=result.confidence,
    affected_subsystem=result.affected_subsystem,
    integrity_check=result.integrity_check,
    anomaly_detection=result.anomaly_detection,
    reasoning=result.reasoning
)
```

### Dashboard

```python
# When user acknowledges an item
logger.log_dashboard_acknowledgment(
    item_id=item_id,
    item_type=item_type,
    acknowledged_by=operator_id,
    item_data=item_data
)
```

## Safety Guarantees

### Immutability
- **No Deletes**: Logs are never deleted
- **No Updates**: Logs are never modified
- **Append-Only**: All operations are insertions only

### Data Integrity
- **Thread-Safe**: Database operations are thread-safe
- **Atomic Writes**: All writes are atomic
- **Structured Data**: All data is stored as structured JSON

### Offline Capability
- **SQLite**: No external dependencies
- **Local Storage**: All data stored locally
- **No Network**: No external logging services

## Limitations

1. **Storage Growth**: Logs grow indefinitely (consider archival strategy)
2. **Query Performance**: Large datasets may require pagination
3. **No Compression**: JSON data is not compressed (consider if needed)
4. **Single Database**: Single SQLite file (consider sharding for very large deployments)

## Best Practices

1. **Regular Queries**: Use timestamp filters to limit query results
2. **Pagination**: Use `limit` and `offset` for large result sets
3. **Metadata**: Include relevant metadata for debugging and analysis
4. **Error Handling**: Wrap logging calls in try/except blocks
5. **Database Backup**: Regularly backup the SQLite database file

## Database File Location

By default, the database file is created in the current working directory as `abhedya_audit.db`. You can specify a custom path:

```python
logger = AdvisoryLogger(db_path="/path/to/abhedya_audit.db")
```

---

**Last Updated**: 2024

