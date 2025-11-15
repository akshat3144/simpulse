"""
Example Usage Script for Formula E Race Simulator
Demonstrates a complete 10-lap race simulation with all features
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from formula_e_simulator import FormulaERaceEngine, TrackConfig


def run_basic_race():
    """Run a basic 10-lap race with default settings"""
    print("\n" + "="*100)
    print("EXAMPLE 1: Basic 10-Lap Race")
    print("="*100)
    
    # Create race engine with default settings
    engine = FormulaERaceEngine(
        num_cars=24,
        num_laps=10,
        use_ml_strategy=True,
        random_seed=42
    )
    
    # Run simulation
    summary = engine.run_simulation(
        display_interval=100,  # Update every 100 steps
        verbose=True
    )
    
    # Print summary statistics
    print("\n" + "="*100)
    print("RACE SUMMARY")
    print("="*100)
    print(f"Total Race Time: {summary['race_info']['race_time_seconds']:.1f} seconds")
    print(f"Total Distance: {summary['race_info']['total_distance_km']:.2f} km")
    print(f"Simulation Speed: {summary['race_info']['simulation_speed']}")
    print(f"\nTotal Events: {summary['events']['total_events']}")
    print(f"  - Overtakes: {summary['events']['overtakes']}")
    print(f"  - Crashes: {summary['events']['crashes']}")
    print(f"  - Attack Mode Activations: {summary['events']['attack_modes']}")
    print(f"  - Safety Cars: {summary['events']['safety_cars']}")
    
    # Export results
    output_dir = Path(__file__).parent / "race_results"
    output_dir.mkdir(exist_ok=True)
    
    engine.export_to_json(str(output_dir / "race_basic.json"))
    engine.export_to_csv(str(output_dir / "leaderboard_basic.csv"))
    
    return engine, summary


def run_custom_track_race():
    """Run a race with custom track configuration"""
    print("\n\n" + "="*100)
    print("EXAMPLE 2: Custom Track Race")
    print("="*100)
    
    # Create custom track
    custom_track = TrackConfig(track_name="Custom Circuit")
    
    # Create race engine with custom track
    engine = FormulaERaceEngine(
        num_cars=20,
        num_laps=15,
        track_config=custom_track,
        use_ml_strategy=True,
        random_seed=123
    )
    
    # Run simulation
    summary = engine.run_simulation(
        display_interval=150,
        verbose=True
    )
    
    # Export results
    output_dir = Path(__file__).parent / "race_results"
    output_dir.mkdir(exist_ok=True)
    
    engine.export_to_json(str(output_dir / "race_custom_track.json"))
    engine.export_to_csv(str(output_dir / "leaderboard_custom_track.csv"))
    
    return engine, summary


def run_step_by_step_race():
    """Run a race step-by-step with detailed monitoring"""
    print("\n\n" + "="*100)
    print("EXAMPLE 3: Step-by-Step Race with Detailed Monitoring")
    print("="*100)
    
    # Create race engine
    engine = FormulaERaceEngine(
        num_cars=12,
        num_laps=5,
        use_ml_strategy=True,
        random_seed=456
    )
    
    print("\nRunning race step-by-step...\n")
    
    # Track some statistics
    lap_times = []
    energy_consumption = []
    
    step_count = 0
    max_steps = 5000  # Safety limit
    
    while not engine.race_finished and step_count < max_steps:
        # Simulate one timestep
        state_matrix, leaderboard, events = engine.simulate_timestep()
        
        # Display every 50 steps
        if step_count % 50 == 0 and step_count > 0:
            leader = None
            for car in engine.race_state.cars:
                if car.position == 1 and car.is_active:
                    leader = car
                    break
            
            if leader:
                print(f"Step {step_count:4d} | Time: {engine.race_state.current_time:6.1f}s | "
                      f"Leader: {leader.driver_name:15s} | Lap: {leader.current_lap}/{engine.num_laps} | "
                      f"Battery: {leader.battery_percentage:5.1f}% | "
                      f"Speed: {leader.get_speed_kmh():6.1f} km/h")
                
                # Track energy consumption
                energy_consumption.append(leader.battery_percentage)
        
        # Show events immediately
        if events:
            for event in events:
                print(f"  ⚠️  {event['description']}")
        
        step_count += 1
    
    # Final statistics
    print("\n" + "="*100)
    print("DETAILED RACE ANALYSIS")
    print("="*100)
    
    # Analyze top 3 finishers
    print("\nTop 3 Finishers Analysis:")
    for i in range(min(3, len(engine.leaderboard.entries))):
        entry = engine.leaderboard.entries[i]
        car = engine.race_state.cars[entry.car_id]
        
        print(f"\n{entry.position}. {entry.driver_name}")
        print(f"   Final Battery: {car.battery_percentage:.1f}%")
        print(f"   Energy Efficiency: {car.get_energy_efficiency():.2f} km/kWh")
        print(f"   Max Speed: {car.max_speed_achieved * 3.6:.1f} km/h")
        print(f"   Overtakes Made: {car.overtakes_made}")
        print(f"   Best Lap: {car.best_lap_time:.3f}s" if car.best_lap_time != np.inf else "N/A")
    
    # Export results
    output_dir = Path(__file__).parent / "race_results"
    output_dir.mkdir(exist_ok=True)
    
    engine.export_to_json(str(output_dir / "race_stepbystep.json"))
    engine.export_to_csv(str(output_dir / "leaderboard_stepbystep.csv"))
    
    return engine


def compare_ml_vs_simple_strategy():
    """Compare ML strategy against simple rule-based strategy"""
    print("\n\n" + "="*100)
    print("EXAMPLE 4: ML Strategy vs Simple Strategy Comparison")
    print("="*100)
    
    results = {}
    
    # Run with ML strategy
    print("\nRace 1: WITH ML Strategy")
    print("-" * 100)
    engine_ml = FormulaERaceEngine(
        num_cars=12,
        num_laps=10,
        use_ml_strategy=True,
        random_seed=789
    )
    summary_ml = engine_ml.run_simulation(display_interval=200, verbose=True)
    results['ml'] = summary_ml
    
    # Run without ML strategy
    print("\n\nRace 2: WITHOUT ML Strategy (Simple AI)")
    print("-" * 100)
    engine_simple = FormulaERaceEngine(
        num_cars=12,
        num_laps=10,
        use_ml_strategy=False,
        random_seed=789  # Same seed for fair comparison
    )
    summary_simple = engine_simple.run_simulation(display_interval=200, verbose=True)
    results['simple'] = summary_simple
    
    # Compare results
    print("\n" + "="*100)
    print("STRATEGY COMPARISON")
    print("="*100)
    
    print(f"\nML Strategy:")
    print(f"  Total Overtakes: {summary_ml['events']['overtakes']}")
    print(f"  Total Crashes: {summary_ml['events']['crashes']}")
    print(f"  Average Driver Rating: {np.mean(list(summary_ml['performance_metrics']['driver_ratings'].values())):.2f}")
    
    print(f"\nSimple Strategy:")
    print(f"  Total Overtakes: {summary_simple['events']['overtakes']}")
    print(f"  Total Crashes: {summary_simple['events']['crashes']}")
    print(f"  Average Driver Rating: {np.mean(list(summary_simple['performance_metrics']['driver_ratings'].values())):.2f}")
    
    return results


def demonstrate_state_vector():
    """Demonstrate the state vector framework"""
    print("\n\n" + "="*100)
    print("EXAMPLE 5: State Vector Framework Demonstration")
    print("="*100)
    
    # Create engine
    engine = FormulaERaceEngine(
        num_cars=6,
        num_laps=3,
        use_ml_strategy=False,
        random_seed=999
    )
    
    print("\nInitial State Matrix:")
    print("-" * 100)
    
    # Get initial state matrix
    initial_state = engine.race_state.get_state_matrix()
    print(f"Shape: {initial_state.shape}")
    print(f"[num_cars={initial_state.shape[0]}, state_dimension={initial_state.shape[1]}]")
    
    print("\nState vector components for Car 0:")
    car = engine.race_state.cars[0]
    state_vec = car.to_vector()
    
    components = [
        "position_x", "position_y", "velocity_x", "velocity_y",
        "battery_%", "battery_temp", "tire_deg", "grip_coef",
        "attack_active", "attack_remaining", "current_lap", "lap_distance",
        "acceleration", "steering", "throttle", "brake",
        "is_active", "position", "gap_to_leader", "total_distance"
    ]
    
    for i, (component, value) in enumerate(zip(components, state_vec)):
        print(f"  [{i:2d}] {component:20s}: {value:10.3f}")
    
    # Run a few steps
    print("\n\nRunning 100 simulation steps...")
    for _ in range(100):
        engine.simulate_timestep()
    
    # Show updated state
    print("\nState Matrix after 100 steps:")
    updated_state = engine.race_state.get_state_matrix()
    print(f"Shape: {updated_state.shape}")
    
    print("\nUpdated state vector for Car 0:")
    car = engine.race_state.cars[0]
    state_vec = car.to_vector()
    
    for i, (component, value) in enumerate(zip(components, state_vec)):
        print(f"  [{i:2d}] {component:20s}: {value:10.3f}")
    
    print("\n" + "="*100)


def main():
    """Run all examples"""
    print("\n" + "="*100)
    print("FORMULA E RACE SIMULATOR - COMPREHENSIVE EXAMPLES")
    print("="*100)
    print("\nThis script demonstrates all capabilities of the simulator:")
    print("1. Basic race simulation")
    print("2. Custom track configuration")
    print("3. Step-by-step monitoring")
    print("4. ML vs Simple strategy comparison")
    print("5. State vector framework")
    print("\n" + "="*100)
    
    try:
        # Run examples
        print("\n>>> Running Example 1: Basic Race...")
        engine1, summary1 = run_basic_race()
        
        print("\n>>> Running Example 2: Custom Track...")
        engine2, summary2 = run_custom_track_race()
        
        print("\n>>> Running Example 3: Step-by-Step...")
        engine3 = run_step_by_step_race()
        
        print("\n>>> Running Example 4: Strategy Comparison...")
        comparison = compare_ml_vs_simple_strategy()
        
        print("\n>>> Running Example 5: State Vector Demo...")
        demonstrate_state_vector()
        
        print("\n\n" + "="*100)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*100)
        print("\nResults have been exported to the 'race_results' directory.")
        print("Check the JSON and CSV files for detailed race data.")
        print("\n" + "="*100)
        
    except Exception as e:
        print(f"\n\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
