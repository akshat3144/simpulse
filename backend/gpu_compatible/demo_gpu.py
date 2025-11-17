"""
GPU vs CPU Benchmark with Actual Race Simulation
Demonstrates GPU acceleration for scalability presentation
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("✓ CuPy detected - GPU acceleration available")
    print(f"  GPU: {cp.cuda.Device()}")
    print(f"  Memory: {cp.cuda.Device().mem_info[1] / 1e9:.1f} GB total")
except ImportError:
    GPU_AVAILABLE = False
    print("✗ CuPy not found - GPU acceleration unavailable")
    print("  Install with: pip install cupy-cuda12x")

from engine_gpu import GPURaceEngine, DriverConfig
from config import TrackConfig


def create_test_drivers(n_cars: int):
    """Create test driver configurations"""
    drivers = []
    teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']
    
    for i in range(n_cars):
        drivers.append(DriverConfig(
            car_id=i + 1,
            driver_name=f"Driver {i+1}",
            team=teams[i % len(teams)],
            skill=0.95 + (i % 5) * 0.01,
            aggression=0.4 + (i % 3) * 0.2,
            consistency=0.92 + (i % 4) * 0.02,
            starting_position=i + 1
        ))
    
    return drivers


def benchmark_race(n_cars: int, n_laps: int, use_gpu: bool, save_history: bool = True):
    """
    Run race simulation and benchmark performance
    
    Returns:
        Dict with timing results
    """
    device = "GPU" if use_gpu else "CPU"
    print(f"\n{'='*60}")
    print(f"🏎️  BENCHMARKING: {n_cars} cars, {n_laps} laps on {device}")
    print(f"{'='*60}")
    
    # Create track (use default Monaco-style track)
    track = TrackConfig()
    
    # Create drivers
    drivers = create_test_drivers(n_cars)
    
    # Initialize engine
    setup_start = time.time()
    engine = GPURaceEngine(track, n_cars, use_gpu=use_gpu)
    engine.setup_drivers(drivers)
    setup_time = time.time() - setup_start
    
    # Run qualifying
    qual_start = time.time()
    qual_results = engine.run_qualifying(duration_seconds=60.0, dt=0.001)
    qual_time = time.time() - qual_start
    
    # Run race
    race_start = time.time()
    race_data = engine.run_race(
        n_laps=n_laps, 
        dt=0.001,
        qualifying_results=qual_results,
        save_history=save_history
    )
    race_time = time.time() - race_start
    
    # Export results
    export_start = time.time()
    engine.export_results(race_data, output_dir=f"race_output_{device.lower()}_{n_cars}cars")
    export_time = time.time() - export_start
    
    total_time = setup_time + qual_time + race_time + export_time
    
    results = {
        'device': device,
        'n_cars': n_cars,
        'n_laps': n_laps,
        'setup_time': setup_time,
        'qual_time': qual_time,
        'race_time': race_time,
        'export_time': export_time,
        'total_time': total_time,
        'total_steps': race_data['total_steps'],
        'steps_per_sec': race_data['total_steps'] / race_time,
        'speedup': race_data['speedup'],
    }
    
    # Print results
    print(f"\n📊 RESULTS:")
    print(f"  Setup:       {setup_time:6.2f}s")
    print(f"  Qualifying:  {qual_time:6.2f}s")
    print(f"  Race:        {race_time:6.2f}s ({race_data['total_steps']:,} steps)")
    print(f"  Export:      {export_time:6.2f}s")
    print(f"  ─────────────────────────")
    print(f"  Total:       {total_time:6.2f}s")
    print(f"  Performance: {results['steps_per_sec']:,.1f} steps/sec")
    print(f"  Speedup:     {results['speedup']:.1f}x realtime")
    
    return results


def run_scaling_benchmark():
    """
    Run benchmark with different numbers of cars
    Demonstrates GPU scalability advantage
    """
    print("\n" + "="*60)
    print("🚀 GPU SCALABILITY DEMONSTRATION")
    print("="*60)
    
    # Test configurations
    test_configs = [
        (10, 5),   # 10 cars, 5 laps
        (20, 5),   # 20 cars, 5 laps
        (50, 3),   # 50 cars, 3 laps (if GPU available)
    ]
    
    all_results = []
    
    for n_cars, n_laps in test_configs:
        # Skip large tests if no GPU
        if n_cars > 20 and not GPU_AVAILABLE:
            print(f"\n⚠️  Skipping {n_cars} cars (GPU not available)")
            continue
        
        # Run on CPU
        cpu_result = benchmark_race(n_cars, n_laps, use_gpu=False, save_history=False)
        all_results.append(cpu_result)
        
        # Run on GPU (if available)
        if GPU_AVAILABLE:
            gpu_result = benchmark_race(n_cars, n_laps, use_gpu=True, save_history=False)
            all_results.append(gpu_result)
            
            # Calculate speedup
            speedup = cpu_result['race_time'] / gpu_result['race_time']
            print(f"\n⚡ GPU SPEEDUP: {speedup:.2f}x faster than CPU")
    
    # Summary table
    print("\n" + "="*60)
    print("📈 PERFORMANCE SUMMARY")
    print("="*60)
    print(f"{'Cars':<6} {'Laps':<6} {'Device':<8} {'Race Time':<12} {'Steps/sec':<15} {'Speedup':<10}")
    print("-" * 60)
    
    for result in all_results:
        print(f"{result['n_cars']:<6} {result['n_laps']:<6} {result['device']:<8} "
              f"{result['race_time']:>8.2f}s    {result['steps_per_sec']:>10,.0f}      "
              f"{result['speedup']:>6.1f}x")
    
    # Calculate GPU vs CPU speedups
    if GPU_AVAILABLE and len(all_results) >= 2:
        print("\n" + "="*60)
        print("🎯 GPU vs CPU COMPARISON")
        print("="*60)
        
        for i in range(0, len(all_results), 2):
            if i+1 < len(all_results):
                cpu_res = all_results[i]
                gpu_res = all_results[i+1]
                
                if cpu_res['device'] == 'CPU' and gpu_res['device'] == 'GPU':
                    speedup = cpu_res['race_time'] / gpu_res['race_time']
                    print(f"{cpu_res['n_cars']} cars, {cpu_res['n_laps']} laps: "
                          f"GPU is {speedup:.2f}x faster "
                          f"({cpu_res['race_time']:.2f}s → {gpu_res['race_time']:.2f}s)")


def run_single_demo():
    """Run a single demonstration race with detailed output"""
    print("\n" + "="*60)
    print("🏁 SINGLE RACE DEMONSTRATION")
    print("="*60)
    
    n_cars = 10
    n_laps = 5
    
    # Run on best available device
    use_gpu = GPU_AVAILABLE
    device = "GPU" if use_gpu else "CPU"
    
    print(f"\nRunning {n_cars} cars, {n_laps} laps on {device}...")
    
    result = benchmark_race(n_cars, n_laps, use_gpu=use_gpu, save_history=True)
    
    print(f"\n✓ Complete! Results saved to race_output_{device.lower()}_{n_cars}cars/")
    print(f"\nKey Metrics:")
    print(f"  • Simulation ran {result['speedup']:.1f}x faster than realtime")
    print(f"  • Processed {result['steps_per_sec']:,.0f} timesteps per second")
    print(f"  • Total simulation time: {result['total_time']:.2f} seconds")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--scale":
        # Run scaling benchmark
        run_scaling_benchmark()
    else:
        # Run single demo
        run_single_demo()
        
        if GPU_AVAILABLE:
            print("\n💡 TIP: Run with --scale to see GPU scalability across different workloads")
        else:
            print("\n💡 Install CuPy to enable GPU acceleration:")
            print("     pip install cupy-cuda12x  # For CUDA 12.x")
            print("     pip install cupy-cuda11x  # For CUDA 11.x")
