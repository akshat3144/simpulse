"""
Example: Using real-time matplotlib visualization with race simulation
Shows live graphs updating during the race
"""

import sys
import os
import time
import matplotlib
matplotlib.use('TkAgg')  # Use interactive backend
import matplotlib.pyplot as plt

# Add parent directory to path if running script directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from the package
from formula_e_simulator.engine import FormulaERaceEngine
from formula_e_simulator.visualization import RaceVisualizer, create_post_race_analysis


def example_1_live_visualization():
    """
    Example 1: Real-time visualization with live updating charts
    Shows position, energy, speed, lap times, and tires
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Real-Time Visualization")
    print("="*80)
    print("\nThis will open a window with 6 live charts:")
    print("  1. Race Positions (bar chart)")
    print("  2. Battery Energy (line graph)")
    print("  3. Speed Profile (line graph)")
    print("  4. Best Lap Times (bar chart)")
    print("  5. Tire Degradation (bar chart)")
    print("  6. Race Information (text panel)")
    print("\nControls:")
    print("  [SPACE] - Pause/Resume")
    print("  [Q] - Quit")
    print("\nStarting race in 3 seconds...")
    time.sleep(3)
    
    # Create race engine
    engine = FormulaERaceEngine(
        num_cars=12,  # Fewer cars for clarity
        num_laps=5,
        use_ml_strategy=True,
        random_seed=42
    )
    
    # Create visualizer
    viz = RaceVisualizer(num_cars=12, history_length=500)
    viz.setup_figure()
    
    print("\n🏁 Race started! Watch the visualization window...")
    print("   (Window may take a moment to appear)\n")
    
    # Enable interactive mode
    plt.ion()
    viz.show(block=False)
    
    # Run simulation with visualization
    step_count = 0
    update_interval = 10  # Update visualization every 10 steps (1 second)
    
    while not engine.race_finished and step_count < 5000:
        # Simulate one timestep
        engine.simulate_timestep()
        
        # Update visualization periodically
        if step_count % update_interval == 0:
            viz.update(engine.race_state)
            plt.pause(0.01)  # Small pause to allow rendering
        
        # Print progress
        if step_count % 100 == 0:
            leader = engine.race_state.cars[0]
            for car in engine.race_state.cars:
                if car.position == 1 and car.is_active:
                    leader = car
                    break
            print(f"Step {step_count:4d} | Time: {engine.race_state.current_time:6.1f}s | "
                  f"Leader: {leader.driver_name:15s} | Lap: {leader.current_lap:2d}")
        
        step_count += 1
    
    print("\n🏁 Race finished!")
    print("\nVisualization window will remain open.")
    print("Close the window to continue...\n")
    
    # Final update
    viz.update(engine.race_state)
    
    # Keep window open
    plt.ioff()
    plt.show()
    
    return engine, viz


def example_2_post_race_analysis():
    """
    Example 2: Post-race analysis with comprehensive statistics
    Creates detailed analysis charts after race completion
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Post-Race Analysis")
    print("="*80)
    print("\nRunning a complete race, then showing detailed analysis...")
    
    # Run race without visualization
    engine = FormulaERaceEngine(
        num_cars=24,
        num_laps=10,
        use_ml_strategy=True,
        random_seed=42
    )
    
    print("\n🏁 Running simulation...")
    summary = engine.run_simulation(display_interval=200, verbose=True)
    
    print("\n📊 Generating post-race analysis charts...")
    
    # Create analysis figure
    fig = create_post_race_analysis(engine.race_state, engine.event_log)
    
    # Save to file
    fig.savefig('race_results/post_race_analysis.png', dpi=150, bbox_inches='tight')
    print("\n✅ Analysis saved to: race_results/post_race_analysis.png")
    
    # Show interactive
    plt.show()
    
    return engine


def example_3_snapshot_recording():
    """
    Example 3: Record race snapshots at intervals
    Saves visualization images during the race
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Snapshot Recording")
    print("="*80)
    print("\nRecording race snapshots every 50 steps...")
    
    import os
    os.makedirs('race_results/snapshots', exist_ok=True)
    
    # Create race engine
    engine = FormulaERaceEngine(
        num_cars=12,
        num_laps=5,
        use_ml_strategy=True,
        random_seed=99
    )
    
    # Create visualizer
    viz = RaceVisualizer(num_cars=12)
    viz.setup_figure()
    plt.ion()
    
    step_count = 0
    snapshot_interval = 50
    snapshot_count = 0
    
    while not engine.race_finished and step_count < 5000:
        engine.simulate_timestep()
        
        # Update and save snapshot
        if step_count % snapshot_interval == 0:
            viz.update(engine.race_state)
            snapshot_path = f'race_results/snapshots/race_snapshot_{snapshot_count:04d}.png'
            viz.save_snapshot(snapshot_path)
            snapshot_count += 1
            print(f"Saved snapshot {snapshot_count} at t={engine.race_state.current_time:.1f}s")
        
        step_count += 1
    
    print(f"\n✅ Saved {snapshot_count} snapshots to race_results/snapshots/")
    print("   You can create a video from these using ffmpeg:")
    print("   ffmpeg -framerate 10 -i race_snapshot_%04d.png -c:v libx264 race_video.mp4")
    
    plt.ioff()
    plt.close()
    
    return engine


def example_4_compare_strategies():
    """
    Example 4: Compare ML vs Simple AI strategies visually
    Runs two races and creates comparison charts
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Strategy Comparison")
    print("="*80)
    print("\nComparing ML strategy vs Simple AI...")
    
    # Run race with ML
    print("\n--- Running Race 1: ML Strategy ---")
    engine_ml = FormulaERaceEngine(
        num_cars=12, num_laps=5, use_ml_strategy=True, random_seed=42
    )
    engine_ml.run_simulation(display_interval=500, verbose=False)
    
    # Run race with Simple AI
    print("\n--- Running Race 2: Simple AI ---")
    engine_simple = FormulaERaceEngine(
        num_cars=12, num_laps=5, use_ml_strategy=False, random_seed=42
    )
    engine_simple.run_simulation(display_interval=500, verbose=False)
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Strategy Comparison: ML vs Simple AI', fontsize=16, fontweight='bold')
    
    # 1. Energy efficiency comparison
    ax = axes[0, 0]
    ml_efficiency = [c.get_energy_efficiency() for c in engine_ml.race_state.cars[:5]]
    simple_efficiency = [c.get_energy_efficiency() for c in engine_simple.race_state.cars[:5]]
    
    x = range(5)
    width = 0.35
    ax.bar([i - width/2 for i in x], ml_efficiency, width, label='ML Strategy', alpha=0.8)
    ax.bar([i + width/2 for i in x], simple_efficiency, width, label='Simple AI', alpha=0.8)
    ax.set_xlabel('Driver')
    ax.set_ylabel('km/kWh')
    ax.set_title('Energy Efficiency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Lap time comparison
    ax = axes[0, 1]
    ml_laps = [c.best_lap_time for c in engine_ml.race_state.cars[:5] if c.best_lap_time != float('inf')]
    simple_laps = [c.best_lap_time for c in engine_simple.race_state.cars[:5] if c.best_lap_time != float('inf')]
    
    if ml_laps and simple_laps:
        ax.bar([i - width/2 for i in range(len(ml_laps))], ml_laps, width, label='ML Strategy', alpha=0.8)
        ax.bar([i + width/2 for i in range(len(simple_laps))], simple_laps, width, label='Simple AI', alpha=0.8)
        ax.set_xlabel('Driver')
        ax.set_ylabel('Lap Time (s)')
        ax.set_title('Best Lap Times')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # 3. Overtakes
    ax = axes[1, 0]
    ml_overtakes = sum(c.overtakes_made for c in engine_ml.race_state.cars)
    simple_overtakes = sum(c.overtakes_made for c in engine_simple.race_state.cars)
    
    ax.bar(['ML Strategy', 'Simple AI'], [ml_overtakes, simple_overtakes], 
           color=['blue', 'orange'], alpha=0.7)
    ax.set_ylabel('Total Overtakes')
    ax.set_title('Overtaking Activity')
    ax.grid(True, alpha=0.3)
    
    # 4. Final positions
    ax = axes[1, 1]
    ml_finishers = len([c for c in engine_ml.race_state.cars if c.is_active])
    simple_finishers = len([c for c in engine_simple.race_state.cars if c.is_active])
    
    ax.bar(['ML Strategy', 'Simple AI'], [ml_finishers, simple_finishers],
           color=['green', 'red'], alpha=0.7)
    ax.set_ylabel('Cars Finished')
    ax.set_title('Race Completion')
    ax.set_ylim([0, 12])
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('race_results/strategy_comparison.png', dpi=150, bbox_inches='tight')
    print("\n✅ Comparison saved to: race_results/strategy_comparison.png")
    plt.show()
    
    return engine_ml, engine_simple


def example_5_live_animation():
    """
    Example 5: Live animation showing cars racing on track
    Top-down view with cars moving in real-time
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Live Race Animation")
    print("="*80)
    print("\nThis will open a window showing:")
    print("  - Top-down track view (START to FINISH)")
    print("  - Cars moving in real-time as colored dots")
    print("  - Live race information (time, laps, leader)")
    print("\nControls:")
    print("  - SPACE: Pause/Resume")
    print("  - Q: Quit")
    print("\nStarting race animation...")
    
    # Import the animator
    from formula_e_simulator.visualization import LiveRaceAnimator
    
    # Create race engine
    engine = FormulaERaceEngine(
        num_cars=12,
        num_laps=5
    )
    
    # Get track length from config
    track_length = engine.track_config.total_length
    
    # Create animator
    animator = LiveRaceAnimator(
        track_length=track_length,
        num_cars=12
    )
    
    # Setup figure
    animator.setup_figure()
    
    print("\n✅ Animation window opened!")
    print("   Watch the cars race across the track!")
    print("   Press SPACE to pause, Q to quit")
    
    # Run animation (this blocks until window closed)
    animator.animate_race(engine, interval=50)
    
    print("\n✅ Animation finished!")
    print(f"   Race completed in {engine.race_state.current_time:.1f}s")


def main():
    """Run visualization examples"""
    print("\n🎨 FORMULA E SIMULATOR - VISUALIZATION EXAMPLES")
    print("=" * 80)
    print("\nAvailable examples:")
    print("  1. Live real-time visualization (6 charts updating during race)")
    print("  2. Post-race analysis (comprehensive statistics)")
    print("  3. Snapshot recording (save images during race)")
    print("  4. Strategy comparison (ML vs Simple AI)")
    print("  5. Live animation (cars racing on track) ⭐ NEW!")
    print("  6. Run all examples")
    print()
    
    choice = input("Select example (1-6) or press Enter for #1: ").strip()
    
    if not choice:
        choice = "1"
    
    try:
        if choice == "1":
            example_1_live_visualization()
        elif choice == "2":
            example_2_post_race_analysis()
        elif choice == "3":
            example_3_snapshot_recording()
        elif choice == "4":
            example_4_compare_strategies()
        elif choice == "5":
            example_5_live_animation()
        elif choice == "6":
            example_1_live_visualization()
            time.sleep(2)
            example_2_post_race_analysis()
            time.sleep(2)
            example_3_snapshot_recording()
            time.sleep(2)
            example_4_compare_strategies()
            time.sleep(2)
            example_5_live_animation()
        else:
            print("Invalid choice. Running example 1...")
            example_1_live_visualization()
        
        print("\n✅ All done! Check the race_results/ folder for saved images.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

