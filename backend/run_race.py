"""
Quick start script for Formula E Simulator
Simple entry point for running races
"""

from formula_e_simulator import FormulaERaceEngine

def main():
    """Run a quick 10-lap race"""
    
    print("\n🏎️  FORMULA E RACE SIMULATOR - Quick Start")
    print("="*80)
    
    # Create and run race
    engine = FormulaERaceEngine(
        num_cars=24,
        num_laps=10,
        use_ml_strategy=True,
        random_seed=42
    )
    
    print("\n🏁 Starting race simulation...\n")
    
    summary = engine.run_simulation(
        display_interval=100,
        verbose=True
    )
    
    # Export results
    print("\n📊 Exporting results...")
    engine.export_to_json("race_results.json")
    engine.export_to_csv("leaderboard.csv")
    
    print("\n✅ Race completed!")
    print(f"   - Winner: {summary['final_standings']['entries'][0]['driver_name']}")
    print(f"   - Total overtakes: {summary['events']['overtakes']}")
    print(f"   - Results saved to: race_results.json and leaderboard.csv")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
