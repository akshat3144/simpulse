# Formula E Simulation Visualization Suite

This folder contains comprehensive visualization tools to analyze and verify the Formula E race simulation.

## Quick Start

Run the visualization script:
```bash
cd visualization_analysis
python3 visualize_race.py
```

This will generate all plots in the `plots/` subdirectory.

## Generated Visualizations

### 1. Track Position (`1_track_position.png`)
- **Purpose**: Verify 2D position calculation is working correctly
- **What to look for**:
  - Track should show a complete circuit layout
  - Cars should follow the track path (not just moving in X direction)
  - Color gradient shows time progression
  - Y-axis should vary significantly (not stuck at 0)

### 2. Speed Profiles (`2_speed_profiles.png`)
- **Purpose**: Verify speed varies realistically through corners
- **What to look for**:
  - Speed should decrease in corners, increase on straights
  - Top panel: All cars' speed over time
  - Bottom panel: Speed vs track position for one lap
  - Should see clear speed reduction at corner sections

### 3. Steering Analysis (`3_steering_analysis.png`)
- **Purpose**: Verify steering angle changes appropriately
- **What to look for**:
  - Steering should vary between negative (left) and positive (right)
  - Should NOT be stuck at 0° throughout
  - Histogram should show distribution of steering angles
  - More time at 0° (straights) is normal, but should have significant corner angles

### 4. Energy Management (`4_energy_management.png`)
- **Purpose**: Verify battery behavior is realistic
- **What to look for**:
  - Battery SOC should gradually decrease over race
  - Battery temperature should INCREASE (not decrease) during racing
  - Temperature should stabilize around 42-45°C with cooling
  - Power output should vary with acceleration/braking

### 5. Tire Degradation (`5_tire_degradation.png`)
- **Purpose**: Verify tire wear is gradual and realistic
- **What to look for**:
  - Degradation should increase slowly over time
  - Should be well below 100% by race end (not hit 1.0 in seconds)
  - Linear or slightly curved increase
  - Typical end value: 0.5-2% for a short race

### 6. Race Positions (`6_race_positions.png`)
- **Purpose**: Verify position tracking and overtakes
- **What to look for**:
  - Position lines should cross when overtakes occur
  - Positions should be integers (1, 2, 3, ...)
  - Some variation is good (shows competitive racing)

### 7. Attack Mode (`7_attack_mode.png`)
- **Purpose**: Verify attack mode timing is correct
- **What to look for**:
  - Attack mode should activate in discrete bursts
  - Maximum duration: 240 seconds
  - Should see clear on/off patterns
  - Cars should use it 1-2 times per race

### 8. Lap Times (`8_lap_times.png`)
- **Purpose**: Verify lap timing consistency
- **What to look for**:
  - Lap times should be relatively consistent per car
  - Variation is normal (traffic, battery level, tires)
  - Typical range: 30-40 seconds per lap for 2.5km track
  - Bar chart shows average lap time comparison

### 9. Race Snapshot (`9_race_snapshot.png`)
- **Purpose**: Visualize race spread at a moment in time
- **What to look for**:
  - Shows relative positions on track
  - Leaders should be ahead on lap distance
  - Clear visualization of gaps between cars

### 10. Dashboard (`10_dashboard.png`)
- **Purpose**: Comprehensive overview of all key metrics
- **What to look for**:
  - Track layout in main panel
  - Speed, battery, and position subplots
  - Quick verification of all major simulation aspects

## Statistics Report

The `race_statistics.txt` file contains:
- Race duration and timestep information
- Position ranges (X, Y coordinates)
- Speed statistics (min, max, average)
- Steering angle usage
- Energy consumption and regeneration per car
- Battery temperature ranges
- Final tire degradation per car
- Attack mode usage statistics
- Final race classification

## Validation Checklist

Use these visualizations to verify:

- [x] **Position Y varies** - Check plot #1, should see full 2D track
- [x] **Speed varies in corners** - Check plot #2, should see speed drops
- [x] **Steering angles change** - Check plot #3, should see non-zero values
- [x] **Lap distance increases** - Check statistics, verify monotonic increase
- [x] **Battery temp increases** - Check plot #4, should rise during race
- [x] **Tire deg is gradual** - Check plot #5, should be < 5% for short races
- [x] **Attack mode correct** - Check plot #7, max 240s duration

## Dependencies

```bash
pip install pandas matplotlib numpy seaborn
```

## Customization

Edit `visualize_race.py` to:
- Change figure sizes (figsize parameter)
- Adjust colors and styles
- Focus on specific cars or time ranges
- Add additional analysis plots

## Troubleshooting

**No plots generated?**
- Ensure `race_output/race_data_timesteps.csv` exists
- Run a race first: `python3 test_complete_race.py`

**Plots look wrong?**
- Check the statistics file for data ranges
- Verify CSV data has expected columns
- Look for error messages in console output

**Want more detail?**
- Increase figure DPI (change `dpi=150` to `dpi=300`)
- Adjust time ranges or sampling rates
- Add print statements to debug specific values
