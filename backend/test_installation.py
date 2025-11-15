"""
Test script to verify Formula E Simulator installation and basic functionality
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("\n" + "="*80)
print("FORMULA E SIMULATOR - INSTALLATION TEST")
print("="*80)

# Test 1: Import dependencies
print("\n[1/6] Testing dependencies...")
try:
    import numpy as np
    import scipy
    import sklearn
    print("  ✓ NumPy version:", np.__version__)
    print("  ✓ SciPy version:", scipy.__version__)
    print("  ✓ Scikit-learn version:", sklearn.__version__)
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    sys.exit(1)

# Test 2: Import simulator modules
print("\n[2/6] Testing simulator imports...")
try:
    from formula_e_simulator import (
        FormulaERaceEngine, CarState, RaceState,
        PhysicsConfig, TrackConfig, SimulationConfig
    )
    print("  ✓ Core modules imported successfully")
except ImportError as e:
    print(f"  ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Create engine
print("\n[3/6] Testing engine creation...")
try:
    engine = FormulaERaceEngine(
        num_cars=6,
        num_laps=2,
        use_ml_strategy=False,  # Disable ML for quick test
        random_seed=42
    )
    print(f"  ✓ Engine created with {engine.num_cars} cars, {engine.num_laps} laps")
except Exception as e:
    print(f"  ✗ Engine creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check state vector
print("\n[4/6] Testing state vector framework...")
try:
    state_matrix = engine.race_state.get_state_matrix()
    print(f"  ✓ State matrix shape: {state_matrix.shape}")
    print(f"  ✓ State dimension per car: {state_matrix.shape[1]}")
    
    car = engine.race_state.cars[0]
    state_vec = car.to_vector()
    print(f"  ✓ Individual car state vector length: {len(state_vec)}")
except Exception as e:
    print(f"  ✗ State vector test failed: {e}")
    sys.exit(1)

# Test 5: Run simulation steps
print("\n[5/6] Testing simulation execution...")
try:
    for i in range(10):
        state_matrix, leaderboard, events = engine.simulate_timestep()
    
    print(f"  ✓ Successfully executed 10 simulation steps")
    print(f"  ✓ Simulation time: {engine.race_state.current_time:.2f} seconds")
    print(f"  ✓ Leader: {engine.race_state.cars[0].driver_name}")
except Exception as e:
    print(f"  ✗ Simulation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Check leaderboard
print("\n[6/6] Testing leaderboard system...")
try:
    engine.leaderboard.update(engine.race_state)
    top_3 = engine.leaderboard.get_top_n(3)
    print(f"  ✓ Leaderboard has {len(engine.leaderboard.entries)} entries")
    print(f"  ✓ Top 3 drivers:")
    for entry in top_3:
        print(f"      {entry.position}. {entry.driver_name} - {entry.speed_kmh:.1f} km/h")
except Exception as e:
    print(f"  ✗ Leaderboard test failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*80)
print("✅ ALL TESTS PASSED - FORMULA E SIMULATOR IS READY!")
print("="*80)
print("\nNext steps:")
print("  1. Run a full race: python run_race.py")
print("  2. Try examples: python example_race.py")
print("  3. Read the documentation: README.md")
print("\n" + "="*80 + "\n")
