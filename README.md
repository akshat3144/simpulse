# SimPulse: Formula E Race Simulator

**A mathematically rigorous, physics-based Formula E racing simulator with stochastic dynamics, probabilistic events, and real-time visualization**

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Mathematical Foundation](#-mathematical-foundation)
- [Core Simulation Logic](#-core-simulation-logic)
  - [Vehicle Dynamics](#1-vehicle-dynamics)
  - [Driver Control System](#2-driver-control-system)
  - [Overtaking Mechanics](#3-overtaking-mechanics)
  - [Energy Management](#4-energy-management)
  - [Tire Degradation](#5-tire-degradation)
  - [Attack Mode](#6-attack-mode)
  - [Event System](#7-event-system)
- [Technical Implementation](#-technical-implementation)
- [Future Roadmap](#-future-roadmap)
- [Installation &amp; Usage](#-installation--usage)
- [Architecture](#-architecture)

---

## 🎯 Overview

SimPulse is a high-fidelity Formula E racing simulator that models the complete racing experience through mathematical rigor and physical accuracy. Unlike arcade-style racing games, SimPulse prioritizes realistic physics, strategic decision-making, and probabilistic uncertainty.

---

## 📁 Project Structure

```
formula_e_simulator/
│
├── 📂 backend/                          # Python simulation engine
│   ├── __init__.py                      # Package initialization
│   ├── config.py                        # Configuration classes (PhysicsConfig, TrackConfig, etc.)
│   ├── state.py                         # State management (CarState, RaceState)
│   ├── physics.py                       # Physics engine (vehicle dynamics, forces)
│   ├── stochastic_dynamics.py           # Stochastic noise models (Gaussian, Weibull)
│   ├── events.py                        # Event system (crashes, overtakes, safety car)
│   ├── engine.py                        # Main simulation orchestrator (100 Hz loop)
│   ├── mdp_framework.py                 # MDP environment for RL (actions, rewards, policies)
│   ├── leaderboard.py                   # Leaderboard tracking and driver ratings
│   ├── qualifying.py                    # Qualifying session simulation
│   ├── race_control.py                  # Race control (flags, penalties, safety car)
│   ├── weather.py                       # Weather system (rain, temperature, wind)
│   ├── server.py                        # FastAPI WebSocket server
│   ├── run_server.py                    # Server entry point
│   ├── test_complete_race.py            # Integration tests
│   ├── requirements.txt                 # Python dependencies
│   ├── README.md                        # Backend documentation
│   └── 📂 race_output/                  # Race results and exports
│       ├── race_*.json                  # Race state snapshots
│       ├── leaderboard_*.csv            # Final standings
│       └── events_*.csv                 # Race events log
│
├── 📂 frontend/                         # Next.js dashboard
│   ├── 📂 app/                          # Next.js 16 app directory
│   │   ├── layout.tsx                   # Root layout component
│   │   ├── page.tsx                     # Main dashboard page
│   │   ├── globals.css                  # Global styles (Tailwind)
│   │   │
│   │   ├── 📂 components/               # React components
│   │   │   ├── Leaderboard.tsx          # Real-time standings
│   │   │   ├── TrackView.tsx            # D3.js track visualization
│   │   │   ├── ControlPanel.tsx         # Race controls (start/pause/create)
│   │   │   ├── EnergyChart.tsx          # Energy visualization
│   │   │   └── TrackInfo.tsx            # Track metadata display
│   │   │
│   │   ├── 📂 hooks/                    # Custom React hooks
│   │   │   └── useWebSocket.ts          # WebSocket connection manager
│   │   │
│   │   └── 📂 types/                    # TypeScript definitions
│   │       └── race.ts                  # Race data types (Car, RaceState)
│   │
│   ├── 📂 public/                       # Static assets
│   │   ├── favicon.ico
│   │   └── *.svg                        # SVG icons
│   │
│   ├── next.config.ts                   # Next.js configuration
│   ├── tsconfig.json                    # TypeScript configuration
│   ├── tailwind.config.ts               # Tailwind CSS configuration
│   ├── package.json                     # NPM dependencies
│   └── README.md                        # Frontend documentation
│
├── 📂 visualization_analysis/           # Post-race analysis tools
│   ├── visualize_race.py                # Generate 10+ matplotlib plots
│   ├── live_dashboard.py                # Plotly live dashboard (alternative)
│   ├── quick_view.py                    # Quick race summary
│   ├── README.md                        # Visualization documentation
│   └── 📂 plots/                        # Generated analysis plots
│       ├── track_position.png           # Position over time
│       ├── speed_profile.png            # Speed traces
│       ├── energy_consumption.png       # Battery usage
│       ├── tire_degradation.png         # Tire wear
│       ├── position_changes.png         # Overtakes visualization
│       └── lap_times.png                # Lap time comparison
│
├── demo_simpulse_features.py            # SimPulse feature demonstration
├── README.md                            # Main project documentation (this file)
├── SIMPULSE_README.md                   # SimPulse mathematical framework docs
└── .gitignore                           # Git ignore rules
```

---

### Key Innovations

1. **Vector Space Representation**: Each car exists as a 20-dimensional state vector enabling efficient computation and reinforcement learning integration
2. **Stochastic Dynamics**: Gaussian noise models capture real-world uncertainty in driver performance, control inputs, and sensor measurements
3. **Probabilistic Event System**: Crashes, overtakes, and safety cars emerge naturally from mathematical probability distributions
4. **MDP Framework**: Built-in Markov Decision Process environment ready for AI/RL agent training
5. **Real-time Visualization**: WebSocket-powered dashboard with live track view and comprehensive telemetry

---

## 🧮 Mathematical Foundation

### Core State Evolution Equation

The simulator is built on the fundamental SimPulse equation:

```
x(t+1) = f(x(t), u(t), θ(t)) + ε(t)
```

**Components:**

- **x(t) ∈ ℝ²⁰**: State vector containing all car parameters
- **f()**: Deterministic physics transition function
- **u(t) ∈ ℝ⁴**: Control inputs [throttle, brake, steering, attack_mode]
- **θ(t)**: Environmental parameters [weather, track_grip, temperature]
- **ε(t) ~ N(0, Σ)**: Gaussian process noise

### State Vector Representation

Each car's complete state is represented as a 20-dimensional vector:

```python
x = [
    v_x,          # Velocity X component (m/s)
    v_y,          # Velocity Y component (m/s)
    pos_x,        # Position X (m)
    pos_y,        # Position Y (m)
    E_batt,       # Battery energy percentage (%)
    T_batt,       # Battery temperature (°C)
    τ_tire,       # Tire degradation (0-1)
    μ,            # Grip coefficient (0.9-1.2)
    ψ_attack,     # Attack mode state (0/1)
    T_brake,      # Brake temperature (°C)
    lap_dist,     # Distance in current lap (m)
    total_dist,   # Total distance traveled (m)
    lap_num,      # Current lap number
    position,     # Race position
    throttle,     # Current throttle input (0-1)
    brake,        # Current brake input (0-1)
    steering,     # Steering angle (rad)
    lateral_g,    # Lateral G-force
    acceleration, # Longitudinal acceleration (m/s²)
    performance   # Performance index P_i(t)
]
```

### Performance Index

Multi-objective performance metric:

```
P_i(t) = w₁·v_norm(t) + w₂·a_norm(t) + w₃·e_norm(t) + w₄·(1-τ(t)) + w₅·ψ_strat(t)

Where:
    w = [0.25, 0.20, 0.20, 0.20, 0.15]  # Weight vector
    v_norm = velocity / max_velocity
    a_norm = acceleration / max_acceleration
    e_norm = energy_remaining / initial_energy
    τ = tire_degradation (0 = new, 1 = worn)
    ψ_strat = strategy_effectiveness (aggression vs conservation)
```

---

## 🏎️ Core Simulation Logic

### 1. Vehicle Dynamics

#### Acceleration Physics

The car's longitudinal acceleration is governed by force balance:

```
F_net = F_drive - F_drag - F_rolling - F_slope

Where:
    F_drive = (P_motor × η_motor) / v                    [Motor power to wheels]
    F_drag = 0.5 × ρ × C_d × A × v²                      [Aerodynamic drag]
    F_rolling = C_r × m × g × cos(α)                     [Rolling resistance]
    F_slope = m × g × sin(α)                              [Gravitational component]

Therefore:
    a = F_net / m
```

**Key Parameters:**

- Motor power: 350 kW (race mode), 400 kW (attack mode)
- Motor efficiency: 97%
- Drag coefficient: 0.32
- Frontal area: 1.5 m²
- Rolling resistance: 0.015
- Total mass: 920 kg (car + driver)

#### Corner Speed Calculation

For cornering, the maximum speed is determined by lateral grip:

```
v_max = √(μ × g × r)

Where:
    μ = tire_grip × track_grip × (1 + downforce_factor)
    g = 9.81 m/s²
    r = corner_radius (meters)

Downforce factor (speed-dependent):
    f_df = min(v / 80.0, 1.0) × 0.05    [Max 5% boost at high speed]
```

**Banking Effect:**

```
μ_effective = μ × (1 + tan(β) × 0.3)
Where β = banking angle
```

This means:

- **Straights**: Limited by max speed (322 km/h)
- **Fast corners** (r=200m, μ=1.2): ~155 km/h
- **Slow corners** (r=50m, μ=1.2): ~77 km/h
- **Tight hairpins** (r=15m, μ=1.2): ~42 km/h

#### Lateral Dynamics

Steering creates lateral acceleration:

```
a_lateral = v² / r

Steering angle required:
    δ = arctan(L / r)
    Where L = wheelbase = 2.97 m
```

**G-Force Calculation:**

```
G_lat = a_lateral / g
Maximum sustainable: ~3.5 G (street circuit limits)
```

### 2. Driver Control System

The driver controller makes decisions at 100 Hz (every 0.01 seconds) based on:

#### Target Speed Calculation

```python
def calculate_target_speed(car, segment, skill, aggression):
    # 1. Base segment speed
    if segment.is_straight():
        base_speed = MAX_SPEED  # 89.44 m/s
    else:
        base_speed = sqrt(μ × g × radius)

    # 2. Attack mode boost (8% on straights, 2% in corners)
    if car.attack_mode_active:
        boost = 1.08 if segment.is_straight() else 1.02
        base_speed *= boost

    # 3. Driver skill factor (95-105%)
    skill_mult = 0.95 + (skill - 0.95) × 0.5
    base_speed *= skill_mult

    # 4. Aggression factor (92-98% of limit)
    aggr_factor = 0.92 + (aggression × 0.06)

    # 5. Race situation adjustments
    if chasing and gap < 1.5s:
        aggr_factor += 0.05  # Push harder
    if leading and gap > 5s:
        aggr_factor × 0.95   # Conserve

    # 6. Resource management
    if battery < 15%:
        aggr_factor × 0.92   # Energy saving
    if tire_deg > 0.7:
        aggr_factor × 0.95   # Tire preservation

    # 7. Weather factor
    if raining:
        aggr_factor × (1.0 - rain_intensity × 0.2)

    return base_speed × aggr_factor
```

#### Steering Control

The steering system uses **predictive lookahead**:

```python
def calculate_steering(car, current_segment, skill, consistency):
    # Lookahead distance (2 seconds ahead)
    lookahead_dist = car.speed × 2.0
    future_pos = (car.lap_distance + lookahead_dist) % track_length
    next_segment = track.get_segment_at(future_pos)

    # If approaching corner from straight, start early steering
    if current_segment.is_straight() and next_segment.is_corner():
        segment_for_steering = next_segment
    else:
        segment_for_steering = current_segment

    # Calculate required steering angle
    if segment_for_steering.is_straight():
        base_steering = 0.0
        noise = (1 - consistency) × 0.01
    else:
        # Ackermann steering geometry
        L = wheelbase  # 2.97 m
        r = segment_for_steering.radius
        base_steering = arctan(L / r)

        # Direction
        if left_corner:
            base_steering = -base_steering
        elif chicane:
            base_steering × sin(lap_distance / 10.0)  # Alternating

        noise = (1 - skill) × 0.03

    # Apply stochastic noise
    steering = base_steering + N(0, noise)

    # Physical limits (±30 degrees)
    return clip(steering, -0.52, 0.52)
```

**Key Insights:**

- **Early Braking**: System looks 2 seconds ahead to brake before corners
- **Progressive Steering**: Smooth steering inputs based on corner geometry
- **Skill Variation**: Less skilled drivers have 3% more steering noise
- **Consistency**: Affects repeatability of steering inputs

#### Throttle & Brake Logic

```python
def calculate_throttle_brake(current_speed, target_speed, segment, skill, aggression):
    speed_error = target_speed - current_speed
    deadband = 1.0  # m/s tolerance

    if speed_error > deadband:
        # ACCELERATE
        throttle = min(speed_error / 15.0, 1.0) × (0.7 + aggression × 0.3)

        # Reduce throttle in corners
        if segment.is_corner():
            throttle × 0.5  # 50% reduction for safety

        brake = 0.0

    elif speed_error < -deadband:
        # BRAKE
        throttle = 0.0
        speed_diff = abs(speed_error)

        # Corner braking (very aggressive)
        if segment.is_corner() and speed_diff > 20:
            brake = 1.0  # Full braking
        elif segment.is_corner():
            brake = speed_diff / 30.0
        else:
            # Straight braking (gentler)
            brake = speed_diff / 50.0

        brake = clip(brake, 0.0, 1.0)

    else:
        # MAINTAIN (within deadband)
        throttle = 0.3  # Gentle maintenance throttle
        brake = 0.0

    return throttle, brake
```

**Braking Strategy:**

- **Full panic braking**: When >20 m/s over target in corner
- **Progressive braking**: Proportional to speed error
- **Earlier braking**: System anticipates corners via lookahead
- **Regen integration**: Brake input includes regenerative braking

### 3. Overtaking Mechanics

Overtaking is **physics-based**, not artificial position swapping. Cars naturally overtake when they have performance advantages.

#### Overtake Detection

```python
def detect_overtake_opportunity(car, other_cars):
    for other_car in other_cars:
        # 1. Check proximity (within 10 meters)
        distance_diff = abs(car.total_distance - other_car.total_distance)
        if distance_diff < 10:

            # 2. Check if ahead in distance but behind in position
            if (car.total_distance > other_car.total_distance and
                car.position > other_car.position):

                # 3. Calculate overtake probability
                prob = calculate_overtake_probability(car, other_car, segment)

                # 4. Attempt overtake
                if random() < prob × 0.1:  # Scale for timestep
                    execute_overtake(car, other_car)
```

#### Overtake Probability Model

Uses **logistic regression** to determine success probability:

```
P(overtake) = 1 / (1 + exp(-z))

Where z = weighted feature sum:

z = Σ w_i × f_i(t)
  = 0.50 × Δv                    [Speed differential]
  + 0.02 × ΔE                    [Battery advantage]
  + 0.30 × attack_active         [Attack mode bonus]
  - 0.20 × defend_attack_active  [Defender attack mode penalty]
  + 0.40 × Δτ                    [Tire advantage]
  + k_track                       [Track segment factor]

Track factors:
    k_straight = 0.8     [Easiest to overtake]
    k_corner = 0.3       [Hardest to overtake]
    k_chicane = 0.5      [Medium difficulty]
```

**Feature Engineering:**

```python
def calculate_overtake_probability(attacker, defender, segment):
    # Speed advantage (m/s)
    speed_diff = attacker.speed - defender.speed

    # Energy advantage (%)
    battery_diff = attacker.battery_pct - defender.battery_pct

    # Attack mode (binary bonuses)
    attack_bonus = 0.3 if attacker.attack_mode_active else 0.0
    defend_penalty = -0.2 if defender.attack_mode_active else 0.0

    # Tire condition advantage
    tire_diff = defender.tire_degradation - attacker.tire_degradation

    # Track position multiplier
    if segment.type == 'straight':
        track_factor = 0.8
    elif segment.type in ['left_corner', 'right_corner']:
        track_factor = 0.3
    else:  # chicane
        track_factor = 0.5

    # Logistic regression
    z = (speed_diff × 0.5 +
         battery_diff × 0.02 +
         attack_bonus + defend_penalty +
         tire_diff × 0.4 +
         track_factor)

    probability = 1.0 / (1.0 + exp(-z))
    return clip(probability, 0.0, 1.0)
```

**Overtake Scenarios:**

1. **DRS-style overtake**: Faster car (5 m/s advantage) on straight with attack mode

   - Probability: ~85%
2. **Bold corner overtake**: Equal speed but fresh tires vs worn tires

   - Probability: ~30-40%
3. **Impossible overtake**: Slower car, no attack mode, defending in corner

   - Probability: ~5%

**Why This Works:**

- **Emergent behavior**: Overtakes happen naturally from physics
- **Strategic depth**: Attack mode timing matters
- **Tire strategy**: Preserving tires helps late-race overtakes
- **Energy management**: Battery conservation affects overtaking power

### 4. Energy Management

#### Battery Physics

```
E(t+1) = E(t) - E_consumed(t) + E_recovered(t)

Energy consumed per timestep:
    E_consumed = (P_motor / η_motor) × dt

    Where:
        P_motor = F_drive × v                     [Power at wheels]
        η_motor = 0.97                            [Motor efficiency]
        dt = 0.01 s                               [Timestep]

Energy recovered (regenerative braking):
    E_recovered = (P_regen × η_regen) × dt

    Where:
        P_regen = min(brake_force × v, P_regen_max)
        P_regen_max = 600 kW (Gen3: front 250kW + rear 350kW)
        η_regen = 0.40                            [40% recovery efficiency]
```

**Battery Depletion Rate:**

```python
def calculate_energy_consumption(car, throttle, brake, dt):
    # Motor power demand
    if throttle > 0:
        power_demand = car.get_motor_power(throttle, car.speed)

        # Attack mode increases consumption by 30%
        if car.attack_mode_active:
            power_demand × 1.30

        energy_consumed = (power_demand / 0.97) × dt
    else:
        energy_consumed = 0

    # Regenerative braking
    if brake > 0:
        brake_force = brake × MAX_BRAKE_FORCE
        regen_power = min(brake_force × car.speed, 600_000)  # 600 kW limit
        energy_recovered = regen_power × 0.40 × dt
    else:
        energy_recovered = 0

    # Net change
    net_energy = energy_recovered - energy_consumed

    # Update battery
    car.battery_energy += net_energy
    car.battery_percentage = (car.battery_energy / BATTERY_CAPACITY) × 100
```

**Energy Strategy Matrix:**

| Battery % | Lap Progress | Strategy           | Throttle Modifier |
| --------- | ------------ | ------------------ | ----------------- |
| < 15%     | Any          | Emergency conserve | 0.92×            |
| 15-30%    | < 50%        | Conservative       | 0.95×            |
| 30-50%    | Any          | Neutral            | 1.00×            |
| > 50%     | > 70%        | Aggressive push    | 1.05×            |
| > 70%     | > 80%        | All-out attack     | 1.10×            |

#### Temperature Management

```
T_battery(t+1) = T_battery(t) + ΔT_generated - ΔT_cooling

Heat generation:
    ΔT_gen = (P_loss × dt) / (m_batt × c_p)

    Where:
        P_loss = P_consumed × (1 - η)     [Waste heat]
        m_batt = 200 kg                    [Battery mass estimate]
        c_p = 850 J/(kg·K)                [Heat capacity]

Active cooling:
    ΔT_cool = k_cool × (T_batt - T_ambient) × dt

    Where:
        k_cool = 15 kW / (m × c_p)        [Cooling coefficient]
        T_ambient = 25°C
```

**Thermal Limits:**

- **Optimal**: 40°C (maximum performance)
- **Warning**: > 50°C (begins performance degradation)
- **Critical**: > 60°C (power derate to protect battery)

### 5. Tire Degradation

#### Multi-Factor Degradation Model

```
τ(t+1) = τ(t) + Δτ_total

Where:
    Δτ_total = Δτ_base + Δτ_temp + Δτ_speed + Δτ_lateral + Δτ_lock

Component breakdown:
    Δτ_base = k_base × dt                          [0.002/s base rate]
    Δτ_temp = k_temp × |T_tire - T_optimal| × dt  [Temperature effect]
    Δτ_speed = k_speed × (v / v_max)² × dt        [Speed-dependent]
    Δτ_lateral = k_lat × |a_lat / g| × dt          [Cornering wear]
    Δτ_lock = k_lock × (brake > 0.95)              [Wheel lock damage]

Parameters:
    k_base = 0.002      [Base degradation]
    k_temp = 0.00005    [Temperature sensitivity]
    k_speed = 0.00003   [Speed sensitivity]
    k_lat = 0.0004      [Lateral G sensitivity]
    k_lock = 0.01       [Lock-up penalty]
```

**Grip Coefficient Decay:**

```
μ(τ) = μ_max - (μ_max - μ_min) × τ

Where:
    μ_max = 1.2    [Fresh tire grip]
    μ_min = 0.9    [Worn tire grip]
    τ ∈ [0, 1]     [Degradation level]

Examples:
    τ = 0.0  → μ = 1.20  (new tires)
    τ = 0.3  → μ = 1.11  (moderate wear)
    τ = 0.7  → μ = 0.99  (heavy wear)
    τ = 1.0  → μ = 0.90  (fully worn)
```

**Temperature-Speed-Degradation Coupling:**

```python
def update_tire_degradation(car, segment, dt):
    # Base degradation
    deg_base = 0.002 × dt

    # Temperature contribution
    temp_diff = abs(car.tire_temp - 90.0)  # 90°C optimal
    deg_temp = 0.00005 × temp_diff × dt

    # Speed contribution (quadratic)
    speed_factor = (car.speed / MAX_SPEED) ** 2
    deg_speed = 0.00003 × speed_factor × dt

    # Lateral G-force (cornering)
    lateral_g = car.lateral_acceleration / 9.81
    deg_lateral = 0.0004 × abs(lateral_g) × dt

    # Wheel lock detection
    if car.brake > 0.95 and car.speed > 20:
        deg_lock = 0.01  # Sudden spike
    else:
        deg_lock = 0

    # Total degradation
    total_deg = deg_base + deg_temp + deg_speed + deg_lateral + deg_lock

    # Update
    car.tire_degradation += total_deg
    car.tire_degradation = min(car.tire_degradation, 1.0)

    # Update grip
    car.grip_coefficient = 1.2 - 0.3 × car.tire_degradation
```

**Tire Strategy Impact:**

| Tire Deg | Grip | Corner Speed | Lap Time | Overtake Defense |
| -------- | ---- | ------------ | -------- | ---------------- |
| 0.0      | 1.20 | 100%         | Baseline | Strong           |
| 0.3      | 1.11 | 96%          | +1.2s    | Good             |
| 0.5      | 1.05 | 94%          | +2.1s    | Moderate         |
| 0.7      | 0.99 | 91%          | +3.5s    | Weak             |
| 1.0      | 0.90 | 87%          | +5.8s    | Very weak        |

### 6. Attack Mode

Formula E's signature feature, implemented with full strategic complexity.

#### Activation Logic

```python
def should_activate_attack_mode(car, position, gap_ahead, laps_remaining, segment):
    # Guard conditions
    if car.attack_uses_left == 0 or car.attack_mode_active:
        return False
    if car.battery_percentage < 40:
        return False  # Need sufficient energy

    # Strategic triggers
    race_progress = 1.0 - (laps_remaining / total_laps)
    in_final_phase = race_progress > 0.7
    close_battle = gap_ahead < 2.0 and gap_ahead > 0.1
    competitive_position = 2 <= position <= 6
    on_straight = segment.type == 'straight'

    # Multi-condition check (need at least 2 conditions)
    conditions = [
        in_final_phase,
        close_battle and on_straight,
        competitive_position and close_battle,
        car.battery_pct > 60 and laps_remaining < 3
    ]

    if sum(conditions) >= 2:
        return random() < 0.05  # 5% chance per timestep

    return False
```

**Attack Mode Effects:**

```
1. Power Boost:
   P_motor: 350 kW → 400 kW (+50 kW)

2. Speed Boost:
   v_max_straight: 322 km/h → 348 km/h (+8%)
   v_corner: minimal boost (~2%)

3. Energy Cost:
   E_consumption: 1.0× → 1.3× (+30%)

4. Duration:
   t_duration = 240 seconds (4 minutes)

5. Activations:
   n_uses = 2 per race (standard)
```

**Optimal Usage Strategy:**

```
Scenario A: Battle for Position (Most Common)
    - Activate when: Within 1.5s of car ahead
    - Location: Approaching long straight
    - Result: High overtake probability

Scenario B: Defensive Activation
    - Activate when: Car behind within 1s
    - Location: Any long straight ahead
    - Result: Maintain gap

Scenario C: Late Race Push
    - Activate when: Final 3 laps, good battery
    - Location: Any time
    - Result: Maximum pace to closing stages

Scenario D: Wasted Activation
    - Activate when: Leading by >5s
    - Result: Unnecessary energy waste
```

### 7. Event System

#### Crash Probability

Uses **sigmoid risk model** with multi-factor risk assessment:

```
P(crash) = base_prob × (1 + R(t) × 50)

Risk factor:
    R(t) = Σ w_i × r_i(t)
         = 0.30 × speed_risk
         + 0.25 × tire_risk
         + 0.20 × aggression_risk
         + 0.15 × proximity_risk
         + 0.10 × energy_stress

Where:
    speed_risk = v / v_max
    tire_risk = τ                    [Degradation level]
    aggression_risk = ψ_aggr         [Driver aggression]
    proximity_risk = min(nearby / 5, 1.0)
    energy_stress = max(0, 1 - E_pct / 100)

Base probability:
    p_base = 0.00001 per timestep (very rare)
```

**Crash Scenarios:**

```python
# Low risk: Comfortable straight, good tires
speed_risk = 0.5, tire_risk = 0.2, aggr = 0.6, prox = 0.2, energy = 0.3
R = 0.30×0.5 + 0.25×0.2 + 0.20×0.6 + 0.15×0.2 + 0.10×0.3
  = 0.15 + 0.05 + 0.12 + 0.03 + 0.03 = 0.38
P(crash) = 0.00001 × (1 + 0.38 × 50) = 0.00020 (0.02% per timestep)

# High risk: Fast corner, worn tires, aggressive, traffic
speed_risk = 0.95, tire_risk = 0.85, aggr = 0.9, prox = 0.8, energy = 0.7
R = 0.30×0.95 + 0.25×0.85 + 0.20×0.9 + 0.15×0.8 + 0.10×0.7
  = 0.285 + 0.213 + 0.18 + 0.12 + 0.07 = 0.868
P(crash) = 0.00001 × (1 + 0.868 × 50) = 0.00044 (0.044% per timestep)
```

#### Safety Car Deployment

**Poisson process** with crash-dependent rate:

```
λ = λ_base × (1 + n_crashes × 0.5)

Where:
    λ_base = 0.1 per lap (safety car every ~10 laps)
    n_crashes = recent crashes (last 2 laps)

Deployment probability:
    P(safety_car | lap) = λ / total_laps

Guards:
    - Not on first lap
    - Not within 5 laps of previous safety car
```

#### Mechanical Failures

**Weibull distribution** for increasing hazard rate:

```
h(t) = (k/λ) × (t/λ)^(k-1)

Where:
    k = 2.5      [Shape parameter, k>1 = increasing failure rate]
    λ = 5000s    [Scale parameter, mean failure time]
    t = race_time

Cumulative failure probability:
    F(t) = 1 - exp(-(t/λ)^k)
```

### 8. Race Control & Penalty System

SimPulse implements a comprehensive FIA-compliant race control system with flags, penalties, and safety car management.

#### Flag System

```python
class FlagType:
    GREEN           # Normal racing
    YELLOW          # Local caution (no overtaking in sector)
    DOUBLE_YELLOW   # Severe incident (slow down significantly)
    RED             # Race stopped
    SAFETY_CAR      # Full course safety car
    BLUE            # Lapped car must let leader pass
    BLACK           # Disqualification
    BLACK_WHITE     # Warning for unsporting behavior
```

#### Penalty Types

Formula E regulations implemented:

```python
class PenaltyType:
    TIME_PENALTY_5S      # +5 seconds added to race time
    TIME_PENALTY_10S     # +10 seconds added to race time
    DRIVE_THROUGH        # Drive through pit lane at speed limit
    STOP_GO_10S          # Stop in pit for 10 seconds
    DISQUALIFICATION     # Excluded from race results
    WARNING              # Official warning (3 warnings = penalty)
    REPRIMAND            # Noted but no immediate action
```

#### Track Limits Enforcement

**3-Strike System:**

```python
def check_track_limits(car, track_width=12.0):
    """
    Monitor track limits violations

    Detection:
        - Car exceeds track boundaries (>50% of car width off track)
        - Position_y > track_width / 2

    Penalty Structure:
        Violation 1: Warning logged
        Violation 2: Second warning
        Violation 3: 5-second time penalty
        [Counter resets after penalty]
    """

    if abs(car.position_y) > track_width / 2:
        violations[car.id] += 1

        if violations[car.id] >= 3:
            issue_penalty(car, TIME_PENALTY_5S, "Track limits (3 violations)")
            violations[car.id] = 0  # Reset
```

**Why Track Limits Matter:**

- **Corner cutting**: Gaining unfair advantage by taking shorter line
- **Safety**: Cars off track in dangerous areas
- **Consistency**: All drivers must follow same racing rules

#### Unsafe Behavior Detection

```python
def check_unsafe_behavior(car, other_cars):
    """
    Detect dangerous driving patterns

    Violations detected:
        1. Weaving under braking (blocking)
        2. Dangerous overtaking (forcing off track)
        3. Causing collision
        4. Excessive aggression
    """

    # Weaving detection
    if abs(steering) > 0.3 and braking and not_in_corner:
        issue_warning(car, "Weaving - blocking behavior")

    # Dangerous proximity
    for other in other_cars:
        distance = calculate_distance(car, other)
        if distance < 2.0 and both_high_speed:
            if random() < 0.005:  # Stewards review
                issue_warning(car, f"Dangerous move on {other.name}")
```

**Warning System:**

```
Warning 1: Logged, driver notified
Warning 2: Final warning
Warning 3: Automatic 5-second time penalty
```

#### Energy Limit Monitoring

Formula E has strict energy usage limits:

```python
def check_energy_limit(car, limit_mj=183.6):
    """
    Monitor total energy consumption

    FIA Regulation:
        Maximum energy: 51 kWh = 183.6 MJ per race
        Includes: Motor usage, battery charging (regen)
        Excludes: Auxiliary systems, cooling

    Penalty:
        Exceeding limit by >1%: Disqualification
    """

    total_energy_used = calculate_total_energy(car)

    if total_energy_used > limit_mj × 1.01:
        issue_penalty(car, DISQUALIFICATION, "Energy limit exceeded")
```

#### Safety Car Procedures

When deployed, safety car enforces:

```python
def apply_safety_car_effects(cars):
    """
    Safety car speed restrictions

    Rules:
        - Maximum speed: 80 km/h (50 mph)
        - No overtaking (except to rejoin line)
        - Bunched field (delta time reset)
        - Lapped cars may unlap themselves

    Duration:
        Typical: 3-5 minutes (180-300 seconds)
        Until: Track clear, cars bunched
    """

    max_speed_sc = 80 / 3.6  # 22.2 m/s

    for car in cars:
        if car.speed > max_speed_sc:
            car.throttle = 0.0
            car.brake = 0.5  # Gentle braking
```

**Strategic Impact:**

- **Bunching**: Gap to leader reset
- **Energy recovery**: Opportunity to cool battery, save energy
- **Tire preservation**: Less wear during slow laps
- **Position changes**: Pit stop strategy affected

#### Penalty Application System

Penalties are applied post-race to final classification:

```python
def apply_penalties_to_results(results):
    """
    Apply time penalties to final results

    Process:
        1. Collect all unserved penalties
        2. Add time penalty to driver's total race time
        3. Re-sort standings by adjusted time
        4. Update final positions

    Example:
        P1: Driver A - 25:43.215
        P2: Driver B - 25:45.892 (+5s penalty)

        After penalty:
        P1: Driver A - 25:43.215
        P2: Driver B - 25:50.892  [Drops to P3 if others closer]
    """

    for penalty in penalties:
        if penalty.time_penalty > 0:
            for result in results:
                if result.car_id == penalty.car_id:
                    result.total_time += penalty.time_penalty

    # Re-sort by total time
    results.sort(key=lambda x: x.total_time)

    # Update positions
    for pos, result in enumerate(results):
        result.position = pos + 1

    return results
```

#### Penalty Statistics

Example penalty scenarios:

| Infraction           | Penalty     | Typical Time Cost | Strategic Impact |
| -------------------- | ----------- | ----------------- | ---------------- |
| Track limits (3×)   | +5s         | 1-2 positions     | Moderate         |
| Unsafe overtake      | +10s        | 2-4 positions     | Severe           |
| Causing collision    | +10s or DSQ | Race ending       | Critical         |
| Energy limit breach  | DSQ         | Excluded          | Race ending      |
| Accumulated warnings | +5s         | 1-2 positions     | Moderate         |
| Ignoring blue flags  | +5s per lap | Cumulative        | Mounting         |

**Real-World Impact Example:**

```
Race Scenario:
    P1: Driver A - 28:45.231
    P2: Driver B - 28:47.892  [+5s penalty for track limits]
    P3: Driver C - 28:48.105

Final Results After Penalties:
    P1: Driver A - 28:45.231  ✓
    P2: Driver C - 28:48.105  ↑ (moved up)
    P3: Driver B - 28:52.892  ↓ (penalty applied)
```

#### Incident Review System

```python
class IncidentReview:
    """
    Stewards investigate incidents post-race

    Typical investigations:
        - Collision between cars
        - Forcing another car off track
        - Gaining advantage by leaving track
        - Blocking / defensive moves
        - Pit lane speed violations

    Decision timeline:
        During race: Warnings, immediate penalties
        Post-race: Time penalties, grid penalties for next race
    """
```

### 9. Qualifying System

SimPulse implements a realistic Formula E qualifying format with flying laps and performance-based grid determination.

#### Qualifying Format

**Session Structure:**

```python
class QualifyingSession:
    """
    Formula E Qualifying Session

    Format:
        - Duration: 10 minutes per group
        - Groups: 4 groups (divide field by championship order)
        - Laps: Each driver gets 2-3 flying laps
        - Goal: Set fastest single lap time

    Procedure:
        1. Out lap (prepare tires, battery)
        2. Flying lap 1 (first timed attempt)
        3. Cool-down / prepare
        4. Flying lap 2 (final attempt)
        5. Best time counts for grid position
    """
```

#### Lap Time Calculation

Qualifying lap times are determined by multiple factors:

```python
def calculate_qualifying_lap_time(driver, track):
    """
    Calculate qualifying lap time

    Base calculation:
        lap_time = track_length / avg_speed

    Where avg_speed considers:
        1. Maximum speed capability
        2. Driver skill factor
        3. Qualifying boost (push mode)
        4. Track conditions
        5. Consistency variation
    """

    # Base speed (70% of max on average due to corners)
    avg_speed = MAX_SPEED × 0.70

    # Driver skill multiplier (0.90 - 1.05)
    avg_speed × driver.skill

    # Theoretical lap time
    base_lap_time = track_length / avg_speed

    # Apply modifiers
    # 1. Qualifying boost (2% faster - full attack mode, no conservation)
    base_lap_time × 0.98

    # 2. Consistency variation (better drivers more consistent)
    consistency_factor = N(1.0, 1 - driver.consistency)  # ±3%
    base_lap_time × clip(consistency_factor, 0.97, 1.03)

    # 3. Track conditions (grip variation, wind, temperature)
    track_factor = N(1.0, 0.01)  # ±1%
    base_lap_time × track_factor

    # 4. Random variance (traffic, small mistakes)
    base_lap_time + N(0, 0.1)  # ±0.1s noise

    return lap_time
```

**Key Factors Explained:**

1. **Driver Skill** (0.90 - 1.05):

   - Elite drivers: 1.02-1.05 (2-5% faster)
   - Average drivers: 0.98-1.02 (baseline)
   - Slower drivers: 0.90-0.98 (2-10% slower)
2. **Consistency** (0.85 - 0.98):

   - High consistency (0.95+): Lap times within 0.3s
   - Medium consistency (0.90): Lap times vary by 0.5-0.8s
   - Low consistency (0.85): Lap times vary by 1.0-1.5s
3. **Qualifying Boost** (2% faster):

   - No energy management concerns
   - Full attack mode throughout
   - Maximum risk taking
   - Fresh tires every attempt

#### Multi-Lap Strategy

Each driver typically gets 2 flying laps:

```python
def run_qualifying_laps(driver, num_laps=2):
    """
    Simulate multiple qualifying attempts

    Strategy:
        Lap 1: Safe banker lap (99% push)
        Lap 2: Maximum attack (100% push)

    Best lap determines grid position
    """

    best_time = infinity

    for lap_number in range(num_laps):
        # First lap: banker (slightly conservative)
        if lap_number == 0:
            push_level = 0.99  # 99% attack
        else:
            # Final lap: all-out attack
            push_level = 1.00  # 100% attack

        lap_time = calculate_lap_time(driver, push_level)
        best_time = min(best_time, lap_time)

    return best_time
```

**Why Two Laps Matter:**

- **Lap 1 (Banker)**: Guarantee a decent time in case lap 2 has issues
- **Lap 2 (Attack)**: Maximum risk, full commitment
- **Track evolution**: Track may improve as more rubber laid down
- **Tire performance**: Tires reach optimal temperature on lap 2

#### Grid Position Determination

```python
def determine_starting_grid(qualifying_results):
    """
    Convert qualifying times to grid positions

    Process:
        1. Sort all drivers by best lap time (fastest first)
        2. Assign grid positions 1 to N
        3. Apply any penalties from previous races
        4. Final grid order determines race start

    Penalties applied:
        - Grid drop: Move back X positions
        - Back of grid: Start last regardless of time
        - Pit lane start: Start from pit lane
    """

    # Sort by lap time
    results.sort(key=lambda x: x.best_lap_time)

    # Assign positions
    for position, driver in enumerate(results):
        driver.grid_position = position + 1

    # Apply penalties
    for penalty in grid_penalties:
        if penalty.type == 'grid_drop':
            driver.grid_position += penalty.places
        elif penalty.type == 'back_of_grid':
            driver.grid_position = len(results)

    # Re-sort after penalties
    results.sort(key=lambda x: x.grid_position)

    return results
```

#### Qualifying Results Format

Example output:

```
================================================================================
FORMULA E QUALIFYING SESSION
================================================================================
Track: Plaksha E-Prix Circuit
Distance: 2980.00m
Flying laps per driver: 2

Qualifying in progress...
  Driver 1                       - 89.245s
  Driver 2                       - 89.523s
  Driver 3                       - 89.891s
  [... all drivers ...]

================================================================================
QUALIFYING RESULTS
================================================================================
  P 1. Lewis Hamilton                  - 88.734s  [POLE POSITION]
  P 2. Max Verstappen                  - 88.892s  +0.158s
  P 3. Charles Leclerc                 - 89.056s  +0.322s
  P 4. Fernando Alonso                 - 89.234s  +0.500s
  P 5. George Russell                  - 89.445s  +0.711s
  [... full grid ...]
  P24. Slowest Driver                  - 92.156s  +3.422s

Pole Position: Lewis Hamilton (88.734s)
Front Row Average: 88.813s
Grid Spread: 3.422s (pole to last)
```

#### Statistical Analysis

**Typical Qualifying Gaps:**

| Position Gap | Time Delta | Percentage |
| ------------ | ---------- | ---------- |
| P1 → P2     | 0.1-0.3s   | 0.1-0.3%   |
| P1 → P5     | 0.5-0.8s   | 0.5-0.9%   |
| P1 → P10    | 1.0-1.5s   | 1.1-1.7%   |
| P1 → P20    | 2.5-4.0s   | 2.8-4.5%   |

**Performance Distribution:**

```
Qualifying Time Distribution (normalized to pole = 100%):

P1  (Pole):        100.0%  ████████████████████████████████
P2-P3:            99.7%   ███████████████████████████████
P4-P6:            99.3%   ██████████████████████████████
P7-P10:           98.8%   █████████████████████████████
P11-P15:          98.2%   ████████████████████████████
P16-P20:          97.5%   ███████████████████████████
P21-P24:          96.5%   ██████████████████████████
```

#### Session Simulation Example

```python
from backend.qualifying import QualifyingSession
from backend.config import TrackConfig

# Setup
track = TrackConfig()  # Plaksha E-Prix
drivers = generate_driver_configs(24)  # 24 drivers

# Run qualifying
quali_session = QualifyingSession(track, drivers, random_seed=42)
results = quali_session.run_qualifying(num_flying_laps=2, verbose=True)

# Get starting grid
grid_order = quali_session.get_starting_grid()

# Export results
quali_session.export_results_csv('qualifying_results.csv')

# Use grid for race
race_engine = FormulaERaceEngine(
    num_cars=24,
    num_laps=40,
    starting_grid=grid_order  # Use qualifying order
)
```

#### Qualifying vs Race Pace

**Key Differences:**

| Aspect                | Qualifying        | Race                  |
| --------------------- | ----------------- | --------------------- |
| **Duration**    | Single lap (~90s) | 40+ laps (45+ min)    |
| **Energy**      | No conservation   | Critical management   |
| **Tires**       | Fresh, optimal    | Degrading over time   |
| **Traffic**     | Minimal           | Heavy (20+ cars)      |
| **Strategy**    | Pure speed        | Multi-dimensional     |
| **Risk**        | Maximum attack    | Balanced approach     |
| **Attack Mode** | Can use freely    | Strategic timing      |
| **Battery**     | 100% available    | Must last entire race |

**Qualifying Specialists vs Race Pace:**

Some drivers excel in qualifying (one-lap pace) but struggle in races:

```
Driver A: Qualifying: P2, Race finish: P8  [Qualifying specialist]
Driver B: Qualifying: P8, Race finish: P2  [Race pace specialist]
```

#### Impact on Race Strategy

Starting position dramatically affects race strategy:

```python
def race_strategy_by_grid_position(grid_pos):
    """
    How grid position influences race strategy
    """

    if grid_pos <= 3:
        # Front row: Defend position, control pace
        strategy = {
            'aggression': 0.85,  # Moderate
            'attack_mode_timing': 'late',  # After mid-race
            'energy_conservation': 0.92  # Slight conservation
        }

    elif grid_pos <= 10:
        # Midfield: Attack early, overtake slower starters
        strategy = {
            'aggression': 0.92,  # High
            'attack_mode_timing': 'early',  # First quarter
            'energy_conservation': 0.88  # Push harder
        }

    else:
        # Back of grid: All-out attack, nothing to lose
        strategy = {
            'aggression': 0.98,  # Maximum
            'attack_mode_timing': 'opportunistic',  # Any chance
            'energy_conservation': 0.85  # Very aggressive
        }

    return strategy
```

**Statistical Impact:**

```
Win Probability by Qualifying Position:
    Pole Position (P1):     35-40% chance of victory
    Front Row (P2):         20-25% chance
    Top 5 (P3-P5):         30-35% combined
    Outside Top 5 (P6+):   10-15% combined

Average Positions Gained/Lost:
    P1 start → P1.8 finish  (-0.8 positions)
    P5 start → P5.2 finish  (-0.2 positions)
    P10 start → P8.5 finish (+1.5 positions)
    P20 start → P16.8 finish (+3.2 positions)
```

---

### Key File Descriptions

#### Backend Core Files

**`config.py`** - Configuration Management

```python
# Contains all simulation parameters
- PhysicsConfig: Vehicle specs (Gen3 Formula E)
- TrackConfig: Circuit definitions (Jakarta, Monaco, etc.)
- DriverConfig: Driver characteristics (skill, aggression, consistency)
- WeatherConditions: Environmental parameters
- PenaltyRecord: Penalty tracking
```

**`state.py`** - State Representation

```python
# State management classes
- CarState: 20D vector representation of car
  • to_vector(): Convert to numpy array for ML
  • from_vector(): Reconstruct from array
  • get_performance_index(): Calculate P_i(t)

- RaceState: Complete race state
  • cars: List[CarState]
  • current_time, current_lap
  • update_positions(): Sort by total_distance
```

**`physics.py`** - Physics Engine

```python
# Vehicle dynamics and control
- DriverController: Calculates throttle/brake/steering
  • calculate_controls(): Decision-making at 100 Hz
  • _calculate_target_speed(): Corner speed logic
  • _calculate_steering(): Ackermann geometry + lookahead
  • _calculate_throttle_brake(): Progressive control

- PhysicsEngine: Force calculations
  • calculate_acceleration(): F=ma with all forces
  • calculate_lateral_forces(): Cornering dynamics
  • update_energy(): Battery and temperature
  • update_tire_degradation(): Multi-factor wear
```

**`stochastic_dynamics.py`** - Noise Models

```python
# Probabilistic uncertainty
- StochasticNoiseModel:
  • apply_process_noise(): ε(t) ~ N(0, Σ)
  • apply_control_noise(): Driver input variation
  • apply_measurement_noise(): Sensor uncertainty

Mathematical models:
  - Gaussian: Driver consistency, control inputs
  - Weibull: Mechanical failures (increasing hazard)
  - Poisson: Random events (safety car)
```

**`events.py`** - Event System

```python
# Probabilistic race events
- EventGenerator:
  • check_crash_probability(): Sigmoid risk model
  • check_overtake(): Logistic regression
  • check_safety_car(): Poisson deployment
  • generate_performance_variation(): N(1.0, 0.05)

- StrategyDecisionMaker:
  • should_activate_attack_mode(): Strategic logic
  • get_energy_management_strategy(): Adaptive control
```

**`engine.py`** - Simulation Orchestrator

```python
# Main simulation loop (100 Hz)
- FormulaERaceEngine:
  • simulate_timestep(dt=0.01): Execute one step
    1. Driver decisions
    2. Apply noise
    3. Physics update
    4. Energy/tire updates
    5. Position updates
    6. Check events (overtakes, crashes)
    7. Update leaderboard

  • get_race_state(): Export current state
  • get_final_standings(): Race results
```

**`mdp_framework.py`** - RL Environment

```python
# OpenAI Gym-style interface
- MDPEnvironment:
  • reset(): Initialize episode
  • step(actions): Execute actions, return (states, rewards, dones, infos)

- ActionSpace: Discrete/continuous actions
  • Discrete: 5 actions (accelerate, brake, left, right, attack)
  • Continuous: [throttle, brake, steering] ∈ [-1, 1]³

- RewardFunction: Multi-objective rewards
  • Position gain: +10 per overtake
  • Energy efficiency: Battery conservation bonus
  • Safety: -100 for crashes
```

**`qualifying.py`** - Qualifying Sessions

```python
# Single-lap performance
- QualifyingSession:
  • run_qualifying(): Simulate all drivers
  • _simulate_qualifying_laps(): 2 flying laps per driver
  • get_starting_grid(): Grid order for race
  • export_results_csv(): Export times
```

**`race_control.py`** - Race Control

```python
# FIA-compliant race control
- RaceControlSystem:
  • check_track_limits(): 3-strike system
  • check_unsafe_behavior(): Dangerous driving detection
  • check_energy_limit(): Energy compliance
  • deploy_safety_car(): Safety car procedures
  • apply_penalties_to_results(): Post-race penalties
```

**`server.py`** - WebSocket Server

```python
# FastAPI real-time streaming
- Endpoints:
  • POST /race/create: Initialize race
  • WebSocket /ws/race: Bi-directional updates
    - Client → Server: {command: "start"/"pause"}
    - Server → Client: {type: "race_update", data: RaceState}

- serialize_car(): Convert CarState to JSON
  • Includes SimPulse features (performance_index, etc.)
```

#### Frontend Core Files

**`page.tsx`** - Main Dashboard

```typescript
// React dashboard with WebSocket
- State management (useState, useEffect)
- WebSocket connection via useWebSocket hook
- Layout: Control panel + Stats grid + Track view + Leaderboard
- Race controls: Create, Start, Pause
```

**`components/Leaderboard.tsx`** - Standings Display

```typescript
// Real-time race positions
- Displays 12+ metrics per car:
  • Position, driver name, lap, time
  • Speed, battery %, energy used
  • Tire degradation, grip
  • Performance index P_i(t) (color-coded)
  • Attack mode indicator
  • Overtakes made
- Mobile responsive grid layout
```

**`components/TrackView.tsx`** - D3.js Visualization

```typescript
// SVG track rendering
- Jakarta E-Prix circuit (2.98 km, 18 turns)
- Real-time car positions (calculated from lap_distance)
- START/FINISH line (green)
- Sector markers (red/yellow)
- Attack mode zones (cyan circles)
- Car tooltips (position, speed, battery)
- Leader in gold, others colored
```

**`components/TrackInfo.tsx`** - Track Metadata

```typescript
// Circuit information cards
- Circuit name, track length
- Number of turns, active cars
- Clean info grid above track view
```

**`hooks/useWebSocket.ts`** - WebSocket Manager

```typescript
// WebSocket connection logic
- Auto-reconnect on disconnect
- Message queuing
- Connection state management
- sendMessage() helper
```

**`types/race.ts`** - TypeScript Types

```typescript
// Type definitions
- Car: 30+ fields including SimPulse features
- RaceState: Complete race state
- WebSocketMessage: Message format
```

#### Visualization Files

**`visualize_race.py`** - Analysis Plots

```python
# Generate 10+ matplotlib plots
1. Track position over time
2. Speed profiles (all cars)
3. Energy consumption curves
4. Battery temperature evolution
5. Tire degradation progression
6. Position changes (overtakes)
7. Lap time comparison
8. Attack mode usage timeline
9. Event markers (crashes, safety car)
10. Statistical summary

Usage: python visualize_race.py --race_file race_basic.json
```

**`live_dashboard.py`** - Plotly Dashboard

```python
# Alternative live dashboard
- Plotly Dash web interface
- Real-time updating plots
- Interactive zoom/pan
- Multiple synchronized views
```

### Data Flow

```
User Input (Frontend)
    ↓
WebSocket (ws://localhost:8000/ws/race)
    ↓
FastAPI Server (server.py)
    ↓
Race Engine (engine.py)
    ↓ [100 Hz loop]
Physics Engine (physics.py) → Events (events.py)
    ↓                              ↓
State Update (state.py) ← Noise (stochastic_dynamics.py)
    ↓
Serialize to JSON (server.py)
    ↓
WebSocket → Frontend
    ↓
D3.js Visualization (TrackView.tsx)
React State Update (page.tsx)
```

### Configuration Files

**Backend:**

- `requirements.txt`: Python dependencies (numpy, fastapi, uvicorn, etc.)
- `test_complete_race.py`: Integration testing

**Frontend:**

- `package.json`: Node dependencies (Next.js, React, D3, TypeScript)
- `tsconfig.json`: TypeScript compiler options
- `tailwind.config.ts`: Tailwind CSS theme
- `next.config.ts`: Next.js build configuration

### Output Files

**Race Results:**

- `race_basic.json`: Complete race state snapshot
- `leaderboard_basic.csv`: Final standings with stats
- `events_basic.csv`: Race events log

**Qualifying:**

- `qualifying_results.csv`: Grid positions and times

**Penalties:**

- `race_penalties.csv`: Penalties issued during race

**Visualizations:**

- `plots/*.png`: All analysis plots

---

## 🏗️ Technical Implementation

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              Frontend (Next.js 16)              │
│  ┌──────────────────────────────────────────┐  │
│  │  Dashboard UI (React 19 + TypeScript)    │  │
│  │  • Real-time leaderboard                 │  │
│  │  • Live track view (D3.js)               │  │
│  │  • Telemetry visualization               │  │
│  └──────────────────────────────────────────┘  │
│                      ↕ WebSocket                │
└─────────────────────────────────────────────────┘
                       ↕ (10 Hz updates)
┌─────────────────────────────────────────────────┐
│           Backend (FastAPI + Python)            │
│  ┌──────────────────────────────────────────┐  │
│  │     Simulation Engine (100 Hz)           │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  Physics Engine                    │  │  │
│  │  │  • Vehicle dynamics (f function)   │  │  │
│  │  │  • Stochastic noise (ε)            │  │  │
│  │  │  • Energy management               │  │  │
│  │  │  • Tire degradation                │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  Driver Controller                 │  │  │
│  │  │  • Target speed calculation        │  │  │
│  │  │  • Steering control (lookahead)    │  │  │
│  │  │  • Throttle/brake logic            │  │  │
│  │  │  • Attack mode strategy            │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  Event System                      │  │  │
│  │  │  • Crash detection (sigmoid)       │  │  │
│  │  │  • Overtake probability (logistic) │  │  │
│  │  │  • Safety car (Poisson)            │  │  │
│  │  │  • Mechanical failures (Weibull)   │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  MDP Framework (RL-Ready)          │  │  │
│  │  │  • Action space (continuous)       │  │  │
│  │  │  • State representation (20D)      │  │  │
│  │  │  • Reward functions                │  │  │
│  │  │  • Policy models                   │  │  │
│  │  └────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Simulation Loop

```python
def simulate_timestep(dt=0.01):  # 100 Hz
    """Main simulation loop executed 100 times per second"""

    for car in race_state.cars:
        if not car.is_active:
            continue

        # 1. Driver decision-making
        throttle, brake, steering, use_attack = driver_controller.calculate_controls(
            car, current_segment, driver_config, race_situation
        )

        # 2. Apply stochastic noise
        throttle, brake, steering = noise_model.apply_control_noise(
            throttle, brake, steering, driver_consistency
        )

        # 3. Physics update
        acceleration = physics.calculate_acceleration(car, throttle, brake)
        lateral_acc = physics.calculate_lateral_acceleration(car, steering)

        # 4. State integration
        car.velocity += acceleration × dt
        car.position += car.velocity × dt
        car.lap_distance += car.velocity × dt

        # 5. Energy update
        energy_consumed = physics.calculate_energy_consumption(car, throttle)
        energy_recovered = physics.calculate_regen(car, brake)
        car.battery_energy += (energy_recovered - energy_consumed) × dt

        # 6. Tire degradation
        tire_wear = physics.calculate_tire_wear(car, lateral_acc, dt)
        car.tire_degradation += tire_wear
        car.grip_coefficient = 1.2 - 0.3 × car.tire_degradation

        # 7. Temperature update
        heat_generated = energy_consumed × (1 - motor_efficiency)
        heat_removed = cooling_system(car.battery_temp)
        car.battery_temp += (heat_generated - heat_removed) × dt

        # 8. Apply process noise
        noise_model.apply_process_noise(car, driver_consistency, dt)

    # 9. Update positions (sort by total_distance)
    race_state.update_positions()

    # 10. Check for overtakes
    for car in race_state.cars:
        for other in race_state.cars:
            if check_proximity(car, other):
                prob = calculate_overtake_probability(car, other, segment)
                if random() < prob × dt:
                    execute_overtake(car, other)

    # 11. Probabilistic events
    check_crashes()
    check_safety_car()
    check_mechanical_failures()

    # 12. Update leaderboard and metrics
    leaderboard.update(race_state)
    metrics.update(race_state)

    return race_state, events
```

### State Management

```python
class CarState:
    """Complete car state with 20-dimensional vector representation"""

    def to_vector(self) -> np.ndarray:
        """Convert state to 20D vector for ML/RL"""
        return np.array([
            self.velocity_x,
            self.velocity_y,
            self.position_x,
            self.position_y,
            self.battery_percentage,
            self.battery_temperature,
            self.tire_degradation,
            self.grip_coefficient,
            float(self.attack_mode_active),
            self.brake_temperature,
            self.lap_distance,
            self.total_distance,
            float(self.current_lap),
            float(self.position),
            self.throttle,
            self.brake_input,
            self.steering_angle,
            self.lateral_g_force,
            self.acceleration,
            self.get_performance_index()
        ])

    def from_vector(self, vec: np.ndarray):
        """Reconstruct state from vector (RL agent output)"""
        self.velocity_x = vec[0]
        self.velocity_y = vec[1]
        # ... restore all 20 components

    def get_performance_index(self) -> float:
        """Calculate P_i(t) performance metric"""
        v_norm = self.get_speed() / MAX_SPEED
        a_norm = self.acceleration / MAX_ACCELERATION
        e_norm = self.battery_percentage / 100.0
        tire_factor = 1.0 - self.tire_degradation
        strategy_factor = self.calculate_strategy_effectiveness()

        weights = [0.25, 0.20, 0.20, 0.20, 0.15]
        components = [v_norm, a_norm, e_norm, tire_factor, strategy_factor]

        return sum(w × c for w, c in zip(weights, components))
```

---

## 🚀 Future Roadmap

#### Reinforcement Learning Integration

- **PPO (Proximal Policy Optimization)** agents for driver behavior
- **SAC (Soft Actor-Critic)** for continuous control optimization
- **Multi-agent competition**: AI vs AI vs Human
- **Transfer learning**: Pre-trained models for different tracks
- **Curriculum learning**: Progressive difficulty for training

#### Advanced Weather System

- **Markov chain weather transitions**: Dynamic rain/dry conditions
- **Track wetness model**: Puddle formation and drying lines
- **Visibility reduction**: Fog, spray from other cars
- **Temperature variations**: Track and air temperature evolution
- **Wind effects**: Headwind/tailwind affecting top speed

#### Enhanced Event System

- **Tire punctures**: Probabilistic failures requiring pit stops
- **Collisions**: Multi-car incident detection and damage modeling
- **Power unit failures**: Sudden or gradual loss of power
- **Brake failures**: Reduced braking effectiveness
- **Sensor failures**: Partial state observability for RL agents

#### Multi-Series Support

- **MotoGP**: Two-wheeled dynamics with lean angles
- **Drone racing**: 3D flight dynamics with gates
- **Autonomous vehicles**: Highway merging and traffic
- **Karting**: Simplified dynamics for faster iteration

#### Advanced Telemetry

- **G-force visualization**: Real-time 3D g-force vectors
- **Thermal imaging**: Tire and brake temperature heatmaps
- **Energy flow diagrams**: Sankey diagrams for power distribution
- **Predictive analytics**: Lap time prediction, tire life estimation

#### Realistic Track Evolution

- **Rubber buildup**: Racing line gets faster over time
- **Track temperature**: Affects grip throughout the race
- **Debris**: Marbles off-line reducing grip
- **Surface degradation**: Bumps and irregularities

#### Team Strategy

- **Pit crew simulation**: Pit stop time variations
- **Team radio**: Strategic instructions and information
- **Multi-car teams**: Teammate cooperation and team orders
- **Strategy optimization**: AI-powered race strategy advisor

#### VR/AR Integration

- **Cockpit view**: First-person perspective
- **360° replay**: Immersive replay system
- **AR telemetry overlay**: Real-time data in VR view

---

## 📦 Installation & Usage

### Prerequisites

- Python 3.8+ (backend)
- Node.js 18+ (frontend)
- 4GB RAM minimum
- Modern web browser (Chrome/Firefox/Edge)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run simulation server
python run_server.py
```

Server will start on `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Dashboard will open at `http://localhost:3000`

### Quick Start Example

```python
from backend.engine import FormulaERaceEngine
from backend.config import TrackConfig

# Create race
engine = FormulaERaceEngine(
    num_cars=12,
    num_laps=10,
    track_config=TrackConfig(),  # Plaksha E-Prix
    random_seed=42
)

# Run simulation
for step in range(10000):  # 100 seconds at 100Hz
    state, events = engine.simulate_timestep()

    # Check race status
    if engine.race_finished:
        print("Race complete!")
        break

# Get results
final_positions = engine.get_final_standings()
race_statistics = engine.get_race_statistics()
```

### Running Tests

```bash
# Complete system test
python test_installation.py

# Specific module tests
python -m pytest tests/test_physics.py
python -m pytest tests/test_events.py
python -m pytest tests/test_mdp.py

# Performance benchmarks
python benchmarks/simulation_speed.py
```

### Visualization Analysis

Generate post-race analysis plots:

```bash
cd visualization_analysis
python visualize_race.py --race_file ../race_results/race_basic.json
```

Outputs:

- Track position over time
- Speed profiles
- Energy consumption
- Tire degradation
- Position changes (overtakes)
- Lap time comparison

---

## 🎓 Educational Use

SimPulse is designed for:

1. **Physics Education**: Demonstrates real-world mechanics
2. **Control Systems**: Driver controller as PID + feedforward
3. **Probability Theory**: Stochastic processes in action
4. **Machine Learning**: RL environment for autonomous racing
5. **Software Engineering**: Clean architecture patterns

### Key Learning Topics

- **State space representation** (vector calculus)
- **Numerical integration** (Euler, RK4 methods)
- **Stochastic differential equations** (SDEs)
- **Probability distributions** (Gaussian, Poisson, Weibull)
- **Optimization** (energy management, race strategy)
- **Real-time systems** (100Hz simulation loop)
- **Event-driven architecture** (asynchronous programming)

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **Physics modeling**: More accurate tire models, aerodynamics
- **AI/RL integration**: Better reward functions, PPO/SAC agents
- **Visualization**: New plot types, interactive 3D views
- **Testing**: Unit tests, integration tests, property-based testing
- **Documentation**: Tutorials, API docs, mathematical derivations
- **Performance**: Vectorization, GPU acceleration, parallel simulation

See `CONTRIBUTING.md` for guidelines.

---

## 📚 References

### Formula E Technical Regulations

- FIA Formula E Gen3 Technical Regulations (2022-2023)
- Formula E Sporting Regulations
- Gen3 Car Specifications (Jaguar, Porsche, Nissan e.dams)

### Academic Papers

- "Stochastic Optimal Control for Hybrid Vehicles" (IEEE Transactions)
- "Probabilistic Models for Racing Applications" (SAE International)
- "Reinforcement Learning for Autonomous Racing" (ICRA)

### Books

- "Race Car Vehicle Dynamics" by Milliken & Milliken
- "Optimal Control Theory" by Kirk
- "Probabilistic Robotics" by Thrun, Burgard, Fox

---

## 📄 License

MIT License - See `LICENSE` file for details.

---

## 🙏 Acknowledgments

- **Formula E** for Gen3 technical specifications
- **FIA** for regulatory documentation
- **OpenAI Gym** for MDP interface inspiration
- **D3.js community** for visualization tools
- **FastAPI** and **Next.js** teams for excellent frameworks

---

## 📞 Contact

- **GitHub**: [github.com/akshat3144/simpulse](https://github.com/akshat3144/simpulse)
- **Email**: akshat3144@gmail.com

---

**Built with ❤️ for the racing and AI community**

_Last updated: November 2025_
