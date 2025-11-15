# Formula E Race Simulator - Backend

A comprehensive, physics-based Formula E race simulation engine built in Python. This simulator implements realistic physics, energy management, tire degradation, race control, dynamic weather, and complete qualifying & race weekend simulations.

## 🏎️ Features

### Core Capabilities

- **Realistic Physics Engine** (NO ML/AI):
  - 2D motion with proper Ackermann steering geometry
  - Realistic cornering speeds (90-110 km/h for 60m radius corners)
  - Hard physics limits enforced based on lateral grip
  - Energy consumption and regenerative braking (600kW regen)
  - Tire degradation with temperature effects
  - Battery thermal management
  - Attack mode boost mechanics (strategic activation)

- **Complete Race Weekend**:
  - Qualifying session with flying laps
  - Full race simulation with dynamic weather
  - Race control system (flags, penalties, safety car)
  - Real-time leaderboard and standings

- **Dynamic Systems**:
  - Weather evolution (temperature, humidity, rain, grip changes)
  - Strategic attack mode activation (2 uses per race, +50kW boost)
  - Realistic event system (crashes, safety car, track limits)
  - Driver performance characteristics (skill, aggression, consistency)

- **Comprehensive Data Export**:
  - JSON: Complete timestep history
  - CSV: Race data, events, penalties, qualifying results
  - All data saved in `backend/race_output/`

## 📊 System Architecture

```
backend/
├── config.py              # Physical constants, track config, Formula E Gen3 specs
├── state.py               # State representation (CarState, RaceState)
├── physics.py             # Physics engine with realistic cornering limits
├── events.py              # Event generators & strategy system
├── engine.py              # Main simulation engine
├── leaderboard.py         # Real-time standings and performance metrics
├── qualifying.py          # Qualifying session simulation
├── race_control.py        # Race control (flags, penalties, safety car)
├── weather.py             # Dynamic weather system
├── test_complete_race.py  # Complete race weekend simulation
├── race_output/           # All race data outputs (CSV, JSON)
└── README.md              # This file
```

## 🚀 Quick Start

### Running a Complete Race Weekend

```bash
cd backend
python3 test_complete_race.py
```

This will run:
1. **Qualifying Session**: 2 flying laps per driver
2. **Race Simulation**: 15 lap race with dynamic weather
3. **Data Export**: All results exported to `race_output/`

### Output Files

All data is saved in `backend/race_output/`:
- `qualifying_results.csv` - Qualifying times and grid positions
- `race_timesteps.csv` - Complete timestep data (all car states)
- `race_data_complete.json` - Full race history in JSON
- `race_events.csv` - All race events
- `race_penalties.csv` - Penalties applied
- `final_leaderboard.csv` - Final race classification

## 📈 Visualization

Visualizations are generated separately in `../visualization_analysis/`:

```bash
cd ../visualization_analysis
python3 visualize_race.py       # Static plots
python3 live_dashboard.py       # Interactive dashboard
```

The visualization scripts automatically read from `backend/race_output/`.

## ⚙️ Key Physics Parameters

### Formula E Gen3 Specifications
- **Mass**: 920 kg (car + driver)
- **Power**: 350 kW race mode, 400 kW (with attack mode)
- **Battery**: 51 kWh usable capacity
- **Regeneration**: 600 kW (front + rear)
- **Top Speed**: 322 km/h
- **Acceleration**: 0-100 km/h in 2.8s

### Realistic Cornering
- **Grip Coefficient (μ)**: 1.2 (Formula E street circuit level)
- **Corner Radius**: 60m (medium-speed corners)
- **Corner Speeds**: 85-110 km/h (realistic for Formula E)
- **Physics Enforcement**: Hard speed limit based on v = √(μ × g × r)

### Timestep
- **Resolution**: 0.001s (1000 Hz) for maximum precision
- **Look-ahead**: 2 seconds for early braking into corners

## 🏁 Race Features

### Qualifying
- Realistic lap times (27-29 seconds for Monaco-style 1.95km track)
- Driver skill and consistency factors
- Flying lap simulation

### Race Control
- Track limits monitoring
- Unsafe behavior detection
- Penalty system (time penalties, drive-through)
- Safety car deployment
- Flag system (yellow, red, green)

### Weather System
- Temperature evolution
- Humidity changes
- Rain probability and intensity
- Grip multiplier based on conditions

### Attack Mode
- Strategic activation (not automatic)
- +50 kW power boost
- 2 uses per race
- Duration: 10-15 seconds per activation

## 🎯 Recent Improvements

1. **Realistic Corner Speeds**: Reduced from 200-250 km/h to 85-110 km/h
2. **Hard Physics Limits**: Cars cannot exceed grip-based speed limits
3. **Look-ahead System**: Early braking before corner entry
4. **Increased Braking**: 5.5 m/s² deceleration (up from 4.5)
5. **Lower Grip**: μ = 1.2 for street circuits (down from 1.8)
6. **Reduced Downforce**: 5% boost (down from 10%)

## 📦 Dependencies

```bash
numpy>=1.21.0
pandas>=1.3.0
```

For visualization:
```bash
matplotlib>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0
dash>=2.0.0
```

## 🔧 Configuration

Edit `config.py` to modify:
- Track layout (segments, corners, lengths)
- Physics parameters (grip, drag, downforce)
- Gen3 specifications (power, battery, mass)
- Simulation settings (timestep, random seed)

---

**Current Status**: ✅ Production Ready
- Realistic cornering speeds (85-110 km/h)
- Complete race weekend simulation
- Comprehensive data export
- Clean, maintainable code structure
