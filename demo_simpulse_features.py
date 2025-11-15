"""
SimPulse Feature Demonstration
Shows the new stochastic dynamics, MDP framework, and mathematical features
"""

import numpy as np
import sys
sys.path.insert(0, '.')

# Import SimPulse modules
from backend.engine import FormulaERaceEngine
from backend.config import TrackConfig, SimulationConfig
from backend.stochastic_dynamics import StochasticNoiseModel, StochasticEventModel
from backend.mdp_framework import (
    MDPEnvironment, ActionSpace, RewardFunction,
    RandomPolicy, GreedyPolicy, Action
)

def demo_stochastic_noise():
    """Demonstrate Gaussian noise model"""
    print("\n" + "="*70)
    print("🎲 STOCHASTIC DYNAMICS DEMONSTRATION")
    print("="*70)
    
    # Initialize noise model
    noise_model = StochasticNoiseModel(seed=42)
    
    # Test control noise
    print("\n1. Control Input Noise (Driver Imperfection)")
    print("-" * 70)
    throttle, brake, steering = 0.80, 0.0, 0.15
    print(f"   Intended controls: throttle={throttle:.3f}, brake={brake:.3f}, steering={steering:.3f}")
    
    for consistency in [1.0, 0.9, 0.7, 0.5]:
        noisy_t, noisy_b, noisy_s = noise_model.apply_control_noise(
            throttle, brake, steering, consistency
        )
        print(f"   Consistency {consistency:.1f}: throttle={noisy_t:.3f}, brake={noisy_b:.3f}, steering={noisy_s:.3f}")
    
    # Test tire degradation noise
    print("\n2. Tire Degradation Stochastic Model")
    print("-" * 70)
    base_deg = 0.001  # Base degradation rate
    for temp in [70, 90, 110]:
        noisy_deg = noise_model.apply_tire_degradation_noise(base_deg, temp)
        print(f"   Temp {temp}°C: base={base_deg:.6f} → noisy={noisy_deg:.6f} (Δ={noisy_deg-base_deg:+.6f})")
    
    # Test energy consumption noise
    print("\n3. Energy Consumption Variability")
    print("-" * 70)
    base_energy = 50000.0  # 50 kJ
    for batt_temp in [30, 40, 50]:
        noisy_energy = noise_model.apply_energy_consumption_noise(base_energy, batt_temp)
        efficiency = (noisy_energy / base_energy - 1) * 100
        print(f"   Battery {batt_temp}°C: {base_energy:.0f}J → {noisy_energy:.0f}J ({efficiency:+.2f}% variation)")


def demo_performance_index():
    """Demonstrate performance index calculation"""
    print("\n" + "="*70)
    print("📊 PERFORMANCE INDEX CALCULATION (SimPulse P_i)")
    print("="*70)
    
    from backend.state import CarState
    
    # Create sample car states
    scenarios = [
        {"name": "Leading (High P)", "speed": 85, "battery": 75, "tire_deg": 0.15, "accel": 2.5},
        {"name": "Conservative", "speed": 70, "battery": 85, "tire_deg": 0.08, "accel": 1.8},
        {"name": "Aggressive", "speed": 88, "battery": 55, "tire_deg": 0.35, "accel": 2.8},
        {"name": "Struggling", "speed": 65, "battery": 25, "tire_deg": 0.60, "accel": 1.2},
    ]
    
    print("\n   Scenario              | v(t) | a(t) | e(t) | τ(t) | ψ(t) | P_i(t)")
    print("-" * 70)
    
    for scenario in scenarios:
        car = CarState(car_id=0, driver_name="Test")
        car.velocity_x = scenario["speed"]
        car.battery_percentage = scenario["battery"]
        car.tire_degradation = scenario["tire_deg"]
        car.acceleration = scenario["accel"]
        
        P_i = car.get_performance_index()
        
        # Get normalized components
        from backend.config import PhysicsConfig
        v_norm = car.get_speed() / PhysicsConfig.MAX_SPEED_MS
        a_norm = car.acceleration / PhysicsConfig.MAX_ACCELERATION
        e_norm = car.battery_percentage / 100.0
        tau_norm = 1.0 - car.tire_degradation
        psi = (v_norm + tau_norm + e_norm) / 3.0
        
        print(f"   {scenario['name']:20s} | {v_norm:.2f} | {a_norm:.2f} | {e_norm:.2f} | {tau_norm:.2f} | {psi:.2f} | {P_i:.3f}")


def demo_mdp_framework():
    """Demonstrate MDP environment and policies"""
    print("\n" + "="*70)
    print("🧠 MDP FRAMEWORK DEMONSTRATION")
    print("="*70)
    
    # Create action space
    print("\n1. Action Space")
    print("-" * 70)
    
    discrete_space = ActionSpace(action_type='discrete')
    continuous_space = ActionSpace(action_type='continuous')
    
    print(f"   Discrete action space: {discrete_space.n_actions} actions")
    print(f"   Continuous action space: {continuous_space.n_actions} dimensions")
    
    # Sample random actions
    print("\n   Sample discrete actions:")
    for i in [0, 50, 100, 150]:
        action = discrete_space.get_discrete_action(i)
        print(f"      Action {i}: throttle={action.throttle:.2f}, brake={action.brake:.2f}, "
              f"steering={action.steering:.2f}, attack={action.activate_attack}")
    
    print("\n   Sample continuous actions:")
    for _ in range(3):
        action = continuous_space.sample()
        print(f"      Random: throttle={action.throttle:.3f}, brake={action.brake:.3f}, "
              f"steering={action.steering:.3f}, attack={action.activate_attack}")
    
    # Reward function
    print("\n2. Reward Function Components")
    print("-" * 70)
    reward_fn = RewardFunction()
    print(f"   Weights: {reward_fn.weights}")
    
    # Test reward calculation
    from backend.state import CarState
    car_prev = CarState(0, "Driver 1")
    car_prev.position = 5
    car_prev.battery_percentage = 70
    car_prev.tire_degradation = 0.2
    car_prev.velocity_x = 80
    car_prev.gap_to_leader = 5.0
    
    car_next = CarState(0, "Driver 1")
    car_next.position = 4  # Overtook someone!
    car_next.battery_percentage = 68
    car_next.tire_degradation = 0.22
    car_next.velocity_x = 82
    car_next.gap_to_leader = 4.5
    car_next.total_distance = 100.0
    
    action = Action(throttle=0.8, brake=0.0, steering=0.1, activate_attack=False)
    race_context = {'gap_to_ahead': 1.5, 'position_change': 1}
    
    reward = reward_fn.calculate_reward(car_prev, car_next, action, race_context)
    print(f"\n   Example transition reward: {reward:.3f}")
    print(f"      Position gain: +1 (P5 → P4)")
    print(f"      Speed increase: {car_prev.velocity_x:.1f} → {car_next.velocity_x:.1f} m/s")
    print(f"      Gap reduction: {car_prev.gap_to_leader:.2f} → {car_next.gap_to_leader:.2f} s")
    
    # Policy comparison
    print("\n3. Policy Models")
    print("-" * 70)
    
    random_policy = RandomPolicy(continuous_space, seed=42)
    greedy_policy = GreedyPolicy(continuous_space, reward_fn)
    
    print("   Random Policy:")
    state = np.random.randn(20)  # Mock state
    for i in range(3):
        action = random_policy.get_action(state)
        print(f"      Sample {i+1}: throttle={action.throttle:.3f}, brake={action.brake:.3f}")
    
    print("\n   Greedy Policy (heuristic-based):")
    # Test with different state conditions
    states = [
        ("Low speed", np.array([0] * 20)),  # state[2] = velocity_x = 0
        ("Low battery", np.array([50.0] * 2 + [0] * 2 + [15.0] + [0] * 15)),  # battery 15%
        ("Normal racing", np.array([50.0] * 2 + [75.0] + [0] + [70.0] + [0] * 15))  # normal
    ]
    
    for name, state in states:
        action = greedy_policy.get_action(state)
        print(f"      {name}: throttle={action.throttle:.2f}, brake={action.brake:.2f}, attack={action.activate_attack}")


def demo_stochastic_events():
    """Demonstrate probabilistic event models"""
    print("\n" + "="*70)
    print("⚡ STOCHASTIC EVENT MODELS")
    print("="*70)
    
    event_model = StochasticEventModel(seed=42)
    
    print("\n1. Weibull Mechanical Failure Model")
    print("-" * 70)
    print("   Component Age | Stress Level | Failure Probability")
    print("   " + "-" * 50)
    
    for age in [0, 1800, 3600, 5400]:  # 0, 30min, 1hr, 1.5hr
        for stress in [0.3, 0.7, 1.0]:
            prob = event_model.mechanical_failure_probability(age, stress)
            print(f"   {age:5d}s        | {stress:.1f}          | {prob:.6f}")
    
    print("\n2. Poisson Event Process")
    print("-" * 70)
    
    lambda_rates = [0.001, 0.01, 0.1]  # Events per second
    dt = 1.0  # 1 second interval
    
    print(f"   Event Rate (λ) | P(event in {dt}s) | Expected in 100s")
    print("   " + "-" * 50)
    
    for lambda_rate in lambda_rates:
        prob = 1.0 - np.exp(-lambda_rate * dt)
        expected = lambda_rate * 100
        print(f"   {lambda_rate:.3f}/s      | {prob:.5f}         | {expected:.1f} events")


def demo_vector_space():
    """Demonstrate vector space state representation"""
    print("\n" + "="*70)
    print("🔢 VECTOR SPACE STATE REPRESENTATION")
    print("="*70)
    
    from backend.state import CarState
    
    # Create car state
    car = CarState(car_id=5, driver_name="Test Driver")
    car.velocity_x = 75.0
    car.velocity_y = 2.5
    car.position_x = 1250.0
    car.battery_percentage = 68.5
    car.tire_degradation = 0.23
    car.attack_mode_active = True
    car.current_lap = 7
    
    # Convert to vector
    state_vec = car.to_vector()
    
    print("\n   State Vector x(t) ∈ ℝ²⁰:")
    print("-" * 70)
    print(f"   Dimensions: {len(state_vec)}")
    print(f"\n   Vector representation:")
    print(f"   {state_vec}")
    
    print(f"\n   Interpretation:")
    print(f"      x[0] = position_x    = {state_vec[0]:.2f} m")
    print(f"      x[1] = position_y    = {state_vec[1]:.2f} m")
    print(f"      x[2] = velocity_x    = {state_vec[2]:.2f} m/s")
    print(f"      x[3] = velocity_y    = {state_vec[3]:.2f} m/s")
    print(f"      x[4] = battery%      = {state_vec[4]:.2f}%")
    print(f"      x[6] = tire_deg      = {state_vec[6]:.3f}")
    print(f"      x[8] = attack_active = {bool(state_vec[8])}")
    print(f"      x[10]= current_lap   = {int(state_vec[10])}")
    
    # Reconstruct from vector
    reconstructed = CarState.from_vector(state_vec, 5, "Test Driver")
    print(f"\n   Reconstruction successful: velocity_x = {reconstructed.velocity_x:.2f} m/s")
    
    # State matrix for multiple cars
    print("\n   State Matrix for N cars: X(t) ∈ ℝ^(N×20)")
    print("-" * 70)
    from backend.state import RaceState
    
    race = RaceState(3, [
        {'name': 'Driver 1', 'skill': 1.0, 'aggression': 0.7},
        {'name': 'Driver 2', 'skill': 1.0, 'aggression': 0.8},
        {'name': 'Driver 3', 'skill': 1.0, 'aggression': 0.6}
    ])
    
    state_matrix = race.get_state_matrix()
    print(f"   Matrix shape: {state_matrix.shape}")
    print(f"   Matrix preview (3 cars × 20 dimensions):")
    print(f"   {state_matrix[:, :5]}")  # Show first 5 dims


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "SimPulse Framework Demo" + " "*25 + "║")
    print("║" + " "*68 + "║")
    print("║  Stochastic Dynamics + MDP Framework + Mathematical Models  ║")
    print("╚" + "="*68 + "╝")
    
    try:
        demo_vector_space()
        demo_performance_index()
        demo_stochastic_noise()
        demo_stochastic_events()
        demo_mdp_framework()
        
        print("\n" + "="*70)
        print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\n🎯 SimPulse Features:")
        print("   ✓ Vector space state representation (x ∈ ℝ²⁰)")
        print("   ✓ Stochastic dynamics: x(t+1) = f(x,u,θ) + ε(t)")
        print("   ✓ Performance index: P_i(t) with 5 components")
        print("   ✓ MDP framework (S, A, P, R, γ)")
        print("   ✓ Probabilistic event models (Weibull, Poisson)")
        print("   ✓ Multi-objective reward functions")
        print("   ✓ Policy models (Random, Greedy, RL-ready)")
        
        print("\n📚 Next Steps:")
        print("   1. Run backend/run_server.py to start simulation")
        print("   2. Integrate RL agents (PPO, SAC, TD3)")
        print("   3. Enable stochastic dynamics in config.py")
        print("   4. Analyze performance index correlations")
        print("   5. Test different noise intensities\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
