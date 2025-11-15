"""
State space representation for Formula E race simulation
Implements high-dimensional vector space framework for complete race state
"""

import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CarState:
    """
    Complete state vector for a single race car
    Represents a point in the high-dimensional state space
    """
    
    # Identity
    car_id: int
    driver_name: str
    
    # Position and motion (2D coordinates)
    position_x: float = 0.0  # meters from start line (longitudinal)
    position_y: float = 0.0  # meters from center line (lateral)
    velocity_x: float = 0.0  # m/s (longitudinal)
    velocity_y: float = 0.0  # m/s (lateral)
    
    # Energy state
    battery_energy: float = 51.0 * 3.6e6  # Joules (starts at 100%)
    battery_percentage: float = 100.0  # 0-100%
    
    # Thermal state
    battery_temperature: float = 40.0  # Celsius
    
    # Tire state
    tire_degradation: float = 0.0  # 0-1 (0=new, 1=completely worn)
    tire_temperature: float = 70.0  # Celsius (tire operating temperature)
    grip_coefficient: float = 1.8  # Current grip level (Gen3 tires)
    
    # Attack mode
    attack_mode_active: bool = False
    attack_mode_remaining: float = 0.0  # seconds
    attack_mode_uses_left: int = 2
    
    # Lap data
    current_lap: int = 0
    lap_distance: float = 0.0  # Distance into current lap (meters)
    total_distance: float = 0.0  # Total distance traveled (meters)
    
    # Performance metrics
    last_lap_time: float = 0.0  # seconds
    best_lap_time: float = np.inf  # seconds
    sector_times: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    current_sector: int = 0
    sector_start_time: float = 0.0
    
    # Race status
    is_active: bool = True  # False if crashed/retired
    gap_to_leader: float = 0.0  # seconds
    gap_to_ahead: float = 0.0  # seconds
    position: int = 1  # Current race position
    
    # Physics state
    acceleration: float = 0.0  # m/s²
    steering_angle: float = 0.0  # radians
    throttle: float = 0.0  # 0-1
    brake: float = 0.0  # 0-1
    
    # Accumulated statistics
    total_energy_consumed: float = 0.0  # Joules
    total_energy_regenerated: float = 0.0  # Joules
    max_speed_achieved: float = 0.0  # m/s
    overtakes_made: int = 0
    overtakes_received: int = 0
    
    # Timestamp
    time: float = 0.0  # Current race time (seconds)
    
    def to_vector(self) -> np.ndarray:
        """
        Convert car state to numpy vector for mathematical operations
        
        Returns:
            State vector of dimension 20
        """
        return np.array([
            self.position_x,
            self.position_y,
            self.velocity_x,
            self.velocity_y,
            self.battery_percentage,
            self.battery_temperature,
            self.tire_degradation,
            self.grip_coefficient,
            float(self.attack_mode_active),
            self.attack_mode_remaining,
            self.current_lap,
            self.lap_distance,
            self.acceleration,
            self.steering_angle,
            self.throttle,
            self.brake,
            float(self.is_active),
            self.position,
            self.gap_to_leader,
            self.total_distance
        ])
    
    @classmethod
    def from_vector(cls, vec: np.ndarray, car_id: int, driver_name: str) -> 'CarState':
        """
        Reconstruct CarState from state vector
        
        Args:
            vec: State vector (numpy array)
            car_id: Car identifier
            driver_name: Driver name
            
        Returns:
            CarState object
        """
        state = cls(car_id=car_id, driver_name=driver_name)
        state.position_x = vec[0]
        state.position_y = vec[1]
        state.velocity_x = vec[2]
        state.velocity_y = vec[3]
        state.battery_percentage = vec[4]
        state.battery_temperature = vec[5]
        state.tire_degradation = vec[6]
        state.grip_coefficient = vec[7]
        state.attack_mode_active = bool(vec[8])
        state.attack_mode_remaining = vec[9]
        state.current_lap = int(vec[10])
        state.lap_distance = vec[11]
        state.acceleration = vec[12]
        state.steering_angle = vec[13]
        state.throttle = vec[14]
        state.brake = vec[15]
        state.is_active = bool(vec[16])
        state.position = int(vec[17])
        state.gap_to_leader = vec[18]
        state.total_distance = vec[19]
        
        return state
    
    def get_speed(self) -> float:
        """Calculate current speed magnitude (m/s)"""
        return np.sqrt(self.velocity_x**2 + self.velocity_y**2)
    
    def get_speed_kmh(self) -> float:
        """Calculate current speed in km/h"""
        return self.get_speed() * 3.6
    
    def update_battery(self, energy_delta: float):
        """
        Update battery state after energy consumption/regeneration
        
        Args:
            energy_delta: Energy change in Joules (negative=consumption, positive=regen)
        """
        from .config import PhysicsConfig
        
        self.battery_energy = np.clip(
            self.battery_energy + energy_delta,
            0.0,
            PhysicsConfig.BATTERY_CAPACITY_J
        )
        
        self.battery_percentage = (
            self.battery_energy / PhysicsConfig.BATTERY_CAPACITY_J * 100.0
        )
        
        if energy_delta < 0:
            self.total_energy_consumed += abs(energy_delta)
        else:
            self.total_energy_regenerated += energy_delta
    
    def activate_attack_mode(self) -> bool:
        """
        Attempt to activate attack mode
        
        Returns:
            True if successfully activated, False otherwise
        """
        from .config import PhysicsConfig
        
        if self.attack_mode_uses_left > 0 and not self.attack_mode_active:
            self.attack_mode_active = True
            self.attack_mode_remaining = PhysicsConfig.ATTACK_MODE_DURATION_SEC
            self.attack_mode_uses_left -= 1
            return True
        return False
    
    def update_attack_mode(self, dt: float):
        """Update attack mode timer"""
        if self.attack_mode_active:
            self.attack_mode_remaining -= dt
            if self.attack_mode_remaining <= 0:
                self.attack_mode_active = False
                self.attack_mode_remaining = 0.0
    
    def get_energy_efficiency(self) -> float:
        """
        Calculate energy efficiency (distance per kWh)
        
        Returns:
            km per kWh
        """
        if self.total_energy_consumed == 0:
            return 0.0
        
        energy_kwh = self.total_energy_consumed / 3.6e6
        distance_km = self.total_distance / 1000.0
        
        return distance_km / energy_kwh if energy_kwh > 0 else 0.0
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary for JSON export"""
        return {
            'car_id': self.car_id,
            'driver_name': self.driver_name,
            'position': self.position,
            'current_lap': self.current_lap,
            'lap_distance': round(self.lap_distance, 2),
            'total_distance': round(self.total_distance, 2),
            'speed_kmh': round(self.get_speed_kmh(), 2),
            'battery_percentage': round(self.battery_percentage, 2),
            'battery_temperature': round(self.battery_temperature, 1),
            'tire_degradation': round(self.tire_degradation, 3),
            'attack_mode_active': self.attack_mode_active,
            'attack_mode_remaining': round(self.attack_mode_remaining, 1),
            'attack_mode_uses_left': self.attack_mode_uses_left,
            'last_lap_time': round(self.last_lap_time, 3),
            'best_lap_time': round(self.best_lap_time, 3) if self.best_lap_time != np.inf else None,
            'gap_to_leader': round(self.gap_to_leader, 3),
            'gap_to_ahead': round(self.gap_to_ahead, 3),
            'is_active': self.is_active,
            'energy_efficiency_km_per_kwh': round(self.get_energy_efficiency(), 2),
            'overtakes_made': self.overtakes_made,
            'overtakes_received': self.overtakes_received,
            'max_speed_achieved_kmh': round(self.max_speed_achieved * 3.6, 2),
            'time': round(self.time, 3)
        }


class RaceState:
    """
    Complete race state containing all cars
    Implements the full state matrix [num_cars × state_dimension]
    """
    
    def __init__(self, num_cars: int, driver_configs: list):
        """
        Initialize race state with all cars
        
        Args:
            num_cars: Number of cars in the race
            driver_configs: List of driver configuration dicts
        """
        self.num_cars = num_cars
        self.cars = []
        
        for i in range(num_cars):
            driver = driver_configs[i] if i < len(driver_configs) else {
                'name': f'Driver {i+1}',
                'skill': 1.0,
                'aggression': 0.7
            }
            
            car = CarState(
                car_id=i,
                driver_name=driver['name'],
                position=i + 1  # Starting grid order
            )
            
            # Stagger starting positions slightly
            car.position_x = -i * 8.0  # 8 meters between cars
            
            self.cars.append(car)
        
        self.current_time = 0.0
        self.safety_car_active = False
        self.race_started = False
        self.race_finished = False
        
    def get_state_matrix(self) -> np.ndarray:
        """
        Get complete state matrix for all cars
        
        Returns:
            Matrix of shape [num_cars, state_dimension]
        """
        return np.array([car.to_vector() for car in self.cars])
    
    def update_positions(self):
        """Sort cars by race distance and update position field"""
        # Sort by total distance (descending)
        sorted_cars = sorted(
            self.cars,
            key=lambda c: (c.current_lap, c.lap_distance) if c.is_active else (-1, -1),
            reverse=True
        )
        
        # Update positions
        for idx, car in enumerate(sorted_cars):
            car.position = idx + 1
        
        # Calculate gaps
        if sorted_cars and sorted_cars[0].is_active:
            leader_distance = sorted_cars[0].total_distance
            leader_time = sorted_cars[0].time
            
            for car in sorted_cars:
                if car.is_active:
                    # Approximate time gap based on distance and speed
                    distance_gap = leader_distance - car.total_distance
                    avg_speed = car.get_speed() if car.get_speed() > 0 else 1.0
                    car.gap_to_leader = distance_gap / avg_speed if avg_speed > 0 else 0.0
                else:
                    car.gap_to_leader = np.inf
            
            # Calculate gap to car ahead
            for i in range(len(sorted_cars)):
                if i == 0:
                    sorted_cars[i].gap_to_ahead = 0.0
                else:
                    if sorted_cars[i].is_active and sorted_cars[i-1].is_active:
                        distance_gap = sorted_cars[i-1].total_distance - sorted_cars[i].total_distance
                        avg_speed = sorted_cars[i].get_speed() if sorted_cars[i].get_speed() > 0 else 1.0
                        sorted_cars[i].gap_to_ahead = distance_gap / avg_speed if avg_speed > 0 else 0.0
                    else:
                        sorted_cars[i].gap_to_ahead = np.inf
    
    def get_active_cars(self) -> list:
        """Get list of cars still active in the race"""
        return [car for car in self.cars if car.is_active]
    
    def to_dict(self) -> Dict:
        """Export race state to dictionary"""
        return {
            'current_time': round(self.current_time, 3),
            'safety_car_active': self.safety_car_active,
            'race_started': self.race_started,
            'race_finished': self.race_finished,
            'num_active_cars': len(self.get_active_cars()),
            'cars': [car.to_dict() for car in self.cars]
        }
