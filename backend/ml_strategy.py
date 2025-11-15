"""
Machine Learning strategy components for Formula E race simulation
Implements neural network for racing line prediction and Q-learning for energy management
"""

import numpy as np
from typing import Tuple, Dict, Optional, List
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from .state import CarState
from .config import MLConfig, TrackConfig


class RacingLinePredictor:
    """
    Neural network that predicts optimal racing line (steering and throttle)
    Input: [pos_x, pos_y, vx, vy, energy, tire, attack, opp_dist, segment_type, lap_progress]
    Output: [steering_angle, throttle_percentage]
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize racing line predictor neural network
        
        Args:
            seed: Random seed for reproducibility
        """
        self.config = MLConfig()
        
        # Create feedforward neural network
        self.model = MLPRegressor(
            hidden_layer_sizes=tuple(self.config.NN_HIDDEN_LAYERS),
            activation='relu',
            solver='adam',
            learning_rate_init=self.config.NN_LEARNING_RATE,
            max_iter=200,
            random_state=seed,
            warm_start=True  # Allow incremental learning
        )
        
        # Scaler for input normalization
        self.scaler = StandardScaler()
        
        # Track if model is trained
        self.is_trained = False
        
        # Generate synthetic training data
        self._initialize_with_synthetic_data()
    
    def _initialize_with_synthetic_data(self):
        """
        Initialize model with synthetic racing data
        This provides a baseline before real race learning
        """
        n_samples = 1000
        rng = np.random.RandomState(42)
        
        # Generate synthetic inputs
        X = np.zeros((n_samples, self.config.NN_INPUT_DIM))
        
        for i in range(n_samples):
            # Position (normalized 0-1)
            X[i, 0] = rng.uniform(0, 1)  # pos_x
            X[i, 1] = rng.uniform(-0.5, 0.5)  # pos_y (lateral)
            
            # Velocity (normalized)
            X[i, 2] = rng.uniform(0, 1)  # vx
            X[i, 3] = rng.uniform(-0.1, 0.1)  # vy
            
            # Energy (0-100)
            X[i, 4] = rng.uniform(30, 100)
            
            # Tire degradation (0-1)
            X[i, 5] = rng.uniform(0, 0.8)
            
            # Attack mode (binary)
            X[i, 6] = rng.choice([0, 1], p=[0.9, 0.1])
            
            # Opponent distance (meters, 0-100)
            X[i, 7] = rng.uniform(0, 100)
            X[i, 8] = rng.uniform(0, 100)
            
            # Segment type (0=straight, 1=corner, 2=chicane)
            X[i, 9] = rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
        
        # Generate synthetic outputs (simplified racing logic)
        y = np.zeros((n_samples, self.config.NN_OUTPUT_DIM))
        
        for i in range(n_samples):
            segment_type = int(X[i, 9])
            velocity = X[i, 2]
            energy = X[i, 4]
            
            # Steering (simplified - depends on segment)
            if segment_type == 0:  # Straight
                y[i, 0] = 0.0
            elif segment_type == 1:  # Corner
                y[i, 0] = rng.uniform(-0.5, 0.5)
            else:  # Chicane
                y[i, 0] = rng.uniform(-0.3, 0.3)
            
            # Throttle (depends on velocity and energy)
            if velocity < 0.7:
                y[i, 1] = 0.8 if energy > 30 else 0.5
            elif velocity > 0.95:
                y[i, 1] = 0.3
            else:
                y[i, 1] = 0.6
        
        # Fit scaler and model
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def prepare_input(
        self,
        car: CarState,
        opponent_distances: List[float],
        segment_type: str,
        track_config: TrackConfig
    ) -> np.ndarray:
        """
        Prepare input vector for neural network
        
        Args:
            car: Current car state
            opponent_distances: List of distances to nearby opponents
            segment_type: Current track segment type
            track_config: Track configuration
            
        Returns:
            Input vector of shape (1, input_dim)
        """
        # Normalize position
        pos_x_norm = car.lap_distance / track_config.total_length
        pos_y_norm = car.position_y / 10.0  # Normalize lateral position
        
        # Normalize velocity
        vx_norm = car.velocity_x / 80.0  # Normalize to ~280 km/h = 78 m/s
        vy_norm = car.velocity_y / 10.0
        
        # Get closest opponents
        if len(opponent_distances) >= 2:
            opp1_dist = opponent_distances[0]
            opp2_dist = opponent_distances[1]
        elif len(opponent_distances) == 1:
            opp1_dist = opponent_distances[0]
            opp2_dist = 100.0
        else:
            opp1_dist = opp2_dist = 100.0
        
        # Encode segment type
        segment_encoding = {
            'straight': 0.0,
            'left_corner': 1.0,
            'right_corner': 1.0,
            'chicane': 2.0
        }
        segment_code = segment_encoding.get(segment_type, 0.0)
        
        # Construct input vector
        input_vec = np.array([[
            pos_x_norm,
            pos_y_norm,
            vx_norm,
            vy_norm,
            car.battery_percentage,
            car.tire_degradation,
            float(car.attack_mode_active),
            opp1_dist,
            opp2_dist,
            segment_code
        ]])
        
        return input_vec
    
    def predict_controls(
        self,
        car: CarState,
        opponent_distances: List[float],
        segment_type: str,
        track_config: TrackConfig
    ) -> Tuple[float, float]:
        """
        Predict optimal steering and throttle
        
        Args:
            car: Current car state
            opponent_distances: Distances to opponents
            segment_type: Track segment type
            track_config: Track configuration
            
        Returns:
            (steering_angle, throttle) tuple
        """
        if not self.is_trained:
            # Fallback to simple controls
            return 0.0, 0.7
        
        # Prepare input
        X = self.prepare_input(car, opponent_distances, segment_type, track_config)
        
        # Scale input
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        
        # Extract and clip outputs
        steering_angle = np.clip(prediction[0], -1.0, 1.0)
        throttle = np.clip(prediction[1], 0.0, 1.0)
        
        return steering_angle, throttle
    
    def update_model(self, X: np.ndarray, y: np.ndarray):
        """
        Update model with new training data (online learning)
        
        Args:
            X: Input features
            y: Target outputs
        """
        if X.shape[0] == 0:
            return
        
        # Update scaler
        self.scaler.partial_fit(X)
        
        # Transform and train
        X_scaled = self.scaler.transform(X)
        self.model.partial_fit(X_scaled, y)


class EnergyManagementQLearning:
    """
    Q-Learning agent for energy management strategy
    State: [lap_number, energy_remaining, position, gap_to_leader]
    Actions: [conserve_energy, neutral, aggressive, activate_attack_mode]
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize Q-learning agent
        
        Args:
            seed: Random seed
        """
        self.config = MLConfig()
        self.rng = np.random.RandomState(seed)
        
        # Q-table: dictionary mapping state -> action values
        self.q_table: Dict[tuple, np.ndarray] = {}
        
        # Learning parameters
        self.alpha = self.config.Q_LEARNING_RATE
        self.gamma = self.config.Q_DISCOUNT_FACTOR
        self.epsilon = self.config.Q_EPSILON
        self.epsilon_decay = self.config.Q_EPSILON_DECAY
        
        # Action space
        self.actions = self.config.ACTIONS
        self.num_actions = len(self.actions)
        
        # State discretization
        self.state_bins = self.config.Q_STATE_DISCRETIZATION
    
    def discretize_state(
        self,
        car: CarState,
        total_laps: int
    ) -> tuple:
        """
        Discretize continuous state into bins
        
        Args:
            car: Current car state
            total_laps: Total race laps
            
        Returns:
            Discretized state tuple
        """
        # Lap number (0 to total_laps)
        lap_bin = min(
            int(car.current_lap / total_laps * self.state_bins['lap_number']),
            self.state_bins['lap_number'] - 1
        )
        
        # Energy remaining (0-100%)
        energy_bin = min(
            int(car.battery_percentage / 100.0 * self.state_bins['energy_remaining']),
            self.state_bins['energy_remaining'] - 1
        )
        
        # Position (1 to num_cars)
        position_bin = min(
            int(car.position / 24 * self.state_bins['position']),
            self.state_bins['position'] - 1
        )
        
        # Gap to leader (0-60 seconds)
        gap_normalized = min(car.gap_to_leader / 60.0, 1.0)
        gap_bin = min(
            int(gap_normalized * self.state_bins['gap_to_leader']),
            self.state_bins['gap_to_leader'] - 1
        )
        
        return (lap_bin, energy_bin, position_bin, gap_bin)
    
    def get_q_values(self, state: tuple) -> np.ndarray:
        """
        Get Q-values for a state, initialize if not seen before
        
        Args:
            state: Discretized state tuple
            
        Returns:
            Array of Q-values for each action
        """
        if state not in self.q_table:
            # Initialize with small random values
            self.q_table[state] = self.rng.uniform(-0.01, 0.01, self.num_actions)
        
        return self.q_table[state]
    
    def select_action(
        self,
        car: CarState,
        total_laps: int,
        epsilon: Optional[float] = None
    ) -> str:
        """
        Select action using epsilon-greedy policy
        
        Args:
            car: Current car state
            total_laps: Total race laps
            epsilon: Exploration rate (uses self.epsilon if None)
            
        Returns:
            Selected action string
        """
        if epsilon is None:
            epsilon = self.epsilon
        
        # Discretize state
        state = self.discretize_state(car, total_laps)
        
        # Get Q-values
        q_values = self.get_q_values(state)
        
        # Epsilon-greedy selection
        if self.rng.random() < epsilon:
            # Explore: random action
            action_idx = self.rng.randint(self.num_actions)
        else:
            # Exploit: best action
            action_idx = np.argmax(q_values)
        
        return self.actions[action_idx]
    
    def update_q_value(
        self,
        state: tuple,
        action: str,
        reward: float,
        next_state: tuple,
        done: bool
    ):
        """
        Update Q-value using Q-learning update rule
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        # Get current Q-value
        q_values = self.get_q_values(state)
        action_idx = self.actions.index(action)
        current_q = q_values[action_idx]
        
        # Get max Q-value for next state
        if done:
            max_next_q = 0.0
        else:
            next_q_values = self.get_q_values(next_state)
            max_next_q = np.max(next_q_values)
        
        # Q-learning update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        
        # Update Q-table
        self.q_table[state][action_idx] = new_q
    
    def calculate_reward(
        self,
        prev_car: CarState,
        current_car: CarState,
        action: str
    ) -> float:
        """
        Calculate reward for the action taken
        
        Args:
            prev_car: Previous car state
            current_car: Current car state
            action: Action taken
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Reward for maintaining good position
        if current_car.position <= 5:
            reward += 2.0
        elif current_car.position <= 10:
            reward += 1.0
        
        # Reward for overtaking
        if current_car.position < prev_car.position:
            reward += 5.0
        
        # Penalty for being overtaken
        if current_car.position > prev_car.position:
            reward -= 3.0
        
        # Reward for energy efficiency
        if current_car.battery_percentage > 50:
            reward += 1.0
        elif current_car.battery_percentage < 10:
            reward -= 5.0  # Danger of running out
        
        # Penalty if car retired
        if not current_car.is_active:
            reward -= 20.0
        
        # Action-specific rewards
        if action == 'conserve_energy':
            # Reward if energy was low
            if prev_car.battery_percentage < 30:
                reward += 2.0
        elif action == 'aggressive':
            # Reward if we gained position
            if current_car.position < prev_car.position:
                reward += 3.0
        elif action == 'activate_attack_mode':
            # Reward if we were close to someone
            if prev_car.gap_to_ahead < 2.0:
                reward += 4.0
        
        return reward
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon, 0.01)
    
    def save_q_table(self, filepath: str):
        """Save Q-table to file"""
        np.save(filepath, dict(self.q_table))
    
    def load_q_table(self, filepath: str):
        """Load Q-table from file"""
        loaded = np.load(filepath, allow_pickle=True).item()
        self.q_table = loaded


class MLStrategyCoordinator:
    """
    Coordinates both ML components (neural network + Q-learning)
    Provides unified interface for ML-driven strategy
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize ML strategy coordinator
        
        Args:
            seed: Random seed
        """
        self.racing_line_predictor = RacingLinePredictor(seed)
        self.energy_management = EnergyManagementQLearning(seed)
        
        # Training data buffers
        self.nn_training_buffer = {'X': [], 'y': []}
        self.prev_states = {}  # Track previous states for Q-learning
    
    def get_ml_controls(
        self,
        car: CarState,
        opponent_distances: List[float],
        segment_type: str,
        track_config: TrackConfig,
        total_laps: int
    ) -> Tuple[float, float, str]:
        """
        Get ML-driven controls for car
        
        Args:
            car: Current car state
            opponent_distances: Distances to opponents
            segment_type: Track segment type
            track_config: Track configuration
            total_laps: Total race laps
            
        Returns:
            (steering_angle, throttle, energy_strategy)
        """
        # Get racing line from neural network
        steering, throttle = self.racing_line_predictor.predict_controls(
            car, opponent_distances, segment_type, track_config
        )
        
        # Get energy strategy from Q-learning
        energy_strategy = self.energy_management.select_action(car, total_laps)
        
        # Modify throttle based on energy strategy
        if energy_strategy == 'conserve_energy':
            throttle *= 0.7
        elif energy_strategy == 'aggressive':
            throttle *= 1.2
            throttle = min(throttle, 1.0)
        
        return steering, throttle, energy_strategy
    
    def update_learning(
        self,
        car_id: int,
        prev_car: CarState,
        current_car: CarState,
        action: str,
        total_laps: int
    ):
        """
        Update both ML models based on race outcomes
        
        Args:
            car_id: Car identifier
            prev_car: Previous car state
            current_car: Current car state
            action: Action taken
            total_laps: Total race laps
        """
        # Update Q-learning
        prev_state = self.energy_management.discretize_state(prev_car, total_laps)
        current_state = self.energy_management.discretize_state(current_car, total_laps)
        reward = self.energy_management.calculate_reward(prev_car, current_car, action)
        done = not current_car.is_active
        
        self.energy_management.update_q_value(
            prev_state, action, reward, current_state, done
        )
