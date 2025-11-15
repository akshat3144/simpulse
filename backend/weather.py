"""
Dynamic Weather System for Formula E
Implements realistic weather transitions and effects
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class WeatherState:
    """Current weather state"""
    temperature: float  # Celsius
    humidity: float  # 0-1
    rain_intensity: float  # 0-1 (0=dry, 1=heavy rain)
    wind_speed: float  # m/s
    wind_direction: float  # radians
    track_wetness: float  # 0-1 (track surface water)
    grip_multiplier: float  # Effect on tire grip


class DynamicWeatherSystem:
    """
    Simulates dynamic weather changes during a race
    """
    
    def __init__(
        self,
        initial_temp: float = 25.0,
        initial_humidity: float = 0.60,
        initial_rain: float = 0.0,
        random_seed: Optional[int] = None
    ):
        """
        Initialize weather system
        
        Args:
            initial_temp: Starting temperature (Celsius)
            initial_humidity: Starting humidity (0-1)
            initial_rain: Starting rain intensity (0-1)
            random_seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(random_seed)
        
        self.state = WeatherState(
            temperature=initial_temp,
            humidity=initial_humidity,
            rain_intensity=initial_rain,
            wind_speed=self.rng.uniform(0, 5),  # 0-5 m/s
            wind_direction=self.rng.uniform(0, 2*np.pi),
            track_wetness=initial_rain * 0.5,  # Track starts drier
            grip_multiplier=self._calculate_grip_multiplier(initial_rain, initial_rain * 0.5)
        )
        
        # Weather evolution parameters
        self.rain_probability = 0.001  # Probability of rain starting per second
        self.rain_clear_probability = 0.002  # Probability of rain stopping per second
        
        # Temperature evolution
        self.temp_drift_rate = 0.01  # °C per minute max
        
        # Track drying rate
        self.track_dry_rate = 0.001  # Per second when not raining
    
    def update(self, dt: float):
        """
        Update weather state based on time elapsed
        
        Args:
            dt: Time step in seconds
        """
        # Update rain intensity
        self._update_rain(dt)
        
        # Update temperature (slow drift)
        temp_change = self.rng.normal(0, self.temp_drift_rate * dt / 60.0)
        self.state.temperature += temp_change
        self.state.temperature = np.clip(self.state.temperature, 10.0, 45.0)
        
        # Update humidity (correlated with rain)
        if self.state.rain_intensity > 0:
            self.state.humidity = min(1.0, self.state.humidity + 0.01 * dt)
        else:
            self.state.humidity += self.rng.normal(0, 0.001 * dt)
            self.state.humidity = np.clip(self.state.humidity, 0.3, 0.95)
        
        # Update wind
        wind_change = self.rng.normal(0, 0.1 * dt)
        self.state.wind_speed += wind_change
        self.state.wind_speed = np.clip(self.state.wind_speed, 0, 15)
        
        wind_dir_change = self.rng.normal(0, 0.1 * dt)
        self.state.wind_direction += wind_dir_change
        self.state.wind_direction = self.state.wind_direction % (2 * np.pi)
        
        # Update track wetness
        self._update_track_wetness(dt)
        
        # Update grip multiplier
        self.state.grip_multiplier = self._calculate_grip_multiplier(
            self.state.rain_intensity,
            self.state.track_wetness
        )
    
    def _update_rain(self, dt: float):
        """
        Update rain intensity with realistic transitions
        
        Args:
            dt: Time step in seconds
        """
        if self.state.rain_intensity == 0:
            # Check if rain starts
            if self.rng.random() < self.rain_probability * dt:
                # Rain starts - light initially
                self.state.rain_intensity = self.rng.uniform(0.1, 0.3)
        else:
            # Rain is active
            # Check if rain stops
            if self.rng.random() < self.rain_clear_probability * dt:
                # Rain stops
                self.state.rain_intensity = 0
            else:
                # Rain intensity changes
                intensity_change = self.rng.normal(0, 0.05 * dt)
                self.state.rain_intensity += intensity_change
                self.state.rain_intensity = np.clip(self.state.rain_intensity, 0.05, 1.0)
    
    def _update_track_wetness(self, dt: float):
        """
        Update track wetness based on rain and drying
        
        Args:
            dt: Time step in seconds
        """
        if self.state.rain_intensity > 0:
            # Track gets wetter
            wetness_increase = self.state.rain_intensity * 0.01 * dt
            self.state.track_wetness += wetness_increase
            self.state.track_wetness = min(1.0, self.state.track_wetness)
        else:
            # Track dries
            # Drying rate depends on temperature and humidity
            dry_rate = self.track_dry_rate * dt
            
            # Temperature effect (hotter = faster drying)
            temp_factor = 1.0 + (self.state.temperature - 25.0) / 25.0
            temp_factor = np.clip(temp_factor, 0.5, 2.0)
            
            # Humidity effect (lower humidity = faster drying)
            humidity_factor = 1.0 - self.state.humidity * 0.5
            
            dry_rate *= temp_factor * humidity_factor
            
            self.state.track_wetness -= dry_rate
            self.state.track_wetness = max(0.0, self.state.track_wetness)
    
    def _calculate_grip_multiplier(self, rain_intensity: float, track_wetness: float) -> float:
        """
        Calculate grip multiplier based on weather conditions
        
        Args:
            rain_intensity: Current rain intensity (0-1)
            track_wetness: Current track wetness (0-1)
            
        Returns:
            Grip multiplier (0.5-1.0)
        """
        # Base grip reduction from wetness
        wetness_effect = 1.0 - track_wetness * 0.35  # Max 35% reduction
        
        # Additional effect from active rain
        rain_effect = 1.0 - rain_intensity * 0.15  # Additional 15% max
        
        grip_multiplier = wetness_effect * rain_effect
        
        # Minimum grip is 50% of dry conditions
        grip_multiplier = max(0.5, grip_multiplier)
        
        return grip_multiplier
    
    def get_aerodynamic_drag_multiplier(self) -> float:
        """
        Get aerodynamic drag multiplier from weather
        
        Returns:
            Drag multiplier (1.0 = normal, higher = more drag)
        """
        # Rain increases drag slightly
        rain_drag = 1.0 + self.state.rain_intensity * 0.05  # Up to 5% increase
        
        # Wind affects drag (simplified - just magnitude)
        wind_drag = 1.0 + self.state.wind_speed * 0.002  # Small effect
        
        return rain_drag * wind_drag
    
    def get_energy_consumption_multiplier(self) -> float:
        """
        Get energy consumption multiplier from weather
        
        Returns:
            Energy multiplier (1.0 = normal, higher = more consumption)
        """
        # Wet conditions require more energy (less grip, more wheel spin)
        wet_effect = 1.0 + self.state.track_wetness * 0.08  # Up to 8% increase
        
        # Wind resistance
        wind_effect = 1.0 + self.state.wind_speed * 0.003
        
        return wet_effect * wind_effect
    
    def get_tire_degradation_multiplier(self) -> float:
        """
        Get tire degradation multiplier from weather
        
        Returns:
            Degradation multiplier (1.0 = normal)
        """
        # Wet conditions reduce tire degradation
        if self.state.track_wetness > 0.3:
            return 0.7  # 30% less degradation in wet
        elif self.state.track_wetness > 0.1:
            return 0.85  # 15% less degradation in damp
        else:
            # Dry conditions - temperature affects degradation
            temp_factor = 1.0 + (self.state.temperature - 25.0) / 50.0
            temp_factor = np.clip(temp_factor, 0.8, 1.3)
            return temp_factor
    
    def get_visibility_factor(self) -> float:
        """
        Get visibility factor (affects driver performance)
        
        Returns:
            Visibility factor (0.5-1.0, lower = worse visibility)
        """
        # Rain reduces visibility
        rain_visibility = 1.0 - self.state.rain_intensity * 0.3  # Up to 30% reduction
        
        return max(0.5, rain_visibility)
    
    def get_crash_risk_multiplier(self) -> float:
        """
        Get crash risk multiplier from weather
        
        Returns:
            Risk multiplier (1.0 = normal, higher = more risk)
        """
        # Wet conditions increase crash risk
        wet_risk = 1.0 + self.state.track_wetness * 1.5  # Up to 150% increase
        
        # Rain reduces visibility
        visibility_risk = 1.0 + self.state.rain_intensity * 0.5  # Up to 50% increase
        
        return wet_risk * visibility_risk
    
    def get_weather_description(self) -> str:
        """
        Get human-readable weather description
        
        Returns:
            Weather description string
        """
        # Temperature
        if self.state.temperature < 15:
            temp_desc = "Cold"
        elif self.state.temperature < 25:
            temp_desc = "Cool"
        elif self.state.temperature < 30:
            temp_desc = "Warm"
        else:
            temp_desc = "Hot"
        
        # Rain
        if self.state.rain_intensity == 0:
            rain_desc = "Dry"
        elif self.state.rain_intensity < 0.3:
            rain_desc = "Light rain"
        elif self.state.rain_intensity < 0.7:
            rain_desc = "Moderate rain"
        else:
            rain_desc = "Heavy rain"
        
        # Track
        if self.state.track_wetness < 0.1:
            track_desc = "dry track"
        elif self.state.track_wetness < 0.4:
            track_desc = "damp track"
        elif self.state.track_wetness < 0.7:
            track_desc = "wet track"
        else:
            track_desc = "very wet track"
        
        # Wind
        if self.state.wind_speed < 3:
            wind_desc = ""
        elif self.state.wind_speed < 7:
            wind_desc = ", light wind"
        else:
            wind_desc = ", strong wind"
        
        return f"{temp_desc} ({self.state.temperature:.1f}°C), {rain_desc}, {track_desc}{wind_desc}"
    
    def to_dict(self) -> dict:
        """
        Export weather state as dictionary
        
        Returns:
            Dictionary with all weather data
        """
        return {
            'temperature': round(self.state.temperature, 1),
            'humidity': round(self.state.humidity, 3),
            'rain_intensity': round(self.state.rain_intensity, 3),
            'wind_speed': round(self.state.wind_speed, 1),
            'wind_direction': round(self.state.wind_direction, 2),
            'track_wetness': round(self.state.track_wetness, 3),
            'grip_multiplier': round(self.state.grip_multiplier, 3),
            'description': self.get_weather_description()
        }
