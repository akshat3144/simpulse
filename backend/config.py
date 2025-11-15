"""
Configuration module for Formula E Race Simulator
Contains all physical constants, tunable parameters, and track configurations
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class PhysicsConfig:
    """Physical constants and constraints for race simulation"""
    
    # Motion constraints
    MAX_ACCELERATION: float = 2.8  # m/s²
    MAX_DECELERATION: float = 3.5  # m/s² (with regenerative braking)
    MAX_SPEED_KMH: float = 280.0  # km/h
    MAX_SPEED_MS: float = 280.0 / 3.6  # m/s
    GRAVITY: float = 9.81  # m/s²
    
    # Energy parameters
    BATTERY_CAPACITY_KWH: float = 51.0  # kWh
    BATTERY_CAPACITY_J: float = 51.0 * 3.6e6  # Joules
    
    # Energy consumption coefficients
    K1_VELOCITY: float = 0.15  # Velocity-dependent consumption
    K2_ACCELERATION: float = 50.0  # Acceleration-dependent consumption
    
    # Regenerative braking
    REGEN_EFFICIENCY: float = 0.25  # 25% energy recovery
    
    # Attack mode
    ATTACK_MODE_POWER_BOOST_KW: float = 50.0
    ATTACK_MODE_DURATION_SEC: float = 240.0  # 4 minutes
    ATTACK_MODE_ACTIVATIONS: int = 2
    ATTACK_MODE_SPEED_BOOST: float = 1.08  # 8% speed increase
    
    # Tire model
    TIRE_OPTIMAL_TEMP: float = 80.0  # Celsius
    TIRE_K_BASE: float = 0.0001  # Base degradation rate
    TIRE_K_TEMP: float = 0.00001  # Temperature factor
    TIRE_K_SPEED: float = 0.000005  # Speed factor
    MU_MAX: float = 1.2  # Maximum grip coefficient
    MU_DEGRADATION_FACTOR: float = 0.3  # 30% grip loss at full degradation
    
    # Temperature model
    AMBIENT_TEMP: float = 25.0  # Celsius
    BATTERY_HEAT_RATE: float = 0.01  # Heating per energy consumption
    BATTERY_COOLING_RATE: float = 0.005  # Cooling rate
    OPTIMAL_BATTERY_TEMP: float = 40.0  # Celsius
    
    # Driver performance variation
    DRIVER_SKILL_MEAN: float = 1.0
    DRIVER_SKILL_STD: float = 0.05
    
    # Crash probability sigmoid parameters
    CRASH_SIGMOID_K: float = 0.1
    CRASH_SIGMOID_X0: float = 50.0
    
    # Safety car probability (Poisson)
    SAFETY_CAR_LAMBDA: float = 0.1  # per lap


@dataclass
class TrackSegment:
    """Represents a single segment of the track"""
    segment_type: str  # 'straight', 'left_corner', 'right_corner', 'chicane'
    length: float  # meters
    radius: float  # meters (for corners, inf for straights)
    grip_level: float  # 0.9-1.1 multiplier
    ideal_speed_kmh: float  # km/h
    

class TrackConfig:
    """Track configuration and geometry"""
    
    def __init__(self, track_name: str = "Monaco"):
        self.track_name = track_name
        self.segments = self._build_track()
        self.total_length = sum(seg.length for seg in self.segments)
        self.lap_record_seconds = 90.0  # Approximate
        
    def _build_track(self) -> List[TrackSegment]:
        """Build a realistic Formula E street circuit"""
        segments = [
            TrackSegment('straight', 400, np.inf, 1.0, 250),
            TrackSegment('right_corner', 150, 50, 0.95, 80),
            TrackSegment('straight', 300, np.inf, 1.0, 220),
            TrackSegment('left_corner', 120, 40, 0.95, 70),
            TrackSegment('chicane', 100, 30, 0.9, 60),
            TrackSegment('straight', 500, np.inf, 1.0, 270),
            TrackSegment('left_corner', 180, 60, 0.95, 90),
            TrackSegment('straight', 250, np.inf, 1.0, 200),
            TrackSegment('right_corner', 140, 45, 0.95, 75),
            TrackSegment('straight', 360, np.inf, 1.0, 240),
        ]
        return segments
    
    def get_segment_at_distance(self, distance: float) -> Tuple[TrackSegment, float]:
        """
        Get track segment and local distance within that segment
        
        Args:
            distance: Total distance from start (meters)
            
        Returns:
            (segment, local_distance_in_segment)
        """
        distance = distance % self.total_length  # Handle lap wrapping
        cumulative = 0.0
        
        for segment in self.segments:
            if cumulative + segment.length > distance:
                return segment, distance - cumulative
            cumulative += segment.length
        
        return self.segments[-1], 0.0
    
    def calculate_max_corner_speed(self, radius: float, grip_coefficient: float) -> float:
        """
        Calculate maximum cornering speed using physics
        v_max = sqrt(μ * g * r)
        
        Args:
            radius: Corner radius (meters)
            grip_coefficient: Current grip level (0-1.2)
            
        Returns:
            Maximum safe speed (m/s)
        """
        if radius == np.inf:
            return PhysicsConfig.MAX_SPEED_MS
        
        g = PhysicsConfig.GRAVITY
        v_max = np.sqrt(grip_coefficient * g * radius)
        return min(v_max, PhysicsConfig.MAX_SPEED_MS)


@dataclass
class SimulationConfig:
    """Simulation runtime parameters"""
    
    TIMESTEP: float = 0.1  # seconds (10 Hz simulation)
    NUM_LAPS: int = 10
    NUM_CARS: int = 24
    RACE_DISTANCE_KM: float = 2.5  # km per lap
    
    # Random seeds for reproducibility
    PHYSICS_SEED: int = 42
    EVENTS_SEED: int = 123
    ML_SEED: int = 456
    
    # Performance optimization
    USE_VECTORIZATION: bool = True
    PARALLEL_PHYSICS: bool = True
    
    # Output configuration
    LOG_FREQUENCY: int = 10  # Log every N timesteps
    EXPORT_JSON: bool = True
    EXPORT_CSV: bool = True


@dataclass
class MLConfig:
    """Machine Learning model configurations"""
    
    # Neural Network for racing line prediction
    NN_INPUT_DIM: int = 10  # [pos_x, pos_y, vx, vy, energy, tire, attack, opp1, opp2, segment]
    NN_HIDDEN_LAYERS: List[int] = None
    NN_OUTPUT_DIM: int = 2  # [steering_angle, throttle_percentage]
    NN_LEARNING_RATE: float = 0.001
    
    # Q-Learning for energy management
    Q_STATE_DISCRETIZATION: Dict[str, int] = None
    Q_LEARNING_RATE: float = 0.1
    Q_DISCOUNT_FACTOR: float = 0.95
    Q_EPSILON: float = 0.1  # Exploration rate
    Q_EPSILON_DECAY: float = 0.995
    
    # Actions for Q-learning
    ACTIONS: List[str] = None
    
    def __post_init__(self):
        if self.NN_HIDDEN_LAYERS is None:
            self.NN_HIDDEN_LAYERS = [64, 32, 16]
        
        if self.Q_STATE_DISCRETIZATION is None:
            self.Q_STATE_DISCRETIZATION = {
                'lap_number': 10,
                'energy_remaining': 10,
                'position': 5,
                'gap_to_leader': 8
            }
        
        if self.ACTIONS is None:
            self.ACTIONS = [
                'conserve_energy',
                'neutral',
                'aggressive',
                'activate_attack_mode'
            ]


class DriverConfig:
    """Individual driver profiles"""
    
    DRIVERS = [
        {"name": "Driver 1", "skill": 1.05, "aggression": 0.8},
        {"name": "Driver 2", "skill": 1.03, "aggression": 0.7},
        {"name": "Driver 3", "skill": 1.02, "aggression": 0.75},
        {"name": "Driver 4", "skill": 1.01, "aggression": 0.65},
        {"name": "Driver 5", "skill": 1.0, "aggression": 0.7},
        {"name": "Driver 6", "skill": 0.99, "aggression": 0.8},
        {"name": "Driver 7", "skill": 0.98, "aggression": 0.6},
        {"name": "Driver 8", "skill": 0.97, "aggression": 0.75},
        {"name": "Driver 9", "skill": 0.96, "aggression": 0.85},
        {"name": "Driver 10", "skill": 0.95, "aggression": 0.7},
        {"name": "Driver 11", "skill": 0.94, "aggression": 0.65},
        {"name": "Driver 12", "skill": 0.93, "aggression": 0.75},
        {"name": "Driver 13", "skill": 0.92, "aggression": 0.8},
        {"name": "Driver 14", "skill": 0.91, "aggression": 0.7},
        {"name": "Driver 15", "skill": 0.90, "aggression": 0.6},
        {"name": "Driver 16", "skill": 0.89, "aggression": 0.65},
        {"name": "Driver 17", "skill": 0.88, "aggression": 0.75},
        {"name": "Driver 18", "skill": 0.87, "aggression": 0.7},
        {"name": "Driver 19", "skill": 0.86, "aggression": 0.8},
        {"name": "Driver 20", "skill": 0.85, "aggression": 0.65},
        {"name": "Driver 21", "skill": 0.84, "aggression": 0.75},
        {"name": "Driver 22", "skill": 0.83, "aggression": 0.7},
        {"name": "Driver 23", "skill": 0.82, "aggression": 0.6},
        {"name": "Driver 24", "skill": 0.81, "aggression": 0.7},
    ]
    
    @classmethod
    def get_driver(cls, car_id: int) -> Dict:
        """Get driver profile by car ID"""
        return cls.DRIVERS[car_id % len(cls.DRIVERS)]


# Global configuration instances
physics_config = PhysicsConfig()
track_config = TrackConfig()
simulation_config = SimulationConfig()
ml_config = MLConfig()
