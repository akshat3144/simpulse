# 🎨 Visualization Quick Start

## Get Live Charts in 3 Steps!

### Step 1: Install Matplotlib

```bash
pip install matplotlib
```

### Step 2: Run Example

```bash
cd formula_e_simulator
python example_visualization.py
```

### Step 3: Choose Option 1

```
Select example (1-5) or press Enter for #1: 1
```

**That's it! You'll see 6 live charts updating in real-time!**

---

## What You'll See

```
┌─────────────────────────────────────────────┐
│  🏁 Formula E Race Simulation - Live        │
├──────────────────┬──────────────────────────┤
│ Race Positions   │ Battery Energy           │
│ (bar chart)      │ (line over time)         │
├──────────────────┼──────────────────────────┤
│ Speed Profile    │ Best Lap Times           │
│ (line over time) │ (bar chart)              │
├──────────────────┼──────────────────────────┤
│ Tire Degradation │ Race Info Panel          │
│ (color-coded)    │ (text display)           │
└──────────────────┴──────────────────────────┘

Controls: [SPACE] Pause/Resume | [Q] Quit
```

---

## More Examples

### Example 2: Post-Race Analysis

```bash
python example_visualization.py
# Select: 2
```

Creates comprehensive analysis charts after race completes.

### Example 3: Record Snapshots

```bash
python example_visualization.py
# Select: 3
```

Saves PNG images during race for creating videos.

### Example 4: Compare Strategies

```bash
python example_visualization.py
# Select: 4
```

Compares ML vs Simple AI strategies side-by-side.

---

## Use in Your Own Code

```python
from formula_e_simulator import FormulaERaceEngine
from formula_e_simulator.visualization import RaceVisualizer
import matplotlib.pyplot as plt

# Create engine and visualizer
engine = FormulaERaceEngine(num_cars=12, num_laps=5)
viz = RaceVisualizer(num_cars=12)
viz.setup_figure()

# Enable interactive mode
plt.ion()
viz.show(block=False)

# Run simulation with live updates
step = 0
while not engine.race_finished:
    engine.simulate_timestep()

    # Update visualization every second
    if step % 10 == 0:
        viz.update(engine.race_state)
        plt.pause(0.01)

    step += 1

# Keep window open
plt.ioff()
plt.show()
```

---

## Common Issues

### Issue: Window doesn't appear

```python
# Add before importing pyplot:
import matplotlib
matplotlib.use('TkAgg')
```

### Issue: ImportError for matplotlib

```bash
pip install matplotlib
```

### Issue: Window freezes

```python
# Reduce update frequency:
if step % 20 == 0:  # Update every 2 seconds instead of 1
    viz.update(engine.race_state)
```

---

## What Each Chart Shows

| Chart                | Information                                             |
| -------------------- | ------------------------------------------------------- |
| **Race Positions**   | Bar chart of distance traveled, color-coded by position |
| **Battery Energy**   | Line graph showing energy depletion for top 5 cars      |
| **Speed Profile**    | Real-time speed (km/h) showing acceleration/braking     |
| **Best Lap Times**   | Fastest laps comparison across drivers                  |
| **Tire Degradation** | Color-coded bars (green/orange/red)                     |
| **Race Info**        | Current time, leader, lap count, controls               |

---

## Features

✅ **Real-time updates** - Charts update during race
✅ **Interactive** - Zoom, pan, save using toolbar
✅ **Color-coded** - Gold/silver/bronze for podium
✅ **Keyboard controls** - Space to pause, Q to quit
✅ **Save snapshots** - Export images at any time
✅ **Post-race analysis** - Comprehensive statistics
✅ **Strategy comparison** - ML vs Simple AI

---

## Next Steps

1. **Try it now**: `python example_visualization.py`
2. **Read full guide**: `VISUALIZATION_GUIDE.md`
3. **Customize charts**: Edit `visualization.py`
4. **Create videos**: Record snapshots + ffmpeg

---

## Learn More

- **Full Documentation**: See `VISUALIZATION_GUIDE.md`
- **Code Examples**: See `example_visualization.py`
- **Customization**: Edit `visualization.py` class methods

---

**Ready? Let's visualize!**

```bash
python example_visualization.py
```

🏎️💨
