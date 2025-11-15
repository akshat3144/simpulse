"""
Complete Formula E Race Simulation with All Features
Includes: Qualifying, Race Control, Dynamic Weather, JSON/CSV Export
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import (
    FormulaERaceEngine,
    QualifyingSession,
    RaceControlSystem,
    DynamicWeatherSystem
)
from backend.config import track_config, DriverConfig

def main():
    """Run complete race weekend simulation"""
    
    print("="*80)
    print("FORMULA E RACE WEEKEND SIMULATION")
    print("="*80)
    print()
    
    # Configuration
    num_cars = 10
    num_laps = 15
    random_seed = 42
    
    # Create output directory in backend folder
    output_dir = os.path.join(os.path.dirname(__file__), "race_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # =======================
    # 1. QUALIFYING SESSION
    # =======================
    print("\n" + "="*80)
    print("STEP 1: QUALIFYING")
    print("="*80)
    
    driver_configs = [DriverConfig.get_driver(i) for i in range(num_cars)]
    
    qualifying = QualifyingSession(
        track_config=track_config,
        driver_configs=driver_configs,
        random_seed=random_seed
    )
    
    qualifying_results = qualifying.run_qualifying(
        num_flying_laps=2,
        verbose=True
    )
    
    # Export qualifying results
    qualifying.export_results_csv(f"{output_dir}/qualifying_results.csv")
    
    starting_grid = qualifying.get_starting_grid()
    
    # =======================
    # 2. RACE SIMULATION
    # =======================
    print("\n" + "="*80)
    print("STEP 2: RACE SIMULATION")
    print("="*80)
    print()
    
    # Initialize race engine
    engine = FormulaERaceEngine(
        num_cars=num_cars,
        num_laps=num_laps,
        random_seed=random_seed
    )
    
    # Initialize race control and weather
    race_control = RaceControlSystem(random_seed=random_seed + 10)
    weather_system = DynamicWeatherSystem(
        initial_temp=28.0,
        initial_humidity=0.65,
        initial_rain=0.0,
        random_seed=random_seed + 20
    )
    
    print(f"Starting Grid (from qualifying):")
    for pos, driver_id in enumerate(starting_grid):
        print(f"  P{pos+1}. {driver_configs[driver_id]['name']}")
    print()
    
    print(f"Initial Weather: {weather_system.get_weather_description()}")
    print()
    
    # Reorder cars based on qualifying
    # (In a full implementation, this would be done in the engine initialization)
    
    print("Starting race...")
    print()
    
    # Run simulation - stop when leader finishes required laps
    max_timesteps = 1000000  # Safety limit
    display_interval = 200  # Display every 10 seconds
    
    for step in range(max_timesteps):
        # Update weather
        weather_system.update(engine.dt)
        
        # Simulate timestep
        state_matrix, leaderboard, events = engine.simulate_timestep()
        
        # Apply race control checks
        for car in engine.race_state.cars:
            if car.is_active:
                # Check track limits
                race_control.check_track_limits(car, track_width=12.0)
                
                # Check unsafe behavior
                other_cars = [c for c in engine.race_state.cars if c.car_id != car.car_id]
                race_control.check_unsafe_behavior(car, other_cars)
                
                # Check energy limit
                race_control.check_energy_limit(car)
        
        # Update safety car
        race_control.update_safety_car(engine.race_state.current_time)
        if race_control.safety_car_active:
            race_control.apply_safety_car_effects(engine.race_state.cars)
        
        # Display progress
        if step % display_interval == 0:
            print(f"\n--- Time: {engine.race_state.current_time:.1f}s ---")
            print(f"Weather: {weather_system.get_weather_description()}")
            print(f"Grip multiplier: {weather_system.state.grip_multiplier:.3f}")
            
            if race_control.safety_car_active:
                print("⚠️  SAFETY CAR DEPLOYED")
            
            print("\nCurrent Standings:")
            for i, entry in enumerate(leaderboard[:5]):
                status = "🟢" if entry.get('status') == 'Running' else "🔴"
                attack = "⚡" if entry.get('attack_mode_active', False) else "  "
                print(f"  {status} P{i+1}. {entry['driver_name']:30s} - "
                      f"Lap {entry['current_lap']}, "
                      f"Speed: {entry['speed_kmh']:3.0f} km/h, "
                      f"Battery: {entry['battery_percentage']:5.1f}% {attack}")
            
            # Show recent events
            if events:
                print("\nRecent Events:")
                for event in events[-3:]:
                    print(f"  - {event['description']}")
        
        # Check if race finished (when leader completes required laps)
        if engine.race_finished:
            print(f"\n🏁 RACE FINISHED at {engine.race_state.current_time:.1f}s")
            break
    
    # =======================
    # 3. FINAL RESULTS
    # =======================
    print("\n" + "="*80)
    print("STEP 3: FINAL RESULTS")
    print("="*80)
    print()
    
    # Apply penalties to results
    final_results = []
    for entry in engine.leaderboard.entries:
        result = {
            'car_id': entry.car_id,
            'driver_name': entry.driver_name,
            'position': entry.position,
            'current_lap': entry.current_lap,
            'best_lap_time': entry.best_lap_time,
            'total_time': engine.race_state.current_time,
            'is_active': entry.is_active
        }
        final_results.append(result)
    
    final_results = race_control.apply_penalties_to_results(final_results)
    
    print("Final Classification:")
    for result in final_results:
        lap_time_str = f"{result['best_lap_time']:.3f}s" if result['best_lap_time'] < float('inf') else "N/A"
        
        # Determine status: FINISHED if race ended and car still active, DNF if crashed
        if not result['is_active']:
            status = "DNF (Crash)"
        elif engine.race_finished and result['is_active']:
            # Race has ended - all active cars are classified as FINISHED
            status = "FINISHED"
        else:
            status = "RUNNING"
        
        penalties_str = f" (+{len(result.get('penalties', []))} penalties)" if result.get('penalties') else ""
        
        print(f"  P{result['position']:2d}. {result['driver_name']:30s} - "
              f"{result['current_lap']} laps, Best: {lap_time_str:10s} - {status}{penalties_str}")
    
    print()
    print(f"Race Control Summary:")
    rc_status = race_control.get_status_summary()
    print(f"  - Total penalties: {rc_status['total_penalties']}")
    print(f"  - Total warnings: {rc_status['total_warnings']}")
    print(f"  - Track limit violations: {rc_status['track_limit_violations']}")
    
    print()
    print(f"Final Weather: {weather_system.get_weather_description()}")
    
    # =======================
    # 4. EXPORT DATA
    # =======================
    print("\n" + "="*80)
    print("STEP 4: EXPORTING DATA")
    print("="*80)
    print()
    
    # Export timestep data (JSON and CSV)
    print("Exporting timestep data...")
    engine.export_timestep_data_json(f"{output_dir}/race_data_complete.json")
    engine.export_timestep_data_csv(f"{output_dir}/race_timesteps.csv")
    
    # Export events
    print("\nExporting events...")
    engine.export_events_csv(f"{output_dir}/race_events.csv")
    
    # Export penalties
    print("\nExporting penalties...")
    race_control.export_penalties_csv(f"{output_dir}/race_penalties.csv")
    
    # Export final leaderboard
    print("\nExporting leaderboard...")
    engine.export_to_csv(f"{output_dir}/final_leaderboard.csv")
    
    print("\n" + "="*80)
    print("✓ RACE WEEKEND COMPLETE!")
    print("="*80)
    print(f"\nAll data exported to: {output_dir}/")
    print("\nFiles created:")
    print("  - qualifying_results.csv")
    print("  - race_data_complete.json (full timestep history)")
    print("  - race_timesteps.csv (all car states per timestep)")
    print("  - race_events.csv")
    print("  - race_penalties.csv")
    print("  - final_leaderboard.csv")

if __name__ == "__main__":
    main()
