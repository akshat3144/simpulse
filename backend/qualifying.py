"""
Formula E Qualifying System
Implements realistic qualifying session with flying laps
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from .state import CarState
from .config import DriverConfig, TrackConfig, PhysicsConfig, simulation_config
from .physics import PhysicsEngine


class QualifyingSession:
    """
    Simulates Formula E qualifying session
    Each driver gets qualifying laps to set their best time
    """
    
    def __init__(
        self,
        track_config: TrackConfig,
        driver_configs: List[Dict],
        random_seed: Optional[int] = None
    ):
        """
        Initialize qualifying session
        
        Args:
            track_config: Track configuration
            driver_configs: List of driver configuration dicts
            random_seed: Random seed for reproducibility
        """
        self.track_config = track_config
        self.driver_configs = driver_configs
        self.rng = np.random.RandomState(random_seed)
        self.physics_engine = PhysicsEngine(track_config)
        
        self.results: List[Dict] = []
    
    def run_qualifying(
        self,
        num_flying_laps: int = 2,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Run qualifying session for all drivers
        
        Args:
            num_flying_laps: Number of flying laps per driver
            verbose: Print progress
            
        Returns:
            List of qualifying results sorted by lap time
        """
        if verbose:
            print("\n" + "="*80)
            print("FORMULA E QUALIFYING SESSION")
            print("="*80)
            print(f"Track: {self.track_config.track_name}")
            print(f"Distance: {self.track_config.total_length:.2f}m")
            print(f"Flying laps per driver: {num_flying_laps}")
            print()
        
        results = []
        
        for driver_idx, driver_config in enumerate(self.driver_configs):
            # Simulate qualifying laps
            best_time = self._simulate_qualifying_laps(
                driver_config,
                driver_idx,
                num_flying_laps
            )
            
            result = {
                'driver_id': driver_idx,
                'driver_name': driver_config['name'],
                'team': driver_config['team'],
                'best_lap_time': best_time,
                'skill': driver_config['skill'],
                'qualifying_position': 0  # Will be set after sorting
            }
            results.append(result)
            
            if verbose:
                print(f"  {driver_config['name']:30s} - {best_time:.3f}s")
        
        # Sort by lap time
        results.sort(key=lambda x: x['best_lap_time'])
        
        # Assign positions
        for pos, result in enumerate(results):
            result['qualifying_position'] = pos + 1
        
        if verbose:
            print("\n" + "="*80)
            print("QUALIFYING RESULTS")
            print("="*80)
            for result in results:
                print(f"  P{result['qualifying_position']:2d}. {result['driver_name']:30s} - {result['best_lap_time']:.3f}s")
            print()
        
        self.results = results
        return results
    
    def _simulate_qualifying_laps(
        self,
        driver_config: Dict,
        driver_idx: int,
        num_laps: int
    ) -> float:
        """
        Simulate qualifying laps for a single driver
        
        Args:
            driver_config: Driver configuration dict
            driver_idx: Driver index
            num_laps: Number of laps to simulate
            
        Returns:
            Best lap time achieved
        """
        # Base lap time estimation
        # Average speed depends on driver skill and track characteristics
        avg_speed_ms = PhysicsConfig.MAX_SPEED_MS * 0.70  # ~70% of max speed on average
        
        # Driver skill factor (better drivers go faster)
        skill_factor = driver_config['skill']
        avg_speed_ms *= skill_factor
        
        # Calculate theoretical lap time
        base_lap_time = self.track_config.total_length / avg_speed_ms
        
        best_lap_time = float('inf')
        
        for lap in range(num_laps):
            # Add randomness for each lap attempt
            consistency_factor = self.rng.normal(1.0, 1.0 - driver_config['consistency'])
            consistency_factor = np.clip(consistency_factor, 0.97, 1.03)  # ±3%
            
            # Traffic and track conditions variability
            track_conditions = self.rng.normal(1.0, 0.01)  # ±1% track variation
            
            # Qualifying mode (push harder, less tire/battery management)
            qualifying_boost = 0.98  # 2% faster in qualifying mode
            
            # Calculate lap time
            lap_time = base_lap_time * consistency_factor * track_conditions * qualifying_boost
            
            # Add small random variation (traffic, mistakes, etc.)
            lap_time += self.rng.normal(0, 0.1)  # ±0.1s random noise
            
            best_lap_time = min(best_lap_time, lap_time)
        
        return best_lap_time
    
    def get_starting_grid(self) -> List[int]:
        """
        Get starting grid order (list of driver IDs)
        
        Returns:
            List of driver IDs in grid order
        """
        if not self.results:
            # If qualifying hasn't run, use default order
            return list(range(len(self.driver_configs)))
        
        return [result['driver_id'] for result in self.results]
    
    def export_results_csv(self, filepath: str):
        """
        Export qualifying results to CSV
        
        Args:
            filepath: Output file path
        """
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Position', 'Driver', 'Team', 'Lap Time', 'Skill'
            ])
            
            # Data rows
            for result in self.results:
                writer.writerow([
                    result['qualifying_position'],
                    result['driver_name'],
                    result['team'],
                    f"{result['best_lap_time']:.3f}",
                    f"{result['skill']:.3f}"
                ])
        
        print(f"[OK] Qualifying results exported to {filepath}")
