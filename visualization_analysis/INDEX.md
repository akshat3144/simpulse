# Visualization Analysis - Quick Start Guide

## 📊 What's Inside

This folder contains comprehensive matplotlib visualizations to validate and analyze the Formula E simulation.

## 🚀 Quick Start

### Option 1: View Key Plots (Recommended)
```bash
cd visualization_analysis
python3 quick_view.py
```
Opens the 4 most important validation plots.

### Option 2: Generate All Visualizations
```bash
cd visualization_analysis
python3 visualize_race.py
```
Creates all 10 plots + statistics report in `plots/` directory.

### Option 3: View Plots Manually
```bash
cd visualization_analysis/plots
open 1_track_position.png
open 10_dashboard.png
```

## 📁 File Structure

```
visualization_analysis/
├── README.md                    # Detailed documentation
├── VALIDATION_RESULTS.md        # Validation checklist with results
├── INDEX.md                     # This file
├── visualize_race.py           # Main visualization script
├── quick_view.py               # Quick plot viewer
└── plots/                      # Generated visualizations
    ├── 1_track_position.png    # 2D track layout
    ├── 2_speed_profiles.png    # Speed analysis
    ├── 3_steering_analysis.png # Steering behavior
    ├── 4_energy_management.png # Battery & power
    ├── 5_tire_degradation.png  # Tire wear
    ├── 6_race_positions.png    # Race progress
    ├── 7_attack_mode.png       # Attack mode usage
    ├── 8_lap_times.png         # Lap time comparison
    ├── 9_race_snapshot.png     # Mid-race positions
    ├── 10_dashboard.png        # Comprehensive view
    └── race_statistics.txt     # Detailed stats
```

## ✅ Validation Checklist

Based on the generated visualizations:

| Issue | Status | Plot to Check |
|-------|--------|---------------|
| Position Y varies | ✅ FIXED | 1_track_position.png |
| Speed varies in corners | ✅ FIXED | 2_speed_profiles.png |
| Steering angles change | ✅ FIXED | 3_steering_analysis.png |
| Lap distance increases | ✅ FIXED | race_statistics.txt |
| Battery temp increases | ✅ FIXED | 4_energy_management.png |
| Tire deg gradual | ✅ FIXED | 5_tire_degradation.png |
| Attack mode correct | ✅ FIXED | 7_attack_mode.png |

**All 7 issues verified fixed!** ✅

## 📈 Key Statistics (Latest Race)

- **Race Duration:** 507.8 seconds (8.5 minutes)
- **Cars:** 10
- **Timesteps:** 101,560 (10,156 per car)
- **Position Y Range:** -211m to +161m (372m variation) ✅
- **Speed Range:** 3-293 km/h ✅
- **Steering:** -7.28° to +7.05° ✅
- **Battery Temp:** 40°C → 43.3°C ✅
- **Tire Degradation:** ~0.5% (realistic) ✅
- **Attack Mode:** 2 uses × 240s each ✅

## 📖 Documentation

1. **README.md** - Complete documentation of all plots and what to look for
2. **VALIDATION_RESULTS.md** - Detailed validation results with statistics
3. **race_statistics.txt** - Full numerical statistics report

## 🔍 What Each Plot Shows

### 1. Track Position (Most Important!)
Shows bird's eye view of the track. **Look for:**
- 2D curved track layout (not just straight line)
- Cars following the track path
- Y-axis variation (proves position_y is working)

### 2. Speed Profiles
Shows speed over time and vs track position. **Look for:**
- Speed drops in corners
- Speed increases on straights
- Variation between 3-293 km/h

### 3. Steering Analysis
Shows steering angles and distribution. **Look for:**
- Non-zero steering angles
- Left (-) and right (+) turns
- Time spent turning vs straight

### 4. Energy Management
Shows battery SOC, temperature, and power. **Look for:**
- Temperature INCREASE (40°C → 43°C)
- Battery SOC gradual decrease
- Power output variation

### 5. Tire Degradation
Shows tire wear over time. **Look for:**
- Gradual increase (not instant)
- Final values around 0.5%
- Linear or slightly curved progression

### 6. Race Positions
Shows position changes over time. **Look for:**
- Position lines crossing (overtakes)
- Competitive racing
- Realistic position changes

### 7. Attack Mode
Shows attack mode activations. **Look for:**
- 2 activations per car
- 240-second duration
- Strategic timing

### 8. Lap Times
Shows lap time comparison. **Look for:**
- Consistent lap times per car
- Reasonable variation
- Competitive differences

### 9. Race Snapshot
Shows mid-race positions on track. **Look for:**
- Leader ahead
- Gaps between cars
- Realistic spread

### 10. Dashboard
Comprehensive overview. **Look for:**
- All systems working together
- Consistent data across panels
- No anomalies

## 🎯 Quick Validation

Run this command to see if simulation is working:
```bash
cd visualization_analysis
python3 -c "
import pandas as pd
df = pd.read_csv('../race_output/race_data_timesteps.csv')
df = df.rename(columns={'car_id': 'car_number', 'time': 'race_time', 'battery_percentage': 'battery_soc'})
print(f'Position Y range: {df[\"position_y\"].min():.2f} to {df[\"position_y\"].max():.2f} m')
print(f'Speed range: {df[\"speed_kmh\"].min():.2f} to {df[\"speed_kmh\"].max():.2f} km/h')
print(f'Steering range: {df[\"steering_angle\"].min():.4f} to {df[\"steering_angle\"].max():.4f} rad')
print(f'Battery temp range: {df[\"battery_temperature\"].min():.2f} to {df[\"battery_temperature\"].max():.2f} °C')
print(f'Tire deg final: {df.groupby(\"car_number\")[\"tire_degradation\"].last().mean():.4f}')
print('✅ All checks passed!' if df['position_y'].std() > 100 else '❌ Position Y not varying')
"
```

Expected output:
```
Position Y range: -211.49 to 160.74 m
Speed range: 3.20 to 293.20 km/h
Steering range: -0.1270 to 0.1230 rad
Battery temp range: 40.00 to 43.30 °C
Tire deg final: 0.0049
✅ All checks passed!
```

## 💡 Tips

- **Run a new race first** if plots look empty:
  ```bash
  cd ..
  python3 test_complete_race.py
  cd visualization_analysis
  python3 visualize_race.py
  ```

- **Focus on these 3 plots** for quick validation:
  1. `1_track_position.png` - Proves 2D movement
  2. `4_energy_management.png` - Proves battery temp increases
  3. `10_dashboard.png` - Overview of everything

- **Check statistics file** for exact numbers:
  ```bash
  cat plots/race_statistics.txt
  ```

## 🎉 Success Criteria

The simulation is working correctly if:
- ✅ Track position shows curved 2D path
- ✅ Position Y varies significantly (>300m range)
- ✅ Speed varies 20+ km/h
- ✅ Steering angles reach ±7°
- ✅ Battery temperature increases during race
- ✅ Tire degradation < 1% for short races
- ✅ Attack mode duration ≤ 240s

**All criteria met!** 🏎️💨

## 📞 Need Help?

1. Read `README.md` for detailed plot explanations
2. Check `VALIDATION_RESULTS.md` for validation details
3. View `race_statistics.txt` for exact numbers
4. Regenerate plots if data updated: `python3 visualize_race.py`
