"""
Configuration module for Formula E Race Simulator
Contains all physical constants, tunable parameters, and track configurations
Based on Gen3 Formula E car specifications (2022-present)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


@dataclass
class PhysicsConfig:
    """
    Physical constants and constraints for race simulation
    Values based on Gen3 Formula E car specifications
    """
    
    # Vehicle mass and dimensions (Gen3 specifications)
    CAR_MASS: float = 840.0  # kg (without driver)
    DRIVER_MASS: float = 80.0  # kg (standardized)
    TOTAL_MASS: float = 920.0  # kg (car + driver)
    CAR_LENGTH: float = 5.016  # meters
    CAR_WIDTH: float = 1.7  # meters
    WHEELBASE: float = 2.97  # meters
    TRACK_WIDTH_FRONT: float = 1.45  # meters
    TRACK_WIDTH_REAR: float = 1.39  # meters
    CENTER_OF_GRAVITY_HEIGHT: float = 0.30  # meters from ground
    
    # Motion constraints (Gen3 realistic values)
    MAX_POWER_KW: float = 350.0  # kW (race mode)
    MAX_POWER_QUALI_KW: float = 350.0  # kW (qualifying)
    MAX_REGEN_POWER_KW: float = 600.0  # kW (world's first with front and rear regen)
    MAX_ACCELERATION: float = 2.8  # m/s² (0-100 km/h in 2.8s)
    MAX_DECELERATION: float = 5.5  # m/s² (Formula E cars can brake harder with carbon brakes + regen)
    MAX_SPEED_KMH: float = 322.0  # km/h (Gen3 top speed record)
    MAX_SPEED_MS: float = 322.0 / 3.6  # m/s (89.44 m/s)
    GRAVITY: float = 9.81  # m/s²
    
    # Aerodynamics (realistic Formula E values)
    DRAG_COEFFICIENT: float = 0.32  # Cd
    FRONTAL_AREA: float = 1.5  # m²
    DOWNFORCE_COEFFICIENT: float = 1.8  # Cl (at max speed)
    AIR_DENSITY: float = 1.225  # kg/m³ (sea level, 15°C)
    ROLLING_RESISTANCE_COEFF: float = 0.015  # Cr
    
    # Energy parameters (Gen3 specifications)
    BATTERY_CAPACITY_KWH: float = 51.0  # kWh (usable capacity)
    BATTERY_CAPACITY_J: float = 51.0 * 3.6e6  # Joules (183.6 MJ)
    BATTERY_VOLTAGE: float = 470.0  # Volts (nominal)
    BATTERY_MAX_DISCHARGE_RATE: float = 350.0  # kW
    BATTERY_MAX_CHARGE_RATE: float = 600.0  # kW (regen)
    BATTERY_EFFICIENCY: float = 0.95  # 95% round-trip efficiency
    
    # Motor parameters
    MOTOR_EFFICIENCY: float = 0.97  # 97% efficiency (Formula E uses highly efficient motors)
    MOTOR_MAX_RPM: float = 20000.0  # rpm
    MOTOR_MAX_TORQUE: float = 338.0  # Nm (per motor)
    GEAR_RATIO: float = 11.0  # Single-speed transmission ratio
    
    # Regenerative braking (realistic Formula E values)
    REGEN_EFFICIENCY: float = 0.40  # 40% energy recovery (Formula E is industry-leading)
    REGEN_MAX_TORQUE: float = 250.0  # Nm (regen torque limit)
    FRONT_REGEN_POWER_KW: float = 250.0  # kW (Gen3 front motor)
    REAR_REGEN_POWER_KW: float = 350.0  # kW (Gen3 rear motor)
    
    # Attack mode (official Formula E rules)
    ATTACK_MODE_POWER_BOOST_KW: float = 50.0  # 350kW -> 400kW (Gen3)
    ATTACK_MODE_DURATION_SEC: float = 240.0  # 4 minutes per activation
    ATTACK_MODE_ACTIVATIONS: int = 2  # 2 activations per race (typical)
    ATTACK_MODE_MIN_DURATION: float = 120.0  # Minimum 2 minutes
    ATTACK_MODE_SPEED_BOOST: float = 1.08  # ~8% speed increase
    ATTACK_MODE_ENERGY_MULTIPLIER: float = 1.30  # 30% more energy consumption
    
    # Tire model (Hankook Formula E tires)
    TIRE_DIAMETER: float = 0.720  # meters (18 inch rims)
    TIRE_WIDTH_FRONT: float = 0.305  # meters
    TIRE_WIDTH_REAR: float = 0.305  # meters
    TIRE_PRESSURE_NOMINAL: float = 1.8  # bar (typical)
    TIRE_OPTIMAL_TEMP: float = 90.0  # Celsius (Formula E slicks optimal)
    TIRE_MIN_TEMP: float = 60.0  # Celsius (below this, grip loss)
    TIRE_MAX_TEMP: float = 120.0  # Celsius (above this, degradation accelerates)
    TIRE_COMPOUND: str = "All-weather slick"  # Single compound for wet and dry
    
    # Tire degradation (realistic parameters)
    TIRE_K_BASE: float = 0.002  # Base degradation rate per second (increased for visibility)
    TIRE_K_TEMP: float = 0.00005  # Temperature-dependent degradation
    TIRE_K_SPEED: float = 0.00003  # Speed-dependent degradation
    TIRE_K_LATERAL: float = 0.0004  # Lateral G-force degradation (cornering)
    TIRE_K_LOCK: float = 0.01  # Degradation spike on wheel lock
    MU_MAX: float = 1.2  # Maximum grip coefficient (Formula E street circuit)
    MU_MIN: float = 0.9  # Minimum grip coefficient (fully worn)
    MU_WET_FACTOR: float = 0.7  # Wet condition grip multiplier
    
    # Temperature model (battery thermal management)
    AMBIENT_TEMP: float = 25.0  # Celsius (standard conditions)
    BATTERY_TEMP_MIN: float = 20.0  # Celsius (minimum operating)
    BATTERY_TEMP_MAX: float = 60.0  # Celsius (maximum safe)
    BATTERY_OPTIMAL_TEMP: float = 40.0  # Celsius (optimal performance)
    BATTERY_HEAT_CAPACITY: float = 850.0  # J/(kg·K)
    BATTERY_COOLING_POWER: float = 15.0  # kW (active cooling system)
    BATTERY_HEAT_GENERATION_FACTOR: float = 0.015  # Heat per power draw
    THERMAL_MASS: float = 200.0  # kg (effective thermal mass of battery)
    
    # Driver performance variation (realistic human factors)
    DRIVER_SKILL_MEAN: float = 1.0
    DRIVER_SKILL_STD: float = 0.08  # 8% variation in skill
    DRIVER_REACTION_TIME_MIN: float = 0.15  # seconds (elite drivers)
    DRIVER_REACTION_TIME_MAX: float = 0.25  # seconds (slower reaction)
    DRIVER_FATIGUE_RATE: float = 0.001  # Performance degradation per minute
    DRIVER_CONSISTENCY: float = 0.95  # Lap time consistency (95%)
    
    # Risk and crash probability (realistic crash rates - extremely rare)
    CRASH_BASE_PROBABILITY: float = 0.0000001  # Base crash probability per second (1000x reduced)
    CRASH_SPEED_FACTOR: float = 0.015  # Speed contribution to crash risk
    CRASH_TIRE_FACTOR: float = 0.25  # Tire degradation contribution
    CRASH_PROXIMITY_FACTOR: float = 0.30  # Close racing risk
    CRASH_AGGRESSION_FACTOR: float = 0.20  # Driver aggression risk
    CRASH_WEATHER_WET_MULTIPLIER: float = 2.5  # Wet conditions risk increase
    
    # Safety car and race control
    SAFETY_CAR_PROBABILITY: float = 0.15  # 15% chance per race (realistic)
    SAFETY_CAR_MIN_DURATION: float = 180.0  # 3 minutes minimum
    SAFETY_CAR_MAX_DURATION: float = 420.0  # 7 minutes maximum
    SAFETY_CAR_SPEED_KMH: float = 60.0  # km/h
    YELLOW_FLAG_SPEED_REDUCTION: float = 0.7  # 30% speed reduction
    RED_FLAG_PROBABILITY: float = 0.02  # 2% chance per race
    
    # Weather effects
    RAIN_GRIP_REDUCTION: float = 0.30  # 30% grip loss in rain
    RAIN_VISIBILITY_REDUCTION: float = 0.20  # 20% visibility loss
    RAIN_ENERGY_INCREASE: float = 0.10  # 10% more energy in wet
    TEMPERATURE_GRIP_FACTOR: float = 0.005  # Grip change per °C
    WIND_DRAG_FACTOR: float = 0.02  # Drag increase per m/s wind


@dataclass
class WeatherConditions:
    """Current weather and track conditions"""
    temperature_air: float = 25.0  # Celsius
    temperature_track: float = 35.0  # Celsius
    humidity: float = 50.0  # Percentage
    wind_speed: float = 0.0  # m/s
    wind_direction: float = 0.0  # degrees (0=headwind, 90=crosswind, 180=tailwind)
    rain_intensity: float = 0.0  # 0=dry, 1=light rain, 2=heavy rain
    track_wetness: float = 0.0  # 0=dry, 1=fully wet
    visibility: float = 100.0  # Percentage


@dataclass
class CarConfiguration:
    """Individual car configuration and specifications"""
    team_name: str
    car_number: int
    driver_name: str
    
    # Performance characteristics (normalized around 1.0)
    power_efficiency: float = 1.0  # Motor efficiency factor
    battery_efficiency: float = 1.0  # Battery efficiency factor
    aero_efficiency: float = 1.0  # Drag/downforce balance
    tire_wear_rate: float = 1.0  # Tire degradation multiplier
    cooling_efficiency: float = 1.0  # Thermal management
    regen_efficiency: float = 1.0  # Regenerative braking effectiveness
    
    # Setup parameters
    downforce_level: float = 1.0  # 0.8=low drag, 1.2=high downforce
    brake_balance: float = 0.55  # Front brake bias (0.5-0.65)
    diff_setting: int = 3  # Differential setting (1-5)
    regen_strength: float = 0.8  # Regen brake strength (0-1)
    
    # Reliability (0-1, 1=perfect reliability)
    reliability_factor: float = 0.98  # 98% reliability


@dataclass  
class RaceControlState:
    """Race control flags and conditions"""
    flag_status: str = "green"  # green, yellow, red, safety_car, vsc
    safety_car_active: bool = False
    vsc_active: bool = False  # Virtual Safety Car
    drs_enabled: bool = False  # Not used in Formula E but kept for extensibility
    attack_mode_zones_active: bool = True
    session_type: str = "race"  # practice, qualifying, race
    race_status: str = "racing"  # racing, paused, finished, abandoned


@dataclass
class PenaltyRecord:
    """Track penalties issued to drivers"""
    car_id: int
    lap_number: int
    timestamp: float
    penalty_type: str  # time_penalty, drive_through, stop_go, disqualification
    penalty_value: float  # seconds of time penalty
    reason: str
    served: bool = False


@dataclass
class TrackSegment:
    """Represents a single segment of the track"""
    segment_type: str  # 'straight', 'left_corner', 'right_corner', 'chicane'
    length: float  # meters
    radius: float  # meters (for corners, inf for straights)
    banking_angle: float  # degrees (positive = banked into corner)
    camber: float  # degrees (road slope)
    elevation_change: float  # meters (positive = uphill)
    grip_level: float  # 0.9-1.1 base grip multiplier
    ideal_speed_kmh: float  # km/h
    attack_mode_zone: bool = False  # Is this an attack mode activation zone?
    racing_line_curvature: float = 0.0  # Ideal racing line curvature (1/radius)
    

class TrackConfig:
    """Track configuration and geometry"""
    
    def __init__(self, track_name: str = "Plaksha"):
        self.track_name = track_name
        self.segments = self._build_track()
        self.total_length = sum(seg.length for seg in self.segments)
        self.lap_record_seconds = 78.0  # Plaksha E-Prix typical lap time
        self.attack_mode_zones = self._get_attack_mode_zones()
        self.pit_lane_length = 180.0  # meters
        self.pit_lane_speed_limit_kmh = 50.0  # km/h
        
    def _build_track(self) -> List[TrackSegment]:
        """Build Plaksha E-Prix Circuit - Real Formula E street circuit"""
        # Plaksha International E-Prix Circuit (2022-present)
        # 2.370 km, 18 turns, flowing street circuit layout
        segments = [
            # Sector 1 - Start/Finish through Turn 1-6
            TrackSegment('straight', 280, np.inf, 0, 0, 0, 1.0, 270, False, 0),  # Start straight
            TrackSegment('left_corner', 55, 40, 0, 1, 0, 0.93, 95, False, 0.0250),  # Turn 1 - Left
            TrackSegment('straight', 90, np.inf, 0, 0, 0, 0.98, 200, False, 0),  # Short straight
            TrackSegment('left_corner', 50, 35, 0, 1, 0, 0.91, 88, False, 0.0286),  # Turn 2 - Tight left
            TrackSegment('straight', 110, np.inf, 0, 0, 0, 0.97, 220, False, 0),  # Acceleration
            TrackSegment('right_corner', 65, 42, 2, 1, 0, 0.93, 98, False, 0.0238),  # Turn 3 - Right sweep
            TrackSegment('straight', 70, np.inf, 0, 0, 0, 0.96, 190, False, 0),  # Short blast
            TrackSegment('left_corner', 60, 38, 0, 2, 0, 0.92, 92, False, 0.0263),  # Turn 4 - Medium left
            TrackSegment('straight', 85, np.inf, 0, 0, 0, 0.97, 210, False, 0),  # Brief straight
            TrackSegment('right_corner', 55, 36, 0, 1, 0, 0.91, 90, False, 0.0278),  # Turn 5 - Tight right
            
            # Sector 2 - Technical section Turn 6-12
            TrackSegment('straight', 130, np.inf, 0, 0, 0, 0.98, 235, False, 0),  # Mid straight
            TrackSegment('left_corner', 70, 45, 3, 2, 0, 0.94, 105, True, 0.0222),  # Turn 6 - ATTACK MODE
            TrackSegment('straight', 95, np.inf, 0, 0, 0, 0.97, 215, False, 0),  # Straight section
            TrackSegment('right_corner', 75, 48, 0, 1, 0, 0.93, 108, False, 0.0208),  # Turn 7 - Right
            TrackSegment('straight', 105, np.inf, 0, 0, 0, 0.98, 225, False, 0),  # Flowing section
            TrackSegment('left_corner', 80, 50, 4, 2, 0, 0.95, 112, False, 0.0200),  # Turn 8 - Fast left
            TrackSegment('chicane', 65, 28, 0, 1, 0, 0.90, 82, False, 0.0357),  # Turn 9 - Chicane complex
            TrackSegment('straight', 140, np.inf, 0, 0, 0, 0.98, 245, False, 0),  # Long straight
            TrackSegment('right_corner', 70, 43, 0, 2, 0, 0.93, 100, False, 0.0233),  # Turn 10 - Right
            TrackSegment('straight', 75, np.inf, 0, 0, 0, 0.96, 195, False, 0),  # Short section
            
            # Sector 3 - Final complex Turn 11-18
            TrackSegment('left_corner', 85, 52, 5, 2, 0, 0.95, 115, False, 0.0192),  # Turn 11 - Sweeping left
            TrackSegment('straight', 125, np.inf, 0, 0, 0, 0.99, 240, False, 0),  # Back straight
            TrackSegment('right_corner', 60, 39, 0, 1, 0, 0.92, 94, False, 0.0256),  # Turn 12 - Right
            TrackSegment('straight', 80, np.inf, 0, 0, 0, 0.97, 205, False, 0),  # Short blast
            TrackSegment('left_corner', 65, 41, 0, 1, 0, 0.92, 96, True, 0.0244),  # Turn 13 - ATTACK MODE
            TrackSegment('straight', 90, np.inf, 0, 0, 0, 0.97, 215, False, 0),  # Acceleration zone
            TrackSegment('right_corner', 70, 44, 2, 2, 0, 0.94, 102, False, 0.0227),  # Turn 14 - Medium right
            TrackSegment('straight', 100, np.inf, 0, 0, 0, 0.98, 230, False, 0),  # Final sector straight
            TrackSegment('chicane', 70, 30, 0, 1, 0, 0.91, 85, False, 0.0333),  # Turn 15-16 - Fast chicane
            TrackSegment('straight', 110, np.inf, 0, 0, 0, 0.98, 235, False, 0),  # Penultimate straight
            TrackSegment('left_corner', 75, 46, 3, 2, 0, 0.94, 106, False, 0.0217),  # Turn 17 - Left
            TrackSegment('right_corner', 55, 37, 0, 1, 0, 0.91, 91, False, 0.0270),  # Turn 18 - Final right
            TrackSegment('straight', 170, np.inf, 0, 0, 0, 0.99, 265, False, 0),  # Final straight to S/F
        ]
        return segments
    
    def _get_attack_mode_zones(self) -> List[Tuple[float, float]]:
        """Get attack mode activation zones (start_distance, end_distance)"""
        zones = []
        cumulative = 0.0
        for seg in self.segments:
            if seg.attack_mode_zone:
                zones.append((cumulative, cumulative + seg.length))
            cumulative += seg.length
        return zones
    
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
    
    def calculate_max_corner_speed(
        self, 
        radius: float, 
        grip_coefficient: float,
        banking_angle: float = 0.0,
        downforce_level: float = 1.0
    ) -> float:
        """
        Calculate maximum cornering speed using physics
        v_max = sqrt((μ * g * r * (1 + tan(θ))) + (Cl * ρ * A * v² / (2 * m)))
        Simplified iterative solution
        
        Args:
            radius: Corner radius (meters)
            grip_coefficient: Current grip level (0-1.8)
            banking_angle: Banking angle (degrees)
            downforce_level: Downforce multiplier (0.8-1.2)
            
        Returns:
            Maximum safe speed (m/s)
        """
        if radius == np.inf:
            return PhysicsConfig.MAX_SPEED_MS
        
        g = PhysicsConfig.GRAVITY
        m = PhysicsConfig.TOTAL_MASS
        
        # Banking contribution
        theta_rad = np.radians(banking_angle)
        banking_factor = 1.0 + np.tan(theta_rad) if banking_angle > 0 else 1.0
        
        # Mechanical grip component
        v_mechanical = np.sqrt(grip_coefficient * g * radius * banking_factor)
        
        # Simplified downforce contribution (iterative approximation)
        # At this speed, approximate downforce load
        Cl = PhysicsConfig.DOWNFORCE_COEFFICIENT * downforce_level
        rho = PhysicsConfig.AIR_DENSITY
        A = PhysicsConfig.FRONTAL_AREA
        
        # Downforce increases effective grip
        # F_down = 0.5 * Cl * rho * A * v²
        # Additional lateral force = F_down * μ
        # This adds to cornering ability
        
        # Iterative solution (2 iterations sufficient for accuracy)
        v_estimate = v_mechanical
        for _ in range(2):
            F_down = 0.5 * Cl * rho * A * (v_estimate ** 2)
            additional_lateral = (F_down / m) * grip_coefficient * radius
            v_estimate = np.sqrt(grip_coefficient * g * radius * banking_factor + additional_lateral)
        
        return min(v_estimate, PhysicsConfig.MAX_SPEED_MS)


@dataclass
class SimulationConfig:
    """Simulation runtime parameters"""
    
    TIMESTEP: float = 0.05  # seconds (1000 Hz simulation for maximum accuracy)
    NUM_LAPS: int = 10
    NUM_CARS: int = 24
    RACE_DISTANCE_KM: float = 2.5  # km per lap
    
    # Random seeds for reproducibility
    PHYSICS_SEED: int = 42
    EVENTS_SEED: int = 123
    WEATHER_SEED: int = 789
    
    # Performance optimization
    USE_VECTORIZATION: bool = True
    PARALLEL_PHYSICS: bool = False  # Single-threaded for deterministic results
    
    # Output configuration
    LOG_FREQUENCY: int = 1000  # Log every N timesteps (1 second at 1000Hz)
    EXPORT_JSON: bool = True
    EXPORT_CSV: bool = True
    STORE_ALL_TIMESTEPS: bool = True  # Store complete state matrix at every timestep
    
    # Qualifying settings
    QUALIFYING_DURATION_SECONDS: float = 600.0  # 10 minutes
    QUALIFYING_GROUPS: int = 4  # Split field into groups
    
    # Race settings  
    TOTAL_RACE_ENERGY_LIMIT_KWH: float = 51.0  # Must finish with at least 0%
    ENABLE_PIT_STOPS: bool = False  # Formula E doesn't have pit stops (except car changes in early years)
    ENABLE_ATTACK_MODE: bool = True
    ENABLE_FANBOOST: bool = False  # Optional FanBoost feature
    
    # Simulation fidelity
    ENABLE_WEATHER: bool = True
    ENABLE_TIRE_TEMPS: bool = True
    ENABLE_BATTERY_TEMPS: bool = True
    ENABLE_DRIVER_FATIGUE: bool = True
    ENABLE_STOCHASTIC_EVENTS: bool = True  # Random mechanical failures, etc.


class DriverConfig:
    """Individual driver profiles with realistic characteristics"""
    
    # Gen3 Formula E teams and drivers (2023-2024 season example)
    DRIVERS = [
        # TAG Heuer Porsche
        {"team": "TAG Heuer Porsche", "name": "Pascal Wehrlein", "number": 94, "skill": 1.08, "aggression": 0.75, "consistency": 0.95, "racecraft": 0.92},
        {"team": "TAG Heuer Porsche", "name": "António Félix da Costa", "number": 13, "skill": 1.07, "aggression": 0.78, "consistency": 0.93, "racecraft": 0.90},
        
        # Jaguar TCS Racing  
        {"team": "Jaguar TCS Racing", "name": "Mitch Evans", "number": 9, "skill": 1.06, "aggression": 0.82, "consistency": 0.91, "racecraft": 0.94},
        {"team": "Jaguar TCS Racing", "name": "Nick Cassidy", "number": 37, "skill": 1.07, "aggression": 0.80, "consistency": 0.92, "racecraft": 0.91},
        
        # DS Penske
        {"team": "DS Penske", "name": "Jean-Éric Vergne", "number": 25, "skill": 1.09, "aggression": 0.76, "consistency": 0.96, "racecraft": 0.95},
        {"team": "DS Penske", "name": "Stoffel Vandoorne", "number": 26, "skill": 1.06, "aggression": 0.72, "consistency": 0.94, "racecraft": 0.90},
        
        # Envision Racing
        {"team": "Envision Racing", "name": "Robin Frijns", "number": 4, "skill": 1.05, "aggression": 0.81, "consistency": 0.89, "racecraft": 0.88},
        {"team": "Envision Racing", "name": "Sébastien Buemi", "number": 23, "skill": 1.08, "aggression": 0.74, "consistency": 0.95, "racecraft": 0.93},
        
        # Nissan Formula E Team
        {"team": "Nissan", "name": "Sacha Fenestraz", "number": 23, "skill": 1.03, "aggression": 0.77, "consistency": 0.88, "racecraft": 0.85},
        {"team": "Nissan", "name": "Norman Nato", "number": 17, "skill": 1.02, "aggression": 0.83, "consistency": 0.86, "racecraft": 0.84},
        
        # Mahindra Racing
        {"team": "Mahindra Racing", "name": "Oliver Rowland", "number": 30, "skill": 1.05, "aggression": 0.79, "consistency": 0.90, "racecraft": 0.89},
        {"team": "Mahindra Racing", "name": "Edoardo Mortara", "number": 48, "skill": 1.06, "aggression": 0.77, "consistency": 0.92, "racecraft": 0.88},
        
        # Maserati MSG Racing
        {"team": "Maserati MSG Racing", "name": "Maximilian Günther", "number": 7, "skill": 1.04, "aggression": 0.80, "consistency": 0.87, "racecraft": 0.87},
        {"team": "Maserati MSG Racing", "name": "Jehan Daruvala", "number": 21, "skill": 1.01, "aggression": 0.78, "consistency": 0.85, "racecraft": 0.82},
        
        # Andretti Formula E
        {"team": "Andretti", "name": "Jake Dennis", "number": 27, "skill": 1.07, "aggression": 0.81, "consistency": 0.93, "racecraft": 0.91},
        {"team": "Andretti", "name": "André Lotterer", "number": 36, "skill": 1.05, "aggression": 0.75, "consistency": 0.91, "racecraft": 0.89},
        
        # ABT Cupra
        {"team": "ABT Cupra", "name": "Nico Müller", "number": 51, "skill": 1.04, "aggression": 0.76, "consistency": 0.89, "racecraft": 0.86},
        {"team": "ABT Cupra", "name": "Lucas di Grassi", "number": 11, "skill": 1.08, "aggression": 0.73, "consistency": 0.94, "racecraft": 0.93},
        
        # Avalanche Andretti
        {"team": "Avalanche Andretti", "name": "Jake Hughes", "number": 28, "skill": 1.03, "aggression": 0.82, "consistency": 0.86, "racecraft": 0.84},
        {"team": "Avalanche Andretti", "name": "Nyck de Vries", "number": 21, "skill": 1.04, "aggression": 0.74, "consistency": 0.90, "racecraft": 0.87},
        
        # Neom McLaren
        {"team": "Neom McLaren", "name": "Sam Bird", "number": 10, "skill": 1.05, "aggression": 0.79, "consistency": 0.90, "racecraft": 0.90},
        {"team": "Neom McLaren", "name": "René Rast", "number": 3, "skill": 1.03, "aggression": 0.77, "consistency": 0.88, "racecraft": 0.85},
        
        # NIO 333 Racing
        {"team": "NIO 333", "name": "Dan Ticktum", "number": 33, "skill": 1.02, "aggression": 0.84, "consistency": 0.84, "racecraft": 0.83},
        {"team": "NIO 333", "name": "Sérgio Sette Câmara", "number": 19, "skill": 1.01, "aggression": 0.80, "consistency": 0.83, "racecraft": 0.81},
        
        # ERT Formula E Team
        {"team": "ERT", "name": "Driver 23", "number": 55, "skill": 1.00, "aggression": 0.76, "consistency": 0.82, "racecraft": 0.80},
        {"team": "ERT", "name": "Driver 24", "number": 56, "skill": 0.99, "aggression": 0.75, "consistency": 0.80, "racecraft": 0.78},
    ]
    
    @classmethod
    def get_driver(cls, car_id: int) -> Dict:
        """Get driver profile by car ID"""
        return cls.DRIVERS[car_id % len(cls.DRIVERS)]
    
    @classmethod
    def get_car_config(cls, car_id: int) -> CarConfiguration:
        """Get car configuration for a specific car"""
        driver = cls.get_driver(car_id)
        
        # Add slight performance variations between teams (±3%)
        np.random.seed(car_id)  # Deterministic per car
        
        return CarConfiguration(
            team_name=driver["team"],
            car_number=driver["number"],
            driver_name=driver["name"],
            power_efficiency=np.random.uniform(0.98, 1.02),
            battery_efficiency=np.random.uniform(0.97, 1.03),
            aero_efficiency=np.random.uniform(0.98, 1.02),
            tire_wear_rate=np.random.uniform(0.95, 1.05),
            cooling_efficiency=np.random.uniform(0.98, 1.02),
            regen_efficiency=np.random.uniform(0.97, 1.03),
            reliability_factor=np.random.uniform(0.96, 0.99)
        )


# Global configuration instances
physics_config = PhysicsConfig()
track_config = TrackConfig()
simulation_config = SimulationConfig()

