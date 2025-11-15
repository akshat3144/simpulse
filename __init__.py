"""
Formula E Race Simulator Package
A comprehensive mathematical engine for simulating Formula E races
"""

from .engine import FormulaERaceEngine
from .state import CarState, RaceState
from .config import (
    PhysicsConfig,
    TrackConfig,
    SimulationConfig,
    MLConfig,
    DriverConfig
)
from .leaderboard import Leaderboard, PerformanceMetrics
from .physics import PhysicsEngine, MotionModel, EnergyModel, TireModel
from .events import EventGenerator, StrategyDecisionMaker
from .ml_strategy import RacingLinePredictor, EnergyManagementQLearning, MLStrategyCoordinator

__version__ = "1.0.0"
__author__ = "Formula E Simulator Team"

__all__ = [
    # Main engine
    'FormulaERaceEngine',
    
    # State management
    'CarState',
    'RaceState',
    
    # Configuration
    'PhysicsConfig',
    'TrackConfig',
    'SimulationConfig',
    'MLConfig',
    'DriverConfig',
    
    # Leaderboard and metrics
    'Leaderboard',
    'PerformanceMetrics',
    
    # Physics models
    'PhysicsEngine',
    'MotionModel',
    'EnergyModel',
    'TireModel',
    
    # Event system
    'EventGenerator',
    'StrategyDecisionMaker',
    
    # ML components
    'RacingLinePredictor',
    'EnergyManagementQLearning',
    'MLStrategyCoordinator',
]
