"""
FastAPI Server for Formula E Race Simulator
Provides REST API and WebSocket endpoints for real-time race simulation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import uvicorn
from datetime import datetime
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.engine import FormulaERaceEngine
    from backend.config import (
        TrackConfig, SimulationConfig, DriverConfig,
        track_config, simulation_config
    )
    from backend.qualifying import QualifyingSession
    from backend.race_control import RaceControlSystem
    from backend.weather import DynamicWeatherSystem
except ImportError:
    from engine import FormulaERaceEngine
    from config import (
        TrackConfig, SimulationConfig, DriverConfig,
        track_config, simulation_config
    )
    from qualifying import QualifyingSession
    from race_control import RaceControlSystem
    from weather import DynamicWeatherSystem

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("=" * 80)
    print("Formula E Race Simulator API Starting...")
    print("=" * 80)
    print(f"Track: {track_config.track_name}")
    print(f"Track Length: {track_config.total_length:.0f}m")
    print(f"Available Drivers: {len(DriverConfig.DRIVERS)}")
    print("=" * 80)
    
    yield
    
    # Shutdown
    global simulation_task
    
    if simulation_task and not simulation_task.done():
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
    
    print("Formula E Race Simulator API Shutdown")

# Initialize FastAPI app
app = FastAPI(
    title="Formula E Race Simulator API",
    description="Real-time Formula E race simulation with physics-based engine",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global race engine instance
race_engine: Optional[FormulaERaceEngine] = None
qualifying_session: Optional[QualifyingSession] = None
race_control: Optional[RaceControlSystem] = None
weather_system: Optional[DynamicWeatherSystem] = None
simulation_task: Optional[asyncio.Task] = None
connected_clients: List[WebSocket] = []
starting_grid: Optional[List[int]] = None
race_active: bool = False


# Pydantic models for request/response
class RaceConfig(BaseModel):
    """Race configuration parameters"""
    num_cars: int = Field(default=24, ge=2, le=24, description="Number of cars (2-24)")
    num_laps: int = Field(default=10, ge=1, le=100, description="Number of laps (1-100)")
    track_name: str = Field(default="Monaco", description="Track name")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    enable_attack_mode: bool = Field(default=True, description="Enable attack mode")
    timestep: float = Field(default=0.05, ge=0.01, le=0.1, description="Simulation timestep in seconds")


class QualifyingConfig(BaseModel):
    """Qualifying session configuration"""
    num_cars: int = Field(default=24, ge=2, le=24, description="Number of cars")
    num_flying_laps: int = Field(default=2, ge=1, le=5, description="Number of flying laps per driver")
    track_name: str = Field(default="Monaco", description="Track name")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")


class WeatherConfig(BaseModel):
    """Weather system configuration"""
    initial_temp: float = Field(default=25.0, ge=10.0, le=45.0, description="Initial temperature (°C)")
    initial_humidity: float = Field(default=0.60, ge=0.0, le=1.0, description="Initial humidity (0-1)")
    initial_rain: float = Field(default=0.0, ge=0.0, le=1.0, description="Initial rain intensity (0-1)")
    random_seed: Optional[int] = Field(default=None, description="Random seed")


class SimulationControl(BaseModel):
    """Simulation control commands"""
    action: str = Field(..., description="Action: start, pause, resume, stop, step")
    steps: Optional[int] = Field(default=1, description="Number of steps for 'step' action")


class RaceStatus(BaseModel):
    """Current race status"""
    is_running: bool
    is_finished: bool
    current_time: float
    current_step: int
    num_active_cars: int
    leader_lap: int
    real_time_factor: float


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Formula E Race Simulator API",
        "version": "2.0.0",
        "status": "online",
        "endpoints": {
            "race": {
                "initialize": "POST /api/race/initialize",
                "start": "POST /api/race/start",
                "stop": "POST /api/race/stop",
                "status": "GET /api/race/status",
                "summary": "GET /api/race/summary",
                "apply_grid": "POST /api/race/apply-grid",
                "export": "POST /api/race/export/json"
            },
            "qualifying": {
                "start": "POST /api/qualifying/start",
                "results": "GET /api/qualifying/results"
            },
            "race_control": {
                "penalties": "GET /api/race/penalties",
                "flags": "GET /api/race/flags",
                "deploy_safety_car": "POST /api/race/safety-car/deploy"
            },
            "weather": {
                "initialize": "POST /api/weather/initialize",
                "current": "GET /api/weather/current"
            },
            "info": {
                "drivers": "GET /api/drivers",
                "track": "GET /api/track/{track_name}",
                "health": "GET /api/health"
            },
            "websocket": "ws://localhost:8000/ws/race",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "race_active": race_engine is not None,
        "connected_clients": len(manager.active_connections)
    }


@app.post("/api/race/initialize")
async def initialize_race(config: RaceConfig):
    """Initialize a new race session"""
    global race_engine, race_control, weather_system, simulation_task, race_active
    
    try:
        # Stop existing simulation if running
        if simulation_task and not simulation_task.done():
            simulation_task.cancel()
            try:
                await simulation_task
            except asyncio.CancelledError:
                pass
        
        race_active = False
        
        # Create new race engine
        track = TrackConfig(track_name=config.track_name)
        race_engine = FormulaERaceEngine(
            num_cars=config.num_cars,
            num_laps=config.num_laps,
            track_config=track,
            random_seed=config.random_seed
        )
        
        # Initialize race control system
        race_control = RaceControlSystem(random_seed=config.random_seed)
        
        # Initialize weather system (default conditions)
        weather_system = DynamicWeatherSystem(
            initial_temp=25.0,
            initial_humidity=0.60,
            initial_rain=0.0,
            random_seed=config.random_seed + 100 if config.random_seed else None
        )
        
        # Update simulation config
        simulation_config.TIMESTEP = config.timestep
        simulation_config.ENABLE_ATTACK_MODE = config.enable_attack_mode
        
        # Apply starting grid if available
        if starting_grid and len(starting_grid) == config.num_cars:
            race_engine.set_starting_grid(starting_grid)
        
        return {
            "status": "success",
            "message": "Race initialized successfully",
            "config": {
                "num_cars": config.num_cars,
                "num_laps": config.num_laps,
                "track_name": config.track_name,
                "track_length": round(track.total_length, 2),
                "total_distance_km": round((track.total_length * config.num_laps) / 1000, 2),
                "starting_grid_applied": starting_grid is not None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize race: {str(e)}")


@app.post("/api/race/start")
async def start_race():
    """Start the race simulation"""
    global race_engine, simulation_task
    
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized. Call /api/race/initialize first.")
    
    if simulation_task and not simulation_task.done():
        raise HTTPException(status_code=400, detail="Race already running")
    
    # Start simulation task
    simulation_task = asyncio.create_task(run_simulation())
    
    return {
        "status": "success",
        "message": "Race started"
    }


@app.post("/api/race/stop")
async def stop_race():
    """Stop the race simulation"""
    global simulation_task
    
    if simulation_task and not simulation_task.done():
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
        
        return {
            "status": "success",
            "message": "Race stopped"
        }
    
    return {
        "status": "info",
        "message": "No race running"
    }


@app.get("/api/race/status")
async def get_race_status() -> RaceStatus:
    """Get current race status"""
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    is_running = simulation_task is not None and not simulation_task.done()
    
    # Find leader lap
    leader_lap = 0
    if race_engine.race_state.cars:
        active_cars = [c for c in race_engine.race_state.cars if c.is_active]
        if active_cars:
            leader_lap = max(c.current_lap for c in active_cars)
    
    return RaceStatus(
        is_running=is_running,
        is_finished=race_engine.race_finished,
        current_time=race_engine.race_state.current_time,
        current_step=race_engine.current_step,
        num_active_cars=len([c for c in race_engine.race_state.cars if c.is_active]),
        leader_lap=leader_lap,
        real_time_factor=race_engine.real_time_factor
    )


@app.get("/api/race/leaderboard")
async def get_leaderboard():
    """Get current race leaderboard"""
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    return {
        "timestamp": race_engine.race_state.current_time,
        "leaderboard": race_engine.get_leaderboard()
    }


@app.get("/api/race/car/{car_id}")
async def get_car_state(car_id: int):
    """Get detailed state for a specific car"""
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    if car_id < 0 or car_id >= race_engine.num_cars:
        raise HTTPException(status_code=404, detail=f"Car {car_id} not found")
    
    car = race_engine.race_state.cars[car_id]
    return car.to_dict()


@app.get("/api/race/events")
async def get_race_events():
    """Get recent race events"""
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    return {
        "total_events": len(race_engine.event_log),
        "events": [event.to_dict() for event in race_engine.event_log[-50:]]  # Last 50 events
    }


@app.get("/api/race/summary")
async def get_race_summary():
    """Get comprehensive race summary"""
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    return race_engine.get_race_summary()


@app.post("/api/qualifying/start")
async def start_qualifying(config: QualifyingConfig):
    """Start a qualifying session"""
    global qualifying_session, starting_grid
    
    try:
        track = TrackConfig(track_name=config.track_name)
        
        # Get driver configs
        driver_configs = [DriverConfig.get_driver(i) for i in range(config.num_cars)]
        
        qualifying_session = QualifyingSession(
            track_config=track,
            driver_configs=driver_configs,
            random_seed=config.random_seed
        )
        
        # Run qualifying
        results = qualifying_session.run_qualifying(
            num_flying_laps=config.num_flying_laps,
            verbose=False
        )
        
        # Store starting grid for race
        starting_grid = qualifying_session.get_starting_grid()
        
        return {
            "status": "success",
            "results": [
                {
                    "position": r["qualifying_position"],
                    "driver_id": r["driver_id"],
                    "driver_name": r["driver_name"],
                    "team": r["team"],
                    "lap_time": r["best_lap_time"],
                    "skill": r["skill"]
                }
                for r in results
            ],
            "starting_grid": starting_grid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qualifying failed: {str(e)}")


@app.get("/api/drivers")
async def get_drivers():
    """Get list of all drivers"""
    return {
        "drivers": DriverConfig.DRIVERS
    }


@app.get("/api/track/{track_name}")
async def get_track_info(track_name: str):
    """Get track configuration details"""
    try:
        track = TrackConfig(track_name=track_name)
        
        return {
            "name": track.track_name,
            "total_length": round(track.total_length, 2),
            "num_segments": len(track.segments),
            "lap_record_seconds": track.lap_record_seconds,
            "attack_mode_zones": len(track.attack_mode_zones),
            "pit_lane_length": track.pit_lane_length,
            "pit_lane_speed_limit_kmh": track.pit_lane_speed_limit_kmh,
            "segments": [
                {
                    "type": seg.segment_type,
                    "length": round(seg.length, 2),
                    "ideal_speed_kmh": seg.ideal_speed_kmh,
                    "attack_mode_zone": seg.attack_mode_zone
                }
                for seg in track.segments
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load track: {str(e)}")


@app.post("/api/race/export/json")
async def export_race_json():
    """Export race data to JSON"""
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    summary = race_engine.get_race_summary()
    return summary


@app.post("/api/weather/initialize")
async def initialize_weather(config: WeatherConfig):
    """Initialize weather system"""
    global weather_system
    
    try:
        weather_system = DynamicWeatherSystem(
            initial_temp=config.initial_temp,
            initial_humidity=config.initial_humidity,
            initial_rain=config.initial_rain,
            random_seed=config.random_seed
        )
        
        return {
            "status": "success",
            "weather": weather_system.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather initialization failed: {str(e)}")


@app.get("/api/weather/current")
async def get_current_weather():
    """Get current weather state"""
    if weather_system is None:
        raise HTTPException(status_code=400, detail="Weather system not initialized")
    
    return weather_system.to_dict()


@app.get("/api/race/penalties")
async def get_penalties():
    """Get all penalties issued during the race"""
    if race_control is None:
        raise HTTPException(status_code=400, detail="Race control not initialized")
    
    return {
        "penalties": [p.to_dict() for p in race_control.penalties],
        "warnings": race_control.warnings,
        "track_limit_violations": race_control.track_limit_violations
    }


@app.get("/api/race/flags")
async def get_flag_status():
    """Get current flag and safety car status"""
    if race_control is None:
        raise HTTPException(status_code=400, detail="Race control not initialized")
    
    return {
        "current_flag": race_control.current_flag.value,
        "safety_car_active": race_control.safety_car_active,
        "safety_car_deployment_time": race_control.safety_car_deployment_time if race_control.safety_car_active else None,
        "flag_sectors": [flag.value for flag in race_control.flag_sectors]
    }


@app.post("/api/race/safety-car/deploy")
async def deploy_safety_car(reason: str, duration: float = 180.0):
    """Deploy safety car"""
    if race_control is None:
        raise HTTPException(status_code=400, detail="Race control not initialized")
    
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    race_control.deploy_safety_car(
        reason=reason,
        current_time=race_engine.race_state.current_time,
        duration=duration
    )
    
    return {
        "status": "success",
        "message": f"Safety car deployed: {reason}"
    }


@app.get("/api/qualifying/results")
async def get_qualifying_results():
    """Get qualifying results"""
    if qualifying_session is None:
        raise HTTPException(status_code=400, detail="No qualifying session completed")
    
    if not qualifying_session.results:
        raise HTTPException(status_code=400, detail="Qualifying session not completed")
    
    return {
        "results": qualifying_session.results,
        "starting_grid": starting_grid if starting_grid else []
    }


@app.post("/api/race/apply-grid")
async def apply_starting_grid():
    """Apply qualifying results to race starting grid"""
    global race_engine, starting_grid
    
    if race_engine is None:
        raise HTTPException(status_code=400, detail="Race not initialized")
    
    if starting_grid is None:
        raise HTTPException(status_code=400, detail="No qualifying results available")
    
    try:
        race_engine.set_starting_grid(starting_grid)
        return {
            "status": "success",
            "message": f"Starting grid applied: {len(starting_grid)} cars reordered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply grid: {str(e)}")


# WebSocket endpoint for real-time updates
@app.websocket("/ws/race")
async def websocket_race_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time race updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Formula E Race Simulator",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages (for potential control commands)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                message = json.loads(data)
                
                # Handle client commands
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


# Background simulation task
async def run_simulation():
    """Run the race simulation and broadcast updates"""
    global race_engine, race_control, weather_system, race_active
    
    if race_engine is None:
        return
    
    print("Starting race simulation...")
    race_active = True
    
    try:
        update_interval = 20  # Send updates every N steps
        step_count = 0
        max_steps = int(race_engine.num_laps * 120 / race_engine.dt)
        
        while not race_engine.race_finished and step_count < max_steps:
            # Update weather
            if weather_system:
                weather_system.update(race_engine.dt)
            
            # Simulate timestep
            state_matrix, leaderboard_data, events = race_engine.simulate_timestep()
            
            # Apply race control checks
            if race_control:
                for car in race_engine.race_state.cars:
                    if car.is_active:
                        # Check track limits
                        race_control.check_track_limits(car, track_width=12.0)
                        
                        # Check unsafe behavior
                        other_cars = [c for c in race_engine.race_state.cars if c.car_id != car.car_id]
                        race_control.check_unsafe_behavior(car, other_cars)
                        
                        # Check energy limit
                        race_control.check_energy_limit(car)
                
                # Update safety car
                race_control.update_safety_car(race_engine.race_state.current_time)
                if race_control.safety_car_active:
                    race_control.apply_safety_car_effects(race_engine.race_state.cars)
            
            step_count += 1
            
            # Broadcast updates at regular intervals
            if step_count % update_interval == 0:
                # Prepare update message
                update_message = {
                    "type": "race_update",
                    "timestamp": race_engine.race_state.current_time,
                    "step": step_count,
                    "leaderboard": leaderboard_data[:10],  # Top 10
                    "events": events,
                    "race_status": {
                        "is_finished": race_engine.race_finished,
                        "leader_lap": max(c.current_lap for c in race_engine.race_state.cars if c.is_active) if any(c.is_active for c in race_engine.race_state.cars) else 0,
                        "num_active_cars": len([c for c in race_engine.race_state.cars if c.is_active]),
                        "real_time_factor": race_engine.real_time_factor
                    }
                }
                
                # Add weather data
                if weather_system:
                    update_message["weather"] = weather_system.to_dict()
                
                # Add race control data
                if race_control:
                    update_message["race_control"] = {
                        "current_flag": race_control.current_flag.value,
                        "safety_car_active": race_control.safety_car_active,
                        "total_penalties": len(race_control.penalties),
                        "recent_penalties": [p.to_dict() for p in race_control.penalties[-3:]] if race_control.penalties else []
                    }
                
                # Broadcast to all connected clients
                await manager.broadcast(update_message)
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.001)
        
        # Apply penalties to final results
        if race_control:
            # Get final results from leaderboard
            final_results = []
            for entry in race_engine.leaderboard.entries:
                result = {
                    'car_id': entry.car_id,
                    'driver_name': entry.driver_name,
                    'position': entry.position,
                    'current_lap': entry.current_lap,
                    'best_lap_time': entry.best_lap_time,
                    'total_time': race_engine.race_state.current_time,
                    'is_active': entry.is_active
                }
                final_results.append(result)
            
            # Apply penalties
            final_results = race_control.apply_penalties_to_results(final_results)
        
        # Send final race results
        final_message = {
            "type": "race_finished",
            "summary": race_engine.get_race_summary()
        }
        
        if race_control:
            final_message["penalties"] = [p.to_dict() for p in race_control.penalties]
            final_message["race_control_summary"] = race_control.get_status_summary()
        
        if weather_system:
            final_message["final_weather"] = weather_system.to_dict()
        
        await manager.broadcast(final_message)
        
        print("Race simulation completed!")
        race_active = False
        
    except asyncio.CancelledError:
        print("Race simulation cancelled")
        race_active = False
        raise
    except Exception as e:
        print(f"Error in simulation: {e}")
        error_message = {
            "type": "error",
            "message": str(e)
        }
        await manager.broadcast(error_message)


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
