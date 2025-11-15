# Formula E Simulator - Quick Reference Card

## 🚀 Getting Started (30 seconds)

```python
from formula_e_simulator import FormulaERaceEngine

engine = FormulaERaceEngine(num_cars=24, num_laps=10)
summary = engine.run_simulation()
engine.export_to_json("race.json")
```

## 📊 Key Components

### 1. State Vector (20 dimensions per car)
```
[pos_x, pos_y, vel_x, vel_y, battery%, temp, tire_deg, grip,
 attack_on, attack_time, lap, lap_dist, accel, steer, throttle, 
 brake, active, position, gap, total_dist]
```

### 2. Physics Equations

**Motion:**
```
v(t+dt) = v(t) + a·dt
x(t+dt) = x(t) + v·dt
v_max_corner = √(μ·g·r)
```

**Energy:**
```
E_consume = k1·v² + k2·a
E_regen = 0.25·ΔKE
```

**Tires:**
```
dD/dt = f(speed, temp, aggression)
μ = 1.2·(1 - 0.3·D)
```

### 3. Probabilistic Events

- **Crash**: P = sigmoid(risk_factors)
- **Safety Car**: λ = 0.1 per lap
- **Overtake**: P = logistic(Δv, ΔE, position)

### 4. ML Strategy

**Neural Network:** [10] → [64,32,16] → [2]
- Input: state + opponents
- Output: steering, throttle

**Q-Learning:** 4D state → 4 actions
- States: [lap, energy, pos, gap]
- Actions: [conserve, neutral, aggressive, attack]

## 🎮 Usage Patterns

### Pattern 1: Run & Export
```python
engine = FormulaERaceEngine(24, 10)
summary = engine.run_simulation()
engine.export_to_json("data.json")
```

### Pattern 2: Step-by-Step
```python
engine = FormulaERaceEngine(12, 5)
while not engine.race_finished:
    state, board, events = engine.simulate_timestep()
    # Your code here
```

### Pattern 3: Custom Config
```python
track = TrackConfig("Monaco")
engine = FormulaERaceEngine(
    num_cars=20,
    track_config=track,
    use_ml_strategy=True,
    random_seed=42
)
```

### Pattern 4: State Analysis
```python
# Access state matrix
matrix = engine.race_state.get_state_matrix()  # [N×20]

# Get individual car
car = engine.race_state.cars[0]
vector = car.to_vector()  # [20]

# Check leaderboard
engine.leaderboard.print_leaderboard(10)
```

## ⚙️ Configuration Cheat Sheet

```python
from formula_e_simulator.config import PhysicsConfig

# Modify physics
PhysicsConfig.MAX_ACCELERATION = 3.0
PhysicsConfig.BATTERY_CAPACITY_KWH = 55.0
PhysicsConfig.REGEN_EFFICIENCY = 0.30

# Track segments
segment = TrackSegment(
    segment_type='straight',
    length=500,           # meters
    radius=np.inf,        # infinite for straight
    grip_level=1.0,       # 0.9-1.1
    ideal_speed_kmh=250   # km/h
)
```

## 📈 Output Data Formats

### JSON Structure
```json
{
  "race_info": {
    "track": "Monaco",
    "laps": 10,
    "race_time_seconds": 920.5
  },
  "final_standings": {
    "entries": [...]
  },
  "events": {
    "overtakes": 45,
    "crashes": 2
  }
}
```

### CSV Columns
```
Position, Driver, Laps, Best Lap, Battery %, 
Tire Deg %, Overtakes, Status
```

## 🔍 Common Operations

### Get Top 3
```python
top_3 = engine.leaderboard.get_top_n(3)
for entry in top_3:
    print(f"{entry.position}. {entry.driver_name}")
```

### Check Events
```python
crashes = engine.event_generator.get_events_by_type('crash')
overtakes = engine.event_generator.get_events_by_type('overtake')
```

### Performance Metrics
```python
rating = engine.metrics.calculate_driver_rating(car, start_pos)
comparison = engine.metrics.get_performance_comparison(car1, car2)
```

## 🎯 Performance Tips

1. **Speed up**: Set `use_ml_strategy=False`
2. **Memory**: Reduce `num_cars` and `num_laps`
3. **Accuracy**: Decrease `SimulationConfig.TIMESTEP`
4. **Logging**: Increase `display_interval` parameter

## 🐛 Quick Troubleshooting

**Import error?**
```python
import sys
sys.path.insert(0, 'path/to/src')
```

**Too slow?**
```python
engine = FormulaERaceEngine(
    num_cars=12,           # Fewer cars
    use_ml_strategy=False  # Disable ML
)
```

**Need reproducibility?**
```python
engine = FormulaERaceEngine(random_seed=42)
```

## 📚 File Quick Links

- **Main Engine**: `engine.py` - FormulaERaceEngine
- **Physics**: `physics.py` - MotionModel, EnergyModel
- **State**: `state.py` - CarState, RaceState
- **Events**: `events.py` - EventGenerator
- **ML**: `ml_strategy.py` - Neural network, Q-learning
- **Config**: `config.py` - All parameters
- **Examples**: `example_race.py` - Usage demos

## 🏆 Example Race Output

```
================================================================================
FORMULA E RACE LEADERBOARD
================================================================================
Pos  Driver           | Lap    | Interval   | Gap        | Battery  | Status
--------------------------------------------------------------------------------
1.   Driver 1         | Lap 10 | Leader     | -          | 15.3%    | ✓
2.   Driver 2         | Lap 10 | +0.234     | +0.234     | 12.1%    | ✓
3.   Driver 5         | Lap 10 | +0.156     | +0.390     | 18.7%    | ✓
```

## 🎓 Mathematical Symbols

- **v**: velocity (m/s)
- **a**: acceleration (m/s²)
- **E**: energy (Joules or kWh)
- **μ**: grip coefficient
- **D**: tire degradation (0-1)
- **T**: temperature (°C)
- **dt**: timestep (seconds)
- **λ**: Poisson rate parameter

## ⚡ Formula E Specs

- **Battery**: 51 kWh
- **Power**: 250 kW (335 kW with attack)
- **Top Speed**: 280 km/h
- **Weight**: ~900 kg
- **Acceleration**: 0-100 km/h in 2.8s
- **Regen**: Up to 250 kW

## 🔗 Quick Commands

```bash
# Test installation
python test_installation.py

# Run quick race
python run_race.py

# Run all examples
python example_race.py
```

---

**Need more details? Check README.md or TECHNICAL_DOCS.md**
