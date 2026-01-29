# Threat Assessment Scoring Examples

## Example 1: Unknown Object Approaching Critical Zone

### Input Data
- **Entity Type**: Unknown Object
  - Classification probability: 0.7
  - Classification uncertainty: 0.3
- **Position**: 15,000 m from origin (in Critical Zone)
- **Velocity**: 250 m/s, heading 20° towards origin
- **Track Confidence**: 0.8

### Factor Calculations

#### 1. Entity Classification Factor (Weight: 25%)
- Base risk for Unknown Object: 0.6
- Adjusted for probability: 0.6 × 0.7 = 0.42
- Adjusted for uncertainty: 0.42 × (1.0 - 0.3 × 0.3) = 0.38
- **Factor Value**: 0.38
- **Contribution**: 0.38 × 0.25 = **0.095**

#### 2. Proximity Factor (Weight: 25%)
- Distance: 15 km (in Critical Zone)
- Proximity risk: 0.9
- Distance factor: 1.0 - (15000 / 200000) = 0.925
- Adjusted risk: 0.9 × (0.5 + 0.5 × 0.925) = 0.89
- **Factor Value**: 0.89
- **Contribution**: 0.89 × 0.25 = **0.223**

#### 3. Behavior Factor (Weight: 20%)
- Heading towards origin (20°): +0.4
- Speed 250 m/s: +0.2
- Base risk: 0.3
- **Factor Value**: 0.3 + 0.4 + 0.2 = 0.9
- **Contribution**: 0.9 × 0.20 = **0.18**

#### 4. Speed Factor (Weight: 15%)
- Speed: 250 m/s (medium-high)
- Speed risk: 0.5
- **Factor Value**: 0.5
- **Contribution**: 0.5 × 0.15 = **0.075**

#### 5. Trajectory Factor (Weight: 10%)
- Heading 20° towards origin (< 45°)
- Trajectory risk: 0.7
- **Factor Value**: 0.7
- **Contribution**: 0.7 × 0.10 = **0.07**

#### 6. Confidence Factor (Weight: 5%)
- Track confidence: 0.8
- Uncertainty risk: (1.0 - 0.8) × 0.5 = 0.1
- **Factor Value**: 0.1
- **Contribution**: 0.1 × 0.05 = **0.005**

### Total Score Calculation
```
Total Score = 0.095 + 0.223 + 0.18 + 0.075 + 0.07 + 0.005
            = 0.648
```

### Assessment Results
- **Risk Score**: 0.648
- **Threat Level**: HIGH (0.648 is in range 0.6-0.8)
- **Threat Likelihood**: 0.648 + (0.3 × 0.2) = 0.708 (70.8%)
- **Confidence**: ~75%
- **Uncertainty**: ~30%

### Score Breakdown (Percentages)
- Entity Classification: 14.7% of total
- Proximity: 34.4% of total
- Behavior: 27.8% of total
- Speed: 11.6% of total
- Trajectory: 10.8% of total
- Confidence: 0.8% of total

---

## Example 2: Known Aircraft in Extended Zone

### Input Data
- **Entity Type**: Aircraft
  - Classification probability: 0.9
  - Classification uncertainty: 0.1
- **Position**: 80,000 m from origin (in Extended Zone)
- **Velocity**: 300 m/s, heading 120° (departing)
- **Track Confidence**: 0.9

### Factor Calculations

#### 1. Entity Classification Factor (Weight: 25%)
- Base risk for Aircraft: 0.3
- Adjusted for probability: 0.3 × 0.9 = 0.27
- Adjusted for uncertainty: 0.27 × (1.0 - 0.1 × 0.3) = 0.26
- **Factor Value**: 0.26
- **Contribution**: 0.26 × 0.25 = **0.065**

#### 2. Proximity Factor (Weight: 25%)
- Distance: 80 km (in Extended Zone)
- Proximity risk: 0.4
- Distance factor: 1.0 - (80000 / 200000) = 0.6
- Adjusted risk: 0.4 × (0.5 + 0.5 × 0.6) = 0.32
- **Factor Value**: 0.32
- **Contribution**: 0.32 × 0.25 = **0.08**

#### 3. Behavior Factor (Weight: 20%)
- Heading 120° (departing): 0.0
- Speed 300 m/s: +0.2
- Base risk: 0.3
- **Factor Value**: 0.3 + 0.2 = 0.5
- **Contribution**: 0.5 × 0.20 = **0.10**

#### 4. Speed Factor (Weight: 15%)
- Speed: 300 m/s (high)
- Speed risk: 0.8
- **Factor Value**: 0.8
- **Contribution**: 0.8 × 0.15 = **0.12**

#### 5. Trajectory Factor (Weight: 10%)
- Heading 120° (departing, > 90°)
- Trajectory risk: 0.3
- **Factor Value**: 0.3
- **Contribution**: 0.3 × 0.10 = **0.03**

#### 6. Confidence Factor (Weight: 5%)
- Track confidence: 0.9
- Uncertainty risk: (1.0 - 0.9) × 0.5 = 0.05
- **Factor Value**: 0.05
- **Contribution**: 0.05 × 0.05 = **0.0025**

### Total Score Calculation
```
Total Score = 0.065 + 0.08 + 0.10 + 0.12 + 0.03 + 0.0025
            = 0.3975
```

### Assessment Results
- **Risk Score**: 0.398
- **Threat Level**: MEDIUM (0.398 is in range 0.3-0.6)
- **Threat Likelihood**: 0.398 + (0.1 × 0.2) = 0.418 (41.8%)
- **Confidence**: ~85%
- **Uncertainty**: ~10%

### Score Breakdown (Percentages)
- Entity Classification: 16.3% of total
- Proximity: 20.1% of total
- Behavior: 25.2% of total
- Speed: 30.2% of total
- Trajectory: 7.5% of total
- Confidence: 0.6% of total

---

## Example 3: Low Confidence Unknown Object

### Input Data
- **Entity Type**: Unknown Object
  - Classification probability: 0.4
  - Classification uncertainty: 0.6
- **Position**: 120,000 m from origin (outside zones)
- **Velocity**: 50 m/s, heading 45° (somewhat towards origin)
- **Track Confidence**: 0.5

### Factor Calculations

#### 1. Entity Classification Factor (Weight: 25%)
- Base risk for Unknown Object: 0.6
- Adjusted for probability: 0.6 × 0.4 = 0.24
- Adjusted for uncertainty: 0.24 × (1.0 - 0.6 × 0.3) = 0.20
- **Factor Value**: 0.20
- **Contribution**: 0.20 × 0.25 = **0.05**

#### 2. Proximity Factor (Weight: 25%)
- Distance: 120 km (outside zones)
- Proximity risk: 0.1
- Distance factor: 1.0 - (120000 / 200000) = 0.4
- Adjusted risk: 0.1 × (0.5 + 0.5 × 0.4) = 0.07
- **Factor Value**: 0.07
- **Contribution**: 0.07 × 0.25 = **0.0175**

#### 3. Behavior Factor (Weight: 20%)
- Heading 45° (somewhat towards origin): +0.2
- Speed 50 m/s: 0.0
- Base risk: 0.3
- **Factor Value**: 0.3 + 0.2 = 0.5
- **Contribution**: 0.5 × 0.20 = **0.10**

#### 4. Speed Factor (Weight: 15%)
- Speed: 50 m/s (low)
- Speed risk: 0.1
- **Factor Value**: 0.1
- **Contribution**: 0.1 × 0.15 = **0.015**

#### 5. Trajectory Factor (Weight: 10%)
- Heading 45° (somewhat towards origin, 45-90°)
- Trajectory risk: 0.5
- **Factor Value**: 0.5
- **Contribution**: 0.5 × 0.10 = **0.05**

#### 6. Confidence Factor (Weight: 5%)
- Track confidence: 0.5
- Uncertainty risk: (1.0 - 0.5) × 0.5 = 0.25
- **Factor Value**: 0.25
- **Contribution**: 0.25 × 0.05 = **0.0125**

### Total Score Calculation
```
Total Score = 0.05 + 0.0175 + 0.10 + 0.015 + 0.05 + 0.0125
            = 0.245
```

### Assessment Results
- **Risk Score**: 0.245
- **Threat Level**: LOW (0.245 < 0.3)
- **Threat Likelihood**: 0.245 + (0.6 × 0.2) = 0.365 (36.5%)
- **Confidence**: ~50%
- **Uncertainty**: ~60%

### Score Breakdown (Percentages)
- Entity Classification: 20.4% of total
- Proximity: 7.1% of total
- Behavior: 40.8% of total
- Speed: 6.1% of total
- Trajectory: 20.4% of total
- Confidence: 5.1% of total

---

## Key Observations

### Score Distribution Patterns

1. **High Threat Scenarios**:
   - High proximity factor (in Critical Zone)
   - High behavior factor (approaching)
   - Unknown or hostile entity type

2. **Medium Threat Scenarios**:
   - Medium proximity (in Protected/Extended Zone)
   - Mixed behavior patterns
   - Known entity types with some risk factors

3. **Low Threat Scenarios**:
   - Low proximity (outside zones)
   - Departing or neutral behavior
   - Known entity types

### Uncertainty Impact

- **High Uncertainty**: Increases threat likelihood but decreases confidence
- **Low Uncertainty**: More confident assessment, but may still have high risk

### Factor Weighting

- **Proximity and Entity Classification**: Highest weights (25% each)
- **Behavior**: Significant weight (20%)
- **Speed and Trajectory**: Moderate weights (15%, 10%)
- **Confidence**: Lowest weight (5%) but still important

---

**IMPORTANT REMINDER**: All threat assessments are ADVISORY ONLY. Threat levels do NOT map to any actions. All outputs explicitly state "Advisory Assessment Only".

---

**Last Updated**: 2024

