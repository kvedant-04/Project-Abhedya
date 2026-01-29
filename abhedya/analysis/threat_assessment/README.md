# Threat Assessment and Risk Scoring Engine

## Overview

The Threat Assessment and Risk Scoring Engine provides multi-factor weighted risk scoring with probabilistic threat likelihood output. All assessments are **ADVISORY ONLY** and do not recommend any actions.

**STRICT RULES**:
- **No binary decisions**: All outputs are probabilistic and continuous
- **No action recommendations**: Assessment does not suggest any actions
- **Threat level does NOT map to actions**: Threat level is purely informational
- **Explicit advisory statement**: All outputs explicitly state "Advisory Assessment Only"

## Features

### 1. Multi-Factor Weighted Risk Scoring

Risk factors with configurable weights:
- **Entity Classification** (25%): Risk based on classified entity type
- **Proximity** (25%): Risk based on distance to protected zones
- **Behavior** (20%): Risk based on behavioral patterns
- **Speed** (15%): Risk based on speed characteristics
- **Trajectory** (10%): Risk based on trajectory analysis
- **Confidence** (5%): Risk based on data confidence

### 2. Probabilistic Threat Likelihood

- Continuous probability value [0.0, 1.0]
- Based on risk score and uncertainty
- Not a binary decision

### 3. Confidence and Uncertainty Bounds

- **Confidence Percentage**: Assessment confidence [0%, 100%]
- **Uncertainty Percentage**: Assessment uncertainty [0%, 100%]
- **Confidence Bounds**: Lower and upper bounds for risk score

### 4. Threat Categories (INFORMATIONAL ONLY)

- **LOW**: Risk score < 0.3
- **MEDIUM**: Risk score 0.3 to 0.6
- **HIGH**: Risk score 0.6 to 0.8
- **CRITICAL**: Risk score ≥ 0.8

**IMPORTANT**: These categories are informational only and do NOT map to any actions.

### 5. Transparent Score Breakdown

Complete breakdown showing:
- Individual factor values
- Factor weights
- Factor contributions
- Percentage of total score
- Reasoning for each factor

## Usage Example

```python
from abhedya.analysis.threat_assessment import ThreatAssessmentEngine
from abhedya.tracking.models import Track

# Initialize engine
engine = ThreatAssessmentEngine()

# Assess track
result = engine.assess_track(track)

# Access results
print(f"Threat Level: {result.threat_level.value} (INFORMATIONAL ONLY)")
print(f"Risk Score: {result.risk_score.total_score:.3f}")
print(f"Threat Likelihood: {result.threat_likelihood:.2%}")
print(f"Confidence: {result.confidence_percentage:.1f}%")
print(f"Uncertainty: {result.uncertainty_percentage:.1f}%")
print(f"\n{result.advisory_statement}")

# Access score breakdown
print("\nScore Breakdown:")
for factor_name, factor_data in result.score_breakdown["factor_contributions"].items():
    print(f"{factor_name}: {factor_data['contribution']:.3f} "
          f"({factor_data['percentage_of_total']:.1f}% of total)")
```

## Risk Scoring Methodology

### Total Risk Score Calculation

```
total_score = Σ(factor_value_i × weight_i)
```

Where:
- `factor_value_i`: Normalized factor value [0.0, 1.0]
- `weight_i`: Factor weight (must sum to 1.0)

### Factor Calculations

#### 1. Entity Classification Factor
- **Hostile**: 0.9 base risk
- **Unknown Object**: 0.6 base risk
- **Aircraft**: 0.3 base risk
- **Aerial Drone**: 0.5 base risk
- Adjusted by classification probability and uncertainty

#### 2. Proximity Factor
- **Critical Zone** (< 20 km): 0.9 risk
- **Protected Zone** (20-50 km): 0.7 risk
- **Extended Zone** (50-100 km): 0.4 risk
- **Outside Zones** (> 100 km): 0.1 risk
- Adjusted by distance

#### 3. Behavior Factor
- Heading towards origin: +0.4 risk
- High speed: +0.2 risk
- Base risk: 0.3

#### 4. Speed Factor
- **High speed** (> 300 m/s): 0.8 risk
- **Medium speed** (200-300 m/s): 0.5 risk
- **Lower speed** (100-200 m/s): 0.3 risk
- **Very low speed** (< 100 m/s): 0.1 risk

#### 5. Trajectory Factor
- Heading towards origin (< 45°): 0.7 risk
- Somewhat towards origin (45-90°): 0.5 risk
- Base risk: 0.3

#### 6. Confidence Factor
- Inverted confidence: `(1.0 - confidence) × 0.5`
- Lower confidence = higher uncertainty risk

### Threat Likelihood Calculation

```
threat_likelihood = risk_score + (uncertainty × 0.2)
```

Uncertainty itself is considered a risk factor.

### Uncertainty Calculation

Combined from:
- Classification uncertainty (40% weight)
- Data confidence uncertainty (30% weight)
- Factor variance (30% weight)

### Confidence Calculation

Combined from:
- Track confidence (50% weight)
- Classification confidence (30% weight)
- Data quality (20% weight)

## Threat Level Mapping (INFORMATIONAL ONLY)

| Risk Score | Threat Level |
|------------|--------------|
| ≥ 0.8      | CRITICAL     |
| 0.6 - 0.8  | HIGH         |
| 0.3 - 0.6  | MEDIUM       |
| < 0.3      | LOW          |

**IMPORTANT**: These levels are informational only and do NOT map to any actions.

## Example Scoring Explanation

### Scenario: Unknown Object Approaching Critical Zone

**Input**:
- Entity: Unknown Object (probability: 0.7, uncertainty: 0.3)
- Distance: 15 km (in Critical Zone)
- Speed: 250 m/s
- Heading: 20° towards origin
- Track confidence: 0.8

**Factor Calculations**:

1. **Entity Classification**: 0.6 × 0.7 × 0.25 = 0.105
   - Unknown object base risk: 0.6
   - Adjusted for probability: 0.6 × 0.7 = 0.42
   - Contribution: 0.42 × 0.25 = 0.105

2. **Proximity**: 0.9 × 0.25 = 0.225
   - In Critical Zone: 0.9 risk
   - Contribution: 0.9 × 0.25 = 0.225

3. **Behavior**: 0.7 × 0.20 = 0.14
   - Heading towards origin: 0.3 + 0.4 = 0.7
   - Contribution: 0.7 × 0.20 = 0.14

4. **Speed**: 0.5 × 0.15 = 0.075
   - Medium speed: 0.5 risk
   - Contribution: 0.5 × 0.15 = 0.075

5. **Trajectory**: 0.7 × 0.10 = 0.07
   - Heading towards origin: 0.7 risk
   - Contribution: 0.7 × 0.10 = 0.07

6. **Confidence**: 0.1 × 0.05 = 0.005
   - Uncertainty risk: (1.0 - 0.8) × 0.5 = 0.1
   - Contribution: 0.1 × 0.05 = 0.005

**Total Score**: 0.105 + 0.225 + 0.14 + 0.075 + 0.07 + 0.005 = **0.62**

**Threat Level**: HIGH (score 0.62 is in range 0.6-0.8)

**Threat Likelihood**: 0.62 + (0.3 × 0.2) = **0.68** (68%)

**Confidence**: ~75% (based on track confidence and classification)

**Uncertainty**: ~30% (from classification uncertainty)

## Advisory Statement

All assessment results include the following statement:

```
ADVISORY ASSESSMENT ONLY - No action recommendations. 
Threat level does not map to any action.
```

This statement is:
- Included in all outputs
- Explicitly stated in reasoning
- Part of the data model
- Cannot be removed or modified

## Configuration

The threat assessment engine uses configuration from `abhedya.infrastructure.config.config`:
- `ThreatAssessmentThresholds`: Threat level thresholds
- `ProtectedAirspaceConfiguration`: Zone definitions
- `ConfidenceThresholds`: Confidence requirements

## Limitations

1. **No Action Mapping**: Threat levels do not map to actions
2. **Probabilistic Only**: No binary decisions
3. **Advisory Only**: All outputs are informational
4. **No Recommendations**: Does not suggest any actions

## Future Enhancements

Potential additions (while maintaining advisory-only nature):
- Additional risk factors
- Adaptive factor weights
- Historical pattern analysis
- Multi-track correlation

---

**Last Updated**: 2024

