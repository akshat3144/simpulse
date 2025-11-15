"""
Markov Decision Process (MDP) Framework for SimPulse
Foundation for reinforcement learning and adaptive AI agents

Mathematical Formulation:
    MDP = (S, A, P, R, γ)
    
Where:
    - S: State space (all car states)
    - A: Action space (throttle, brake, steering, attack mode)
    - P: Transition probability P(s'|s,a)
    - R: Reward function R(s,a,s')
    - γ: Discount factor for future rewards

Value Function:
    V(s) = max_a [R(s,a) + γ * Σ P(s'|s,a) * V(s')]
    
Q-Function:
    Q(s,a) = R(s,a) + γ * Σ P(s'|s,a) * max_a' Q(s',a')
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from .state import CarState, RaceState
from .config import PhysicsConfig


@dataclass
class Action:
    """
    Action representation for MDP
    Discrete or continuous control inputs
    """
    throttle: float  # 0-1
    brake: float  # 0-1
    steering: float  # radians
    activate_attack: bool  # Boolean decision
    
    def to_vector(self) -> np.ndarray:
        """Convert action to vector form"""
        return np.array([
            self.throttle,
            self.brake,
            self.steering,
            float(self.activate_attack)
        ])
    
    @classmethod
    def from_vector(cls, vec: np.ndarray) -> 'Action':
        """Create action from vector"""
        return cls(
            throttle=float(vec[0]),
            brake=float(vec[1]),
            steering=float(vec[2]),
            activate_attack=bool(vec[3] > 0.5)
        )


class ActionSpace:
    """
    Defines the action space for racing agents
    Supports both discrete and continuous action spaces
    """
    
    def __init__(self, action_type: str = 'continuous'):
        """
        Args:
            action_type: 'discrete' or 'continuous'
        """
        self.action_type = action_type
        
        if action_type == 'discrete':
            # Discretized action space
            self.throttle_levels = [0.0, 0.3, 0.6, 1.0]
            self.brake_levels = [0.0, 0.3, 0.6, 1.0]
            self.steering_levels = [-0.3, -0.1, 0.0, 0.1, 0.3]
            self.attack_options = [False, True]
            
            self.n_actions = (
                len(self.throttle_levels) *
                len(self.brake_levels) *
                len(self.steering_levels) *
                len(self.attack_options)
            )
        else:
            # Continuous action space bounds
            self.bounds = {
                'throttle': (0.0, 1.0),
                'brake': (0.0, 1.0),
                'steering': (-0.5, 0.5),
                'attack': (0, 1)  # Will be thresholded
            }
            self.n_actions = 4  # Dimension of action vector
    
    def sample(self, rng: np.random.RandomState = None) -> Action:
        """Sample random action from space"""
        if rng is None:
            rng = np.random.RandomState()
        
        if self.action_type == 'discrete':
            throttle = rng.choice(self.throttle_levels)
            brake = rng.choice(self.brake_levels)
            steering = rng.choice(self.steering_levels)
            attack = rng.choice(self.attack_options)
        else:
            throttle = rng.uniform(*self.bounds['throttle'])
            brake = rng.uniform(*self.bounds['brake'])
            steering = rng.uniform(*self.bounds['steering'])
            attack = rng.random() > 0.95  # Rarely activate randomly
        
        return Action(throttle, brake, steering, attack)
    
    def get_discrete_action(self, action_index: int) -> Action:
        """Convert discrete action index to Action object"""
        if self.action_type != 'discrete':
            raise ValueError("Action space is not discrete")
        
        # Decode multi-dimensional action index
        n_attack = len(self.attack_options)
        n_steering = len(self.steering_levels)
        n_brake = len(self.brake_levels)
        
        attack_idx = action_index % n_attack
        remainder = action_index // n_attack
        
        steering_idx = remainder % n_steering
        remainder = remainder // n_steering
        
        brake_idx = remainder % n_brake
        throttle_idx = remainder // n_brake
        
        return Action(
            throttle=self.throttle_levels[throttle_idx],
            brake=self.brake_levels[brake_idx],
            steering=self.steering_levels[steering_idx],
            activate_attack=self.attack_options[attack_idx]
        )


class RewardFunction:
    """
    Reward function design for racing MDP
    
    Multi-objective reward balancing:
    - Position gain (primary objective)
    - Energy efficiency (constraint)
    - Tire preservation (long-term strategy)
    - Collision avoidance (safety)
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Args:
            weights: Dictionary of reward component weights
        """
        self.weights = weights or {
            'position_gain': 10.0,      # Reward for overtaking
            'lap_time': -1.0,            # Penalty for slow laps
            'energy_efficiency': 2.0,    # Reward for efficient driving
            'tire_preservation': 1.5,    # Reward for low degradation
            'speed': 0.5,                # Reward for high speed
            'crash_penalty': -100.0,     # Large penalty for crashes
            'battery_depletion': -50.0,  # Penalty for running out of energy
            'attack_mode_usage': 5.0,    # Reward for strategic attack mode
            'gap_reduction': 3.0         # Reward for closing gap to leader
        }
    
    def calculate_reward(
        self,
        car_prev: CarState,
        car_next: CarState,
        action: Action,
        race_context: Dict
    ) -> float:
        """
        Calculate reward for state transition s → s'
        
        R(s,a,s') = Σ w_i * r_i(s,a,s')
        
        Args:
            car_prev: Previous car state
            car_next: Next car state
            action: Action taken
            race_context: Additional context (position changes, etc.)
            
        Returns:
            Scalar reward value
        """
        reward = 0.0
        
        # Position gain reward
        position_change = car_prev.position - car_next.position
        reward += self.weights['position_gain'] * position_change
        
        # Speed reward (encourage racing pace)
        speed_kmh = car_next.get_speed_kmh()
        normalized_speed = speed_kmh / PhysicsConfig.MAX_SPEED_KMH
        reward += self.weights['speed'] * normalized_speed
        
        # Energy efficiency reward
        if car_next.total_distance > car_prev.total_distance:
            distance_delta = car_next.total_distance - car_prev.total_distance
            energy_delta = car_prev.battery_percentage - car_next.battery_percentage
            if energy_delta > 0:
                efficiency = distance_delta / energy_delta
                reward += self.weights['energy_efficiency'] * np.log1p(efficiency)
        
        # Tire preservation reward
        tire_delta = car_next.tire_degradation - car_prev.tire_degradation
        reward += self.weights['tire_preservation'] * (-tire_delta * 100)
        
        # Crash penalty
        if car_next.is_active == False and car_prev.is_active == True:
            reward += self.weights['crash_penalty']
        
        # Battery depletion penalty
        if car_next.battery_percentage < 5.0:
            reward += self.weights['battery_depletion']
        
        # Attack mode strategic reward
        if action.activate_attack and car_next.attack_mode_active:
            # Reward based on race context (good if overtaking opportunity)
            gap_to_ahead = race_context.get('gap_to_ahead', 10.0)
            if gap_to_ahead < 3.0:
                reward += self.weights['attack_mode_usage']
        
        # Gap reduction reward
        gap_delta = car_prev.gap_to_leader - car_next.gap_to_leader
        reward += self.weights['gap_reduction'] * gap_delta
        
        return reward
    
    def calculate_lap_reward(
        self,
        car: CarState,
        lap_time: float,
        position: int
    ) -> float:
        """
        Calculate reward for completing a lap
        
        Args:
            car: Car state at lap end
            lap_time: Lap time in seconds
            position: Final lap position
            
        Returns:
            Lap completion reward
        """
        reward = 0.0
        
        # Position-based reward (exponential for podium)
        if position == 1:
            reward += 50.0
        elif position == 2:
            reward += 30.0
        elif position == 3:
            reward += 20.0
        else:
            reward += max(0, 10.0 - position)
        
        # Lap time reward (faster = better)
        target_lap_time = 80.0  # seconds (Formula E typical)
        time_delta = target_lap_time - lap_time
        reward += time_delta * 0.5
        
        return reward


class PolicyModel:
    """
    Base class for racing policy models
    
    Policy π(a|s) maps states to action probabilities
    """
    
    def __init__(self, action_space: ActionSpace):
        self.action_space = action_space
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> Action:
        """
        Get action from policy given current state
        
        Args:
            state: State vector
            deterministic: If True, return best action; else sample
            
        Returns:
            Action to take
        """
        raise NotImplementedError("Subclass must implement get_action()")
    
    def update(self, trajectory: List[Tuple], reward: float):
        """
        Update policy based on trajectory and reward
        
        Args:
            trajectory: List of (state, action, reward, next_state)
            reward: Total trajectory reward
        """
        raise NotImplementedError("Subclass must implement update()")


class RandomPolicy(PolicyModel):
    """Random policy for baseline comparison"""
    
    def __init__(self, action_space: ActionSpace, seed: int = None):
        super().__init__(action_space)
        self.rng = np.random.RandomState(seed)
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> Action:
        """Return random action"""
        return self.action_space.sample(self.rng)
    
    def update(self, trajectory: List[Tuple], reward: float):
        """Random policy doesn't learn"""
        pass


class GreedyPolicy(PolicyModel):
    """
    Greedy policy that always chooses locally optimal action
    Based on immediate reward heuristics
    """
    
    def __init__(self, action_space: ActionSpace, reward_fn: RewardFunction):
        super().__init__(action_space)
        self.reward_fn = reward_fn
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> Action:
        """
        Choose action with highest immediate expected reward
        
        Simple heuristic-based greedy strategy
        """
        # Decode state vector to get current conditions
        # state[2] = velocity_x, state[4] = battery%, state[6] = tire_deg
        
        speed = state[2] if len(state) > 2 else 50.0
        battery_pct = state[4] if len(state) > 4 else 50.0
        tire_deg = state[6] if len(state) > 6 else 0.5
        
        # Greedy strategy
        if speed < 70.0:  # Slow, accelerate
            throttle = 0.8
            brake = 0.0
        elif battery_pct < 20.0:  # Low battery, conserve
            throttle = 0.5
            brake = 0.0
        else:  # Normal racing
            throttle = 0.7
            brake = 0.0
        
        steering = 0.0  # Simplified (would use track data)
        attack = battery_pct > 50.0 and tire_deg < 0.3
        
        return Action(throttle, brake, steering, attack)
    
    def update(self, trajectory: List[Tuple], reward: float):
        """Greedy policy doesn't learn from experience"""
        pass


class MDPEnvironment:
    """
    MDP environment wrapper for racing simulation
    
    Provides standard RL interface:
    - reset(): Initialize episode
    - step(action): Execute action, return (state, reward, done, info)
    - get_state(): Current state vector
    """
    
    def __init__(
        self,
        race_engine,
        reward_function: RewardFunction,
        action_space: ActionSpace
    ):
        """
        Args:
            race_engine: FormulaERaceEngine instance
            reward_function: Reward calculator
            action_space: Action space definition
        """
        self.race_engine = race_engine
        self.reward_fn = reward_function
        self.action_space = action_space
        
        self.previous_states = {}  # Car ID -> previous state
        self.episode_rewards = []
    
    def reset(self) -> Dict[int, np.ndarray]:
        """
        Reset environment for new episode
        
        Returns:
            Dictionary of car_id -> initial state vector
        """
        # Reset race engine (would need to implement)
        self.previous_states = {}
        self.episode_rewards = []
        
        # Get initial states
        states = {}
        for car in self.race_engine.race_state.cars:
            states[car.car_id] = car.to_vector()
            self.previous_states[car.car_id] = car
        
        return states
    
    def step(
        self,
        actions: Dict[int, Action]
    ) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Execute one environment step with given actions
        
        Args:
            actions: Dictionary of car_id -> Action
            
        Returns:
            (states, rewards, dones, infos)
            - states: Dict of car_id -> next state vector
            - rewards: Dict of car_id -> reward value
            - dones: Dict of car_id -> episode done flag
            - infos: Dict of car_id -> additional info
        """
        # Apply actions to cars (would integrate with physics engine)
        # For now, this is a placeholder showing the interface
        
        states = {}
        rewards = {}
        dones = {}
        infos = {}
        
        for car_id, action in actions.items():
            car = self.race_engine.race_state.cars[car_id]
            prev_car = self.previous_states.get(car_id)
            
            if prev_car:
                # Calculate reward
                race_context = {
                    'gap_to_ahead': car.gap_to_ahead,
                    'position_change': prev_car.position - car.position
                }
                reward = self.reward_fn.calculate_reward(
                    prev_car, car, action, race_context
                )
                rewards[car_id] = reward
            else:
                rewards[car_id] = 0.0
            
            # Update state
            states[car_id] = car.to_vector()
            self.previous_states[car_id] = CarState(**car.__dict__)
            
            # Check if done
            dones[car_id] = not car.is_active or car.current_lap >= self.race_engine.num_laps
            
            # Additional info
            infos[car_id] = {
                'position': car.position,
                'lap': car.current_lap,
                'battery': car.battery_percentage
            }
        
        return states, rewards, dones, infos
    
    def get_observation_space_size(self) -> int:
        """Return dimension of state vector"""
        return 20  # As defined in CarState.to_vector()
    
    def get_action_space_size(self) -> int:
        """Return dimension of action space"""
        return self.action_space.n_actions
