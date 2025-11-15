"""
Leaderboard and performance metrics calculator
Provides real-time race standings, timing, and statistical analysis
"""

import numpy as np
from typing import List, Dict, Optional
from .state import CarState, RaceState
from .config import TrackConfig


class LeaderboardEntry:
    """Single entry in the leaderboard"""
    
    def __init__(
        self,
        position: int,
        car: CarState,
        interval: float,
        gap_to_leader: float
    ):
        self.position = position
        self.car_id = car.car_id
        self.driver_name = car.driver_name
        self.current_lap = car.current_lap
        self.last_lap_time = car.last_lap_time
        self.best_lap_time = car.best_lap_time
        self.battery_percentage = car.battery_percentage
        self.tire_degradation = car.tire_degradation
        self.attack_mode_active = car.attack_mode_active
        self.attack_mode_uses_left = car.attack_mode_uses_left
        self.interval = interval  # Gap to car ahead
        self.gap_to_leader = gap_to_leader
        self.is_active = car.is_active
        self.speed_kmh = car.get_speed_kmh()
        self.total_distance = car.total_distance
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for export"""
        return {
            'position': self.position,
            'driver_name': self.driver_name,
            'current_lap': self.current_lap,
            'interval': round(self.interval, 3) if self.interval != 0 else '-',
            'gap_to_leader': round(self.gap_to_leader, 3) if self.gap_to_leader != 0 else '-',
            'last_lap_time': f"{self.last_lap_time:.3f}" if self.last_lap_time > 0 else '-',
            'best_lap_time': f"{self.best_lap_time:.3f}" if self.best_lap_time != np.inf else '-',
            'battery_percentage': round(self.battery_percentage, 1),
            'tire_degradation': round(self.tire_degradation * 100, 1),
            'attack_mode_active': self.attack_mode_active,
            'attack_mode_uses': self.attack_mode_uses_left,
            'speed_kmh': round(self.speed_kmh, 1),
            'status': 'Running' if self.is_active else 'Retired'
        }
    
    def to_string(self) -> str:
        """Format as string for console display"""
        interval_str = f"+{self.interval:.3f}" if self.interval > 0 else "Leader"
        gap_str = f"+{self.gap_to_leader:.3f}" if self.gap_to_leader > 0 else "-"
        attack_str = "ATK" if self.attack_mode_active else f"({self.attack_mode_uses_left})"
        status = "✓" if self.is_active else "✗"
        
        return (
            f"{self.position:2d}. {self.driver_name:15s} | "
            f"Lap {self.current_lap:2d} | "
            f"Int: {interval_str:8s} | "
            f"Gap: {gap_str:8s} | "
            f"Bat: {self.battery_percentage:5.1f}% | "
            f"Tire: {self.tire_degradation*100:4.1f}% | "
            f"Attack: {attack_str:4s} | "
            f"{status}"
        )


class Leaderboard:
    """
    Manages race leaderboard and calculates real-time standings
    """
    
    def __init__(self, track_config: TrackConfig):
        self.track_config = track_config
        self.entries: List[LeaderboardEntry] = []
        self.fastest_lap_time = np.inf
        self.fastest_lap_driver = None
    
    def update(self, race_state: RaceState):
        """
        Update leaderboard from current race state
        
        Args:
            race_state: Current race state
        """
        # Sort cars by distance (descending)
        sorted_cars = sorted(
            race_state.cars,
            key=lambda c: (c.current_lap, c.lap_distance) if c.is_active else (-1, -1),
            reverse=True
        )
        
        self.entries.clear()
        
        # Calculate leader info
        if sorted_cars and sorted_cars[0].is_active:
            leader = sorted_cars[0]
            leader_distance = leader.total_distance
            leader_time = leader.time
        else:
            leader_distance = 0
            leader_time = 0
        
        # Create leaderboard entries
        for position, car in enumerate(sorted_cars, start=1):
            # Calculate interval (gap to car ahead)
            if position == 1:
                interval = 0.0
            else:
                prev_car = sorted_cars[position - 2]
                if car.is_active and prev_car.is_active:
                    distance_gap = prev_car.total_distance - car.total_distance
                    interval = distance_gap / car.get_speed() if car.get_speed() > 0 else 0.0
                else:
                    interval = np.inf
            
            # Calculate gap to leader
            if position == 1:
                gap_to_leader = 0.0
            else:
                if car.is_active:
                    distance_gap = leader_distance - car.total_distance
                    gap_to_leader = distance_gap / car.get_speed() if car.get_speed() > 0 else 0.0
                else:
                    gap_to_leader = np.inf
            
            entry = LeaderboardEntry(position, car, interval, gap_to_leader)
            self.entries.append(entry)
            
            # Track fastest lap
            if car.best_lap_time < self.fastest_lap_time:
                self.fastest_lap_time = car.best_lap_time
                self.fastest_lap_driver = car.driver_name
    
    def get_top_n(self, n: int = 10) -> List[LeaderboardEntry]:
        """Get top N positions"""
        return self.entries[:n]
    
    def get_entry_by_driver(self, driver_name: str) -> Optional[LeaderboardEntry]:
        """Get leaderboard entry for specific driver"""
        for entry in self.entries:
            if entry.driver_name == driver_name:
                return entry
        return None
    
    def get_entry_by_position(self, position: int) -> Optional[LeaderboardEntry]:
        """Get leaderboard entry at specific position"""
        if 1 <= position <= len(self.entries):
            return self.entries[position - 1]
        return None
    
    def print_leaderboard(self, num_entries: int = 10):
        """
        Print formatted leaderboard to console
        
        Args:
            num_entries: Number of entries to display
        """
        print("\n" + "="*100)
        print("FORMULA E RACE LEADERBOARD")
        print("="*100)
        print(
            f"{'Pos':<4} {'Driver':<15} | {'Lap':<6} | {'Interval':<10} | "
            f"{'Gap':<10} | {'Battery':<8} | {'Tire':<7} | {'Attack':<6} | {'Status'}"
        )
        print("-"*100)
        
        for entry in self.entries[:num_entries]:
            print(entry.to_string())
        
        print("-"*100)
        if self.fastest_lap_driver:
            print(f"Fastest Lap: {self.fastest_lap_driver} - {self.fastest_lap_time:.3f}s")
        print("="*100 + "\n")
    
    def to_dict(self) -> Dict:
        """Export leaderboard to dictionary"""
        return {
            'entries': [entry.to_dict() for entry in self.entries],
            'fastest_lap_time': float(self.fastest_lap_time) if self.fastest_lap_time != np.inf else None,
            'fastest_lap_driver': self.fastest_lap_driver
        }


class PerformanceMetrics:
    """
    Calculate and track comprehensive performance metrics
    """
    
    def __init__(self):
        self.sector_times = {}  # {car_id: [sector1, sector2, sector3]}
        self.lap_times = {}  # {car_id: [lap1, lap2, ...]}
        self.top_speeds = {}  # {car_id: max_speed}
        self.energy_efficiency = {}  # {car_id: km_per_kwh}
        self.overtakes = {}  # {car_id: overtake_count}
        self.positions_gained = {}  # {car_id: positions_gained}
        
    def update_from_race_state(self, race_state: RaceState):
        """
        Update metrics from current race state
        
        Args:
            race_state: Current race state
        """
        for car in race_state.cars:
            car_id = car.car_id
            
            # Top speeds
            self.top_speeds[car_id] = max(
                self.top_speeds.get(car_id, 0),
                car.max_speed_achieved * 3.6  # Convert to km/h
            )
            
            # Energy efficiency
            self.energy_efficiency[car_id] = car.get_energy_efficiency()
            
            # Overtakes
            self.overtakes[car_id] = car.overtakes_made
    
    def calculate_driver_rating(self, car: CarState, starting_position: int) -> float:
        """
        Calculate overall driver performance rating (0-100)
        
        Args:
            car: Car state
            starting_position: Starting grid position
            
        Returns:
            Performance rating
        """
        rating = 50.0  # Base rating
        
        # Position change component
        position_change = starting_position - car.position
        rating += position_change * 3.0  # +3 points per position gained
        
        # Best lap time component (if faster than expected)
        if car.best_lap_time != np.inf:
            expected_time = 90.0  # Expected lap time
            time_diff = expected_time - car.best_lap_time
            rating += time_diff * 2.0  # +2 points per second faster
        
        # Overtakes component
        rating += car.overtakes_made * 2.0
        
        # Energy management component
        if car.is_active:
            # Reward good energy management
            if car.battery_percentage > 30:
                rating += 5.0
            elif car.battery_percentage > 10:
                rating += 2.0
        else:
            # Penalty for retiring
            rating -= 20.0
        
        # Tire management component
        if car.tire_degradation < 0.5:
            rating += 3.0
        
        # Clamp to 0-100 range
        return np.clip(rating, 0.0, 100.0)
    
    def get_race_summary(self, race_state: RaceState, starting_grid: List[int]) -> Dict:
        """
        Generate comprehensive race summary statistics
        
        Args:
            race_state: Final race state
            starting_grid: List of starting positions
            
        Returns:
            Summary dictionary
        """
        summary = {
            'total_cars': race_state.num_cars,
            'finished_cars': len([c for c in race_state.cars if c.is_active]),
            'retired_cars': len([c for c in race_state.cars if not c.is_active]),
            'total_overtakes': sum(c.overtakes_made for c in race_state.cars),
            'average_speed_kmh': np.mean([c.max_speed_achieved * 3.6 for c in race_state.cars]),
            'fastest_lap': min((c.best_lap_time for c in race_state.cars if c.best_lap_time != np.inf), default=None),
            'driver_ratings': {}
        }
        
        # Calculate driver ratings
        for i, car in enumerate(race_state.cars):
            start_pos = starting_grid[i] if i < len(starting_grid) else i + 1
            rating = self.calculate_driver_rating(car, start_pos)
            summary['driver_ratings'][car.driver_name] = round(rating, 2)
        
        return summary
    
    def export_sector_analysis(self, car_id: int) -> Dict:
        """
        Export detailed sector analysis for a car
        
        Args:
            car_id: Car identifier
            
        Returns:
            Sector analysis dictionary
        """
        if car_id not in self.sector_times:
            return {}
        
        sectors = self.sector_times[car_id]
        return {
            'sector_1': sectors[0] if len(sectors) > 0 else None,
            'sector_2': sectors[1] if len(sectors) > 1 else None,
            'sector_3': sectors[2] if len(sectors) > 2 else None,
            'total': sum(sectors) if sectors else None
        }
    
    def get_performance_comparison(
        self,
        car1: CarState,
        car2: CarState
    ) -> Dict:
        """
        Compare performance between two cars
        
        Args:
            car1: First car
            car2: Second car
            
        Returns:
            Comparison dictionary
        """
        return {
            'position_difference': car1.position - car2.position,
            'lap_time_difference': car1.best_lap_time - car2.best_lap_time if car1.best_lap_time != np.inf and car2.best_lap_time != np.inf else None,
            'speed_difference_kmh': (car1.max_speed_achieved - car2.max_speed_achieved) * 3.6,
            'energy_efficiency_difference': car1.get_energy_efficiency() - car2.get_energy_efficiency(),
            'overtake_difference': car1.overtakes_made - car2.overtakes_made
        }
