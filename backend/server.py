"""
FastAPI Server for Formula E Race Simulator
Provides REST API and WebSocket for real-time race data
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime

from .engine import FormulaERaceEngine
from .state import RaceState, CarState
from .config import TrackConfig

app = FastAPI(
    title="Formula E Race Simulator API",
    description="Real-time race simulation with WebSocket support",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global race engine instance
race_engine: FormulaERaceEngine = None
race_active: bool = False
connected_clients: List[WebSocket] = []


def serialize_car(car: CarState) -> Dict[str, Any]:
    """Convert CarState to JSON-serializable dict"""
    return {
        "id": car.car_id,
        "driver_name": car.driver_name,
        "position": car.position,
        "current_lap": car.current_lap,
        "lap_distance": car.lap_distance,
        "total_distance": car.total_distance,
        "battery_percentage": car.battery_percentage,
        "battery_energy": car.battery_energy,
        "battery_temperature": car.battery_temperature,
        "tire_degradation": car.tire_degradation,
        "grip_coefficient": car.grip_coefficient,
        "velocity_x": car.velocity_x,
        "velocity_y": car.velocity_y,
        "speed": (car.velocity_x**2 + car.velocity_y**2)**0.5,
        "speed_kmh": ((car.velocity_x**2 + car.velocity_y**2)**0.5) * 3.6,
        "attack_mode_active": car.attack_mode_active,
        "attack_mode_remaining": car.attack_mode_remaining,
        "attack_mode_uses_left": car.attack_mode_uses_left,
        "last_lap_time": car.last_lap_time,
        "best_lap_time": car.best_lap_time,
        "is_active": car.is_active,
        "gap_to_leader": car.gap_to_leader,
        "gap_to_ahead": car.gap_to_ahead,
        "total_energy_consumed": car.total_energy_consumed,
        "max_speed_achieved": car.max_speed_achieved,
        "overtakes_made": car.overtakes_made,
        "time": car.time
    }


def serialize_race_state(state: RaceState) -> Dict[str, Any]:
    """Convert RaceState to JSON-serializable dict"""
    cars = [serialize_car(car) for car in state.cars]
    
    # Sort by position for leaderboard
    sorted_cars = sorted(
        [car for car in cars if car["is_active"]],
        key=lambda c: (-c["current_lap"], -c["total_distance"])
    )
    
    # Add positions
    for i, car in enumerate(sorted_cars):
        car["position"] = i + 1
    
    return {
        "current_time": state.current_time,
        "current_lap": state.current_lap,
        "cars": cars,
        "leaderboard": sorted_cars[:10],  # Top 10
        "active_cars": len([c for c in cars if c["is_active"]]),
        "total_cars": len(cars),
        "race_finished": race_engine.race_finished if race_engine else False
    }


@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Formula E Race Simulator API",
        "version": "1.0.0",
        "status": "running",
        "race_active": race_active
    }


@app.post("/race/create")
async def create_race(
    num_cars: int = 24,
    num_laps: int = 10,
    use_ml_strategy: bool = True
):
    """Create a new race instance"""
    global race_engine, race_active
    
    try:
        race_engine = FormulaERaceEngine(
            num_cars=num_cars,
            num_laps=num_laps,
            use_ml_strategy=use_ml_strategy
        )
        race_active = False
        
        return {
            "status": "success",
            "message": "Race created successfully",
            "config": {
                "num_cars": num_cars,
                "num_laps": num_laps,
                "track_length": race_engine.track_config.total_length,
                "use_ml_strategy": use_ml_strategy
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.get("/race/state")
async def get_race_state():
    """Get current race state"""
    if not race_engine:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "No race created"}
        )
    
    return serialize_race_state(race_engine.race_state)


@app.post("/race/start")
async def start_race():
    """Start the race"""
    global race_active
    
    if not race_engine:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "No race created"}
        )
    
    race_active = True
    return {"status": "success", "message": "Race started"}


@app.post("/race/pause")
async def pause_race():
    """Pause the race"""
    global race_active
    race_active = False
    return {"status": "success", "message": "Race paused"}


@app.post("/race/stop")
async def stop_race():
    """Stop and reset the race"""
    global race_engine, race_active
    race_engine = None
    race_active = False
    return {"status": "success", "message": "Race stopped"}


@app.get("/race/leaderboard")
async def get_leaderboard():
    """Get current leaderboard"""
    if not race_engine:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "No race created"}
        )
    
    state = serialize_race_state(race_engine.race_state)
    return {"leaderboard": state["leaderboard"]}


@app.websocket("/ws/race")
async def websocket_race(websocket: WebSocket):
    """WebSocket endpoint for real-time race updates"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        print(f"Client connected. Total clients: {len(connected_clients)}")
        
        # Send initial state
        if race_engine:
            initial_state = serialize_race_state(race_engine.race_state)
            await websocket.send_json({
                "type": "initial_state",
                "data": initial_state
            })
        
        # Listen for client messages
        while True:
            try:
                # Check for client messages (with timeout)
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1
                )
                
                data = json.loads(message)
                
                # Handle client commands
                if data.get("command") == "start":
                    global race_active
                    race_active = True
                    await websocket.send_json({
                        "type": "command_response",
                        "data": {"status": "started"}
                    })
                    
                elif data.get("command") == "pause":
                    race_active = False
                    await websocket.send_json({
                        "type": "command_response",
                        "data": {"status": "paused"}
                    })
                    
            except asyncio.TimeoutError:
                # No message received, continue to simulation
                pass
            
            # Simulation loop
            if race_active and race_engine and not race_engine.race_finished:
                # Simulate one timestep
                race_engine.simulate_timestep()
                
                # Send updated state to all connected clients
                state = serialize_race_state(race_engine.race_state)
                
                for client in connected_clients[:]:  # Copy list to avoid modification issues
                    try:
                        await client.send_json({
                            "type": "race_update",
                            "data": state,
                            "timestamp": datetime.now().isoformat()
                        })
                    except:
                        # Remove disconnected clients
                        if client in connected_clients:
                            connected_clients.remove(client)
                
                # Control update rate (10 updates per second)
                await asyncio.sleep(0.1)
            else:
                # When not racing, just wait
                await asyncio.sleep(0.1)
                
    except WebSocketDisconnect:
        print("Client disconnected")
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"Total clients: {len(connected_clients)}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "race_engine": "initialized" if race_engine else "not_initialized",
        "race_active": race_active,
        "connected_clients": len(connected_clients)
    }
