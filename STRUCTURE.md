# Abhedya Air Defense System - Folder Structure

## Defence-Grade Project Structure

```
Abhedya/
├── abhedya/                          # Main application package
│   ├── domain/                       # Domain models and entities
│   │   ├── __init__.py
│   │   ├── entities/                 # Core domain entities
│   │   ├── value_objects/            # Value objects and types
│   │   └── enums/                    # Domain enumerations
│   │
│   ├── simulation/                   # Sensor simulation layer
│   │   ├── __init__.py
│   │   ├── sensors/                 # Sensor implementations
│   │   ├── fusion/                   # Sensor fusion algorithms
│   │   └── models/                   # Simulation-specific models
│   │
│   ├── analysis/                     # Threat analysis and assessment
│   │   ├── __init__.py
│   │   ├── classification/          # Entity classification
│   │   ├── threat_assessment/       # Threat level assessment
│   │   ├── behavior_analysis/       # Behavior pattern analysis
│   │   └── explainability/          # Assessment explainability
│   │
│   ├── advisory/                     # Advisory decision-support (NO EXECUTION)
│   │   ├── __init__.py
│   │   ├── recommendation/           # Recommendation generation
│   │   ├── reasoning/               # Reasoning and explanation
│   │   └── validation/              # Recommendation validation
│   │
│   ├── interface/                    # Human-in-the-loop interface layer
│   │   ├── __init__.py
│   │   ├── presentation/            # Recommendation presentation
│   │   ├── approval/                # Approval workflow management
│   │   └── operator/                # Operator interface
│   │
│   ├── infrastructure/              # Infrastructure and cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── audit/                   # Audit logging and trail
│   │   ├── config/                  # Configuration management
│   │   ├── logging/                 # Application logging
│   │   └── validation/              # Safety and validation
│   │
│   ├── core/                         # Core system orchestration
│   │   ├── __init__.py
│   │   ├── system.py                # Main system orchestrator
│   │   ├── interfaces.py            # Component interfaces
│   │   └── constants.py             # System constants
│   │
│   └── __init__.py
│
├── tests/                             # Test suite
│   ├── unit/                         # Unit tests
│   │   ├── domain/
│   │   ├── simulation/
│   │   ├── analysis/
│   │   ├── advisory/
│   │   └── interface/
│   ├── integration/                  # Integration tests
│   ├── safety/                       # Safety constraint tests
│   └── fixtures/                     # Test fixtures and mocks
│
├── docs/                              # Documentation
│   ├── architecture/                 # Architecture documentation
│   ├── api/                          # API documentation
│   ├── ethics/                       # Ethics and compliance
│   └── user_guide/                   # User guides
│
├── config/                            # Configuration files
│   ├── default.yaml                  # Default configuration
│   ├── development.yaml              # Development configuration
│   └── production.yaml               # Production configuration
│
├── scripts/                           # Utility scripts
│   ├── setup.py                      # Setup scripts
│   └── validation.py                 # Validation scripts
│
├── examples/                          # Example scenarios
│   ├── basic/                        # Basic examples
│   ├── scenarios/                    # Scenario demonstrations
│   └── tutorials/                    # Tutorial examples
│
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Development dependencies
├── setup.py                          # Package setup
├── README.md                          # Project overview
├── LICENSE                            # License file
├── .gitignore                         # Git ignore rules
└── pyproject.toml                     # Modern Python project config
```

## Directory Explanations

### `abhedya/domain/`
**Purpose**: Core domain models, entities, and business logic
- **entities/**: Core domain entities (Track, Entity, Threat, etc.)
- **value_objects/**: Immutable value objects (Coordinates, Velocity, etc.)
- **enums/**: Domain enumerations (EntityType, ThreatLevel, etc.)
- **Separation**: Pure domain logic, no infrastructure dependencies

### `abhedya/simulation/`
**Purpose**: Sensor simulation and detection systems
- **sensors/**: Sensor implementations (Radar, IFF, Optical, etc.)
- **fusion/**: Sensor fusion algorithms and track correlation
- **models/**: Simulation-specific data models
- **Separation**: Strictly simulation - no real hardware interfaces

### `abhedya/analysis/`
**Purpose**: Threat analysis, classification, and assessment
- **classification/**: Entity classification algorithms
- **threat_assessment/**: Threat level evaluation
- **behavior_analysis/**: Behavioral pattern recognition
- **explainability/**: Assessment explanation generation
- **Separation**: Analysis only - no decision execution

### `abhedya/advisory/`
**Purpose**: Advisory recommendation generation (NO EXECUTION AUTHORITY)
- **recommendation/**: Recommendation generation logic
- **reasoning/**: Probabilistic reasoning and explanation
- **validation/**: Recommendation validation and safety checks
- **Separation**: Advisory only - explicitly no execution capability

### `abhedya/interface/`
**Purpose**: Human-in-the-loop interface and approval workflows
- **presentation/**: Recommendation presentation to operators
- **approval/**: Approval workflow management
- **operator/**: Operator interface components
- **Separation**: Interface layer - mandatory human interaction

### `abhedya/infrastructure/`
**Purpose**: Cross-cutting infrastructure concerns
- **audit/**: Audit logging and trail management
- **config/**: Configuration management
- **logging/**: Application logging
- **validation/**: Safety and constraint validation
- **Separation**: Infrastructure - supports all layers

### `abhedya/core/`
**Purpose**: System orchestration and coordination
- **system.py**: Main system orchestrator
- **interfaces.py**: Component interface definitions
- **constants.py**: System-wide constants and defaults
- **Separation**: Orchestration only - coordinates components

### `tests/`
**Purpose**: Comprehensive test suite
- **unit/**: Unit tests for each module
- **integration/**: Integration tests
- **safety/**: Safety constraint validation tests
- **fixtures/**: Test data and mocks

### `docs/`
**Purpose**: System documentation
- **architecture/**: Architecture documentation
- **api/**: API reference
- **ethics/**: Ethics and compliance documentation
- **user_guide/**: User guides and tutorials

### `config/`
**Purpose**: Configuration files
- YAML-based configuration
- Environment-specific configs
- Fail-safe defaults enforced

### `scripts/`
**Purpose**: Utility and setup scripts
- Setup and installation scripts
- Validation and safety checks

### `examples/`
**Purpose**: Example scenarios and demonstrations
- Basic usage examples
- Scenario demonstrations
- Tutorial materials

## Design Principles

### 1. Strict Separation of Concerns
- **Simulation**: Isolated sensor simulation layer
- **Analysis**: Separate threat analysis logic
- **Advisory**: Advisory-only, no execution authority
- **Interface**: Human interface layer (mandatory)

### 2. No Execution Authority
- No modules with execution capability
- Advisory logic explicitly separated
- All recommendations require human approval
- Fail-safe defaults enforced

### 3. Defence-Grade Structure
- Clear module boundaries
- Auditable code organization
- Professional naming conventions
- Comprehensive documentation structure

### 4. Extensibility
- Interface-based design
- Modular components
- Easy to add new sensors, analyzers, advisors
- Clear extension points

## Safety Guarantees

1. **No Execution Modules**: No modules contain execution authority
2. **Clear Boundaries**: Strict separation prevents accidental execution
3. **Interface Enforcement**: All components implement defined interfaces
4. **Validation Layer**: Infrastructure validation ensures safety constraints
5. **Audit Trail**: Complete traceability through infrastructure layer

