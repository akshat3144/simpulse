"""
Quick test of GPU engine with CPU fallback
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
print("Testing imports...")
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print(f"✓ CuPy available - GPU: {cp.cuda.Device()}")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠ CuPy not available - using CPU fallback")

from engine_gpu import GPURaceEngine, DriverConfig
from config import TrackConfig

print("\n" + "="*60)
print("QUICK GPU ENGINE TEST")
print("="*60)

# Create small test
n_cars = 5
n_laps = 2

print(f"\nTest: {n_cars} cars, {n_laps} laps")
print(f"Device: {'GPU' if GPU_AVAILABLE else 'CPU (fallback)'}")

# Create track
track = TrackConfig()
print(f"Track: {track.track_name}, {track.total_length:.0f}m")

# Create engine
engine = GPURaceEngine(track, n_cars, use_gpu=GPU_AVAILABLE)

# Setup drivers
drivers = []
for i in range(n_cars):
    drivers.append(DriverConfig(
        car_id=i + 1,
        driver_name=f"Driver {i+1}",
        team=f"Team {(i % 3) + 1}",
        skill=0.96 + i * 0.008,
        aggression=0.5,
        consistency=0.94,
        starting_position=i + 1
    ))

engine.setup_drivers(drivers)
print(f"✓ {n_cars} drivers configured")

# Run qualifying
print("\nRunning qualifying...")
start = time.time()
qual_results = engine.run_qualifying(duration_seconds=30.0, dt=0.001)
qual_time = time.time() - start

print(f"\nQualifying Results ({qual_time:.2f}s):")
for result in qual_results[:3]:
    print(f"  {result['position']}. {result['driver_name']}: {result['best_lap_time']:.3f}s")

# Run race  
print("\nRunning race...")
start = time.time()
race_data = engine.run_race(n_laps, dt=0.001, qualifying_results=qual_results, save_history=False)
race_time = time.time() - start

print(f"\n✓ Race complete!")
print(f"  Total steps: {race_data['total_steps']:,}")
print(f"  Real time: {race_time:.2f}s")
print(f"  Performance: {race_data['total_steps']/race_time:,.0f} steps/sec")
print(f"  Speedup: {race_data['speedup']:.1f}x realtime")

print(f"\nFinal Standings:")
for result in race_data['results']:
    print(f"  {result['position']}. {result['driver_name']}: "
          f"{result['laps_completed']} laps, {result['total_time']:.1f}s")

print(f"\n✓ Test complete!")
