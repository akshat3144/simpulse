"""
Stochastic Dynamics Module for SimPulse
Implements Gaussian noise and probabilistic state transitions

Mathematical Foundation:
    x(t+1) = f(x(t), u(t), θ(t)) + ε(t)
    
Where:
    - x(t): State vector at time t
    - f(): Deterministic transition function
    - u(t): Control inputs (throttle, brake, steering)
    - θ(t): Environmental parameters (weather, track conditions)
    - ε(t): Stochastic noise term ~ N(0, Σ)
"""

import numpy as np
from typing import Dict, Optional, Tuple
from .state import CarState
from .config import PhysicsConfig


class StochasticNoiseModel:
    """
    Implements additive Gaussian noise for realistic state uncertainty
    
    Noise sources:
    - Process noise: Inherent system unpredictability
    - Measurement noise: Sensor uncertainty
    - Driver inconsistency: Human error in control execution
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize noise model with random number generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(seed)
        
        # Noise standard deviations (tunable parameters)
        self.sigma_velocity = 0.15  # m/s (velocity measurement noise)
        self.sigma_position = 0.05  # m (position tracking error)
        self.sigma_acceleration = 0.08  # m/s² (acceleration noise)
        self.sigma_steering = 0.005  # rad (steering execution error)
        self.sigma_control = 0.02  # 0-1 (throttle/brake jitter)
        self.sigma_tire_temp = 0.5  # °C (thermal fluctuation)
        self.sigma_battery_temp = 0.3  # °C (battery thermal noise)
        
    def apply_process_noise(
        self, 
        car: CarState, 
        driver_consistency: float = 1.0,
        dt: float = 0.01
    ) -> None:
        """
        Apply Gaussian process noise to car state
        
        Noise magnitude scales with:
        - Driver inconsistency: (1 - consistency)
        - Time step: sqrt(dt) for proper diffusion scaling
        
        Args:
            car: Car state to add noise to
            driver_consistency: Driver skill (0=erratic, 1=perfect)
            dt: Time step duration
        """
        # Inconsistency factor (higher = more noise)
        inconsistency = (1.0 - driver_consistency)
        scale = np.sqrt(dt)  # Proper Brownian motion scaling
        
        # Velocity noise (measurement + execution uncertainty)
        # ε_v ~ N(0, σ_v² * inconsistency)
        velocity_noise_x = self.rng.normal(
            0, self.sigma_velocity * inconsistency * scale
        )
        velocity_noise_y = self.rng.normal(
            0, self.sigma_velocity * inconsistency * scale * 0.5
        )
        
        car.velocity_x += velocity_noise_x
        car.velocity_y += velocity_noise_y
        
        # Position drift (GPS/sensor uncertainty)
        position_noise_x = self.rng.normal(
            0, self.sigma_position * scale
        )
        car.position_x += position_noise_x
        
        # Acceleration noise (power delivery variance)
        accel_noise = self.rng.normal(
            0, self.sigma_acceleration * inconsistency * scale
        )
        car.acceleration += accel_noise
        
        # Thermal fluctuations
        tire_temp_noise = self.rng.normal(
            0, self.sigma_tire_temp * scale
        )
        battery_temp_noise = self.rng.normal(
            0, self.sigma_battery_temp * scale
        )
        
        car.tire_temperature += tire_temp_noise
        car.battery_temperature += battery_temp_noise
        
        # Clamp physical limits
        car.velocity_x = np.clip(car.velocity_x, 0.0, PhysicsConfig.MAX_SPEED_MS)
        car.velocity_y = np.clip(car.velocity_y, -20.0, 20.0)
        car.tire_temperature = np.clip(
            car.tire_temperature, 
            PhysicsConfig.TIRE_MIN_TEMP, 
            PhysicsConfig.TIRE_MAX_TEMP + 10
        )
        car.battery_temperature = np.clip(
            car.battery_temperature,
            PhysicsConfig.BATTERY_TEMP_MIN,
            PhysicsConfig.BATTERY_TEMP_MAX + 5
        )
    
    def apply_control_noise(
        self,
        throttle: float,
        brake: float,
        steering: float,
        driver_consistency: float = 1.0
    ) -> Tuple[float, float, float]:
        """
        Add execution noise to control inputs (driver imperfection)
        
        Models the difference between intended and actual control inputs
        
        Args:
            throttle: Intended throttle (0-1)
            brake: Intended brake (0-1)
            steering: Intended steering angle (radians)
            driver_consistency: Driver precision (0-1)
            
        Returns:
            (noisy_throttle, noisy_brake, noisy_steering)
        """
        inconsistency = (1.0 - driver_consistency)
        
        # Control input jitter
        throttle_noise = self.rng.normal(0, self.sigma_control * inconsistency)
        brake_noise = self.rng.normal(0, self.sigma_control * inconsistency)
        steering_noise = self.rng.normal(0, self.sigma_steering * inconsistency)
        
        noisy_throttle = np.clip(throttle + throttle_noise, 0.0, 1.0)
        noisy_brake = np.clip(brake + brake_noise, 0.0, 1.0)
        noisy_steering = np.clip(
            steering + steering_noise,
            -PhysicsConfig.MAX_STEERING_ANGLE if hasattr(PhysicsConfig, 'MAX_STEERING_ANGLE') else -0.5,
            PhysicsConfig.MAX_STEERING_ANGLE if hasattr(PhysicsConfig, 'MAX_STEERING_ANGLE') else 0.5
        )
        
        return noisy_throttle, noisy_brake, noisy_steering
    
    def apply_tire_degradation_noise(
        self,
        base_degradation: float,
        tire_temperature: float
    ) -> float:
        """
        Add stochastic component to tire degradation
        
        Captures unpredictable wear patterns and compound inconsistencies
        
        Args:
            base_degradation: Deterministic degradation value
            tire_temperature: Current tire temperature
            
        Returns:
            Noisy degradation value
        """
        # Temperature affects noise magnitude (hot tires = more variance)
        temp_factor = 1.0 + (tire_temperature - 70.0) / 100.0
        noise = self.rng.normal(0, base_degradation * 0.15 * temp_factor)
        
        return max(0.0, base_degradation + noise)
    
    def apply_energy_consumption_noise(
        self,
        base_consumption: float,
        battery_temperature: float
    ) -> float:
        """
        Add stochastic variation to energy consumption
        
        Models battery efficiency variations with temperature
        
        Args:
            base_consumption: Deterministic energy consumption (Joules)
            battery_temperature: Current battery temperature
            
        Returns:
            Noisy consumption value
        """
        # Temperature affects efficiency (optimal ~40°C)
        temp_deviation = abs(battery_temperature - 40.0)
        noise_scale = 0.02 + temp_deviation * 0.001
        
        noise = self.rng.normal(0, base_consumption * noise_scale)
        return max(0.0, base_consumption + noise)


class StochasticEventModel:
    """
    Enhanced event probability model with time-varying hazard rates
    
    Uses:
    - Weibull distribution for mechanical failures (increasing hazard)
    - Poisson process for random incidents
    - Markov chain for weather transitions
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.RandomState(seed)
    
    def mechanical_failure_probability(
        self,
        component_age: float,
        stress_level: float,
        shape_param: float = 2.0,
        scale_param: float = 3600.0
    ) -> float:
        """
        Weibull hazard function for component failures
        
        h(t) = (k/λ) * (t/λ)^(k-1)
        
        Args:
            component_age: Time in use (seconds)
            stress_level: Normalized stress (0-1)
            shape_param: k > 1 for increasing failure rate
            scale_param: λ characteristic lifetime
            
        Returns:
            Failure probability for this timestep
        """
        # Stress accelerates aging
        effective_age = component_age * (1.0 + stress_level)
        
        # Weibull hazard rate
        if effective_age <= 0:
            return 0.0
        
        hazard = (shape_param / scale_param) * \
                 (effective_age / scale_param) ** (shape_param - 1)
        
        return min(hazard * 0.01, 0.01)  # Convert to per-timestep probability
    
    def poisson_event_check(
        self,
        lambda_rate: float,
        dt: float
    ) -> bool:
        """
        Check if Poisson event occurs in time interval dt
        
        P(event in dt) = 1 - exp(-λ * dt)
        
        Args:
            lambda_rate: Event rate (events per second)
            dt: Time interval
            
        Returns:
            True if event occurs
        """
        prob = 1.0 - np.exp(-lambda_rate * dt)
        return self.rng.random() < prob
