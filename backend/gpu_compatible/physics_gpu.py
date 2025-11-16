"""
GPU-Accelerated Physics Engine for Formula E Simulation
Uses CuPy for GPU matrix operations
Processes all cars in parallel using vectorized operations
"""

import numpy as np
from typing import Tuple, Optional
import sys
from pathlib import Path

# Add parent directory to path for config imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cupy as cp
    GPU_AVAILABLE = True
    xp = cp  # Use CuPy by default
except ImportError:
    GPU_AVAILABLE = False
    xp = np  # Fallback to NumPy
    cp = np  # Alias for compatibility

from config import PhysicsConfig, TrackConfig, WeatherConditions


class GPUPhysicsEngine:
    """
    Vectorized physics engine that processes all cars simultaneously on GPU
    State representation: N_cars × N_features matrices
    """
    
    def __init__(self, track_config: TrackConfig, use_gpu: bool = True):
        self.track_config = track_config
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.xp = cp if self.use_gpu else np
        
        if self.use_gpu:
            print(f"✓ GPU Physics Engine initialized on {cp.cuda.Device()}")
        else:
            print(f"⚠ GPU not available, using CPU fallback")
    
    def initialize_state_matrix(self, n_cars: int):
        """
        Initialize state matrix for all cars
        Returns: State dict with all arrays on GPU
        """
        xp = self.xp
        
        state = {
            # Position and velocity (2D)
            'position_x': xp.zeros(n_cars, dtype=xp.float32),
            'position_y': xp.zeros(n_cars, dtype=xp.float32),
            'velocity_x': xp.zeros(n_cars, dtype=xp.float32),
            'velocity_y': xp.zeros(n_cars, dtype=xp.float32),
            
            # Acceleration and forces
            'acceleration': xp.zeros(n_cars, dtype=xp.float32),
            'steering_angle': xp.zeros(n_cars, dtype=xp.float32),
            
            # Track position
            'lap_distance': xp.zeros(n_cars, dtype=xp.float32),
            'total_distance': xp.zeros(n_cars, dtype=xp.float32),
            'current_lap': xp.zeros(n_cars, dtype=xp.int32),
            
            # Controls
            'throttle': xp.zeros(n_cars, dtype=xp.float32),
            'brake': xp.zeros(n_cars, dtype=xp.float32),
            
            # Energy and battery
            'battery_energy_mj': xp.full(n_cars, PhysicsConfig.BATTERY_CAPACITY_J / 1e6, dtype=xp.float32),
            'battery_percentage': xp.full(n_cars, 100.0, dtype=xp.float32),
            'battery_temperature': xp.full(n_cars, 45.0, dtype=xp.float32),
            
            # Tires
            'tire_degradation': xp.zeros(n_cars, dtype=xp.float32),
            'tire_temperature': xp.full(n_cars, 85.0, dtype=xp.float32),
            'grip_coefficient': xp.full(n_cars, PhysicsConfig.MU_MAX, dtype=xp.float32),
            
            # Attack mode
            'attack_mode_active': xp.zeros(n_cars, dtype=xp.bool_),
            'attack_mode_timer': xp.zeros(n_cars, dtype=xp.float32),
            'attack_mode_uses_left': xp.full(n_cars, 2, dtype=xp.int32),
            
            # Race status
            'is_active': xp.ones(n_cars, dtype=xp.bool_),
            'time': xp.zeros(n_cars, dtype=xp.float32),
        }
        
        return state
    
    def calculate_controls_batch(self, state: dict, driver_configs: dict, 
                                 segment_data: dict) -> Tuple:
        """
        Calculate controls for all cars in parallel using vectorized operations
        
        Args:
            state: GPU state matrix
            driver_configs: Driver parameters (skill, aggression, etc.)
            segment_data: Current segment info for all cars
            
        Returns:
            (throttle, brake, steering) - all as GPU arrays
        """
        xp = self.xp
        n_cars = len(state['position_x'])
        
        # Get current speeds
        speeds = xp.sqrt(state['velocity_x']**2 + state['velocity_y']**2)
        
        # Calculate target speeds based on segments (vectorized)
        target_speeds = self._calculate_target_speeds_vectorized(
            state, speeds, segment_data, driver_configs
        )
        
        # Calculate throttle and brake (vectorized)
        throttle, brake = self._calculate_throttle_brake_vectorized(
            speeds, target_speeds, segment_data
        )
        
        # Calculate steering (vectorized)
        steering = self._calculate_steering_vectorized(
            state, segment_data, driver_configs
        )
        
        return throttle, brake, steering
    
    def _calculate_target_speeds_vectorized(self, state: dict, speeds, 
                                           segment_data: dict, driver_configs: dict):
        """Vectorized target speed calculation for all cars"""
        xp = self.xp
        n_cars = len(speeds)
        
        # Get segment radii for all cars
        radii = segment_data['radius']
        grip_levels = segment_data['grip_level']
        
        # Identify straights vs corners
        is_straight = radii > 10000  # inf represented as large number
        
        # Corner speed calculation: v = sqrt(mu * g * r)
        mu = state['grip_coefficient'] * grip_levels
        corner_speeds = xp.sqrt(mu * PhysicsConfig.GRAVITY * radii * 1.1)
        corner_speeds = xp.minimum(corner_speeds, PhysicsConfig.MAX_SPEED_MS)
        
        # Use straight speed for straights, corner speed for corners
        base_speeds = xp.where(
            is_straight,
            PhysicsConfig.MAX_SPEED_MS,
            corner_speeds
        )
        
        # Apply driver skill multiplier (vectorized)
        skills = xp.array([driver_configs[i]['skill'] for i in range(n_cars)], dtype=xp.float32)
        skill_multiplier = 0.95 + (skills - 0.95) * 0.5
        skilled_speeds = base_speeds * skill_multiplier
        
        # Apply aggression factor (vectorized)
        aggressions = xp.array([driver_configs[i]['aggression'] for i in range(n_cars)], dtype=xp.float32)
        aggression_factor = 0.92 + aggressions * 0.06
        target_speeds = skilled_speeds * aggression_factor
        
        # Apply attack mode boost
        attack_boost = xp.where(
            state['attack_mode_active'],
            PhysicsConfig.ATTACK_MODE_SPEED_BOOST,
            1.0
        )
        target_speeds *= attack_boost
        
        return xp.minimum(target_speeds, PhysicsConfig.MAX_SPEED_MS)
    
    def _calculate_throttle_brake_vectorized(self, speeds, target_speeds, segment_data):
        """Vectorized throttle/brake calculation"""
        xp = self.xp
        
        speed_error = target_speeds - speeds
        is_corner = segment_data['radius'] < 10000
        
        # Throttle when speed too low
        need_throttle = speed_error > 1.0
        throttle = xp.where(
            need_throttle,
            xp.minimum(speed_error / 15.0, 1.0) * 0.9,
            0.15  # Maintenance throttle
        )
        
        # Reduce throttle in corners
        throttle = xp.where(is_corner, throttle * 0.5, throttle)
        
        # Brake when speed too high
        need_brake = speed_error < -1.0
        brake = xp.where(
            need_brake,
            xp.minimum(xp.abs(speed_error) / 8.0, 1.0),
            0.0
        )
        
        # Aggressive braking in corners
        brake = xp.where(
            is_corner & need_brake,
            xp.maximum(brake, 0.8),
            brake
        )
        
        return xp.clip(throttle, 0.0, 1.0), xp.clip(brake, 0.0, 1.0)
    
    def _calculate_steering_vectorized(self, state: dict, segment_data: dict, 
                                       driver_configs: dict):
        """Vectorized steering calculation"""
        xp = self.xp
        n_cars = len(state['position_x'])
        
        radii = segment_data['radius']
        segment_types = segment_data['type']  # 0=straight, 1=left, 2=right
        
        # Calculate Ackermann steering: delta = arctan(L / R)
        L = PhysicsConfig.WHEELBASE
        
        # For straights, no steering
        is_straight = radii > 10000
        base_steering = xp.where(
            is_straight,
            0.0,
            xp.arctan(L / xp.maximum(radii, 1.0))
        )
        
        # Apply direction (left negative, right positive)
        is_left = segment_types == 1
        base_steering = xp.where(is_left, -base_steering, base_steering)
        
        # Add driver noise (simplified for GPU)
        consistencies = xp.array([driver_configs[i]['consistency'] 
                                 for i in range(n_cars)], dtype=xp.float32)
        noise_scale = (1.0 - consistencies) * 0.02
        noise = xp.random.randn(n_cars).astype(xp.float32) * noise_scale
        
        steering = base_steering + noise
        
        return xp.clip(steering, -0.52, 0.52)
    
    def update_physics_batch(self, state: dict, dt: float, 
                            segment_data: dict, weather: WeatherConditions):
        """
        Vectorized physics update for all cars simultaneously
        This is the core GPU-accelerated function
        """
        xp = self.xp
        n_cars = len(state['position_x'])
        m = PhysicsConfig.TOTAL_MASS
        
        # Get current speeds
        speeds = xp.sqrt(state['velocity_x']**2 + state['velocity_y']**2)
        speeds = xp.maximum(speeds, 1e-6)  # Avoid division by zero
        
        # Motor force (vectorized)
        max_power = xp.where(
            state['attack_mode_active'],
            PhysicsConfig.MAX_POWER_KW * 1000 * PhysicsConfig.ATTACK_MODE_SPEED_BOOST,
            PhysicsConfig.MAX_POWER_KW * 1000
        )
        motor_power = max_power * state['throttle']
        F_motor = motor_power / speeds
        
        # Aerodynamic drag (vectorized)
        Cd = PhysicsConfig.DRAG_COEFFICIENT
        A = PhysicsConfig.FRONTAL_AREA
        rho = PhysicsConfig.AIR_DENSITY
        F_drag = 0.5 * rho * Cd * A * speeds**2
        
        # Downforce (vectorized)
        F_down = 0.5 * rho * PhysicsConfig.DOWNFORCE_COEFFICIENT * A * speeds**2
        N = m * PhysicsConfig.GRAVITY + F_down
        
        # Rolling resistance (vectorized)
        F_roll = PhysicsConfig.ROLLING_RESISTANCE_COEFF * N
        
        # Brake force (vectorized)
        max_brake_force = m * PhysicsConfig.MAX_DECELERATION
        F_brake = max_brake_force * state['brake']
        
        # Net force (vectorized)
        F_net = F_motor - F_drag - F_roll - F_brake
        
        # Traction limit (vectorized)
        F_max_traction = state['grip_coefficient'] * N
        F_net = xp.clip(F_net, -F_max_traction, F_max_traction)
        
        # Update velocity (vectorized)
        acceleration = F_net / m
        state['acceleration'] = acceleration
        new_velocity_x = state['velocity_x'] + acceleration * dt
        new_velocity_x = xp.clip(new_velocity_x, 0.0, PhysicsConfig.MAX_SPEED_MS)
        
        # Enforce corner speed limit (vectorized)
        radii = segment_data['radius']
        is_corner = radii < 10000
        grip_levels = segment_data['grip_level']
        mu_corner = state['grip_coefficient'] * grip_levels
        max_corner_speed = xp.sqrt(mu_corner * PhysicsConfig.GRAVITY * radii * 1.1)
        
        # Apply corner limit only in corners
        new_velocity_x = xp.where(
            is_corner & (new_velocity_x > max_corner_speed),
            max_corner_speed,
            new_velocity_x
        )
        
        state['velocity_x'] = new_velocity_x
        
        # Update positions (vectorized)
        state['position_x'] += state['velocity_x'] * dt
        state['lap_distance'] += state['velocity_x'] * dt
        state['total_distance'] += state['velocity_x'] * dt
        
        # Lap completion (vectorized)
        completed_lap = state['lap_distance'] >= self.track_config.total_length
        state['current_lap'] = xp.where(completed_lap, state['current_lap'] + 1, state['current_lap'])
        state['lap_distance'] = xp.where(completed_lap, 
                                         state['lap_distance'] - self.track_config.total_length,
                                         state['lap_distance'])
        
        # Energy consumption (vectorized)
        energy_used_j = motor_power * dt
        energy_used_mj = energy_used_j / 1e6
        state['battery_energy_mj'] = xp.maximum(state['battery_energy_mj'] - energy_used_mj, 0.0)
        battery_capacity_mj = PhysicsConfig.BATTERY_CAPACITY_J / 1e6
        state['battery_percentage'] = (state['battery_energy_mj'] / battery_capacity_mj) * 100.0
        
        # Battery temperature (simplified, vectorized)
        state['battery_temperature'] += 0.01 * state['throttle'] * dt
        state['battery_temperature'] = xp.clip(state['battery_temperature'], 20.0, 80.0)
        
        # Tire degradation (vectorized)
        deg_rate = PhysicsConfig.TIRE_K_BASE + PhysicsConfig.TIRE_K_SPEED * (speeds / 50.0)
        state['tire_degradation'] += deg_rate * dt
        state['tire_degradation'] = xp.clip(state['tire_degradation'], 0.0, 1.0)
        
        # Update grip based on degradation (vectorized)
        state['grip_coefficient'] = PhysicsConfig.MU_MAX - (PhysicsConfig.MU_MAX - PhysicsConfig.MU_MIN) * state['tire_degradation']
        
        # Attack mode timer (vectorized)
        state['attack_mode_timer'] = xp.maximum(state['attack_mode_timer'] - dt, 0.0)
        state['attack_mode_active'] = state['attack_mode_timer'] > 0.0
        
        # Time update (vectorized)
        state['time'] += dt
        
        return state
    
    def get_segment_data_batch(self, state: dict):
        """
        Get segment information for all cars based on their lap positions
        Returns dict with vectorized segment properties
        """
        xp = self.xp
        n_cars = len(state['lap_distance'])
        
        # Pre-compute segment data (this could be cached)
        segments = self.track_config.segments
        segment_starts = [0.0]
        for seg in segments:
            segment_starts.append(segment_starts[-1] + seg.length)
        segment_starts = xp.array(segment_starts[:-1], dtype=xp.float32)
        
        # Find which segment each car is in (vectorized)
        lap_distances = state['lap_distance']
        
        # Simple approach: iterate segments (could be optimized with binary search)
        segment_indices = xp.zeros(n_cars, dtype=xp.int32)
        for i, seg_start in enumerate(segment_starts):
            seg_end = seg_start + segments[i].length
            in_segment = (lap_distances >= seg_start) & (lap_distances < seg_end)
            segment_indices = xp.where(in_segment, i, segment_indices)
        
        # Extract segment properties (vectorized)
        radii = xp.array([segments[i].radius for i in range(len(segments))], dtype=xp.float32)
        grip_levels = xp.array([segments[i].grip_level for i in range(len(segments))], dtype=xp.float32)
        segment_types_list = []
        for seg in segments:
            if seg.segment_type == 'straight':
                segment_types_list.append(0)
            elif seg.segment_type == 'left_corner':
                segment_types_list.append(1)
            else:  # right_corner
                segment_types_list.append(2)
        segment_types = xp.array(segment_types_list, dtype=xp.int32)
        
        # Index into arrays to get values for each car
        segment_data = {
            'radius': radii[segment_indices.get() if self.use_gpu else segment_indices],
            'grip_level': grip_levels[segment_indices.get() if self.use_gpu else segment_indices],
            'type': segment_types[segment_indices.get() if self.use_gpu else segment_indices],
        }
        
        # Convert back to GPU if needed
        if self.use_gpu:
            segment_data = {k: xp.array(v) for k, v in segment_data.items()}
        
        return segment_data
    
    def state_to_cpu(self, state: dict) -> dict:
        """Convert GPU state to CPU (NumPy) for export"""
        if not self.use_gpu:
            return state
        
        return {k: cp.asnumpy(v) if isinstance(v, cp.ndarray) else v 
                for k, v in state.items()}
    
    def state_to_gpu(self, state: dict) -> dict:
        """Convert CPU state to GPU"""
        if not self.use_gpu:
            return state
        
        return {k: cp.array(v) if isinstance(v, np.ndarray) else v 
                for k, v in state.items()}
