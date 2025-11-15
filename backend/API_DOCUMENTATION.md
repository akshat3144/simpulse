# Formula E Race Simulator API Documentation

Version: 2.0.0

## Overview

The Formula E Race Simulator API provides comprehensive endpoints for running complete race weekends including qualifying, race simulation with dynamic weather, race control (penalties, flags, safety car), and real-time WebSocket updates.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### 1. Race Management

#### Initialize Race

```http
POST /api/race/initialize
Content-Type: application/json

{
  "num_cars": 24,
  "num_laps": 10,
  "track_name": "Monaco",
  "random_seed": 42,
  "enable_attack_mode": true,
  "timestep": 0.05
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Race initialized successfully",
  "config": {
    "num_cars": 24,
    "num_laps": 10,
    "track_name": "Monaco",
    "track_length": 1948.0,
    "total_distance_km": 19.48,
    "starting_grid_applied": true
  }
}
```

#### Start Race

```http
POST /api/race/start
```

**Response:**

```json
{
  "status": "success",
  "message": "Race started successfully"
}
```

#### Stop Race

```http
POST /api/race/stop
```

#### Get Race Status

```http
GET /api/race/status
```

**Response:**

```json
{
  "is_running": true,
  "is_finished": false,
  "current_time": 125.5,
  "current_step": 2510,
  "num_active_cars": 24,
  "leader_lap": 3,
  "real_time_factor": 1500.0
}
```

#### Get Race Summary

```http
GET /api/race/summary
```

#### Apply Starting Grid

```http
POST /api/race/apply-grid
```

Applies qualifying results to race starting order.

---

### 2. Qualifying System

#### Start Qualifying Session

```http
POST /api/qualifying/start
Content-Type: application/json

{
  "num_cars": 24,
  "num_flying_laps": 2,
  "track_name": "Monaco",
  "random_seed": 42
}
```

**Response:**

```json
{
  "status": "success",
  "results": [
    {
      "position": 1,
      "driver_id": 4,
      "driver_name": "Jean-Éric Vergne",
      "team": "DS Penske",
      "lap_time": 27.279,
      "skill": 1.09
    },
    ...
  ],
  "starting_grid": [4, 7, 3, 2, ...]
}
```

#### Get Qualifying Results

```http
GET /api/qualifying/results
```

Returns stored qualifying results and starting grid order.

---

### 3. Race Control System

#### Get Penalties

```http
GET /api/race/penalties
```

**Response:**

```json
{
  "penalties": [
    {
      "car_id": 5,
      "driver_name": "Stoffel Vandoorne",
      "penalty_type": "5s_time_penalty",
      "reason": "Track limits violation (3 warnings)",
      "lap_issued": 8,
      "time_penalty": 5.0,
      "served": false
    }
  ],
  "warnings": {
    "3": 2,
    "5": 3
  },
  "track_limit_violations": {
    "5": 4,
    "12": 2
  }
}
```

#### Get Flag Status

```http
GET /api/race/flags
```

**Response:**

```json
{
  "current_flag": "green",
  "safety_car_active": false,
  "safety_car_deployment_time": null,
  "flag_sectors": ["green", "green", "green"]
}
```

#### Deploy Safety Car

```http
POST /api/race/safety-car/deploy?reason=Crash%20at%20Turn%205&duration=180.0
```

**Response:**

```json
{
  "status": "success",
  "message": "Safety car deployed: Crash at Turn 5"
}
```

---

### 4. Weather System

#### Initialize Weather

```http
POST /api/weather/initialize
Content-Type: application/json

{
  "initial_temp": 28.0,
  "initial_humidity": 0.65,
  "initial_rain": 0.0,
  "random_seed": 42
}
```

**Response:**

```json
{
  "status": "success",
  "weather": {
    "temperature": 28.0,
    "humidity": 0.65,
    "rain_intensity": 0.0,
    "wind_speed": 2.5,
    "wind_direction": 1.57,
    "track_wetness": 0.0,
    "grip_multiplier": 1.0,
    "description": "Warm (28.0°C), Dry, dry track"
  }
}
```

#### Get Current Weather

```http
GET /api/weather/current
```

Returns current weather state with same format as initialization.

---

### 5. Information Endpoints

#### Get All Drivers

```http
GET /api/drivers
```

Returns list of all 24 Formula E drivers with teams and statistics.

#### Get Track Information

```http
GET /api/track/{track_name}
```

**Example:** `GET /api/track/Monaco`

**Response:**

```json
{
  "name": "Monaco",
  "total_length": 1948.0,
  "num_segments": 10,
  "lap_record_seconds": 90.0,
  "attack_mode_zones": 2,
  "pit_lane_length": 250.0,
  "pit_lane_speed_limit_kmh": 60.0,
  "segments": [...]
}
```

#### Health Check

```http
GET /api/health
```

---

## WebSocket Connection

### Endpoint

```
ws://localhost:8000/ws/race
```

### Connection

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/race");

ws.onopen = () => {
  console.log("Connected to race simulator");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleRaceUpdate(data);
};
```

### Message Types

#### 1. Connection Confirmation

```json
{
  "type": "connection",
  "message": "Connected to Formula E Race Simulator",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

#### 2. Race Update (sent every ~2 seconds)

```json
{
  "type": "race_update",
  "timestamp": 125.5,
  "step": 2510,
  "leaderboard": [
    {
      "position": 1,
      "car_id": 4,
      "driver_name": "Jean-Éric Vergne",
      "current_lap": 5,
      "lap_distance": 1234.5,
      "total_distance": 10982.5,
      "speed_kmh": 245.3,
      "battery_percentage": 78.5,
      "attack_mode_active": true,
      "best_lap_time": 89.234,
      "status": "Running"
    },
    ...
  ],
  "events": [
    {
      "type": "attack_mode",
      "timestamp": 124.8,
      "description": "Jean-Éric Vergne activates Attack Mode!"
    }
  ],
  "race_status": {
    "is_finished": false,
    "leader_lap": 5,
    "num_active_cars": 24,
    "real_time_factor": 1500.0
  },
  "weather": {
    "temperature": 28.2,
    "humidity": 0.66,
    "rain_intensity": 0.0,
    "track_wetness": 0.0,
    "grip_multiplier": 1.0,
    "description": "Warm (28.2°C), Dry, dry track"
  },
  "race_control": {
    "current_flag": "green",
    "safety_car_active": false,
    "total_penalties": 2,
    "recent_penalties": [...]
  }
}
```

#### 3. Race Finished

```json
{
  "type": "race_finished",
  "summary": {
    "race_info": {...},
    "final_standings": [...],
    "performance_metrics": {...},
    "events": {...}
  },
  "penalties": [...],
  "race_control_summary": {
    "current_flag": "green",
    "safety_car_active": false,
    "total_penalties": 5,
    "total_warnings": 12,
    "track_limit_violations": 28
  },
  "final_weather": {...}
}
```

---

## Complete Race Weekend Workflow

### 1. Run Qualifying

```bash
# Start qualifying session
curl -X POST http://localhost:8000/api/qualifying/start \
  -H "Content-Type: application/json" \
  -d '{
    "num_cars": 24,
    "num_flying_laps": 2,
    "track_name": "Monaco",
    "random_seed": 42
  }'

# Get results
curl http://localhost:8000/api/qualifying/results
```

### 2. Initialize Race

```bash
curl -X POST http://localhost:8000/api/race/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "num_cars": 24,
    "num_laps": 15,
    "track_name": "Monaco",
    "random_seed": 42
  }'
```

### 3. Optional: Initialize Custom Weather

```bash
curl -X POST http://localhost:8000/api/weather/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "initial_temp": 30.0,
    "initial_humidity": 0.75,
    "initial_rain": 0.2
  }'
```

### 4. Start Race

```bash
curl -X POST http://localhost:8000/api/race/start
```

### 5. Connect WebSocket for Live Updates

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/race");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "race_update") {
    updateLeaderboard(data.leaderboard);
    updateWeather(data.weather);
    updateFlags(data.race_control);
  }
};
```

### 6. Monitor Race Control

```bash
# Check penalties
curl http://localhost:8000/api/race/penalties

# Check flag status
curl http://localhost:8000/api/race/flags

# Deploy safety car if needed
curl -X POST "http://localhost:8000/api/race/safety-car/deploy?reason=Incident&duration=240"
```

### 7. Get Final Results

```bash
curl http://localhost:8000/api/race/summary
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:

- `400`: Bad Request (invalid parameters, race not initialized)
- `404`: Not Found
- `500`: Internal Server Error

---

## Python Client Example

```python
import requests
import websocket
import json

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/race"

# 1. Run qualifying
response = requests.post(f"{BASE_URL}/api/qualifying/start", json={
    "num_cars": 10,
    "num_flying_laps": 2,
    "random_seed": 42
})
print("Qualifying:", response.json())

# 2. Initialize race
response = requests.post(f"{BASE_URL}/api/race/initialize", json={
    "num_cars": 10,
    "num_laps": 5,
    "random_seed": 42
})
print("Race initialized:", response.json())

# 3. Start race
response = requests.post(f"{BASE_URL}/api/race/start")
print("Race started:", response.json())

# 4. Connect to WebSocket
def on_message(ws, message):
    data = json.loads(message)
    if data['type'] == 'race_update':
        print(f"Lap {data['race_status']['leader_lap']}: "
              f"{data['leaderboard'][0]['driver_name']} leads")

ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
ws.run_forever()
```

---

## Notes

- All POST endpoints accept JSON payloads
- WebSocket updates are sent approximately every 2 seconds during active race
- Weather system updates every simulation timestep (default 0.05s)
- Race control checks are performed every timestep
- Starting grid from qualifying is automatically applied when race is initialized
- Penalties are applied to final results automatically

---

## Server Startup

```bash
cd backend
python run_server.py
```

Server will start on `http://localhost:8000`

Interactive API documentation available at: `http://localhost:8000/docs`
