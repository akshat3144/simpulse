# SimPulse: Competitive Mobility Systems Simulator

**A lightweight, mathematically rigorous simulation framework for competitive motion, decision-making, and event-driven dynamics**

![SimPulse](https://img.shields.io/badge/SimPulse-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 🎯 Vision

SimPulse models multiple competing entities moving within dynamic environments — from Formula E cars and MotoGP bikes to drone swarms and autonomous vehicle trials. The framework captures the essence of competitive motion, strategic decision-making, and stochastic uncertainty in real time.

**Key Innovation**: Vector space representation + probabilistic dynamics + event-driven architecture = expressive, efficient, interpretable racing simulation.

---

## 🧮 Mathematical Foundation

### Core State Evolution

Each competitor is represented as a **state vector** in high-dimensional space:

```
x(t) = [v_x, v_y, x, y, E, T_batt, τ_tire, μ, ψ, ...]ᵀ ∈ ℝⁿ
```

**State transition function** (SimPulse core equation):

```
x(t+1) = f(x(t), u(t), θ(t)) + ε(t)
```

Where:

- **x(t)**: State vector (velocity, position, energy, temperature, tire condition)
- **f()**: Deterministic physics transition function
- **u(t)**: Control inputs (throttle, brake, steering, attack mode)
- **θ(t)**: Environmental parameters (weather, track grip, temperature)
- **ε(t) ~ N(0, Σ)**: Gaussian process noise (driver inconsistency, measurement error)

### Performance Index

Competitors are ranked by a **weighted performance metric**:

```
P_i(t) = w₁·v(t) + w₂·a(t) + w₃·e(t) + w₄·τ(t) + w₅·ψ(t)
```

Components:

- **v(t)**: Velocity factor (normalized speed)
- **a(t)**: Acceleration capability
- **e(t)**: Energy efficiency
- **τ(t)**: Tire/equipment condition
- **ψ(t)**: Strategy parameter (aggression vs. conservation)

### Stochastic Event Model

**Crash Probability** (sigmoid risk model):

```
P(crash) = base_prob × (1 + R(t) × 50)
R(t) = Σᵢ wᵢ · rᵢ(t)  [speed, tire, aggression, proximity, energy]
```

**Safety Car** (Poisson process):

```
P(event ∈ [t, t+dt]) = 1 - e^(-λ·dt)
```

**Mechanical Failure** (Weibull distribution):

```
h(t) = (k/λ) · (t/λ)^(k-1),  k > 1 (increasing hazard)
```

---

## 🔧 Architecture

### Modular Design

```
┌─────────────────────────────────────────┐
│         SimPulse Framework              │
├─────────────────────────────────────────┤
│  🎯 Core Simulation Engine              │
│     • Vector state representation       │
│     • Stochastic dynamics (ε noise)     │
│     • Physics-based motion              │
├─────────────────────────────────────────┤
│  📊 Event & Strategy Layer              │
│     • Probabilistic event generator     │
│     • Strategic decision making         │
│     • Attack mode / pit stops           │
├─────────────────────────────────────────┤
│  🧠 MDP Framework (RL-Ready)            │
│     • Action space (discrete/continuous)│
│     • Reward function design            │
│     • Policy models (Random/Greedy/RL)  │
├─────────────────────────────────────────┤
│  📈 Visualization & Analysis            │
│     • Real-time leaderboard             │
│     • Live track visualization (D3.js)  │
│     • Performance metrics tracking      │
└─────────────────────────────────────────┘
```

---

## 🚀 Features

### ✅ Implemented (v1.0)

- ✅ **Vector Space State Representation**: 20-dimensional state vectors with `to_vector()` / `from_vector()`
- ✅ **Stochastic Dynamics**: Gaussian noise model for control inputs, process noise, and measurement uncertainty
- ✅ **Probabilistic Events**: Crash detection, safety car, mechanical failures with mathematical distributions
- ✅ **Physics Engine**: Realistic Formula E Gen3 dynamics (power, aerodynamics, energy, tires)
- ✅ **Event-Driven Architecture**: Real-time event injection and logging
- ✅ **Performance Index**: Multi-objective ranking system `P_i(t)`
- ✅ **MDP Framework**: Markov Decision Process foundation for reinforcement learning
- ✅ **Action/State Spaces**: Discrete and continuous action spaces for RL agents
- ✅ **Reward Functions**: Multi-objective reward design (position, energy, tires, safety)
- ✅ **Live Visualization**: Next.js + D3.js real-time dashboard with WebSocket streaming

### 🔜 Roadmap (v2.0)

- 🔜 **Reinforcement Learning Integration**: PyTorch-based RL agents (PPO, SAC, TD3)
- 🔜 **Multi-Agent Competition**: AI vs. AI vs. Human racing
- 🔜 **Swarm Coordination**: Drone racing and autonomous vehicle trials
- 🔜 **Weather Dynamics**: Markov chain weather transitions affecting grip
- 🔜 **Adaptive Strategies**: Online learning and strategy evolution
- 🔜 **Extended Event Library**: Tire punctures, collisions, mechanical failures
- 🔜 **Domain Generalization**: MotoGP, drone racing, autonomous logistics

---

## 📦 Installation

### Backend (Python)

```bash
cd backend
pip install -r requirements.txt
python run_server.py
```

**Requirements**: `numpy`, `fastapi`, `websockets`, `uvicorn`

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:3000`

---

## 🎮 Quick Start

### Basic Race Simulation

```python
from backend.engine import FormulaERaceEngine
from backend.config import TrackConfig

# Initialize race engine
engine = FormulaERaceEngine(
    num_cars=12,
    num_laps=10,
    track_config=TrackConfig(),  # Jakarta E-Prix
    random_seed=42  # Reproducibility
)

# Run simulation
for step in range(1000):
    state_matrix, leaderboard, events = engine.simulate_timestep()

    # state_matrix: [12 × 20] numpy array
    # leaderboard: List of car positions
    # events: List of race events (crashes, attack mode, etc.)
```

### Using Stochastic Dynamics

```python
from backend.stochastic_dynamics import StochasticNoiseModel

# Initialize noise model
noise_model = StochasticNoiseModel(seed=42)

# Apply process noise to car state
noise_model.apply_process_noise(
    car=car_state,
    driver_consistency=0.85,  # 85% consistency
    dt=0.01
)

# Apply control noise
noisy_throttle, noisy_brake, noisy_steering = noise_model.apply_control_noise(
    throttle=0.8,
    brake=0.0,
    steering=0.1,
    driver_consistency=0.85
)
```

### MDP Environment for RL

```python
from backend.mdp_framework import MDPEnvironment, ActionSpace, RewardFunction

# Create MDP environment
action_space = ActionSpace(action_type='continuous')
reward_fn = RewardFunction()
env = MDPEnvironment(engine, reward_fn, action_space)

# Standard RL loop
states = env.reset()
for _ in range(100):
    actions = {car_id: action_space.sample() for car_id in states.keys()}
    next_states, rewards, dones, infos = env.step(actions)
    states = next_states
```

---

## 📊 Example Output

### Performance Index (P_i)

```python
car.get_performance_index()
# Output: 0.742  [Components: v=0.85, a=0.72, e=0.68, τ=0.91, ψ=0.78]
```

### State Vector

```python
car.to_vector()
# Output: array([145.2, 1.3, 1250.0, 2.4, 78.5, 42.1, 0.12, 1.75, 1.0, 120.0, ...])
#         [v_x, v_y, pos_x, pos_y, battery%, T_batt, tire_deg, grip, attack, ...]
```

### Race Events

```
[CRASH] Lap 3: Driver 7 crashes out! Speed: 243.7 km/h, Tire degradation: 18.3%
[ATTACK] Lap 5: Driver 2 activates attack mode (240s remaining)
[SAFETY] Lap 6: Safety car deployed
[OVERTAKE] Lap 8: Driver 4 overtakes Driver 5 at Turn 9
```

---

## 🧪 Testing & Validation

### Run Complete Test Suite

```bash
cd backend
python test_complete_race.py
```

### Validate Stochastic Dynamics

```bash
python -c "from stochastic_dynamics import StochasticNoiseModel; m=StochasticNoiseModel(42); print('✓ Stochastic module loaded')"
```

### Check MDP Framework

```bash
python -c "from mdp_framework import MDPEnvironment, ActionSpace; print('✓ MDP framework ready')"
```

---

## 🎨 Visualization Dashboard

**Features:**

- 📊 Real-time leaderboard with 10+ metrics per car
- 🗺️ Live track view (D3.js SVG) with car positions
- ⚡ Attack mode indicators
- 🔋 Battery, temperature, tire monitoring
- 📱 Fully responsive (mobile/tablet/desktop)
- 🔄 WebSocket streaming at 10 Hz

**Tech Stack:** Next.js 16, React 19, TypeScript, D3.js, Tailwind CSS

---

## 📚 Documentation

### Core Modules

- **`state.py`**: Vector space representation (`CarState`, `RaceState`)
- **`physics.py`**: Deterministic dynamics f(x,u,θ) + stochastic noise
- **`stochastic_dynamics.py`**: Gaussian noise models, Weibull failures, Poisson events
- **`mdp_framework.py`**: MDP environment, action/state spaces, reward functions, policy models
- **`events.py`**: Probabilistic event generator (crashes, safety car, overtakes)
- **`engine.py`**: Main simulation orchestrator

### Mathematical Details

See `MATHEMATICAL_FOUNDATION.md` for:

- Detailed derivations
- Parameter sensitivity analysis
- Noise model calibration
- Reward function design principles

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

1. **RL Integration**: Implement PPO/SAC agents
2. **Domain Extension**: Add MotoGP, drone racing, autonomous logistics
3. **Advanced Events**: Weather systems, tire punctures, pit strategies
4. **Optimization**: Vectorized physics, GPU acceleration
5. **Validation**: Compare with real Formula E telemetry

---

## 📖 Citation

If you use SimPulse in research, please cite:

```bibtex
@software{simpulse2025,
  title={SimPulse: Competitive Mobility Systems Simulator},
  author={Akshat Sharma},
  year={2025},
  url={https://github.com/akshat3144/simpulse},
  note={Lightweight simulation framework for competitive motion with stochastic dynamics}
}
```

---

## 📄 License

MIT License - See `LICENSE` file for details

---

## 🙏 Acknowledgments

- Formula E for Gen3 specifications
- OpenAI Gym for MDP interface design inspiration
- D3.js community for visualization tools

---

## 🔗 Links

- **Live Demo**: [https://simpulse-demo.vercel.app](https://simpulse-demo.vercel.app)
- **Documentation**: [https://docs.simpulse.dev](https://docs.simpulse.dev)
- **GitHub**: [https://github.com/akshat3144/simpulse](https://github.com/akshat3144/simpulse)

---

**Built with ❤️ for the racing and robotics community**
