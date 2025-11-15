"""
Physics models for Formula E race simulation
Implements all mathematical equations for motion, energy, and tire dynamics
"""

import numpy as np
from typing import Tuple, Optional
from .config import PhysicsConfig, TrackConfig
from .state import CarState


class MotionModel:
    """
    2D kinematic equations with realistic constraints
    Implements vehicle dynamics and motion physics
    """
    
    @staticmethod
    def update_motion(
        car: CarState,
        dt: float,
        throttle_input: float,
        brake_input: float,
        track_config: TrackConfig
    ) -> Tuple[float, float, float, float]:
        """
        Update car position and velocity using physics
        
        Args:
            car: Current car state
            dt: Timestep (seconds)
            throttle_input: Throttle position (0-1)
            brake_input: Brake position (0-1)
            track_config: Track configuration
            
        Returns:
            (new_position_x, new_velocity_x, acceleration, energy_consumed)
        """
        # Get current track segment
        segment, _ = track_config.get_segment_at_distance(car.lap_distance)
        
        # Calculate maximum speed for current segment
        max_speed_segment = track_config.calculate_max_corner_speed(
            segment.radius,
            car.grip_coefficient * segment.grip_level
        )
        
        # Apply attack mode boost
        if car.attack_mode_active:
            max_speed_segment *= PhysicsConfig.ATTACK_MODE_SPEED_BOOST
        
        # Current speed
        current_speed = car.get_speed()
        
        # Determine target acceleration
        if brake_input > 0.1:
            # Braking
            target_acceleration = -PhysicsConfig.MAX_DECELERATION * brake_input
        elif throttle_input > 0.1:
            # Accelerating
            # Check if we're below max speed
            speed_ratio = current_speed / max_speed_segment
            
            if speed_ratio < 0.95:
                # Can accelerate
                target_acceleration = PhysicsConfig.MAX_ACCELERATION * throttle_input
                # Reduce acceleration at high speeds
                target_acceleration *= (1.0 - speed_ratio * 0.5)
            else:
                # At or above max speed, maintain
                target_acceleration = 0.0
        else:
            # Coasting - drag deceleration
            target_acceleration = -0.3  # Air resistance
        
        # Apply acceleration
        acceleration = target_acceleration
        new_velocity_x = car.velocity_x + acceleration * dt
        
        # Enforce speed limits
        new_velocity_x = np.clip(new_velocity_x, 0, max_speed_segment)
        
        # Update position
        new_position_x = car.position_x + new_velocity_x * dt
        
        # Calculate energy consumed
        energy_consumed = EnergyModel.calculate_energy_consumption(
            car.get_speed(),
            acceleration,
            dt,
            car.attack_mode_active
        )
        
        return new_position_x, new_velocity_x, acceleration, energy_consumed
    
    @staticmethod
    def calculate_optimal_speed(
        segment_type: str,
        radius: float,
        grip_coefficient: float,
        skill_factor: float
    ) -> float:
        """
        Calculate optimal speed for a segment considering driver skill
        
        Args:
            segment_type: Type of segment
            radius: Corner radius
            grip_coefficient: Current grip
            skill_factor: Driver skill multiplier
            
        Returns:
            Optimal speed (m/s)
        """
        if segment_type == 'straight':
            return PhysicsConfig.MAX_SPEED_MS * skill_factor
        else:
            # Corner speed
            g = PhysicsConfig.GRAVITY
            base_speed = np.sqrt(grip_coefficient * g * radius)
            return base_speed * skill_factor
    
    @staticmethod
    def calculate_lap_time_delta(skill_factor: float, tire_deg: float) -> float:
        """
        Calculate lap time variation based on driver and tire state
        
        Args:
            skill_factor: Driver skill (0.8-1.2)
            tire_deg: Tire degradation (0-1)
            
        Returns:
            Time delta multiplier
        """
        # Better drivers are faster
        skill_component = 2.0 - skill_factor  # 1.05 skill -> 0.95 time
        
        # Worn tires are slower
        tire_component = 1.0 + (tire_deg * 0.15)  # Up to 15% slower
        
        return skill_component * tire_component


class EnergyModel:
    """
    Battery energy management and consumption model
    """
    
    @staticmethod
    def calculate_energy_consumption(
        velocity: float,
        acceleration: float,
        dt: float,
        attack_mode: bool
    ) -> float:
        """
        Calculate energy consumed during timestep
        E_consumed = k1 * v² * dt + k2 * a * dt
        
        Args:
            velocity: Current velocity (m/s)
            acceleration: Current acceleration (m/s²)
            dt: Timestep (seconds)
            attack_mode: Whether attack mode is active
            
        Returns:
            Energy consumed (Joules, negative value)
        """
        # Velocity-dependent consumption (air resistance)
        velocity_component = PhysicsConfig.K1_VELOCITY * (velocity ** 2) * dt
        
        # Acceleration-dependent consumption (motor power)
        if acceleration > 0:
            accel_component = PhysicsConfig.K2_ACCELERATION * acceleration * dt
        else:
            accel_component = 0.0
        
        # Attack mode increases consumption
        attack_multiplier = 1.3 if attack_mode else 1.0
        
        total_consumption = (velocity_component + accel_component) * attack_multiplier
        
        return -total_consumption  # Negative because it's consumption
    
    @staticmethod
    def calculate_regenerative_braking(
        velocity_before: float,
        velocity_after: float,
        car_mass: float = 900.0  # kg (approximate Formula E car mass)
    ) -> float:
        """
        Calculate energy regenerated during braking
        E_regen = efficiency * ΔKE
        
        Args:
            velocity_before: Velocity before braking (m/s)
            velocity_after: Velocity after braking (m/s)
            car_mass: Vehicle mass (kg)
            
        Returns:
            Energy regenerated (Joules, positive value)
        """
        if velocity_after >= velocity_before:
            return 0.0
        
        # Kinetic energy lost
        ke_before = 0.5 * car_mass * (velocity_before ** 2)
        ke_after = 0.5 * car_mass * (velocity_after ** 2)
        ke_lost = ke_before - ke_after
        
        # Apply regeneration efficiency
        energy_regen = PhysicsConfig.REGEN_EFFICIENCY * ke_lost
        
        return energy_regen
    
    @staticmethod
    def predict_energy_to_finish(
        current_lap: int,
        total_laps: int,
        energy_remaining: float,
        avg_energy_per_lap: float
    ) -> Tuple[float, bool]:
        """
        Predict if car has enough energy to finish race
        
        Args:
            current_lap: Current lap number
            total_laps: Total race laps
            energy_remaining: Current battery energy (Joules)
            avg_energy_per_lap: Average energy consumption per lap
            
        Returns:
            (predicted_finish_energy_percentage, can_finish)
        """
        laps_remaining = total_laps - current_lap
        energy_needed = avg_energy_per_lap * laps_remaining
        
        predicted_finish = energy_remaining - energy_needed
        predicted_percentage = (predicted_finish / PhysicsConfig.BATTERY_CAPACITY_J) * 100
        
        can_finish = predicted_finish > 0
        
        return predicted_percentage, can_finish


class TireModel:
    """
    Tire degradation and grip model
    """
    
    @staticmethod
    def calculate_degradation_rate(
        velocity: float,
        temperature: float,
        aggression: float
    ) -> float:
        """
        Calculate tire degradation rate
        dD/dt = k_base + k_temp * (T - T_optimal)² + k_speed * v²
        
        Args:
            velocity: Current velocity (m/s)
            temperature: Tire temperature (Celsius)
            aggression: Driver aggression factor (0-1)
            
        Returns:
            Degradation rate per second
        """
        # Base degradation
        base = PhysicsConfig.TIRE_K_BASE
        
        # Temperature-dependent component
        temp_diff = temperature - PhysicsConfig.TIRE_OPTIMAL_TEMP
        temp_component = PhysicsConfig.TIRE_K_TEMP * (temp_diff ** 2)
        
        # Speed-dependent component
        speed_component = PhysicsConfig.TIRE_K_SPEED * (velocity ** 2)
        
        # Aggression multiplier
        aggression_multiplier = 1.0 + (aggression * 0.5)
        
        total_rate = (base + temp_component + speed_component) * aggression_multiplier
        
        return total_rate
    
    @staticmethod
    def calculate_grip_coefficient(degradation: float) -> float:
        """
        Calculate current grip coefficient based on degradation
        μ(t) = μ_max * (1 - factor * D(t))
        
        Args:
            degradation: Tire degradation level (0-1)
            
        Returns:
            Current grip coefficient
        """
        mu_current = PhysicsConfig.MU_MAX * (
            1.0 - PhysicsConfig.MU_DEGRADATION_FACTOR * degradation
        )
        
        return np.clip(mu_current, 0.3, PhysicsConfig.MU_MAX)
    
    @staticmethod
    def update_tire_state(
        car: CarState,
        dt: float,
        aggression: float
    ):
        """
        Update tire degradation and grip in-place
        
        Args:
            car: Car state to update
            dt: Timestep (seconds)
            aggression: Driver aggression factor
        """
        # Calculate degradation rate
        deg_rate = TireModel.calculate_degradation_rate(
            car.get_speed(),
            car.battery_temperature,  # Using battery temp as proxy
            aggression
        )
        
        # Update degradation
        car.tire_degradation += deg_rate * dt
        car.tire_degradation = np.clip(car.tire_degradation, 0.0, 1.0)
        
        # Update grip coefficient
        car.grip_coefficient = TireModel.calculate_grip_coefficient(
            car.tire_degradation
        )


class TemperatureModel:
    """
    Battery and component temperature model
    """
    
    @staticmethod
    def update_battery_temperature(
        car: CarState,
        energy_consumed: float,
        dt: float,
        ambient_temp: float = None
    ):
        """
        Update battery temperature based on energy usage
        
        Args:
            car: Car state to update
            energy_consumed: Energy consumed in timestep (Joules)
            dt: Timestep (seconds)
            ambient_temp: Ambient temperature (Celsius)
        """
        if ambient_temp is None:
            ambient_temp = PhysicsConfig.AMBIENT_TEMP
        
        # Heating from energy consumption
        heat_generated = abs(energy_consumed) * PhysicsConfig.BATTERY_HEAT_RATE
        temp_increase = heat_generated / 1000.0  # Simplified heat capacity
        
        # Cooling towards ambient
        temp_diff = car.battery_temperature - ambient_temp
        cooling = temp_diff * PhysicsConfig.BATTERY_COOLING_RATE * dt
        
        # Update temperature
        car.battery_temperature += temp_increase - cooling
        
        # Clamp to reasonable range
        car.battery_temperature = np.clip(car.battery_temperature, 20.0, 100.0)
    
    @staticmethod
    def get_temperature_efficiency_factor(temperature: float) -> float:
        """
        Calculate efficiency factor based on temperature
        Optimal at 40°C, decreases as temperature deviates
        
        Args:
            temperature: Battery temperature (Celsius)
            
        Returns:
            Efficiency factor (0.8-1.0)
        """
        optimal = PhysicsConfig.OPTIMAL_BATTERY_TEMP
        deviation = abs(temperature - optimal)
        
        # Efficiency decreases by 1% per 10°C deviation
        efficiency = 1.0 - (deviation / 100.0)
        
        return np.clip(efficiency, 0.8, 1.0)


class PhysicsEngine:
    """
    Main physics engine that orchestrates all physics updates
    """
    
    def __init__(self, track_config: TrackConfig):
        self.track_config = track_config
    
    def update_car_physics(
        self,
        car: CarState,
        dt: float,
        throttle: float,
        brake: float,
        driver_skill: float,
        driver_aggression: float
    ):
        """
        Update all physics for a single car
        
        Args:
            car: Car state to update
            dt: Timestep (seconds)
            throttle: Throttle input (0-1)
            brake: Brake input (0-1)
            driver_skill: Driver skill factor
            driver_aggression: Driver aggression factor
        """
        if not car.is_active:
            return
        
        # Store previous velocity for regen calculation
        velocity_before = car.get_speed()
        
        # Update motion
        new_pos_x, new_vel_x, accel, energy_consumed = MotionModel.update_motion(
            car, dt, throttle, brake, self.track_config
        )
        
        # Apply updates
        car.position_x = new_pos_x
        car.velocity_x = new_vel_x
        car.acceleration = accel
        car.throttle = throttle
        car.brake = brake
        
        # Update distance tracking
        distance_delta = new_vel_x * dt
        car.lap_distance += distance_delta
        car.total_distance += distance_delta
        
        # Check for lap completion
        if car.lap_distance >= self.track_config.total_length:
            car.current_lap += 1
            car.lap_distance -= self.track_config.total_length
            
            # Record lap time (simplified)
            if car.time > 0:
                lap_time = 90.0  # Approximate, would need proper timing
                car.last_lap_time = lap_time
                if lap_time < car.best_lap_time:
                    car.best_lap_time = lap_time
        
        # Update max speed
        current_speed = car.get_speed()
        if current_speed > car.max_speed_achieved:
            car.max_speed_achieved = current_speed
        
        # Calculate regenerative braking
        velocity_after = car.get_speed()
        if velocity_after < velocity_before:
            energy_regen = EnergyModel.calculate_regenerative_braking(
                velocity_before, velocity_after
            )
            car.update_battery(energy_regen)
        
        # Update battery
        car.update_battery(energy_consumed)
        
        # Update temperature
        TemperatureModel.update_battery_temperature(car, energy_consumed, dt)
        
        # Update tires
        TireModel.update_tire_state(car, dt, driver_aggression)
        
        # Update attack mode timer
        car.update_attack_mode(dt)
        
        # Update time
        car.time += dt
        
        # Check if out of energy
        if car.battery_percentage < 1.0:
            car.is_active = False
    
    def update_all_cars(
        self,
        cars: list,
        dt: float,
        driver_configs: list,
        control_inputs: Optional[dict] = None
    ):
        """
        Update physics for all cars using vectorization
        
        Args:
            cars: List of car states
            dt: Timestep (seconds)
            driver_configs: List of driver configuration dicts
            control_inputs: Optional dict of {car_id: (throttle, brake)}
        """
        for i, car in enumerate(cars):
            if not car.is_active:
                continue
            
            # Get driver config
            driver = driver_configs[i] if i < len(driver_configs) else {
                'skill': 1.0,
                'aggression': 0.7
            }
            
            # Get control inputs (or use simple AI)
            if control_inputs and car.car_id in control_inputs:
                throttle, brake = control_inputs[car.car_id]
            else:
                # Simple AI: accelerate or brake based on segment
                segment, _ = self.track_config.get_segment_at_distance(car.lap_distance)
                max_speed = self.track_config.calculate_max_corner_speed(
                    segment.radius, car.grip_coefficient
                )
                
                current_speed = car.get_speed()
                if current_speed < max_speed * 0.9:
                    throttle = 0.8
                    brake = 0.0
                elif current_speed > max_speed * 1.05:
                    throttle = 0.0
                    brake = 0.6
                else:
                    throttle = 0.3
                    brake = 0.0
            
            # Update car physics
            self.update_car_physics(
                car, dt, throttle, brake,
                driver['skill'], driver['aggression']
            )
