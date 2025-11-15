# Formula E Race Simulator

A comprehensive, mathematically rigorous Formula E race simulation engine built in Python. This simulator implements a high-dimensional vector space framework to model complete race dynamics including physics, energy management, tire degradation, probabilistic events, and machine learning-based strategy.

## 🏎️ Features

### Core Capabilities

- **Vector Space Framework**: High-dimensional state representation for complete race physics
- **Realistic Physics Engine**: 
  - 2D kinematic motion with acceleration/deceleration constraints
  - Energy consumption and regenerative braking models
  - Tire degradation and grip dynamics
  - Battery temperature simulation
  - Attack mode boost mechanics

- **Probabilistic Event System**:
  - Crash probability (sigmoid function based on risk factors)
  - Safety car deployment (Poisson process)
  - Overtaking probability (logistic regression)
  - Driver performance variation (normal distribution)

- **Machine Learning Integration**:
  - Neural network for racing line prediction
  - Q-learning agent for energy management strategy
  - Adaptive decision-making based on race state

- **Real-time Leaderboard**: Live race standings with gaps, intervals, and performance metrics

- **Comprehensive Output**: JSON and CSV export for data analysis and visualization

## 📊 System Architecture

```
formula_e_simulator/
├── config.py          # Physical constants, track configuration, tunable parameters
├── state.py           # State vector representation (CarState, RaceState)
├── physics.py         # Physics models (motion, energy, tires, temperature)
├── events.py          # Probabilistic event generators
├── ml_strategy.py     # Neural network + Q-learning components
├── leaderboard.py     # Real-time standings and performance metrics
├── engine.py          # Main simulation engine (FormulaERaceEngine)
├── example_race.py    # Comprehensive usage examples
└── run_race.py        # Quick start script
```

## 🚀 Quick Start

### Installation

```bash
# Install required dependencies
pip install numpy scipy scikit-learn pandas

# Navigate to the simulator directory
cd src/formula_e_simulator
```

### Run Your First Race

```python
from formula_e_simulator import FormulaERaceEngine

# Create race engine
engine = FormulaERaceEngine(
    num_cars=24,
    num_laps=10,
    use_ml_strategy=True,
    random_seed=42
)

# Run simulation
summary = engine.run_simulation(verbose=True)

# Export results
engine.export_to_json("race_results.json")
engine.export_to_csv("leaderboard.csv")
```

Or use the quick start script:

```bash
python run_race.py
```

## 📖 Detailed Usage Examples

### Example 1: Basic Race

```python
from formula_e_simulator import FormulaERaceEngine

engine = FormulaERaceEngine(num_cars=24, num_laps=10)
summary = engine.run_simulation()
```

### Example 2: Custom Track

```python
from formula_e_simulator import FormulaERaceEngine, TrackConfig

# Create custom track
custom_track = TrackConfig(track_name="Monaco Street Circuit")
engine = FormulaERaceEngine(num_cars=20, num_laps=15, track_config=custom_track)
summary = engine.run_simulation()
```

### Example 3: Step-by-Step Simulation

```python
engine = FormulaERaceEngine(num_cars=12, num_laps=5)

while not engine.race_finished:
    state_matrix, leaderboard, events = engine.simulate_timestep()
    
    # Process state_matrix for custom analysis
    # state_matrix shape: [num_cars, state_dimension]
    
    # Check for events
    for event in events:
        print(f"Event: {event['description']}")
```

### Example 4: Access State Vectors

```python
engine = FormulaERaceEngine(num_cars=6, num_laps=3)

# Get state matrix for all cars
state_matrix = engine.race_state.get_state_matrix()
# Shape: [6, 20] - 6 cars, 20-dimensional state vector

# Access individual car state
car = engine.race_state.cars[0]
state_vector = car.to_vector()

# State vector components:
# [pos_x, pos_y, vel_x, vel_y, battery_%, temp, tire_deg, grip,
#  attack_active, attack_remaining, lap, lap_dist, accel, steering,
#  throttle, brake, is_active, position, gap, total_distance]
```

## 🔬 Mathematical Models

### Motion Model

```
dv/dt = a(t)
v_max_corner = sqrt(μ * g * r)
where:
  a_max = 2.8 m/s² (acceleration)
  a_min = -3.5 m/s² (braking with regen)
  v_max = 280 km/h
```

### Energy Model

```
E_consumed = k1 * v² * dt + k2 * a * dt
E_regen = η * ΔKE
where:
  k1 = 0.15 (velocity coefficient)
  k2 = 50.0 (acceleration coefficient)
  η = 0.25 (regeneration efficiency)
```

### Tire Degradation Model

```
dD/dt = k_base + k_temp * (T - T_opt)² + k_speed * v²
μ(t) = μ_max * (1 - 0.3 * D(t))
where:
  D ∈ [0,1] (degradation level)
  μ_max = 1.2 (maximum grip)
```

### Crash Probability (Sigmoid)

```
P(crash) = 1 / (1 + exp(-k * (risk - x0)))
risk = f(speed, tire_deg, aggression, proximity, energy)
```

## 🤖 Machine Learning Components

### Neural Network (Racing Line Predictor)

- **Input**: [position, velocity, energy, tire_state, opponents, segment]
- **Architecture**: Feedforward MLP with [64, 32, 16] hidden layers
- **Output**: [steering_angle, throttle_percentage]
- **Training**: Online learning from race outcomes

### Q-Learning (Energy Management)

- **State Space**: Discretized [lap, energy, position, gap]
- **Actions**: [conserve, neutral, aggressive, activate_attack]
- **Reward Function**: Based on position, overtakes, energy efficiency
- **Update Rule**: Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]

## 📊 Output Data

### JSON Export Structure

```json
{
  "race_info": {
    "track": "Monaco",
    "laps": 10,
    "total_distance_km": 25.0,
    "race_time_seconds": 920.5
  },
  "final_standings": {
    "entries": [
      {
        "position": 1,
        "driver_name": "Driver 1",
        "current_lap": 10,
        "battery_percentage": 15.3,
        "best_lap_time": 88.234
      }
    ]
  },
  "events": {
    "overtakes": 45,
    "crashes": 2,
    "attack_modes": 38
  }
}
```

### CSV Export (Leaderboard)

```
Position,Driver,Laps,Best Lap,Battery %,Tire Deg %,Overtakes,Status
1,Driver 1,10,88.234,15.3,67.2,5,Running
2,Driver 2,10,88.891,12.1,71.8,3,Running
...
```

## ⚙️ Configuration

All parameters are tunable via configuration classes:

```python
from formula_e_simulator.config import PhysicsConfig

# Modify physics parameters
PhysicsConfig.MAX_ACCELERATION = 3.0  # Increase acceleration
PhysicsConfig.BATTERY_CAPACITY_KWH = 55.0  # Larger battery
PhysicsConfig.REGEN_EFFICIENCY = 0.30  # Better regen

# Create track with custom segments
track = TrackConfig()
track.segments[0].grip_level = 1.1  # Higher grip on first segment
```

## 🎯 Performance

- **Simulation Speed**: 10-20x real-time (depends on hardware)
- **Scalability**: Supports up to 24 cars simultaneously
- **Numerical Stability**: Maintained over 45+ minute race simulations
- **Vectorization**: NumPy-optimized for efficient computation

## 🧪 Advanced Features

### Custom Event Handlers

```python
# Access event generator
events = engine.event_generator

# Check specific event types
crashes = events.get_events_by_type('crash')
overtakes = events.get_events_by_type('overtake')
```

### Performance Metrics

```python
metrics = engine.metrics

# Get driver rating
rating = metrics.calculate_driver_rating(car, starting_position=5)

# Compare two drivers
comparison = metrics.get_performance_comparison(car1, car2)
```

### Real-time Monitoring

```python
while not engine.race_finished:
    state_matrix, leaderboard, events = engine.simulate_timestep()
    
    # Update external visualization
    update_visualization(state_matrix)
    
    # Log to database
    log_race_state(leaderboard)
```

## 📚 Complete Examples

Run the comprehensive example suite:

```bash
python example_race.py
```

This demonstrates:
1. Basic race simulation
2. Custom track configuration  
3. Step-by-step monitoring
4. ML vs simple strategy comparison
5. State vector framework usage

## 🔧 Requirements

- Python 3.7+
- numpy >= 1.19.0
- scipy >= 1.5.0
- scikit-learn >= 0.23.0
- pandas >= 1.1.0

## 📝 Technical Specifications

- **State Vector Dimension**: 20 per car
- **Simulation Timestep**: 0.1 seconds (10 Hz)
- **Track Length**: ~2-3 km (configurable)
- **Physics Update Rate**: 10 Hz
- **Random Seeds**: Controllable for reproducibility

## 🏆 Use Cases

- **Research**: Study race strategy optimization
- **Education**: Learn physics-based simulation
- **Game Development**: Backend for racing games
- **Data Analysis**: Generate datasets for ML training
- **Strategy Testing**: Evaluate different racing approaches

## 📄 License

See LICENSE file for details.

## 👥 Contributors

Formula E Simulator Team

---

**Ready to race? Start your engines! 🏁**
