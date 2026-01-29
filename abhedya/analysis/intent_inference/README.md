# Intent Probability Inference Engine

## Overview

The Intent Probability Inference Engine provides probabilistic intent assessment for tracked objects using explainable, rule-based logic. All outputs are **ADVISORY ONLY** and do not recommend any actions.

**CRITICAL DECLARATION**: Intent inference does NOT replace classification or threat assessment. It provides an additional advisory layer for human operator interpretation.

## Key Principles

1. **Advisory Only**: All outputs are informational and require human interpretation
2. **Explainable Logic**: Rule-based and statistical methods only (NO deep learning)
3. **Probabilistic Outputs**: Intent probabilities sum to ≤ 100%
4. **Fail-Safe Defaults**: Returns None if inputs are missing or inconsistent
5. **Uncertainty-Aware**: Conservative by default, includes confidence scores

## Intent Categories

The engine assesses three intent categories:

- **Transit Intent**: Object appears to be in transit through airspace
- **Surveillance Intent**: Object appears to be conducting surveillance activities
- **Hostile Intent**: Object shows indicators of hostile intent

**IMPORTANT**: These categories are informational only and do NOT map to any actions.

## Inputs

The engine consumes:

- **Classification Results**: Object type (Aerial Drone, Aircraft, Unknown)
- **Trajectory Prediction**: Predicted future positions
- **Speed and Altitude**: Current speed and altitude characteristics
- **Maneuver Stability**: Velocity change patterns
- **Airspace Context**: Proximity to protected zones
- **Position History**: Historical position data (if available)

## Outputs

### Intent Probabilities

- **Transit Probability**: [0.0, 1.0]
- **Surveillance Probability**: [0.0, 1.0]
- **Hostile Probability**: [0.0, 1.0]
- **Total Probability**: ≤ 1.0 (probabilities may not sum to 1.0 due to uncertainty)

### Confidence and Reasoning

- **Intent Confidence**: Overall confidence in assessment [0.0, 1.0]
- **Reasoning**: Human-readable list of reasoning statements

## Rule-Based Logic

### Transit Intent Indicators

- Moderate to high speed (50-300 m/s)
- Stable trajectory
- Low loitering behavior
- High maneuver stability

### Surveillance Intent Indicators

- Low to moderate speed
- Loitering patterns
- Stable altitude
- Proximity to protected zones
- Repeated perimeter probing

### Hostile Intent Indicators

- Strong proximity risk indicators
- Unstable maneuver patterns
- Unknown object classification
- Anomalous behavior patterns

**Note**: Hostile intent probability is calculated conservatively and requires strong indicators.

## Fail-Safe Behavior

If required inputs are missing or inconsistent:

- Returns `None` (not an IntentProbabilityResult)
- System should default to `MONITORING_ONLY`
- No intent probabilities are generated
- No false positives from incomplete data

## Usage Example

```python
from abhedya.analysis.intent_inference import IntentInferenceEngine
from abhedya.tracking.models import Track

# Initialize engine
engine = IntentInferenceEngine()

# Infer intent
result = engine.infer_intent(
    track=track,
    trajectory_prediction=trajectory_prediction,
    proximity_estimate=proximity_estimate,
    is_training_mode=False
)

if result:
    print(f"Transit Probability: {result.transit_probability:.1%}")
    print(f"Surveillance Probability: {result.surveillance_probability:.1%}")
    print(f"Hostile Probability: {result.hostile_probability:.1%}")
    print(f"Intent Confidence: {result.intent_confidence:.1%}")
    print(f"Reasoning: {result.reasoning}")
else:
    print("Insufficient data - Monitoring Only")
```

## Ethical and Legal Compliance

### Advisory-Only Operation

- Intent probabilities are informational only
- Do not trigger any actions
- Require human operator interpretation
- Do not replace classification or threat assessment

### Uncertainty Handling

- Conservative probability estimates
- Explicit confidence scores
- Uncertainty-aware calculations
- Fail-safe defaults

### Data Privacy

- All processing is local
- No external data transmission
- Immutable audit logs

## Integration

The Intent Inference Engine integrates with:

- **Tracking Module**: Consumes track data and classification results
- **Trajectory Analysis**: Consumes trajectory predictions
- **Threat Assessment**: Provides additional context (does not replace)
- **Dashboard**: Displays intent probabilities for human review
- **Logging and Audit**: Logs all intent assessments

## Limitations

1. **Rule-Based Only**: Uses explainable rules, not machine learning
2. **Probabilistic**: Probabilities are estimates, not certainties
3. **Context-Dependent**: Requires sufficient data for accurate assessment
4. **Advisory Only**: Does not recommend actions or replace human judgment

## Future Enhancements

Potential future enhancements (subject to ethical constraints):

- Additional intent categories
- Temporal pattern analysis
- Multi-object intent correlation
- Enhanced uncertainty quantification

**Note**: All enhancements must maintain advisory-only operation and ethical constraints.

