"""
GPU-Accelerated Race Engine
Runs complete race simulation with all cars processed in parallel on GPU
"""

import numpy as np
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    cp = None

sys.path.insert(0, str(Path(__file__).parent))
from physics_gpu import GPUPhysicsEngine
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PhysicsConfig, TrackConfig, WeatherConditions


@dataclass
class DriverConfig:
    """Configuration for each driver"""
    car_id: int
    driver_name: str
    team: str
    skill: float = 1.0  # 0.95-1.0
    aggression: float = 0.5  # 0-1
    consistency: float = 0.95  # 0.9-1.0
    starting_position: int = 1


class GPURaceEngine:
    """
    GPU-accelerated race engine
    Processes all cars in parallel using matrix operations
    """
    
    def __init__(self, track_config: TrackConfig, n_cars: int, use_gpu: bool = True):
        self.track_config = track_config
        self.n_cars = n_cars
        self.use_gpu = use_gpu and GPU_AVAILABLE
        
        # Initialize GPU physics engine
        self.physics = GPUPhysicsEngine(track_config, use_gpu=use_gpu)
        
        # Initialize state matrix
        self.state = self.physics.initialize_state_matrix(n_cars)
        
        # Driver configurations (list of dicts for easy access)
        self.driver_configs = []
        
        # Timestep history (stored on CPU for export)
        self.history = []
        
        # Weather
        self.weather = WeatherConditions()
        
        print(f"{'GPU' if self.use_gpu else 'CPU'} Race Engine initialized with {n_cars} cars")
    
    def setup_drivers(self, drivers: List[DriverConfig]):
        """Setup driver configurations"""
        assert len(drivers) == self.n_cars, f"Expected {self.n_cars} drivers, got {len(drivers)}"
        
        self.driver_configs = []
        for i, driver in enumerate(drivers):
            self.driver_configs.append({
                'car_id': driver.car_id,
                'driver_name': driver.driver_name,
                'team': driver.team,
                'skill': driver.skill,
                'aggression': driver.aggression,
                'consistency': driver.consistency,
                'starting_position': driver.starting_position,
            })
        
        # Set starting positions (staggered start)
        xp = self.physics.xp
        for i, driver in enumerate(drivers):
            grid_pos = driver.starting_position - 1
            self.state['position_x'][i] = -grid_pos * 10.0  # 10m spacing
            self.state['lap_distance'][i] = max(0, -grid_pos * 10.0)  # Negative means behind start line
    
    def run_qualifying(self, duration_seconds: float = 60.0, dt: float = 0.001):
        """
        Run qualifying session
        Returns: List of (car_id, best_lap_time) sorted by lap time
        """
        print(f"\n🏁 Starting Qualifying ({duration_seconds}s) on {'GPU' if self.use_gpu else 'CPU'}...")
        start_time = time.time()
        
        xp = self.physics.xp
        
        # Reset state
        self.state = self.physics.initialize_state_matrix(self.n_cars)
        
        # Track best lap times
        best_lap_times = xp.full(self.n_cars, xp.inf, dtype=xp.float32)
        lap_start_times = xp.zeros(self.n_cars, dtype=xp.float32)
        previous_laps = xp.zeros(self.n_cars, dtype=xp.int32)
        
        # Convert driver configs for GPU access
        driver_configs_dict = {i: self.driver_configs[i] for i in range(self.n_cars)}
        
        elapsed = 0.0
        steps = 0
        
        while elapsed < duration_seconds:
            # Get segment data for all cars
            segment_data = self.physics.get_segment_data_batch(self.state)
            
            # Calculate controls for all cars
            throttle, brake, steering = self.physics.calculate_controls_batch(
                self.state, driver_configs_dict, segment_data
            )
            
            # Update state
            self.state['throttle'] = throttle
            self.state['brake'] = brake
            self.state['steering_angle'] = steering
            
            # Physics update (GPU accelerated)
            self.state = self.physics.update_physics_batch(
                self.state, dt, segment_data, self.weather
            )
            
            # Check for lap completions
            lap_completed = self.state['current_lap'] > previous_laps
            
            # Update best times (vectorized)
            current_times = self.state['time']
            lap_times = current_times - lap_start_times
            
            # Update best times for completed laps
            best_lap_times = xp.where(
                lap_completed & (lap_times < best_lap_times),
                lap_times,
                best_lap_times
            )
            
            # Reset lap start times for completed laps
            lap_start_times = xp.where(lap_completed, current_times, lap_start_times)
            previous_laps = self.state['current_lap'].copy()
            
            elapsed += dt
            steps += 1
        
        elapsed_real = time.time() - start_time
        
        # Convert results to CPU for sorting
        if self.use_gpu:
            best_lap_times_cpu = cp.asnumpy(best_lap_times)
        else:
            best_lap_times_cpu = best_lap_times
        
        # Create results list
        results = []
        for i in range(self.n_cars):
            results.append({
                'car_id': self.driver_configs[i]['car_id'],
                'driver_name': self.driver_configs[i]['driver_name'],
                'team': self.driver_configs[i]['team'],
                'best_lap_time': float(best_lap_times_cpu[i]),
                'position': 0  # Will be set after sorting
            })
        
        # Sort by lap time
        results.sort(key=lambda x: x['best_lap_time'])
        for i, result in enumerate(results):
            result['position'] = i + 1
        
        print(f"✓ Qualifying complete: {steps} steps in {elapsed_real:.2f}s "
              f"({steps/elapsed_real:.1f} steps/sec, {elapsed/elapsed_real:.1f}x realtime)")
        
        return results
    
    def run_race(self, n_laps: int, dt: float = 0.001, 
                 qualifying_results: Optional[List[Dict]] = None,
                 save_history: bool = True):
        """
        Run complete race simulation on GPU
        
        Args:
            n_laps: Number of laps to complete
            dt: Timestep in seconds (default 0.001 = 1ms)
            qualifying_results: Optional qualifying results for grid order
            save_history: Whether to save timestep history (slower)
        
        Returns:
            Dict with race results
        """
        print(f"\n🏁 Starting Race ({n_laps} laps) on {'GPU' if self.use_gpu else 'CPU'}...")
        start_time = time.time()
        
        xp = self.physics.xp
        
        # Reset state
        self.state = self.physics.initialize_state_matrix(self.n_cars)
        self.history = []
        
        # Set grid positions from qualifying
        if qualifying_results:
            for result in qualifying_results:
                car_idx = result['car_id'] - 1
                grid_pos = result['position'] - 1
                self.state['position_x'][car_idx] = -grid_pos * 10.0
                self.state['lap_distance'][car_idx] = max(0, -grid_pos * 10.0)
        
        # Convert driver configs
        driver_configs_dict = {i: self.driver_configs[i] for i in range(self.n_cars)}
        
        # Race loop
        steps = 0
        race_complete = False
        
        while not race_complete:
            # Get segment data
            segment_data = self.physics.get_segment_data_batch(self.state)
            
            # Calculate controls
            throttle, brake, steering = self.physics.calculate_controls_batch(
                self.state, driver_configs_dict, segment_data
            )
            
            # Update state
            self.state['throttle'] = throttle
            self.state['brake'] = brake
            self.state['steering_angle'] = steering
            
            # Physics update (GPU)
            self.state = self.physics.update_physics_batch(
                self.state, dt, segment_data, self.weather
            )
            
            # Save history (copy to CPU)
            if save_history and steps % 100 == 0:  # Save every 100 steps to reduce memory
                snapshot = self.physics.state_to_cpu(self.state)
                self.history.append({
                    'step': steps,
                    'time': float(snapshot['time'][0]),  # Use first car's time
                    'snapshot': snapshot
                })
            
            # Check race completion
            if self.use_gpu:
                max_lap = int(cp.asnumpy(xp.max(self.state['current_lap'])))
            else:
                max_lap = int(xp.max(self.state['current_lap']))
            
            race_complete = max_lap >= n_laps
            
            steps += 1
            
            # Progress update every 10k steps
            if steps % 10000 == 0:
                elapsed_real = time.time() - start_time
                print(f"  Step {steps}: Max lap {max_lap}/{n_laps}, "
                      f"{steps/elapsed_real:.1f} steps/sec, {steps*dt/elapsed_real:.1f}x realtime")
        
        elapsed_real = time.time() - start_time
        elapsed_sim = steps * dt
        
        print(f"✓ Race complete: {steps} steps in {elapsed_real:.2f}s "
              f"({steps/elapsed_real:.1f} steps/sec, {elapsed_sim/elapsed_real:.1f}x realtime)")
        
        # Generate results
        state_cpu = self.physics.state_to_cpu(self.state)
        
        results = []
        for i in range(self.n_cars):
            results.append({
                'car_id': self.driver_configs[i]['car_id'],
                'driver_name': self.driver_configs[i]['driver_name'],
                'team': self.driver_configs[i]['team'],
                'position': 0,  # Will be set after sorting
                'laps_completed': int(state_cpu['current_lap'][i]),
                'total_distance': float(state_cpu['total_distance'][i]),
                'total_time': float(state_cpu['time'][i]),
                'battery_remaining': float(state_cpu['battery_percentage'][i]),
                'tire_degradation': float(state_cpu['tire_degradation'][i]),
            })
        
        # Sort by laps then distance
        results.sort(key=lambda x: (-x['laps_completed'], -x['total_distance']))
        for i, result in enumerate(results):
            result['position'] = i + 1
        
        return {
            'results': results,
            'total_steps': steps,
            'simulation_time': elapsed_sim,
            'real_time': elapsed_real,
            'speedup': elapsed_sim / elapsed_real,
            'history': self.history if save_history else None
        }
    
    def export_results(self, race_data: dict, output_dir: str = "race_output"):
        """Export race results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export leaderboard
        with open(output_path / "final_leaderboard.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['position', 'car_id', 'driver_name', 
                                                   'team', 'laps_completed', 'total_time',
                                                   'total_distance', 'battery_remaining', 
                                                   'tire_degradation'])
            writer.writeheader()
            writer.writerows(race_data['results'])
        
        # Export timesteps (if history saved)
        if race_data['history']:
            print(f"Exporting {len(race_data['history'])} timestep snapshots...")
            
            with open(output_path / "race_timesteps.csv", "w", newline='') as f:
                fieldnames = ['step', 'time', 'car_id', 'driver_name', 'lap', 'lap_distance',
                            'velocity', 'battery_pct', 'tire_deg', 'attack_mode']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in race_data['history']:
                    snapshot = record['snapshot']
                    for i in range(self.n_cars):
                        speed = float(snapshot['velocity_x'][i])
                        writer.writerow({
                            'step': record['step'],
                            'time': record['time'],
                            'car_id': self.driver_configs[i]['car_id'],
                            'driver_name': self.driver_configs[i]['driver_name'],
                            'lap': int(snapshot['current_lap'][i]),
                            'lap_distance': float(snapshot['lap_distance'][i]),
                            'velocity': speed,
                            'battery_pct': float(snapshot['battery_percentage'][i]),
                            'tire_deg': float(snapshot['tire_degradation'][i]),
                            'attack_mode': bool(snapshot['attack_mode_active'][i]),
                        })
        
        # Export summary JSON
        summary = {
            'race_statistics': {
                'total_steps': race_data['total_steps'],
                'simulation_time': race_data['simulation_time'],
                'real_time': race_data['real_time'],
                'speedup': race_data['speedup'],
                'device': 'GPU' if self.use_gpu else 'CPU',
            },
            'final_standings': race_data['results']
        }
        
        with open(output_path / "race_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Results exported to {output_path}/")
