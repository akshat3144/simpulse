# FastAPI Server - Formula E Race Simulator

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server

```bash
python server.py
```

Server starts on: `http://localhost:8000`

---

## API Endpoints

### REST API

#### Health Check

```
GET /
```

Returns API status and version.

#### Create Race

```
POST /race/create?num_cars=24&num_laps=10&use_ml_strategy=true
```

Creates a new race instance.

**Parameters:**

- `num_cars` (int): Number of cars (default: 24)
- `num_laps` (int): Number of laps (default: 10)
- `use_ml_strategy` (bool): Use ML strategy (default: true)

#### Start Race

```
POST /race/start
```

Starts the race simulation.

#### Pause Race

```
POST /race/pause
```

Pauses the race.

#### Stop Race

```
POST /race/stop
```

Stops and resets the race.

#### Get Race State

```
GET /race/state
```

Returns current race state with all car data.

#### Get Leaderboard

```
GET /race/leaderboard
```

Returns top 10 cars.

#### Health Check

```
GET /health
```

Returns server health status.

---

### WebSocket

#### Real-Time Race Updates

```
ws://localhost:8000/ws/race
```

**Connect and receive updates:**

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/race");

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === "initial_state") {
    console.log("Initial state:", message.data);
  }

  if (message.type === "race_update") {
    console.log("Race update:", message.data);
  }
};
```

**Send commands:**

```javascript
// Start race
ws.send(JSON.stringify({ command: "start" }));

// Pause race
ws.send(JSON.stringify({ command: "pause" }));
```

---

## Data Structures

### Car Object

```json
{
  "id": 0,
  "driver_name": "Driver 1",
  "position": 1,
  "current_lap": 3,
  "lap_distance": 1250.5,
  "total_distance": 6250.5,
  "battery_percentage": 78.5,
  "speed_kmh": 245.3,
  "tire_degradation": 0.15,
  "attack_mode_active": false,
  "attack_mode_uses_left": 2,
  "last_lap_time": 89.2,
  "best_lap_time": 88.5,
  "is_active": true,
  "gap_to_leader": 0.0,
  "gap_to_ahead": 0.0,
  "overtakes_made": 3
}
```

### Race State Object

```json
{
  "current_time": 267.5,
  "current_lap": 3,
  "cars": [...],
  "leaderboard": [...],
  "active_cars": 24,
  "total_cars": 24,
  "race_finished": false
}
```

---

## Testing

### Using curl

**Create race:**

```bash
curl -X POST "http://localhost:8000/race/create?num_cars=12&num_laps=5"
```

**Start race:**

```bash
curl -X POST "http://localhost:8000/race/start"
```

**Get state:**

```bash
curl "http://localhost:8000/race/state"
```

### Using Python

```python
import requests

# Create race
response = requests.post('http://localhost:8000/race/create', params={
    'num_cars': 24,
    'num_laps': 10
})
print(response.json())

# Start race
requests.post('http://localhost:8000/race/start')

# Get state
state = requests.get('http://localhost:8000/race/state').json()
print(state)
```

### Using WebSocket (Python)

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/race"
    async with websockets.connect(uri) as websocket:
        # Start race
        await websocket.send(json.dumps({"command": "start"}))

        # Receive updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Update: {data['type']}")

asyncio.run(test_websocket())
```

---

## Interactive API Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly in the browser!

---

## CORS Configuration

CORS is enabled for:

- `http://localhost:3000` (Next.js dev server)
- `http://localhost:3001` (alternative port)

To add more origins, edit `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    ...
)
```

---

## Features

✅ **REST API** - Full race control via HTTP endpoints
✅ **WebSocket** - Real-time updates at 10 Hz
✅ **CORS Enabled** - Works with frontend
✅ **Auto Docs** - Swagger UI included
✅ **Type Safe** - Full type hints
✅ **Multi-Client** - Multiple WebSocket connections supported
✅ **Race Control** - Start, pause, stop races
✅ **Leaderboard** - Real-time race positions

---

## Architecture

```
FastAPI Server (server.py)
    │
    ├─ REST API Endpoints
    │   ├─ /race/create    → Create race instance
    │   ├─ /race/start     → Start simulation
    │   ├─ /race/pause     → Pause simulation
    │   ├─ /race/stop      → Stop simulation
    │   ├─ /race/state     → Get current state
    │   └─ /race/leaderboard → Get top 10
    │
    ├─ WebSocket Endpoint
    │   └─ /ws/race        → Real-time updates
    │       ├─ Receives: commands (start/pause)
    │       └─ Sends: race_update events
    │
    └─ Race Engine Integration
        └─ FormulaERaceEngine
            ├─ simulate_timestep()
            ├─ race_state (serialized)
            └─ race_finished flag
```

---

## Next Steps

1. **Test the server:**

   ```bash
   python server.py
   # Open http://localhost:8000/docs
   ```

2. **Connect frontend:**

   - Next.js will connect to `ws://localhost:8000/ws/race`
   - React components will receive real-time updates

3. **Deploy:**
   - Use Uvicorn for production
   - Deploy on Heroku/Railway/Render

---

## Status

✅ **FastAPI server is complete and ready to use!**

Run `python server.py` to start the backend.
