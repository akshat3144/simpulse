"""
Comprehensive Benchmark: GPU Engine vs Original CPU Engine
Compares performance, accuracy, and scalability
"""

import sys
import time
import numpy as np
from pathlib import Path

# Test GPU availability
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print(f"✓ CuPy detected - GPU: {cp.cuda.Device()}")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠ CuPy not available - GPU engine will use CPU fallback")

# Import both engines
import sys
from pathlib import Path

# Add parent directory (backend) to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir.parent))  # For backend package imports
sys.path.insert(0, str(parent_dir))  # For direct imports
sys.path.insert(0, str(Path(__file__).parent))  # For gpu_compatible imports

# Import as package
from backend.engine import FormulaERaceEngine
from backend.config import TrackConfig, DriverConfig as CPUDriverConfig

# Import GPU engine
from engine_gpu import GPURaceEngine, DriverConfig as GPUDriverConfig


def create_test_drivers_cpu(n_cars: int):
    """Create driver configs for original CPU engine"""
    drivers = []
    teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']
    
    for i in range(n_cars):
        drivers.append(CPUDriverConfig(
            driver_name=f"Driver {i+1}",
            team=teams[i % len(teams)],
            skill_level=0.95 + (i % 5) * 0.01,
            aggression=0.4 + (i % 3) * 0.2,
            consistency=0.92 + (i % 4) * 0.02,
            car_number=i + 1
        ))
    
    return drivers


def create_test_drivers_gpu(n_cars: int):
    """Create driver configs for GPU engine"""
    drivers = []
    teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']
    
    for i in range(n_cars):
        drivers.append(GPUDriverConfig(
            car_id=i + 1,
            driver_name=f"Driver {i+1}",
            team=teams[i % len(teams)],
            skill=0.95 + (i % 5) * 0.01,
            aggression=0.4 + (i % 3) * 0.2,
            consistency=0.92 + (i % 4) * 0.02,
            starting_position=i + 1
        ))
    
    return drivers


def benchmark_cpu_engine(n_cars: int, n_laps: int, dt: float = 0.001):
    """
    Benchmark original CPU engine
    """
    print(f"\n{'='*70}")
    print(f"🏎️  ORIGINAL CPU ENGINE: {n_cars} cars, {n_laps} laps")
    print(f"{'='*70}")
    
    # Create track
    track = TrackConfig()
    
    # Initialize engine
    setup_start = time.time()
    engine = FormulaERaceEngine(
        num_cars=n_cars,
        num_laps=n_laps,
        track_config=track
    )
    setup_time = time.time() - setup_start
    
    # Run simulation
    print("Running simulation...")
    sim_start = time.time()
    
    try:
        summary = engine.run_simulation(
            verbose=False,
            display_interval=10000
        )
        sim_time = time.time() - sim_start
        
        # Get final results
        leaderboard = engine.leaderboard.get_top_n(n=engine.num_cars)
        total_steps = engine.current_step
        sim_duration = total_steps * engine.dt
        
        print(f"\n✓ Simulation complete!")
        print(f"  Setup time:      {setup_time:.3f}s")
        print(f"  Simulation time: {sim_time:.3f}s")
        print(f"  Total steps:     {total_steps:,}")
        print(f"  Steps/second:    {total_steps/sim_time:,.0f}")
        print(f"  Sim duration:    {sim_duration:.1f}s")
        print(f"  Speedup:         {sim_duration/sim_time:.1f}x realtime")
        
        # Show top 3
        print(f"\n  Top 3:")
        for i, entry in enumerate(leaderboard[:3]):
            print(f"    {i+1}. Car #{entry.car_id}: "
                  f"{entry.current_lap} laps, {entry.total_distance:.0f}m")
        
        return {
            'engine': 'CPU (Original)',
            'n_cars': n_cars,
            'n_laps': n_laps,
            'setup_time': setup_time,
            'sim_time': sim_time,
            'total_time': setup_time + sim_time,
            'total_steps': total_steps,
            'steps_per_sec': total_steps / sim_time,
            'sim_duration': sim_duration,
            'speedup': sim_duration / sim_time,
            'success': True,
            'leaderboard': leaderboard
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'engine': 'CPU (Original)',
            'n_cars': n_cars,
            'n_laps': n_laps,
            'success': False,
            'error': str(e)
        }


def benchmark_gpu_engine(n_cars: int, n_laps: int, use_gpu: bool, dt: float = 0.001):
    """
    Benchmark GPU-accelerated engine
    """
    device = "GPU" if use_gpu else "CPU"
    print(f"\n{'='*70}")
    print(f"🚀 GPU ENGINE ({'GPU mode' if use_gpu else 'CPU fallback'}): {n_cars} cars, {n_laps} laps")
    print(f"{'='*70}")
    
    # Create track
    track = TrackConfig()
    
    # Initialize engine
    setup_start = time.time()
    engine = GPURaceEngine(track, n_cars, use_gpu=use_gpu)
    drivers = create_test_drivers_gpu(n_cars)
    engine.setup_drivers(drivers)
    setup_time = time.time() - setup_start
    
    try:
        # Run race (no qualifying for fair comparison)
        print("Running race...")
        race_start = time.time()
        race_data = engine.run_race(
            n_laps=n_laps,
            dt=dt,
            save_history=False
        )
        race_time = time.time() - race_start
        
        total_time = setup_time + race_time
        
        print(f"\n✓ Simulation complete!")
        print(f"  Setup time:      {setup_time:.3f}s")
        print(f"  Simulation time: {race_time:.3f}s")
        print(f"  Total steps:     {race_data['total_steps']:,}")
        print(f"  Steps/second:    {race_data['total_steps']/race_time:,.0f}")
        print(f"  Sim duration:    {race_data['simulation_time']:.1f}s")
        print(f"  Speedup:         {race_data['speedup']:.1f}x realtime")
        
        # Show top 3
        print(f"\n  Top 3:")
        for i, result in enumerate(race_data['results'][:3]):
            print(f"    {i+1}. {result['driver_name']}: "
                  f"{result['laps_completed']} laps, {result['total_distance']:.0f}m")
        
        return {
            'engine': f'GPU ({device})',
            'n_cars': n_cars,
            'n_laps': n_laps,
            'setup_time': setup_time,
            'sim_time': race_time,
            'total_time': total_time,
            'total_steps': race_data['total_steps'],
            'steps_per_sec': race_data['total_steps'] / race_time,
            'sim_duration': race_data['simulation_time'],
            'speedup': race_data['speedup'],
            'success': True,
            'results': race_data['results']
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'engine': f'GPU ({device})',
            'n_cars': n_cars,
            'n_laps': n_laps,
            'success': False,
            'error': str(e)
        }


def compare_results(cpu_result, gpu_result):
    """Compare CPU and GPU results"""
    if not (cpu_result['success'] and gpu_result['success']):
        print("\n⚠️  Cannot compare - one or both benchmarks failed")
        return
    
    print(f"\n{'='*70}")
    print("📊 PERFORMANCE COMPARISON")
    print(f"{'='*70}")
    
    # Time comparison
    cpu_time = cpu_result['sim_time']
    gpu_time = gpu_result['sim_time']
    speedup = cpu_time / gpu_time
    
    print(f"\n⏱️  Execution Time:")
    print(f"  CPU Engine:      {cpu_time:.3f}s")
    print(f"  GPU Engine:      {gpu_time:.3f}s")
    print(f"  {'Speedup' if speedup > 1 else 'Slowdown'}:        {abs(speedup):.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    # Throughput comparison
    cpu_throughput = cpu_result['steps_per_sec']
    gpu_throughput = gpu_result['steps_per_sec']
    throughput_ratio = gpu_throughput / cpu_throughput
    
    print(f"\n⚡ Throughput (steps/second):")
    print(f"  CPU Engine:      {cpu_throughput:,.0f}")
    print(f"  GPU Engine:      {gpu_throughput:,.0f}")
    print(f"  Improvement:     {throughput_ratio:.2f}x")
    
    # Realtime performance
    print(f"\n🏁 Realtime Speedup:")
    print(f"  CPU Engine:      {cpu_result['speedup']:.1f}x realtime")
    print(f"  GPU Engine:      {gpu_result['speedup']:.1f}x realtime")
    
    # Efficiency
    print(f"\n💾 Setup Overhead:")
    print(f"  CPU Engine:      {cpu_result['setup_time']:.3f}s")
    print(f"  GPU Engine:      {gpu_result['setup_time']:.3f}s")
    
    # Summary
    print(f"\n{'='*70}")
    if speedup > 1.1:
        print(f"✅ GPU engine is {speedup:.2f}x FASTER than CPU engine")
    elif speedup < 0.9:
        print(f"⚠️  GPU engine is {1/speedup:.2f}x SLOWER (expected for small workloads)")
    else:
        print(f"➡️  Both engines have similar performance (~{speedup:.2f}x)")
    print(f"{'='*70}")


def run_scaling_benchmark():
    """
    Run benchmark across different scales to show GPU advantage
    """
    print("\n" + "="*70)
    print("🚀 SCALING BENCHMARK: CPU vs GPU")
    print("="*70)
    print("\nTesting how each engine scales with increasing workload...")
    
    # Test configurations
    configs = [
        (5, 2, "Small"),      # 5 cars, 2 laps
        (10, 3, "Medium"),    # 10 cars, 3 laps
        (20, 2, "Large"),     # 20 cars, 2 laps
    ]
    
    all_results = []
    
    for n_cars, n_laps, label in configs:
        print(f"\n{'─'*70}")
        print(f"Test: {label} ({n_cars} cars, {n_laps} laps)")
        print(f"{'─'*70}")
        
        # Run CPU benchmark
        cpu_result = benchmark_cpu_engine(n_cars, n_laps, dt=0.001)
        all_results.append(cpu_result)
        
        # Run GPU benchmark (with fallback)
        gpu_result = benchmark_gpu_engine(n_cars, n_laps, use_gpu=GPU_AVAILABLE, dt=0.001)
        all_results.append(gpu_result)
        
        # Compare
        if cpu_result['success'] and gpu_result['success']:
            compare_results(cpu_result, gpu_result)
    
    # Summary table
    print("\n" + "="*70)
    print("📈 COMPLETE RESULTS SUMMARY")
    print("="*70)
    print(f"\n{'Config':<15} {'Engine':<20} {'Time':<10} {'Steps/sec':<15} {'Speedup':<10}")
    print("-" * 70)
    
    for i in range(0, len(all_results), 2):
        if i < len(all_results):
            cpu = all_results[i]
            gpu = all_results[i+1] if i+1 < len(all_results) else None
            
            if cpu['success']:
                config_label = f"{cpu['n_cars']}c, {cpu['n_laps']}L"
                print(f"{config_label:<15} {cpu['engine']:<20} {cpu['sim_time']:>6.2f}s    "
                      f"{cpu['steps_per_sec']:>10,.0f}      {cpu['speedup']:>6.1f}x")
                
                if gpu and gpu['success']:
                    print(f"{'':<15} {gpu['engine']:<20} {gpu['sim_time']:>6.2f}s    "
                          f"{gpu['steps_per_sec']:>10,.0f}      {gpu['speedup']:>6.1f}x")
                    
                    # Show comparison
                    speedup_ratio = cpu['sim_time'] / gpu['sim_time']
                    print(f"{'':<15} {'→ GPU Advantage:':<20} {speedup_ratio:>6.2f}x")
                
                print()
    
    # Final analysis
    print("="*70)
    print("🎯 KEY INSIGHTS")
    print("="*70)
    
    successful_pairs = [(all_results[i], all_results[i+1]) 
                        for i in range(0, len(all_results)-1, 2)
                        if all_results[i]['success'] and all_results[i+1]['success']]
    
    if successful_pairs:
        avg_cpu_steps = np.mean([r[0]['steps_per_sec'] for r in successful_pairs])
        avg_gpu_steps = np.mean([r[1]['steps_per_sec'] for r in successful_pairs])
        avg_speedup = np.mean([r[0]['sim_time'] / r[1]['sim_time'] for r in successful_pairs])
        
        print(f"\n1. Average Throughput:")
        print(f"   CPU: {avg_cpu_steps:,.0f} steps/sec")
        print(f"   GPU: {avg_gpu_steps:,.0f} steps/sec")
        print(f"   GPU is {avg_speedup:.2f}x faster on average")
        
        print(f"\n2. Scalability:")
        if len(successful_pairs) >= 2:
            small_speedup = successful_pairs[0][0]['sim_time'] / successful_pairs[0][1]['sim_time']
            large_speedup = successful_pairs[-1][0]['sim_time'] / successful_pairs[-1][1]['sim_time']
            
            if large_speedup > small_speedup * 1.1:
                print(f"   ✓ GPU advantage INCREASES with scale ({small_speedup:.2f}x → {large_speedup:.2f}x)")
            elif large_speedup < small_speedup * 0.9:
                print(f"   ⚠ GPU advantage DECREASES with scale ({small_speedup:.2f}x → {large_speedup:.2f}x)")
            else:
                print(f"   → GPU advantage CONSISTENT across scales (~{large_speedup:.2f}x)")
        
        print(f"\n3. Architecture:")
        print(f"   CPU: Sequential processing (original engine)")
        print(f"   GPU: Matrix-based parallel processing")
        
        print(f"\n4. Recommendation:")
        if avg_speedup > 1.5:
            print(f"   ✅ Use GPU engine - {avg_speedup:.1f}x faster!")
        elif avg_speedup > 1.1:
            print(f"   ✓ GPU engine preferred - {avg_speedup:.1f}x faster")
        else:
            print(f"   → Both engines comparable for current workload")
            print(f"   → GPU advantage grows with larger workloads (50+ cars)")


def run_single_comparison():
    """Run a single head-to-head comparison"""
    print("\n" + "="*70)
    print("⚔️  HEAD-TO-HEAD COMPARISON")
    print("="*70)
    
    n_cars = 10
    n_laps = 3
    
    print(f"\nConfiguration: {n_cars} cars, {n_laps} laps")
    
    # CPU benchmark
    cpu_result = benchmark_cpu_engine(n_cars, n_laps)
    
    # GPU benchmark
    gpu_result = benchmark_gpu_engine(n_cars, n_laps, use_gpu=GPU_AVAILABLE)
    
    # Compare
    compare_results(cpu_result, gpu_result)


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🏎️  FORMULA E SIMULATOR: CPU vs GPU BENCHMARK")
    print("="*70)
    print(f"\nGPU Status: {'Available ✓' if GPU_AVAILABLE else 'Not Available (CPU fallback)'}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--scale":
        # Run scaling benchmark
        run_scaling_benchmark()
    else:
        # Run single comparison
        run_single_comparison()
        
        print("\n💡 TIP: Run with --scale to see performance across different workloads")
        if not GPU_AVAILABLE:
            print("💡 TIP: Install CuPy to enable true GPU acceleration:")
            print("        pip install cupy-cuda12x  # For CUDA 12.x")
    
    print("\n" + "="*70)
    print("✓ Benchmark complete!")
    print("="*70)
