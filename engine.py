"""
Main Formula E Race Simulation Engine
Orchestrates all components for complete race simulation
"""

import numpy as np
import json
import time
from typing import Dict, List, Optional, Tuple
from .state import CarState, RaceState
from .config import (
    PhysicsConfig, TrackConfig, SimulationConfig,
    MLConfig, DriverConfig, physics_config, track_config,
    simulation_config, ml_config
)
from .physics import PhysicsEngine
from .events import EventGenerator, StrategyDecisionMaker, Event
from .ml_strategy import MLStrategyCoordinator
from .leaderboard import Leaderboard, PerformanceMetrics


class FormulaERaceEngine:
    """
    Main simulation engine for Formula E racing
    Integrates physics, events, ML strategy, and leaderboard management
    """
    
    def __init__(
        self,
        num_cars: int = 24,
        num_laps: int = 10,
        track_config: Optional[TrackConfig] = None,
        use_ml_strategy: bool = True,
        random_seed: Optional[int] = None
    ):
        """
        Initialize Formula E race engine
        
        Args:
            num_cars: Number of cars in the race
            num_laps: Number of laps to complete
            track_config: Track configuration (uses default if None)
            use_ml_strategy: Whether to use ML-based strategy
            random_seed: Random seed for reproducibility
        """
        # Configuration
        self.num_cars = num_cars
        self.num_laps = num_laps
        self.track_config = track_config or TrackConfig()
        self.use_ml_strategy = use_ml_strategy
        
        # Set random seeds
        if random_seed is not None:
            np.random.seed(random_seed)
            self.physics_seed = random_seed
            self.events_seed = random_seed + 1
            self.ml_seed = random_seed + 2
        else:
            self.physics_seed = simulation_config.PHYSICS_SEED
            self.events_seed = simulation_config.EVENTS_SEED
            self.ml_seed = simulation_config.ML_SEED
        
        # Initialize driver configurations
        self.driver_configs = [
            DriverConfig.get_driver(i) for i in range(num_cars)
        ]
        
        # Initialize race state
        self.race_state = RaceState(num_cars, self.driver_configs)
        self.starting_grid = [i + 1 for i in range(num_cars)]
        
        # Initialize subsystems
        self.physics_engine = PhysicsEngine(self.track_config)
        self.event_generator = EventGenerator(self.events_seed)
        self.strategy_maker = StrategyDecisionMaker(self.events_seed)
        
        if self.use_ml_strategy:
            self.ml_coordinator = MLStrategyCoordinator(self.ml_seed)
        else:
            self.ml_coordinator = None
        
        self.leaderboard = Leaderboard(self.track_config)
        self.metrics = PerformanceMetrics()
        
        # Simulation state
        self.current_step = 0
        self.dt = simulation_config.TIMESTEP
        self.race_started = False
        self.race_finished = False
        
        # Event log
        self.event_log: List[Event] = []
        
        # Performance tracking
        self.simulation_start_time = None
        self.real_time_factor = 0.0
        
    def simulate_timestep(self, dt: Optional[float] = None) -> Tuple[np.ndarray, List[Dict], List[Dict]]:
        """
        Simulate one timestep of the race
        
        Args:
            dt: Timestep duration (uses default if None)
            
        Returns:
            (state_matrix, leaderboard_entries, new_events)
        """
        if dt is None:
            dt = self.dt
        
        if self.race_finished:
            return self.race_state.get_state_matrix(), [], []
        
        # Start race if not started
        if not self.race_started:
            self.race_started = True
            self.race_state.race_started = True
            self.simulation_start_time = time.time()
        
        new_events = []
        
        # Update each car
        for car in self.race_state.cars:
            if not car.is_active:
                continue
            
            # Get driver config
            driver = self.driver_configs[car.car_id]
            
            # Get current track segment
            segment, _ = self.track_config.get_segment_at_distance(car.lap_distance)
            
            # Calculate opponent distances (simplified)
            opponent_distances = []
            for other_car in self.race_state.cars:
                if other_car.car_id != car.car_id and other_car.is_active:
                    dist = abs(other_car.total_distance - car.total_distance)
                    if dist < 100:  # Within 100m
                        opponent_distances.append(dist)
            opponent_distances.sort()
            
            # Determine control inputs
            if self.use_ml_strategy and self.ml_coordinator:
                # Use ML strategy
                steering, throttle, energy_strategy = self.ml_coordinator.get_ml_controls(
                    car, opponent_distances[:2], segment.segment_type,
                    self.track_config, self.num_laps
                )
                
                # Check if should activate attack mode
                if energy_strategy == 'activate_attack_mode':
                    if car.activate_attack_mode():
                        event = Event(
                            'attack_mode',
                            car.time,
                            f"{car.driver_name} activates Attack Mode!"
                        )
                        new_events.append(event)
                        self.event_log.append(event)
                
                # Convert to brake (simplified)
                brake = 0.0
                if throttle < 0.3:
                    brake = 0.3 - throttle
                    throttle = 0.0
            else:
                # Simple AI strategy
                segment_max_speed = self.track_config.calculate_max_corner_speed(
                    segment.radius, car.grip_coefficient * segment.grip_level
                )
                
                current_speed = car.get_speed()
                if current_speed < segment_max_speed * 0.9:
                    throttle = 0.8
                    brake = 0.0
                elif current_speed > segment_max_speed * 1.05:
                    throttle = 0.0
                    brake = 0.6
                else:
                    throttle = 0.5
                    brake = 0.0
                
                # Decide on attack mode
                laps_remaining = self.num_laps - car.current_lap
                if self.strategy_maker.should_activate_attack_mode(
                    car, car.position, car.gap_to_ahead,
                    laps_remaining, segment.segment_type
                ):
                    if car.activate_attack_mode():
                        event = Event(
                            'attack_mode',
                            car.time,
                            f"{car.driver_name} activates Attack Mode!"
                        )
                        new_events.append(event)
                        self.event_log.append(event)
            
            # Store previous state for ML learning
            if self.use_ml_strategy:
                prev_state = CarState(
                    car_id=car.car_id,
                    driver_name=car.driver_name
                )
                # Copy key attributes
                prev_state.position = car.position
                prev_state.battery_percentage = car.battery_percentage
                prev_state.current_lap = car.current_lap
            
            # Update physics
            self.physics_engine.update_car_physics(
                car, dt, throttle, brake,
                driver['skill'], driver['aggression']
            )
            
            # Check for crash
            nearby_cars = len([d for d in opponent_distances if d < 20])
            crashed, crash_event = self.event_generator.check_crash_probability(
                car, driver['aggression'], nearby_cars
            )
            if crashed:
                car.is_active = False
                new_events.append(crash_event)
                self.event_log.append(crash_event)
            
            # Update ML learning (if using ML)
            if self.use_ml_strategy and self.ml_coordinator:
                # Get energy strategy for this car
                energy_strategy = self.ml_coordinator.energy_management.select_action(
                    car, self.num_laps
                )
                
                self.ml_coordinator.update_learning(
                    car.car_id, prev_state, car, energy_strategy, self.num_laps
                )
        
        # Update race positions
        self.race_state.update_positions()
        
        # Check for overtakes
        for i, car in enumerate(self.race_state.cars):
            if not car.is_active:
                continue
            
            # Find cars within overtaking distance
            for other_car in self.race_state.cars:
                if other_car.car_id == car.car_id or not other_car.is_active:
                    continue
                
                distance_diff = abs(car.total_distance - other_car.total_distance)
                if distance_diff < 10:  # Within 10 meters
                    # Check if car is ahead but should be behind
                    if (car.total_distance > other_car.total_distance and 
                        car.position > other_car.position):
                        # Potential overtake
                        segment, _ = self.track_config.get_segment_at_distance(car.lap_distance)
                        overtook, overtake_event = self.event_generator.check_overtake(
                            car, other_car, segment.segment_type, car.time
                        )
                        if overtook:
                            car.overtakes_made += 1
                            other_car.overtakes_received += 1
                            new_events.append(overtake_event)
                            self.event_log.append(overtake_event)
        
        # Check for safety car (once per lap)
        if self.current_step % int(90.0 / dt) == 0:  # Approximately every lap
            active_cars_list = [c for c in self.race_state.cars if c.is_active]
            if len(active_cars_list) > 0:
                leader_lap = max(c.current_lap for c in active_cars_list)
                active_cars = len(active_cars_list)
                
                safety_car, sc_event = self.event_generator.check_safety_car(
                    leader_lap, self.num_laps, active_cars
                )
                if safety_car:
                    self.race_state.safety_car_active = True
                    new_events.append(sc_event)
                    self.event_log.append(sc_event)
        
        # Update leaderboard
        self.leaderboard.update(self.race_state)
        
        # Update metrics
        self.metrics.update_from_race_state(self.race_state)
        
        # Check if race is finished
        active_cars_count = sum(1 for c in self.race_state.cars if c.is_active)
        
        # Race ends if all cars retired
        if active_cars_count == 0:
            self.race_finished = True
            self.race_state.race_finished = True
        else:
            # Check if leader finished
            leader = self.race_state.cars[0]
            for car in self.race_state.cars:
                if car.is_active and car.position == 1:
                    leader = car
                    break
            
            if leader.current_lap >= self.num_laps:
                self.race_finished = True
                self.race_state.race_finished = True
        
        # Update simulation time
        self.race_state.current_time += dt
        self.current_step += 1
        
        # Calculate real-time factor
        if self.simulation_start_time:
            real_elapsed = time.time() - self.simulation_start_time
            sim_elapsed = self.race_state.current_time
            self.real_time_factor = sim_elapsed / real_elapsed if real_elapsed > 0 else 0.0
        
        # Return state matrix, leaderboard, and events
        state_matrix = self.race_state.get_state_matrix()
        leaderboard_data = [entry.to_dict() for entry in self.leaderboard.entries]
        event_data = [event.to_dict() for event in new_events]
        
        return state_matrix, leaderboard_data, event_data
    
    def run_simulation(
        self,
        display_interval: int = 100,
        verbose: bool = True
    ) -> Dict:
        """
        Run complete race simulation
        
        Args:
            display_interval: Steps between leaderboard displays
            verbose: Whether to print progress
            
        Returns:
            Final race summary dictionary
        """
        if verbose:
            print(f"\n{'='*100}")
            print(f"FORMULA E RACE SIMULATION")
            print(f"Track: {self.track_config.track_name}")
            print(f"Laps: {self.num_laps}")
            print(f"Cars: {self.num_cars}")
            print(f"Track Length: {self.track_config.total_length:.0f}m")
            print(f"{'='*100}\n")
            print("Starting race...\n")
        
        step_count = 0
        max_steps = int(self.num_laps * 120 / self.dt)  # Max race time estimate
        
        while not self.race_finished and step_count < max_steps:
            # Simulate timestep
            state_matrix, leaderboard_data, events = self.simulate_timestep()
            
            # Display progress
            if verbose and step_count % display_interval == 0:
                # Find leader (prefer active cars)
                leader = None
                for car in self.race_state.cars:
                    if car.is_active and car.position == 1:
                        leader = car
                        break
                
                # If no active leader, use first car in leaderboard
                if leader is None:
                    leader = self.race_state.cars[0]
                
                print(f"\n--- Step {step_count} | Time: {self.race_state.current_time:.1f}s | "
                      f"Leader: {leader.driver_name} (Lap {leader.current_lap}/{self.num_laps}) | "
                      f"Speed: {self.real_time_factor:.1f}x real-time ---")
                
                # Show top 5
                for entry in self.leaderboard.get_top_n(5):
                    print(entry.to_string())
                
                # Show recent events
                if events:
                    print("\nRecent events:")
                    for event in events:
                        print(f"  - {event['description']}")
            
            step_count += 1
        
        # Race finished
        if verbose:
            print(f"\n{'='*100}")
            print("RACE FINISHED!")
            print(f"{'='*100}\n")
            self.leaderboard.print_leaderboard(self.num_cars)
        
        # Generate final summary
        summary = self.get_race_summary()
        
        return summary
    
    def get_leaderboard(self) -> List[Dict]:
        """
        Get current leaderboard
        
        Returns:
            List of leaderboard entry dictionaries
        """
        return self.leaderboard.to_dict()
    
    def detect_events(self) -> List[Dict]:
        """
        Get recent race events
        
        Returns:
            List of event dictionaries
        """
        recent_time = self.race_state.current_time - 10.0  # Last 10 seconds
        recent_events = self.event_generator.get_recent_events(recent_time)
        return [event.to_dict() for event in recent_events]
    
    def get_race_summary(self) -> Dict:
        """
        Generate comprehensive race summary
        
        Returns:
            Summary dictionary with all statistics
        """
        summary = {
            'race_info': {
                'track': self.track_config.track_name,
                'laps': self.num_laps,
                'total_distance_km': (self.track_config.total_length * self.num_laps) / 1000.0,
                'num_cars': self.num_cars,
                'race_time_seconds': self.race_state.current_time,
                'simulation_speed': f"{self.real_time_factor:.1f}x real-time"
            },
            'final_standings': self.leaderboard.to_dict(),
            'performance_metrics': self.metrics.get_race_summary(
                self.race_state, self.starting_grid
            ),
            'events': {
                'total_events': len(self.event_log),
                'crashes': len([e for e in self.event_log if e.event_type == 'crash']),
                'overtakes': len([e for e in self.event_log if e.event_type == 'overtake']),
                'attack_modes': len([e for e in self.event_log if e.event_type == 'attack_mode']),
                'safety_cars': len([e for e in self.event_log if e.event_type == 'safety_car']),
            },
            'all_events': [event.to_dict() for event in self.event_log]
        }
        
        return summary
    
    def export_to_json(self, filepath: str):
        """
        Export race data to JSON file
        
        Args:
            filepath: Output file path
        """
        summary = self.get_race_summary()
        
        # Add full state data
        summary['final_state'] = self.race_state.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Race data exported to {filepath}")
    
    def export_to_csv(self, filepath: str):
        """
        Export leaderboard to CSV file
        
        Args:
            filepath: Output file path
        """
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Position', 'Driver', 'Laps', 'Best Lap', 'Last Lap',
                'Battery %', 'Tire Deg %', 'Overtakes', 'Status'
            ])
            
            # Data rows
            for entry in self.leaderboard.entries:
                writer.writerow([
                    entry.position,
                    entry.driver_name,
                    entry.current_lap,
                    f"{entry.best_lap_time:.3f}" if entry.best_lap_time != np.inf else 'N/A',
                    f"{entry.last_lap_time:.3f}" if entry.last_lap_time > 0 else 'N/A',
                    f"{entry.battery_percentage:.1f}",
                    f"{entry.tire_degradation * 100:.1f}",
                    self.race_state.cars[entry.car_id].overtakes_made,
                    'Running' if entry.is_active else 'Retired'
                ])
        
        print(f"Leaderboard exported to {filepath}")
