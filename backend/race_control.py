"""
Race Control System - Flags, Penalties, and Safety Car
Implements FIA Formula E race control procedures
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from enum import Enum
from .state import CarState, RaceState
from .config import PhysicsConfig


class FlagType(Enum):
    """Types of flags in Formula E"""
    GREEN = "green"          # Normal racing
    YELLOW = "yellow"        # Local caution
    DOUBLE_YELLOW = "double_yellow"  # Severe incident, no overtaking
    RED = "red"              # Session stopped
    SAFETY_CAR = "safety_car"  # Full safety car
    BLUE = "blue"            # Lapping situation
    BLACK = "black"          # Disqualification
    BLACK_WHITE = "black_white"  # Warning for unsporting behavior


class PenaltyType(Enum):
    """Types of penalties"""
    TIME_PENALTY_5S = "5s_time_penalty"
    TIME_PENALTY_10S = "10s_time_penalty"
    DRIVE_THROUGH = "drive_through"
    STOP_GO_10S = "stop_go_10s"
    DISQUALIFICATION = "disqualification"
    WARNING = "warning"
    REPRIMAND = "reprimand"


class Penalty:
    """Represents a penalty issued to a driver"""
    
    def __init__(
        self,
        car_id: int,
        driver_name: str,
        penalty_type: PenaltyType,
        reason: str,
        lap_issued: int,
        time_penalty: float = 0.0
    ):
        self.car_id = car_id
        self.driver_name = driver_name
        self.penalty_type = penalty_type
        self.reason = reason
        self.lap_issued = lap_issued
        self.time_penalty = time_penalty
        self.served = False
    
    def to_dict(self) -> Dict:
        return {
            'car_id': self.car_id,
            'driver_name': self.driver_name,
            'penalty_type': self.penalty_type.value,
            'reason': self.reason,
            'lap_issued': self.lap_issued,
            'time_penalty': self.time_penalty,
            'served': self.served
        }


class RaceControlSystem:
    """
    Manages race control, flags, penalties, and safety car
    """
    
    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize race control system
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(random_seed)
        
        # Current flag status
        self.current_flag = FlagType.GREEN
        self.flag_sectors: List[FlagType] = [FlagType.GREEN] * 3
        
        # Safety car
        self.safety_car_active = False
        self.safety_car_deployment_time = 0.0
        self.safety_car_duration = 0.0
        
        # Penalties
        self.penalties: List[Penalty] = []
        self.warnings: Dict[int, int] = {}  # car_id -> warning count
        
        # Track limits
        self.track_limit_violations: Dict[int, int] = {}  # car_id -> violation count
        
        # Incident tracking
        self.incidents: List[Dict] = []
    
    def check_track_limits(self, car: CarState, track_width: float = 12.0) -> bool:
        """
        Check if car exceeded track limits
        
        Args:
            car: Car state
            track_width: Track width in meters
            
        Returns:
            True if violation occurred
        """
        if not car.is_active:
            return False
        
        # Check if car is too far from track center
        if abs(car.position_y) > track_width / 2:
            # Record violation
            if car.car_id not in self.track_limit_violations:
                self.track_limit_violations[car.car_id] = 0
            
            self.track_limit_violations[car.car_id] += 1
            
            # Issue penalty after 3 violations
            if self.track_limit_violations[car.car_id] >= 3:
                self._issue_penalty(
                    car,
                    PenaltyType.TIME_PENALTY_5S,
                    "Track limits violation (3 warnings)",
                    5.0
                )
                self.track_limit_violations[car.car_id] = 0  # Reset counter
                return True
        
        return False
    
    def check_unsafe_behavior(
        self,
        car: CarState,
        other_cars: List[CarState]
    ) -> bool:
        """
        Check for unsafe driving behavior
        
        Args:
            car: Car to check
            other_cars: All other cars
            
        Returns:
            True if violation occurred
        """
        if not car.is_active:
            return False
        
        # Check for excessive weaving (rapid steering changes)
        if abs(car.steering_angle) > 0.3 and abs(car.acceleration) < 0.5:
            # Potential weaving under braking
            if self.rng.random() < 0.01:  # 1% chance to detect
                self._issue_warning(
                    car,
                    "Weaving on track - unsafe behavior"
                )
                return True
        
        # Check for dangerous overtaking
        for other in other_cars:
            if not other.is_active or other.car_id == car.car_id:
                continue
            
            # Calculate distance
            dx = car.position_x - other.position_x
            dy = car.position_y - other.position_y
            distance = np.sqrt(dx**2 + dy**2)
            
            # If very close and both at high speed
            if distance < 2.0 and car.get_speed() > 60.0 and other.get_speed() > 60.0:
                if self.rng.random() < 0.005:  # 0.5% chance
                    self._issue_warning(
                        car,
                        f"Dangerous overtaking maneuver on {other.driver_name}"
                    )
                    return True
        
        return False
    
    def check_energy_limit(self, car: CarState, energy_limit_mj: float = 183.6) -> bool:
        """
        Check if car exceeded energy limit
        
        Args:
            car: Car state
            energy_limit_mj: Maximum allowed energy (default: 51 kWh = 183.6 MJ)
            
        Returns:
            True if violation occurred
        """
        # In Formula E, total energy used is monitored
        # This would need historical tracking of energy used
        # For now, just check if battery is somehow over capacity
        
        battery_energy_mj = car.battery_energy / 1e6  # Convert J to MJ
        
        if battery_energy_mj > energy_limit_mj * 1.01:  # 1% tolerance
            self._issue_penalty(
                car,
                PenaltyType.DISQUALIFICATION,
                "Energy limit exceeded",
                0.0
            )
            return True
        
        return False
    
    def deploy_safety_car(
        self,
        reason: str,
        current_time: float,
        duration: float = 180.0
    ):
        """
        Deploy safety car
        
        Args:
            reason: Reason for safety car
            current_time: Current race time
            duration: Expected duration in seconds
        """
        if not self.safety_car_active:
            self.safety_car_active = True
            self.safety_car_deployment_time = current_time
            self.safety_car_duration = duration
            self.current_flag = FlagType.SAFETY_CAR
            
            self.incidents.append({
                'time': current_time,
                'type': 'safety_car',
                'reason': reason,
                'duration': duration
            })
    
    def update_safety_car(self, current_time: float) -> bool:
        """
        Update safety car status
        
        Args:
            current_time: Current race time
            
        Returns:
            True if safety car is still active
        """
        if self.safety_car_active:
            elapsed = current_time - self.safety_car_deployment_time
            
            if elapsed >= self.safety_car_duration:
                # End safety car period
                self.safety_car_active = False
                self.current_flag = FlagType.GREEN
                return False
        
        return self.safety_car_active
    
    def apply_safety_car_effects(self, cars: List[CarState]):
        """
        Apply safety car speed restrictions to all cars
        
        Args:
            cars: All cars in the race
        """
        if not self.safety_car_active:
            return
        
        # Force all active cars to slow down
        max_speed_sc = PhysicsConfig.SAFETY_CAR_SPEED_KMH / 3.6  # Convert to m/s
        
        for car in cars:
            if car.is_active:
                current_speed = car.get_speed()
                if current_speed > max_speed_sc:
                    # Gradually slow down
                    car.brake = 0.5
                    car.throttle = 0.0
    
    def _issue_penalty(
        self,
        car: CarState,
        penalty_type: PenaltyType,
        reason: str,
        time_penalty: float
    ):
        """
        Issue a penalty to a driver
        
        Args:
            car: Car state
            penalty_type: Type of penalty
            reason: Reason for penalty
            time_penalty: Time penalty in seconds
        """
        penalty = Penalty(
            car_id=car.car_id,
            driver_name=car.driver_name,
            penalty_type=penalty_type,
            reason=reason,
            lap_issued=car.current_lap,
            time_penalty=time_penalty
        )
        
        self.penalties.append(penalty)
        
        # Apply disqualification immediately
        if penalty_type == PenaltyType.DISQUALIFICATION:
            car.is_active = False
            car.dnf_reason = f"DSQ: {reason}"
    
    def _issue_warning(self, car: CarState, reason: str):
        """
        Issue a warning to a driver
        
        Args:
            car: Car state
            reason: Reason for warning
        """
        if car.car_id not in self.warnings:
            self.warnings[car.car_id] = 0
        
        self.warnings[car.car_id] += 1
        
        # After 3 warnings, issue penalty
        if self.warnings[car.car_id] >= 3:
            self._issue_penalty(
                car,
                PenaltyType.TIME_PENALTY_5S,
                f"Accumulated warnings: {reason}",
                5.0
            )
            self.warnings[car.car_id] = 0
    
    def apply_penalties_to_results(self, results: List[Dict]) -> List[Dict]:
        """
        Apply time penalties to final results
        
        Args:
            results: List of race results
            
        Returns:
            Updated results with penalties applied
        """
        # Apply time penalties
        for penalty in self.penalties:
            if not penalty.served and penalty.time_penalty > 0:
                for result in results:
                    if result['car_id'] == penalty.car_id:
                        # Add time penalty to race time
                        if 'total_time' in result:
                            result['total_time'] += penalty.time_penalty
                        result['penalties'] = result.get('penalties', [])
                        result['penalties'].append(penalty.to_dict())
                        penalty.served = True
        
        # Re-sort by total time
        results.sort(key=lambda x: x.get('total_time', float('inf')))
        
        # Update positions
        for pos, result in enumerate(results):
            result['position'] = pos + 1
        
        return results
    
    def get_status_summary(self) -> Dict:
        """
        Get current race control status
        
        Returns:
            Dictionary with current status
        """
        return {
            'current_flag': self.current_flag.value,
            'safety_car_active': self.safety_car_active,
            'total_penalties': len(self.penalties),
            'total_warnings': sum(self.warnings.values()),
            'track_limit_violations': sum(self.track_limit_violations.values())
        }
    
    def export_penalties_csv(self, filepath: str):
        """
        Export penalties to CSV
        
        Args:
            filepath: Output file path
        """
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Driver', 'Penalty Type', 'Reason', 'Lap Issued', 
                'Time Penalty (s)', 'Served'
            ])
            
            # Data rows
            for penalty in self.penalties:
                writer.writerow([
                    penalty.driver_name,
                    penalty.penalty_type.value,
                    penalty.reason,
                    penalty.lap_issued,
                    penalty.time_penalty,
                    'Yes' if penalty.served else 'No'
                ])
        
        print(f"[OK] Penalties exported to {filepath}")
