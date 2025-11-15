"""
Probabilistic event system for Formula E race simulation
Implements SimPulse stochastic event framework

Mathematical Foundation:
    Event Probability Models:
    
    1. Crash Probability (Logistic/Sigmoid):
        P(crash) = base_prob × (1 + risk_factor × scale)
        
        Risk Factor:
            R = Σ w_i · r_i(t)
            Components: speed, tire degradation, aggression, proximity, energy stress
    
    2. Safety Car Deployment (Poisson Process):
        P(event in [t, t+dt]) = 1 - exp(-λ·dt)
        λ: Event rate (events per unit time)
    
    3. Mechanical Failures (Weibull Distribution):
        Hazard rate: h(t) = (k/λ) · (t/λ)^(k-1)
        k > 1: Increasing failure rate (wear-out)
    
    4. Overtaking Probability (Logistic Regression):
        P(overtake) = 1 / (1 + exp(-β·Δx))
        Δx: Feature vector (speed differential, attack mode, tire condition)

Implements random events, crashes, safety cars, and strategic decisions
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from .state import CarState, RaceState
from .config import PhysicsConfig


class Event:
    """Base class for race events"""
    
    def __init__(self, event_type: str, timestamp: float, description: str):
        self.event_type = event_type
        self.timestamp = timestamp
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            'type': self.event_type,
            'time': round(self.timestamp, 3),
            'description': self.description
        }


class EventGenerator:
    """
    Generates probabilistic race events using various probability distributions
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize event generator with random seed
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(seed)
        self.events: List[Event] = []
        self.last_safety_car_lap = -10  # Track when last safety car occurred
        
    def check_crash_probability(
        self,
        car: CarState,
        aggression: float,
        other_cars_nearby: int = 0
    ) -> Tuple[bool, Optional[Event]]:
        """
        Calculate crash probability using sigmoid function
        P(crash) = 1 / (1 + exp(-k * (risk_factor - x0)))
        
        Args:
            car: Car state
            aggression: Driver aggression (0-1)
            other_cars_nearby: Number of cars within 20m
            
        Returns:
            (crashed, event_object or None)
        """
        if not car.is_active:
            return False, None
        
        # Calculate risk factors
        speed_risk = car.get_speed() / PhysicsConfig.MAX_SPEED_MS  # 0-1
        tire_risk = car.tire_degradation  # 0-1
        aggression_risk = aggression  # 0-1
        proximity_risk = min(other_cars_nearby / 5.0, 1.0)  # 0-1
        energy_stress = max(0, 1.0 - car.battery_percentage / 100.0)  # Low energy = more risk
        
        # Combined risk factor (additive, normalized to 0-1 range)
        risk_factor = (
            speed_risk * 0.30 +
            tire_risk * 0.25 +
            aggression_risk * 0.20 +
            proximity_risk * 0.15 +
            energy_stress * 0.10
        )
        
        # Simplified crash probability
        # Base probability scaled by risk (exponential scaling for realism)
        crash_probability = PhysicsConfig.CRASH_BASE_PROBABILITY * (1.0 + risk_factor * 50.0)
        
        # Random check
        if self.rng.random() < crash_probability:
            event = Event(
                'crash',
                car.time,
                f"{car.driver_name} crashes out! Speed: {car.get_speed_kmh():.1f} km/h, "
                f"Tire degradation: {car.tire_degradation*100:.1f}%"
            )
            self.events.append(event)
            return True, event
        
        return False, None
    
    def check_safety_car(
        self,
        current_lap: int,
        total_laps: int,
        active_cars: int
    ) -> Tuple[bool, Optional[Event]]:
        """
        Check for safety car deployment using Poisson process
        λ = 0.1 per lap (safety car ~once every 10 laps on average)
        
        Args:
            current_lap: Current lap number
            total_laps: Total race laps
            active_cars: Number of active cars
            
        Returns:
            (deploy_safety_car, event_object or None)
        """
        # Don't deploy on first lap or if recently deployed
        if current_lap < 2 or (current_lap - self.last_safety_car_lap) < 5:
            return False, None
        
        # Simple probability per lap
        probability = PhysicsConfig.SAFETY_CAR_PROBABILITY / total_laps
        
        # Increase probability if there have been crashes
        recent_crashes = len([e for e in self.events 
                             if e.event_type == 'crash' 
                             and e.timestamp > (current_lap - 2) * 90.0])
        
        probability *= (1.0 + recent_crashes * 0.5)
        
        if self.rng.random() < probability:
            event = Event(
                'safety_car',
                current_lap * 90.0,  # Approximate time
                f"Safety car deployed on lap {current_lap}"
            )
            self.events.append(event)
            self.last_safety_car_lap = current_lap
            return True, event
        
        return False, None
    
    def calculate_overtake_probability(
        self,
        attacking_car: CarState,
        defending_car: CarState,
        track_segment_type: str
    ) -> float:
        """
        Calculate overtaking probability using logistic regression approach
        Based on speed differential, battery delta, and track position
        
        Args:
            attacking_car: Car attempting overtake
            defending_car: Car being overtaken
            track_segment_type: Type of track segment
            
        Returns:
            Probability of successful overtake (0-1)
        """
        # Speed advantage (m/s)
        speed_diff = attacking_car.get_speed() - defending_car.get_speed()
        
        # Battery/energy advantage
        battery_diff = attacking_car.battery_percentage - defending_car.battery_percentage
        
        # Attack mode advantage
        attack_advantage = 0.3 if attacking_car.attack_mode_active else 0.0
        attack_disadvantage = -0.2 if defending_car.attack_mode_active else 0.0
        
        # Track position advantage (straights easier for overtaking)
        if track_segment_type == 'straight':
            track_factor = 0.8
        elif track_segment_type in ['left_corner', 'right_corner']:
            track_factor = 0.3
        else:  # chicane
            track_factor = 0.5
        
        # Tire advantage
        tire_diff = defending_car.tire_degradation - attacking_car.tire_degradation
        
        # Logistic regression features
        z = (
            speed_diff * 0.5 +
            battery_diff * 0.02 +
            attack_advantage + attack_disadvantage +
            tire_diff * 0.4 +
            track_factor
        )
        
        # Logistic function
        probability = 1.0 / (1.0 + np.exp(-z))
        
        return np.clip(probability, 0.0, 1.0)
    
    def check_overtake(
        self,
        attacking_car: CarState,
        defending_car: CarState,
        track_segment_type: str,
        current_time: float
    ) -> Tuple[bool, Optional[Event]]:
        """
        Attempt an overtake maneuver
        
        Args:
            attacking_car: Car attempting overtake
            defending_car: Car being overtaken
            track_segment_type: Type of track segment
            current_time: Current race time
            
        Returns:
            (overtake_successful, event_object or None)
        """
        probability = self.calculate_overtake_probability(
            attacking_car, defending_car, track_segment_type
        )
        
        # Base probability is per second, adjust for timestep
        if self.rng.random() < probability * 0.1:  # Scale down for timestep
            event = Event(
                'overtake',
                current_time,
                f"{attacking_car.driver_name} overtakes {defending_car.driver_name}! "
                f"Speed advantage: {(attacking_car.get_speed() - defending_car.get_speed()) * 3.6:.1f} km/h"
            )
            self.events.append(event)
            return True, event
        
        return False, None
    
    def generate_performance_variation(
        self,
        base_skill: float,
        current_lap: int,
        total_laps: int
    ) -> float:
        """
        Generate driver performance variation using normal distribution
        N(1.0, 0.05) - drivers vary lap to lap
        
        Args:
            base_skill: Base driver skill factor
            current_lap: Current lap number
            total_laps: Total race laps
            
        Returns:
            Adjusted skill factor
        """
        # Random variation
        variation = self.rng.normal(
            PhysicsConfig.DRIVER_SKILL_MEAN,
            PhysicsConfig.DRIVER_SKILL_STD
        )
        
        # Fatigue factor (slight degradation towards end)
        race_progress = current_lap / total_laps
        fatigue = 1.0 - (race_progress * 0.05)  # Up to 5% slower at race end
        
        # Combine factors
        adjusted_skill = base_skill * variation * fatigue
        
        return np.clip(adjusted_skill, 0.7, 1.3)
    
    def get_recent_events(self, since_time: float) -> List[Event]:
        """Get events that occurred after given time"""
        return [e for e in self.events if e.timestamp >= since_time]
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type"""
        return [e for e in self.events if e.event_type == event_type]
    
    def clear_events(self):
        """Clear event history"""
        self.events.clear()


class StrategyDecisionMaker:
    """
    Makes strategic decisions using probabilistic models
    Determines when to activate attack mode, conserve energy, etc.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.RandomState(seed)
    
    def should_activate_attack_mode(
        self,
        car: CarState,
        position: int,
        gap_to_ahead: float,
        laps_remaining: int,
        track_segment_type: str
    ) -> bool:
        """
        Strategic attack mode activation - only in key moments
        
        Args:
            car: Current car state
            position: Current race position
            gap_to_ahead: Gap to car ahead (seconds)
            laps_remaining: Laps remaining in race
            track_segment_type: Current track segment
            
        Returns:
            True if should activate attack mode
        """
        if car.attack_mode_uses_left == 0 or car.attack_mode_active:
            return False
        
        # Strategic conditions - must meet multiple criteria
        
        # 1. Battery must be sufficient
        if car.battery_percentage < 40:
            return False
        
        # 2. Only activate in specific race situations
        
        # Strategy A: Attack near end of race (last 30% of laps)
        race_progress = 1.0 - (laps_remaining / 15.0)  # Assuming ~15 lap race
        in_final_phase = race_progress > 0.7
        
        # Strategy B: Close battle - within 2 seconds of car ahead
        close_battle = gap_to_ahead < 2.0 and gap_to_ahead > 0.1
        
        # Strategy C: Good position to fight (2nd to 6th)
        competitive_position = 2 <= position <= 6
        
        # Strategy D: On a straight (best place to use power)
        on_straight = track_segment_type == 'straight'
        
        # Decision logic: Need at least 2 key conditions
        conditions_met = sum([
            in_final_phase,
            close_battle and on_straight,
            competitive_position and close_battle,
            car.battery_percentage > 60 and laps_remaining < 3
        ])
        
        # Only activate if strong strategic reason (low probability)
        if conditions_met >= 2:
            # Even then, only 5% chance per timestep to avoid spam
            return self.rng.random() < 0.05
        
        return False
    
    def get_energy_management_strategy(
        self,
        car: CarState,
        current_lap: int,
        total_laps: int,
        position: int
    ) -> str:
        """
        Determine energy management strategy
        Returns: 'conserve', 'neutral', 'aggressive'
        
        Args:
            car: Current car state
            current_lap: Current lap
            total_laps: Total laps
            position: Current position
            
        Returns:
            Strategy string
        """
        race_progress = current_lap / total_laps
        battery_pct = car.battery_percentage
        
        # Decision tree approach
        if battery_pct < 20:
            return 'conserve'
        elif battery_pct > 70 and race_progress > 0.7:
            return 'aggressive'
        elif position <= 3 and battery_pct > 40:
            return 'aggressive'
        elif battery_pct < 40 and race_progress < 0.5:
            return 'conserve'
        else:
            return 'neutral'
    
    def calculate_pit_stop_benefit(
        self,
        car: CarState,
        tire_deg: float,
        laps_remaining: int
    ) -> float:
        """
        Calculate benefit of pit stop (tire change)
        Note: Formula E typically doesn't have pit stops, but included for completeness
        
        Args:
            car: Car state
            tire_deg: Tire degradation level
            laps_remaining: Laps remaining
            
        Returns:
            Benefit score (higher = should pit)
        """
        # Time lost in pit: ~20 seconds
        pit_time_loss = 20.0
        
        # Time gained per lap with fresh tires
        time_gain_per_lap = tire_deg * 1.5  # seconds
        
        # Total potential gain
        total_gain = time_gain_per_lap * laps_remaining
        
        # Net benefit
        benefit = total_gain - pit_time_loss
        
        return benefit
