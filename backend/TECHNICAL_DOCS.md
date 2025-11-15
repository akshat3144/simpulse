# Formula E Race Simulator - Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Mathematical Framework](#mathematical-framework)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Configuration Guide](#configuration-guide)
6. [Performance Optimization](#performance-optimization)
7. [Extension Guide](#extension-guide)

---

## System Overview

The Formula E Race Simulator is a comprehensive, physics-based racing simulation engine that models the complete dynamics of Formula E electric racing. It implements a **high-dimensional vector space framework** where each point represents the complete physical reality of the race at time t.

### Key Features
- **Vector Space State Representation**: 20-dimensional state vectors per car
- **Physics-Based Motion**: Realistic kinematics with energy constraints
- **Probabilistic Events**: Crashes, safety cars, overtakes using statistical models
- **Machine Learning Strategy**: Neural networks + Q-learning for adaptive racing
- **Real-Time Simulation**: 10-20x real-time speed capability

---

## Mathematical Framework

### 1. State Space Definition

Each car exists in a 20-dimensional state space:

**State Vector S(t) = [s₁, s₂, ..., s₂₀]**

```
s₁, s₂    : Position (x, y) [meters]
s₃, s₄    : Velocity (vₓ, vᵧ) [m/s]
s₅        : Battery percentage [0-100]
s₆        : Battery temperature [°C]
s₇        : Tire degradation [0-1]
s₈        : Grip coefficient [0-1.2]
s₉        : Attack mode active [boolean]
s₁₀       : Attack mode remaining [seconds]
s₁₁       : Current lap [integer]
s₁₂       : Lap distance [meters]
s₁₃       : Acceleration [m/s²]
s₁₄       : Steering angle [radians]
s₁₅       : Throttle [0-1]
s₁₆       : Brake [0-1]
s₁₇       : Is active [boolean]
s₁₈       : Position [integer]
s₁₉       : Gap to leader [seconds]
s₂₀       : Total distance [meters]
```

### 2. Motion Dynamics

**Position Update:**
```
x(t+Δt) = x(t) + v(t)·Δt
```

**Velocity Update:**
```
v(t+Δt) = v(t) + a(t)·Δt
where: a_max = 2.8 m/s², a_min = -3.5 m/s²
```

**Corner Speed Limit:**
```
v_max(corner) = √(μ·g·r)
where:
  μ = grip coefficient (0.3-1.2)
  g = 9.81 m/s²
  r = corner radius [m]
```

### 3. Energy Model

**Consumption Rate:**
```
dE/dt = -[k₁·v²(t) + k₂·a(t)]
where:
  k₁ = 0.15 (velocity-dependent term)
  k₂ = 50.0 (acceleration-dependent term)
  E₀ = 51 kWh = 183.6 MJ
```

**Regenerative Braking:**
```
E_regen = η·ΔKE = η·½·m·(v₁² - v₂²)
where:
  η = 0.25 (25% efficiency)
  m = 900 kg (car mass)
```

**Attack Mode Boost:**
```
P_boost = 50 kW for 240 seconds
v_boost = 1.08 × v_normal
Activations: 2 per race
```

### 4. Tire Degradation

**Degradation Rate:**
```
dD/dt = k_base + k_temp·(T - T_opt)² + k_speed·v²
where:
  k_base = 0.0001
  k_temp = 0.00001
  k_speed = 0.000005
  T_opt = 80°C
```

**Grip Model:**
```
μ(D) = μ_max·(1 - α·D)
where:
  μ_max = 1.2
  α = 0.3 (30% loss at full degradation)
  D ∈ [0,1]
```

### 5. Probabilistic Models

**Crash Probability (Sigmoid):**
```
P(crash) = 1 / (1 + e^(-k·(R - R₀)))
where:
  R = risk_score (weighted sum of factors)
  k = 0.1 (steepness)
  R₀ = 50.0 (threshold)
  
Risk factors:
  R = 30·(v/v_max) + 25·D_tire + 20·aggression + 15·proximity + 10·energy_stress
```

**Safety Car (Poisson Process):**
```
P(safety_car) = 1 - e^(-λ)
where:
  λ = 0.1 per lap
  Expected frequency: ~1 per 10 laps
```

**Overtake Probability (Logistic Regression):**
```
P(overtake) = 1 / (1 + e^(-z))
where:
  z = β₁·Δv + β₂·ΔE + β₃·attack + β₄·track + β₅·Δtire
  
Coefficients:
  β₁ = 0.5 (speed differential)
  β₂ = 0.02 (battery differential)
  β₃ = 0.3 (attack mode advantage)
  β₄ = track factor (0.3-0.8)
  β₅ = 0.4 (tire differential)
```

**Driver Performance Variation:**
```
skill(t) ~ N(μ, σ²)
where:
  μ = base_skill (0.8-1.2)
  σ = 0.05
```

### 6. Temperature Model

**Battery Temperature:**
```
dT/dt = α·|E_consumed| - β·(T - T_ambient)
where:
  α = 0.01 (heating rate)
  β = 0.005 (cooling rate)
  T_ambient = 25°C
```

**Efficiency Factor:**
```
η_temp(T) = max(0.8, 1 - |T - T_opt|/100)
where:
  T_opt = 40°C
```

---

## Architecture

### Module Structure

```
formula_e_simulator/
│
├── config.py              # Configuration classes
│   ├── PhysicsConfig      # Physical constants
│   ├── TrackConfig        # Track geometry
│   ├── SimulationConfig   # Runtime parameters
│   ├── MLConfig           # ML hyperparameters
│   └── DriverConfig       # Driver profiles
│
├── state.py               # State representation
│   ├── CarState          # Individual car state
│   └── RaceState         # Complete race state
│
├── physics.py             # Physics engine
│   ├── MotionModel       # Kinematic updates
│   ├── EnergyModel       # Battery management
│   ├── TireModel         # Degradation & grip
│   ├── TemperatureModel  # Thermal dynamics
│   └── PhysicsEngine     # Main physics coordinator
│
├── events.py              # Event system
│   ├── Event             # Event base class
│   ├── EventGenerator    # Probabilistic events
│   └── StrategyDecisionMaker  # Strategy logic
│
├── ml_strategy.py         # ML components
│   ├── RacingLinePredictor    # Neural network
│   ├── EnergyManagementQLearning  # Q-learning
│   └── MLStrategyCoordinator  # ML integration
│
├── leaderboard.py         # Rankings & metrics
│   ├── LeaderboardEntry  # Single entry
│   ├── Leaderboard       # Standings manager
│   └── PerformanceMetrics  # Statistics
│
└── engine.py              # Main simulation engine
    └── FormulaERaceEngine  # Orchestrates all components
```

### Data Flow

```
┌─────────────────────────────────────────────────────┐
│           FormulaERaceEngine.simulate_timestep()    │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌────────┐   ┌──────────┐   ┌──────────┐
│Physics │   │  Events  │   │    ML    │
│Engine  │   │Generator │   │ Strategy │
└────┬───┘   └────┬─────┘   └────┬─────┘
     │            │              │
     └────────────┼──────────────┘
                  ▼
         ┌────────────────┐
         │   RaceState    │
         │  (State Matrix)│
         └────────┬───────┘
                  │
         ┌────────┼────────┐
         ▼        ▼        ▼
    ┌─────────┐ ┌──────┐ ┌────────┐
    │Leaderbd │ │Metric│ │ Output │
    │ Manager │ │  s   │ │Export  │
    └─────────┘ └──────┘ └────────┘
```

---

## API Reference

### FormulaERaceEngine

**Constructor:**
```python
FormulaERaceEngine(
    num_cars: int = 24,
    num_laps: int = 10,
    track_config: Optional[TrackConfig] = None,
    use_ml_strategy: bool = True,
    random_seed: Optional[int] = None
)
```

**Methods:**

**simulate_timestep(dt: float = None) -> Tuple[ndarray, List[Dict], List[Dict]]**
- Simulates one timestep
- Returns: (state_matrix, leaderboard_data, events)

**run_simulation(display_interval: int = 100, verbose: bool = True) -> Dict**
- Runs complete race simulation
- Returns: comprehensive race summary

**get_leaderboard() -> List[Dict]**
- Returns current standings

**detect_events() -> List[Dict]**
- Returns recent events

**export_to_json(filepath: str)**
- Exports race data to JSON

**export_to_csv(filepath: str)**
- Exports leaderboard to CSV

### CarState

**Key Attributes:**
- `position_x, position_y`: Position coordinates
- `velocity_x, velocity_y`: Velocity components
- `battery_percentage`: Remaining battery (0-100%)
- `tire_degradation`: Tire wear (0-1)
- `attack_mode_active`: Attack mode status

**Methods:**
- `to_vector() -> ndarray`: Convert to state vector
- `get_speed() -> float`: Current speed (m/s)
- `activate_attack_mode() -> bool`: Activate attack mode
- `to_dict() -> Dict`: Export to dictionary

### RaceState

**Attributes:**
- `cars: List[CarState]`: All car states
- `current_time: float`: Race time
- `safety_car_active: bool`: Safety car status

**Methods:**
- `get_state_matrix() -> ndarray`: Get [N×20] state matrix
- `update_positions()`: Recalculate race positions
- `get_active_cars() -> List[CarState]`: Active cars only

---

## Configuration Guide

### Physics Configuration

```python
from formula_e_simulator.config import PhysicsConfig

# Modify parameters
PhysicsConfig.MAX_ACCELERATION = 3.0  # Increase power
PhysicsConfig.BATTERY_CAPACITY_KWH = 55.0  # Larger battery
PhysicsConfig.REGEN_EFFICIENCY = 0.30  # Better regen
PhysicsConfig.MU_MAX = 1.3  # More grip
```

### Track Configuration

```python
from formula_e_simulator.config import TrackConfig, TrackSegment

# Create custom track
track = TrackConfig(track_name="Custom Circuit")

# Add custom segments
track.segments = [
    TrackSegment('straight', 600, np.inf, 1.0, 280),
    TrackSegment('right_corner', 200, 80, 0.95, 120),
    # ... more segments
]
```

### ML Configuration

```python
from formula_e_simulator.config import MLConfig

config = MLConfig()
config.NN_HIDDEN_LAYERS = [128, 64, 32]  # Deeper network
config.Q_LEARNING_RATE = 0.15  # Faster learning
config.Q_EPSILON = 0.15  # More exploration
```

---

## Performance Optimization

### Vectorization

All physics calculations use NumPy vectorization:

```python
# Bad: Loop over cars
for car in cars:
    car.velocity += car.acceleration * dt

# Good: Vectorized operation
velocities = state_matrix[:, 2:4]
accelerations = state_matrix[:, 12]
velocities += accelerations * dt
```

### Timestep Selection

- Smaller dt: More accurate, slower
- Larger dt: Faster, potential instability
- Recommended: dt = 0.1 seconds (10 Hz)

### Memory Management

State matrix preallocated:
```python
state_matrix = np.zeros((num_cars, 20))
# Reuse same array throughout simulation
```

### Parallel Processing

Currently single-threaded. For parallel:
```python
from multiprocessing import Pool

def update_car(car_state):
    # Update physics for one car
    return updated_state

with Pool(processes=4) as pool:
    updated_states = pool.map(update_car, cars)
```

---

## Extension Guide

### Adding Custom Physics Models

```python
from formula_e_simulator.physics import PhysicsEngine

class CustomPhysicsEngine(PhysicsEngine):
    def update_car_physics(self, car, dt, ...):
        # Call parent
        super().update_car_physics(car, dt, ...)
        
        # Add custom physics
        car.custom_attribute = self.calculate_custom(car)
```

### Adding New Events

```python
from formula_e_simulator.events import Event, EventGenerator

class CustomEvent(Event):
    def __init__(self, timestamp, data):
        super().__init__('custom', timestamp, f"Custom: {data}")

# In EventGenerator
def check_custom_event(self, car):
    if self.custom_condition(car):
        event = CustomEvent(car.time, car.data)
        self.events.append(event)
        return True, event
    return False, None
```

### Custom ML Models

```python
from formula_e_simulator.ml_strategy import MLStrategyCoordinator

class CustomMLStrategy(MLStrategyCoordinator):
    def __init__(self, seed=None):
        super().__init__(seed)
        # Add custom model
        self.custom_model = YourCustomModel()
    
    def get_ml_controls(self, car, ...):
        # Override with custom logic
        return custom_steering, custom_throttle, custom_strategy
```

### Data Export Extensions

```python
# Add custom data export
def export_telemetry(engine, filepath):
    telemetry = {
        'timestamp': [],
        'speeds': [],
        'energies': [],
        # ... custom fields
    }
    
    for car in engine.race_state.cars:
        telemetry['speeds'].append(car.get_speed())
        # ... collect data
    
    with open(filepath, 'w') as f:
        json.dump(telemetry, f)
```

---

## Troubleshooting

### Common Issues

**1. Import Errors**
```python
# Solution: Add parent directory to path
import sys
sys.path.insert(0, 'path/to/src')
from formula_e_simulator import FormulaERaceEngine
```

**2. Numerical Instability**
- Reduce timestep: `dt = 0.05`
- Check for infinite/NaN values
- Ensure proper value clipping

**3. Slow Performance**
- Disable ML: `use_ml_strategy=False`
- Reduce car count
- Increase display interval

**4. Memory Issues**
- Use fewer laps
- Clear event log periodically
- Reduce logging frequency

---

## References

- Formula E Technical Regulations 2024
- Vehicle Dynamics: Theory and Application (Rajamani)
- Reinforcement Learning: An Introduction (Sutton & Barto)
- NumPy Documentation: numpy.org

---

**Version:** 1.0.0  
**Last Updated:** 2025  
**Maintainer:** Formula E Simulator Team
