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
    DriverConfig,
    WeatherConditions,
    CarConfiguration
)
from .leaderboard import Leaderboard, PerformanceMetrics
from .physics import PhysicsEngine
from .events import EventGenerator, StrategyDecisionMaker
from .qualifying import QualifyingSession
from .race_control import RaceControlSystem, FlagType, PenaltyType, Penalty
from .weather import DynamicWeatherSystem, WeatherState

# Visualization (optional import - requires matplotlib)
try:
    from .visualization import RaceVisualizer, LiveRaceAnimator, create_post_race_analysis
    _has_visualization = True
except ImportError:
    _has_visualization = False
    RaceVisualizer = None
    LiveRaceAnimator = None
    create_post_race_analysis = None

__version__ = "2.0.0"
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
    'DriverConfig',
    'WeatherConditions',
    'CarConfiguration',
    
    # Leaderboard and metrics
    'Leaderboard',
    'PerformanceMetrics',
    
    # Physics models
    'PhysicsEngine',
    
    # Event system
    'EventGenerator',
    'StrategyDecisionMaker',
    
    # Qualifying
    'QualifyingSession',
    
    # Race control
    'RaceControlSystem',
    'FlagType',
    'PenaltyType',
    'Penalty',
    
    # Weather
    'DynamicWeatherSystem',
    'WeatherState',
    
    # Visualization (optional)
    'RaceVisualizer',
    'LiveRaceAnimator',
    'create_post_race_analysis',
]
