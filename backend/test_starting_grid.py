"""
Test script to verify starting grid integration works correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import (
    FormulaERaceEngine,
    QualifyingSession,
    DriverConfig
)
from backend.config import track_config

def test_starting_grid():
    """Test that qualifying results properly reorder starting grid"""
    
    print("="*80)
    print("STARTING GRID INTEGRATION TEST")
    print("="*80)
    print()
    
    # Configuration
    num_cars = 6
    num_laps = 2
    random_seed = 42
    
    # Create drivers
    driver_configs = [DriverConfig.get_driver(i) for i in range(num_cars)]
    
    print("Original Driver Order (by car ID):")
    for i, driver in enumerate(driver_configs):
        print(f"  Car {i}: {driver['name']} (skill: {driver['skill']:.3f})")
    print()
    
    # =======================
    # 1. RUN QUALIFYING
    # =======================
    print("Running qualifying session...")
    qualifying = QualifyingSession(
        track_config=track_config,
        driver_configs=driver_configs,
        random_seed=random_seed
    )
    
    qualifying_results = qualifying.run_qualifying(
        num_flying_laps=2,
        verbose=False
    )
    
    starting_grid = qualifying.get_starting_grid()
    
    print("\nQualifying Results:")
    for result in qualifying_results:
        print(f"  P{result['qualifying_position']}. {result['driver_name']:30s} - "
              f"{result['best_lap_time']:.3f}s (Car ID: {result['driver_id']})")
    print()
    
    print(f"Starting Grid Order: {starting_grid}")
    print()
    
    # =======================
    # 2. INITIALIZE RACE ENGINE
    # =======================
    print("Initializing race engine...")
    engine = FormulaERaceEngine(
        num_cars=num_cars,
        num_laps=num_laps,
        random_seed=random_seed
    )
    
    # Check initial order (should be default 0, 1, 2, 3, 4, 5)
    print("\nBEFORE setting starting grid:")
    for car in engine.race_state.cars:
        print(f"  Position {car.position}: Car ID {car.car_id} - {car.driver_name}")
    print()
    
    # =======================
    # 3. APPLY STARTING GRID
    # =======================
    print("Applying qualifying results to starting grid...")
    engine.set_starting_grid(starting_grid)
    print()
    
    # Check new order (should match qualifying)
    print("AFTER setting starting grid:")
    for car in engine.race_state.cars:
        print(f"  Position {car.position}: Car ID {car.car_id} - {car.driver_name}")
    print()
    
    # =======================
    # 4. VERIFY CORRECTNESS
    # =======================
    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print()
    
    # Verify positions match qualifying
    success = True
    for idx, (car, expected_original_id) in enumerate(zip(engine.race_state.cars, starting_grid)):
        expected_driver = driver_configs[expected_original_id]['name']
        actual_driver = car.driver_name
        
        if actual_driver != expected_driver:
            print(f"❌ Position {idx + 1}: Expected {expected_driver}, got {actual_driver}")
            success = False
        else:
            print(f"✓ Position {idx + 1}: {actual_driver} (correct)")
    
    print()
    
    # =======================
    # 5. RUN SHORT RACE TO TEST
    # =======================
    if success:
        print("="*80)
        print("RUNNING SHORT RACE TEST")
        print("="*80)
        print()
        
        print("Starting race with qualifying grid order...")
        
        # Simulate a few seconds
        for step in range(50):  # 5 seconds at 0.1s timestep
            engine.simulate_timestep()
        
        print(f"\nRace standings after 5 seconds:")
        leaderboard_entries = engine.leaderboard.entries
        for entry in leaderboard_entries[:6]:
            print(f"  P{entry.position}. {entry.driver_name:30s} - "
                  f"Distance: {entry.total_distance:.1f}m, "
                  f"Speed: {entry.speed_kmh:.0f} km/h")
        
        print()
        print("="*80)
        print("✅ TEST PASSED - Starting grid integration working correctly!")
        print("="*80)
    else:
        print()
        print("="*80)
        print("❌ TEST FAILED - Starting grid not properly applied")
        print("="*80)

if __name__ == "__main__":
    test_starting_grid()
