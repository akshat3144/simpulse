"""
Comprehensive Physics Engine for Formula E Simulation
Implements SimPulse stochastic dynamics framework

Mathematical Foundation (SimPulse):
    State Evolution: x(t+1) = f(x(t), u(t), θ(t)) + ε(t)
    
    Where:
        x(t) ∈ ℝⁿ: State vector (velocity, position, energy, temperature, tire condition)
        u(t) ∈ ℝᵐ: Control vector (throttle, brake, steering, attack mode)
        θ(t) ∈ ℝᵏ: Environmental parameters (weather, track grip, temperature)
        ε(t) ~ N(0, Σ): Gaussian process noise (driver inconsistency, measurement error)
        f(): Deterministic physics transition function
    
    Performance Index:
        P_i(t) = w₁·v(t) + w₂·a(t) + w₃·e(t) + w₄·τ(t) + w₅·ψ(t)
        
        Components:
            v(t): Velocity factor
            a(t): Acceleration capability
            e(t): Energy efficiency
            τ(t): Tire condition
            ψ(t): Strategy parameter (aggression vs conservation)

Realistic driver controls, corner handling, and physics-based motion
Integrates stochastic noise for realistic uncertainty
"""

import numpy as np
from typing import Tuple
from .config import PhysicsConfig, TrackConfig, WeatherConditions, CarConfiguration
from .state import CarState

try:
    from .stochastic_dynamics import StochasticNoiseModel
    STOCHASTIC_AVAILABLE = True
except ImportError:
    STOCHASTIC_AVAILABLE = False


class DriverController:
    """
    Realistic driver behavior without ML/AI
    Makes decisions based on track conditions, race situation, and driver characteristics
    """
    
    @staticmethod
    def calculate_controls(
        car: CarState,
        segment,
        track_config: TrackConfig,
        driver_skill: float,
        driver_aggression: float,
        driver_consistency: float,
        race_position: int,
        gap_to_ahead: float,
        gap_to_leader: float,
        laps_remaining: int,
        in_attack_zone: bool,
        weather: WeatherConditions
    ) -> Tuple[float, float, float, bool]:
        """
        Calculate throttle, brake, steering, and attack mode decision
        
        Returns:
            (throttle, brake, steering_angle, activate_attack_mode)
        """
        current_speed = car.get_speed()
        
        # Look ahead for corners to enable early braking
        lookahead_distance = current_speed * 2.0  # Look 2 seconds ahead
        future_distance = (car.lap_distance + lookahead_distance) % track_config.total_length
        next_segment, _ = track_config.get_segment_at_distance(future_distance)
        
        # If approaching a corner from a straight, use next segment's target speed
        if segment.segment_type == 'straight' and next_segment.segment_type != 'straight':
            # Use the corner's target speed to start braking early
            target_segment = next_segment
        else:
            # Use current segment's target speed
            target_segment = segment
        
        # Calculate target speed for the relevant segment
        target_speed = DriverController._calculate_target_speed(
            car, target_segment, driver_skill, driver_aggression,
            race_position, gap_to_ahead, weather
        )
        
        # Calculate steering angle needed for current segment
        steering = DriverController._calculate_steering(
            car, segment, driver_skill, driver_consistency
        )
        
        # Calculate throttle and brake
        throttle, brake = DriverController._calculate_throttle_brake(
            current_speed, target_speed, segment, driver_skill, driver_aggression
        )
        
        # Decide on attack mode
        activate_attack = DriverController._decide_attack_mode(
            car, race_position, gap_to_ahead, gap_to_leader,
            laps_remaining, in_attack_zone, driver_aggression
        )
        
        return throttle, brake, steering, activate_attack
    
    @staticmethod
    def _calculate_target_speed(
        car: CarState,
        segment,
        driver_skill: float,
        driver_aggression: float,
        race_position: int,
        gap_to_ahead: float,
        weather: WeatherConditions
    ) -> float:
        """Calculate target speed based on segment and conditions"""
        
        # Base max speed for segment (simplified corner speed calculation)
        if segment.radius == np.inf:
            # Straight
            base_speed = PhysicsConfig.MAX_SPEED_MS
        else:
            # Corner: v = sqrt(μ * g * r) with realistic Formula E limits
            g = PhysicsConfig.GRAVITY
            mu = car.grip_coefficient * segment.grip_level
            
            # Add banking contribution (conservative)
            if segment.banking_angle > 0:
                mu *= (1.0 + np.tan(np.radians(segment.banking_angle)) * 0.3)
            
            # Realistic downforce contribution (Formula E has moderate downforce)
            # Limit to 5% boost maximum to keep speeds realistic for street circuits
            speed_factor = min(car.get_speed() / 80.0, 1.0)
            downforce_factor = 1.0 + (speed_factor * 0.05)  # Up to 5% more grip
            mu *= downforce_factor
            
            base_speed = np.sqrt(mu * g * segment.radius)
            base_speed = min(base_speed, PhysicsConfig.MAX_SPEED_MS)
        
        # Attack mode boost (only on straights, minimal in corners)
        if car.attack_mode_active:
            if segment.radius == np.inf:
                base_speed *= PhysicsConfig.ATTACK_MODE_SPEED_BOOST
            else:
                # Much smaller boost in corners (only ~2%)
                base_speed *= 1.02
        
        # Driver skill factor (realistic range: 95-105%)
        skill_multiplier = 0.95 + (driver_skill - 0.95) * 0.5  # Compress to 0.95-1.05 range
        skilled_speed = base_speed * skill_multiplier
        
        # Aggression factor (how close to limit) - realistic 92-98%
        aggression_factor = 0.92 + (driver_aggression * 0.06)  # 92-98% of limit
        
        # Race situation adjustments
        if gap_to_ahead < 1.5 and race_position > 1:
            # Pushing to overtake
            aggression_factor = min(1.0, aggression_factor + 0.05)
        elif race_position == 1 and gap_to_ahead > 5.0:
            # Leading comfortably, conserve
            aggression_factor *= 0.95
        
        # Energy management
        if car.battery_percentage < 15.0:
            aggression_factor *= 0.92  # Slow down when low on energy
        
        # Tire management
        if car.tire_degradation > 0.7:
            aggression_factor *= 0.95  # Preserve worn tires
        
        # Weather
        if weather.rain_intensity > 0:
            rain_factor = 1.0 - (weather.rain_intensity * 0.20)
            aggression_factor *= rain_factor
        
        target = skilled_speed * aggression_factor
        return min(target, PhysicsConfig.MAX_SPEED_MS)
    
    @staticmethod
    def _calculate_steering(
        car: CarState,
        segment,
        driver_skill: float,
        driver_consistency: float
    ) -> float:
        """Calculate steering angle for current segment"""
        
        if segment.segment_type == 'straight':
            # Small corrections only
            base_steering = 0.0
            noise = (1.0 - driver_consistency) * 0.01
        else:
            # Calculate required steering for corner
            # δ = arctan(L / R)
            L = PhysicsConfig.WHEELBASE
            R = segment.radius
            
            if R > 0 and R < 10000:
                base_steering = np.arctan(L / R)
            else:
                base_steering = 0.0
            
            # Direction
            if segment.segment_type == 'left_corner':
                base_steering = -base_steering
            elif segment.segment_type == 'chicane':
                # Alternate in chicane
                base_steering *= np.sin(car.lap_distance / 10.0)
            
            # Skill affects precision
            noise = (1.0 - driver_skill) * 0.03
        
        # Add stochastic variation
        steering = base_steering + np.random.randn() * noise
        
        # Limit to physical maximum
        max_steer = 0.52  # ~30 degrees
        return np.clip(steering, -max_steer, max_steer)
    
    @staticmethod
    def _calculate_throttle_brake(
        current_speed: float,
        target_speed: float,
        segment,
        driver_skill: float,
        driver_aggression: float
    ) -> Tuple[float, float]:
        """Calculate throttle and brake inputs"""
        
        speed_error = target_speed - current_speed
        deadband = 1.0  # m/s (tighter control)
        
        if speed_error > deadband:
            # Accelerate
            throttle = min(speed_error / 15.0, 1.0) * (0.7 + driver_aggression * 0.3)
            
            # Reduce throttle mid-corner
            if segment.segment_type != 'straight':
                throttle *= 0.5  # Much more cautious in corners
            
            brake = 0.0
            
        elif speed_error < -deadband:
            # Brake - need much stronger braking for corners
            speed_diff = abs(speed_error)
            
            # If approaching corner (not straight) and speed too high, brake harder
            if segment.segment_type != 'straight':
                # Very aggressive braking for corners - full brake if way over speed
                brake = min(speed_diff / 8.0, 1.0)  # Even more aggressive
                brake = max(brake, 0.8)  # Minimum 80% brake in corners when over speed
            else:
                # Normal braking on straights
                brake = min(speed_diff / 15.0, 1.0) * (0.6 + driver_aggression * 0.4)
            
            throttle = 0.0
            
        else:
            # Maintenance
            if segment.segment_type == 'straight':
                throttle = 0.4
            else:
                throttle = 0.15  # Very light throttle in corners
            brake = 0.0
        
        return np.clip(throttle, 0.0, 1.0), np.clip(brake, 0.0, 1.0)
    
    @staticmethod
    def _decide_attack_mode(
        car: CarState,
        race_position: int,
        gap_to_ahead: float,
        gap_to_leader: float,
        laps_remaining: int,
        in_attack_zone: bool,
        driver_aggression: float
    ) -> bool:
        """Decide whether to activate attack mode"""
        
        if not in_attack_zone or car.attack_mode_uses_left == 0 or car.attack_mode_active:
            return False
        
        # Strategy: Use when close to overtaking opportunity
        if gap_to_ahead < 2.0 and race_position > 1:
            if np.random.random() < (0.6 + driver_aggression * 0.3):
                return True
        
        # Use in final laps
        if laps_remaining <= 3:
            if np.random.random() < 0.5:
                return True
        
        # Use mid-race if both available
        total_laps = car.current_lap + laps_remaining
        if 0.4 < (car.current_lap / total_laps) < 0.6:
            if car.attack_mode_uses_left == 2 and np.random.random() < 0.3:
                return True
        
        return False


class PhysicsEngine:
    """
    Main physics engine with realistic motion model
    
    Implements SimPulse deterministic dynamics f(x,u,θ) plus stochastic noise ε(t)
    """
    
    def __init__(self, track_config: TrackConfig, enable_stochastic: bool = True, noise_seed: int = None):
        self.track_config = track_config
        self.weather = WeatherConditions()
        self.enable_stochastic = enable_stochastic
        
        # Initialize stochastic noise model
        if enable_stochastic and STOCHASTIC_AVAILABLE:
            self.noise_model = StochasticNoiseModel(seed=noise_seed)
        else:
            self.noise_model = None
    
    def update_car_physics(
        self,
        car: CarState,
        dt: float,
        driver_config: dict,
        race_position: int,
        gap_to_ahead: float,
        laps_remaining: int,
        config: CarConfiguration = None,
        stochastic_seed: int = None
    ):
        """
        Update car physics for one timestep
        
        SimPulse State Transition: x(t+1) = f(x(t), u(t), θ(t)) + ε(t)
        
        Steps:
            1. Calculate control inputs u(t) from driver model
            2. Apply deterministic physics f(x,u,θ)
            3. Add stochastic noise ε(t) ~ N(0, Σ)
            4. Update auxiliary states (battery, tires, temperature)
        
        Args:
            car: Car state to update (x(t))
            dt: Timestep duration (seconds)
            driver_config: Dict with 'skill', 'aggression', 'consistency'
            race_position: Current position in race
            gap_to_ahead: Gap to car ahead (seconds)
            laps_remaining: Laps remaining in race
            config: Car configuration (optional)
            stochastic_seed: Random seed (optional)
        """
        if not car.is_active:
            return
        
        # Set random seed for reproducibility
        if stochastic_seed is not None:
            np.random.seed(stochastic_seed + car.car_id + int(car.time * 100))
        
        # Get driver characteristics
        driver_skill = driver_config.get('skill', 1.0)
        driver_aggression = driver_config.get('aggression', 0.7)
        driver_consistency = driver_config.get('consistency', 0.9)
        
        # Get current track segment
        segment, local_dist = self.track_config.get_segment_at_distance(car.lap_distance)
        
        # Check if in attack mode zone
        in_attack_zone = any(
            zone[0] <= car.lap_distance < zone[1]
            for zone in self.track_config.attack_mode_zones
        )
        
        # Get control inputs from driver model (u(t) in MDP formulation)
        throttle, brake, steering, activate_attack = DriverController.calculate_controls(
            car, segment, self.track_config, driver_skill, driver_aggression,
            driver_consistency, race_position, gap_to_ahead, car.gap_to_leader,
            laps_remaining, in_attack_zone, self.weather
        )
        
        # Apply control noise from driver imperfection (part of ε(t))
        if self.noise_model is not None:
            throttle, brake, steering = self.noise_model.apply_control_noise(
                throttle, brake, steering, driver_consistency
            )
        
        # Activate attack mode if decided
        if activate_attack:
            car.activate_attack_mode()
        
        # Calculate forces and motion
        current_speed = car.get_speed()
        m = PhysicsConfig.TOTAL_MASS
        
        # === LONGITUDINAL MOTION ===
        
        # Motor force
        if throttle > 0 and brake == 0:
            # Power available
            if car.attack_mode_active:
                power = (PhysicsConfig.MAX_POWER_KW + PhysicsConfig.ATTACK_MODE_POWER_BOOST_KW) * 1000
            else:
                power = PhysicsConfig.MAX_POWER_KW * 1000
            
            # Apply config efficiency
            if config:
                power *= config.power_efficiency
            
            # Apply throttle and motor efficiency
            power = power * throttle * PhysicsConfig.MOTOR_EFFICIENCY
            
            # Battery derating at low SOC
            if car.battery_percentage < 10.0:
                power *= (car.battery_percentage / 10.0)
            
            # Force = Power / velocity (avoid divide by zero)
            velocity_safe = max(current_speed, 1.0)
            F_motor = power / velocity_safe
        else:
            F_motor = 0.0
        
        # Drag force: F_drag = 0.5 * ρ * Cd * A * v²
        Cd = PhysicsConfig.DRAG_COEFFICIENT
        if config:
            Cd *= config.aero_efficiency
        A = PhysicsConfig.FRONTAL_AREA
        rho = PhysicsConfig.AIR_DENSITY
        F_drag = 0.5 * rho * Cd * A * (current_speed ** 2)
        
        # Rolling resistance
        F_down = 0.5 * rho * PhysicsConfig.DOWNFORCE_COEFFICIENT * A * (current_speed ** 2)
        N = m * PhysicsConfig.GRAVITY + F_down
        F_roll = PhysicsConfig.ROLLING_RESISTANCE_COEFF * N
        
        # Brake force and regen
        if brake > 0:
            max_brake_force = m * PhysicsConfig.MAX_DECELERATION
            F_brake = max_brake_force * brake
            
            # Regenerative braking (up to 70% of braking)
            max_regen_power = PhysicsConfig.MAX_REGEN_POWER_KW * 1000
            velocity_safe = max(current_speed, 1.0)
            max_regen_force = max_regen_power / velocity_safe
            
            F_regen = min(F_brake * 0.7, max_regen_force)
            regen_power = F_regen * current_speed * PhysicsConfig.REGEN_EFFICIENCY
            
            if config:
                regen_power *= config.regen_efficiency
            
            # Can't regen if battery full
            if car.battery_percentage >= 99.9:
                regen_power = 0.0
            
            energy_regen = regen_power * dt
        else:
            F_brake = 0.0
            energy_regen = 0.0
        
        # Gradient force
        gradient_angle = np.arctan(segment.elevation_change / segment.length) if segment.length > 0 else 0
        F_gradient = m * PhysicsConfig.GRAVITY * np.sin(gradient_angle)
        
        # Net force
        F_net = F_motor - F_drag - F_roll - F_brake - F_gradient
        
        # Traction limit
        F_max_traction = car.grip_coefficient * N
        F_net = np.clip(F_net, -F_max_traction, F_max_traction)
        
        # Acceleration
        acceleration = F_net / m
        
        # Update velocity
        new_velocity_x = car.velocity_x + acceleration * dt
        new_velocity_x = np.clip(new_velocity_x, 0.0, PhysicsConfig.MAX_SPEED_MS)
        
        # CRITICAL: Enforce corner speed limit based on lateral grip
        # In corners, if speed exceeds what the tires can handle, force it down
        if segment.radius < 10000:  # If in a corner
            # Maximum safe speed for this corner: v_max = sqrt(μ * g * r)
            mu_corner = car.grip_coefficient * segment.grip_level
            max_corner_speed = np.sqrt(mu_corner * PhysicsConfig.GRAVITY * segment.radius * 1.1)  # 10% safety margin
            
            # Hard limit: cannot exceed corner speed limit
            if new_velocity_x > max_corner_speed:
                # Force speed down (simulate loss of traction / mandatory slowdown)
                new_velocity_x = max_corner_speed
        
        # Lateral velocity (simplified - from steering)
        # a_lat = v² * tan(δ) / L
        if abs(steering) > 0.001:
            a_lat = (current_speed ** 2) * np.tan(steering) / PhysicsConfig.WHEELBASE
            # Limit to grip
            a_lat_max = car.grip_coefficient * PhysicsConfig.GRAVITY
            a_lat = np.clip(a_lat, -a_lat_max, a_lat_max)
            new_velocity_y = car.velocity_y + a_lat * dt
            new_velocity_y = np.clip(new_velocity_y, -20.0, 20.0)
        else:
            new_velocity_y = car.velocity_y * 0.9  # Decay lateral velocity
            a_lat = 0.0
        
        # Energy consumption
        if F_motor > 0:
            motor_power = F_motor * current_speed / PhysicsConfig.MOTOR_EFFICIENCY
            energy_consumed = motor_power * dt
        else:
            energy_consumed = 0.0
        
        # Update car state
        car.velocity_x = new_velocity_x
        car.velocity_y = new_velocity_y
        car.acceleration = acceleration
        car.throttle = throttle
        car.brake = brake
        car.steering_angle = steering
        
        # Update position along track
        distance_delta = car.get_speed() * dt
        
        # Ensure distance only increases (never decreases)
        if distance_delta > 0:
            car.lap_distance += distance_delta
            car.total_distance += distance_delta
        
        # Calculate 2D position from track distance using proper track geometry
        cumulative = 0.0
        current_x = 0.0
        current_y = 0.0
        angle = 0.0  # Track direction in radians (0 = East, increases counter-clockwise)
        
        for seg in self.track_config.segments:
            if cumulative + seg.length > car.lap_distance:
                # Car is in this segment
                local_dist = car.lap_distance - cumulative
                
                if seg.segment_type == 'straight':
                    # Straight section - move in current direction
                    current_x += local_dist * np.cos(angle)
                    current_y += local_dist * np.sin(angle)
                    
                elif seg.segment_type in ['left_corner', 'right_corner']:
                    # Corner section - use proper arc geometry
                    if seg.radius > 1.0:
                        # Calculate how much of the corner we've traversed
                        turn_direction = 1 if seg.segment_type == 'left_corner' else -1
                        
                        # Total angle swept by this corner
                        total_angle = seg.length / seg.radius  # radians
                        
                        # Angle swept so far in this corner
                        swept_angle = (local_dist / seg.length) * total_angle
                        
                        # Find center of the circular arc
                        # For left turn: center is 90° left of current direction
                        # For right turn: center is 90° right of current direction
                        center_offset_angle = angle + (np.pi / 2) * turn_direction
                        center_x = current_x + seg.radius * np.cos(center_offset_angle)
                        center_y = current_y + seg.radius * np.sin(center_offset_angle)
                        
                        # New angle after partial turn
                        new_angle = angle + swept_angle * turn_direction
                        
                        # Calculate new position on arc from center
                        from_center_angle = center_offset_angle + np.pi  # Start 180° from center offset
                        from_center_angle += swept_angle * turn_direction
                        
                        current_x = center_x + seg.radius * np.cos(from_center_angle)
                        current_y = center_y + seg.radius * np.sin(from_center_angle)
                        
                        # Update angle for next segment
                        angle = new_angle
                    else:
                        # Very tight corner or invalid radius - treat as straight
                        current_x += local_dist * np.cos(angle)
                        current_y += local_dist * np.sin(angle)
                        
                elif seg.segment_type == 'chicane':
                    # Chicane - approximate as straight with lateral oscillation
                    forward_dist = local_dist * np.cos(angle)
                    lateral_offset = 10.0 * np.sin(2.0 * np.pi * local_dist / seg.length)
                    
                    current_x += forward_dist - lateral_offset * np.sin(angle)
                    current_y += local_dist * np.sin(angle) + lateral_offset * np.cos(angle)
                
                break
            else:
                # Process full segment to update position and angle
                if seg.segment_type == 'straight':
                    current_x += seg.length * np.cos(angle)
                    current_y += seg.length * np.sin(angle)
                    # Angle stays the same
                    
                elif seg.segment_type in ['left_corner', 'right_corner']:
                    if seg.radius > 1.0:
                        turn_direction = 1 if seg.segment_type == 'left_corner' else -1
                        total_angle = seg.length / seg.radius
                        
                        # Find arc center
                        center_offset_angle = angle + (np.pi / 2) * turn_direction
                        center_x = current_x + seg.radius * np.cos(center_offset_angle)
                        center_y = current_y + seg.radius * np.sin(center_offset_angle)
                        
                        # Update angle for full corner
                        angle += total_angle * turn_direction
                        
                        # Calculate end position
                        from_center_angle = center_offset_angle + np.pi + total_angle * turn_direction
                        current_x = center_x + seg.radius * np.cos(from_center_angle)
                        current_y = center_y + seg.radius * np.sin(from_center_angle)
                    else:
                        current_x += seg.length * np.cos(angle)
                        current_y += seg.length * np.sin(angle)
                        
                elif seg.segment_type == 'chicane':
                    # Full chicane - treat as straight
                    current_x += seg.length * np.cos(angle)
                    current_y += seg.length * np.sin(angle)
                
                cumulative += seg.length
        
        car.position_x = current_x
        car.position_y = current_y
        
        # Check lap completion
        if car.lap_distance >= self.track_config.total_length:
            car.current_lap += 1
            car.lap_distance -= self.track_config.total_length
            
            # Record lap time (if we have a valid lap start time)
            if car.current_lap > 1 and car.time > 0:  # Skip lap 0 (formation lap)
                lap_time = car.time - car.sector_start_time
                car.last_lap_time = lap_time
                
                # Update best lap time
                if lap_time < car.best_lap_time:
                    car.best_lap_time = lap_time
                
                # Reset lap timer
                car.sector_start_time = car.time
        
        # Update max speed
        if car.get_speed() > car.max_speed_achieved:
            car.max_speed_achieved = car.get_speed()
        
        # Update battery (with stochastic consumption noise)
        net_energy = energy_regen - energy_consumed
        if config:
            net_energy *= config.battery_efficiency
        
        # Apply energy consumption noise (battery efficiency variations)
        if self.noise_model is not None and energy_consumed > 0:
            noisy_consumption = self.noise_model.apply_energy_consumption_noise(
                energy_consumed, car.battery_temperature
            )
            net_energy = energy_regen - noisy_consumption
        
        car.update_battery(net_energy)
        car.battery_energy = np.clip(car.battery_energy, 0.0, PhysicsConfig.BATTERY_CAPACITY_J)
        car.battery_percentage = (car.battery_energy / PhysicsConfig.BATTERY_CAPACITY_J) * 100.0
        
        car.total_energy_consumed += energy_consumed
        car.total_energy_regenerated += energy_regen
        
        # Update tire degradation (reduced 1000x for realistic race-long wear)
        tire_deg_rate = PhysicsConfig.TIRE_K_BASE * 0.001
        tire_deg_rate += PhysicsConfig.TIRE_K_SPEED * (current_speed ** 2) * 0.001
        tire_deg_rate += PhysicsConfig.TIRE_K_LATERAL * (abs(a_lat) ** 2) * 0.001
        tire_deg_rate *= (1.0 + driver_aggression * 0.3)
        
        # Apply stochastic tire degradation noise
        if self.noise_model is not None:
            tire_deg_rate = self.noise_model.apply_tire_degradation_noise(
                tire_deg_rate, car.tire_temperature
            )
        
        car.tire_degradation += tire_deg_rate * dt
        car.tire_degradation = np.clip(car.tire_degradation, 0.0, 1.0)
        
        # Update grip based on degradation
        base_grip = PhysicsConfig.MU_MAX
        grip_loss = (base_grip - PhysicsConfig.MU_MIN) * car.tire_degradation
        car.grip_coefficient = base_grip - grip_loss
        
        # Weather effects on grip
        if self.weather.rain_intensity > 0:
            car.grip_coefficient *= (1.0 - self.weather.rain_intensity * 0.25)
        
        # Update tire temperature (simplified)
        friction_heat = abs(a_lat) * 0.5 + abs(acceleration) * 0.3
        car.tire_temperature += friction_heat * dt
        cooling = (car.tire_temperature - self.weather.temperature_air) * 0.1 * dt
        car.tire_temperature -= cooling
        car.tire_temperature = np.clip(car.tire_temperature, self.weather.temperature_air, 130.0)
        
        # Update battery temperature - increases with usage, cools when idle
        # Heat generation from power consumption (both motor and regen create heat)
        power_output = abs(energy_consumed - energy_regen) / dt if dt > 0 else 0
        heat_gen = power_output / 100000.0  # Scale factor for temperature rise
        car.battery_temperature += heat_gen * dt
        
        # Active cooling when above optimal temperature
        if car.battery_temperature > PhysicsConfig.BATTERY_OPTIMAL_TEMP:
            cooling_rate = (car.battery_temperature - PhysicsConfig.BATTERY_OPTIMAL_TEMP) * 0.8
            car.battery_temperature -= cooling_rate * dt
        
        # Passive cooling to ambient
        if car.battery_temperature > self.weather.temperature_air:
            ambient_cool = (car.battery_temperature - self.weather.temperature_air) * 0.05 * dt
            car.battery_temperature -= ambient_cool
        
        car.battery_temperature = np.clip(
            car.battery_temperature,
            PhysicsConfig.BATTERY_TEMP_MIN,
            PhysicsConfig.BATTERY_TEMP_MAX
        )
        
        # Update attack mode
        car.update_attack_mode(dt)
        
        # Update time
        car.time += dt
        
        # Apply process noise to state (final stochastic term ε(t))
        if self.noise_model is not None:
            self.noise_model.apply_process_noise(car, driver_consistency, dt)
        
        # Check if out of energy
        if car.battery_percentage < 0.5:
            car.is_active = False
    
    def set_weather(self, weather: WeatherConditions):
        """Set weather conditions"""
        self.weather = weather
