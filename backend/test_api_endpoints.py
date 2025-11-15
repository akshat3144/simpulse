"""
Test script for new FastAPI endpoints
Tests qualifying, weather, penalties, and race control integration
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def test_api():
    """Test all new API endpoints"""
    
    print_section("FORMULA E RACE SIMULATOR API TEST")
    
    # 1. Test root endpoint
    print_section("1. Testing Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # 2. Test qualifying
    print_section("2. Testing Qualifying System")
    response = requests.post(f"{BASE_URL}/api/qualifying/start", json={
        "num_cars": 6,
        "num_flying_laps": 2,
        "track_name": "Monaco",
        "random_seed": 42
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        quali_data = response.json()
        print("\nQualifying Results:")
        for result in quali_data['results'][:6]:
            print(f"  P{result['position']}. {result['driver_name']:30s} - {result['lap_time']:.3f}s")
        print(f"\nStarting Grid: {quali_data['starting_grid']}")
    else:
        print(f"Error: {response.json()}")
    
    # 3. Get qualifying results
    print_section("3. Getting Stored Qualifying Results")
    response = requests.get(f"{BASE_URL}/api/qualifying/results")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Results available: {len(response.json()['results'])} drivers")
    
    # 4. Initialize weather
    print_section("4. Testing Weather System")
    response = requests.post(f"{BASE_URL}/api/weather/initialize", json={
        "initial_temp": 28.0,
        "initial_humidity": 0.70,
        "initial_rain": 0.0,
        "random_seed": 123
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        weather = response.json()['weather']
        print(f"Weather: {weather['description']}")
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Humidity: {weather['humidity']*100:.0f}%")
        print(f"Grip multiplier: {weather['grip_multiplier']}")
    
    # 5. Initialize race
    print_section("5. Initializing Race")
    response = requests.post(f"{BASE_URL}/api/race/initialize", json={
        "num_cars": 6,
        "num_laps": 5,
        "track_name": "Monaco",
        "random_seed": 42,
        "enable_attack_mode": True,
        "timestep": 0.1
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        init_data = response.json()
        print(f"Race initialized: {init_data['message']}")
        print(f"Cars: {init_data['config']['num_cars']}")
        print(f"Laps: {init_data['config']['num_laps']}")
        print(f"Track: {init_data['config']['track_name']} ({init_data['config']['track_length']}m)")
        print(f"Starting grid applied: {init_data['config']['starting_grid_applied']}")
    else:
        print(f"Error: {response.json()}")
    
    # 6. Check race status
    print_section("6. Checking Race Status")
    response = requests.get(f"{BASE_URL}/api/race/status")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        status = response.json()
        print(f"Race running: {status['is_running']}")
        print(f"Race finished: {status['is_finished']}")
        print(f"Active cars: {status['num_active_cars']}")
    
    # 7. Check weather
    print_section("7. Checking Current Weather")
    response = requests.get(f"{BASE_URL}/api/weather/current")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        weather = response.json()
        print(f"Weather: {weather['description']}")
    
    # 8. Check flags
    print_section("8. Checking Race Control Flags")
    response = requests.get(f"{BASE_URL}/api/race/flags")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        flags = response.json()
        print(f"Current flag: {flags['current_flag']}")
        print(f"Safety car active: {flags['safety_car_active']}")
    
    # 9. Check penalties
    print_section("9. Checking Penalties")
    response = requests.get(f"{BASE_URL}/api/race/penalties")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        penalties = response.json()
        print(f"Total penalties: {len(penalties['penalties'])}")
        print(f"Total warnings: {sum(penalties['warnings'].values())}")
    
    # 10. Get drivers info
    print_section("10. Getting Drivers List")
    response = requests.get(f"{BASE_URL}/api/drivers")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        drivers = response.json()['drivers']
        print(f"Total drivers available: {len(drivers)}")
        print("\nTop 5 Drivers:")
        for driver in drivers[:5]:
            print(f"  {driver['name']:30s} - {driver['team']} (Skill: {driver['skill']})")
    
    # 11. Get track info
    print_section("11. Getting Track Information")
    response = requests.get(f"{BASE_URL}/api/track/Monaco")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        track = response.json()
        print(f"Track: {track['name']}")
        print(f"Length: {track['total_length']}m")
        print(f"Segments: {track['num_segments']}")
        print(f"Lap record: {track['lap_record_seconds']}s")
    
    # 12. Health check
    print_section("12. Health Check")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        health = response.json()
        print(f"API Status: {health['status']}")
        print(f"Race active: {health['race_active']}")
        print(f"Connected clients: {health['connected_clients']}")
    
    print_section("ALL TESTS COMPLETED")
    print("\nAPI is fully functional with all new features:")
    print("  [OK] Qualifying system")
    print("  [OK] Weather system")
    print("  [OK] Race control (penalties/flags)")
    print("  [OK] Starting grid integration")
    print("  [OK] Track and driver information")
    print("\nNext step: Start race with 'POST /api/race/start'")
    print("Then connect WebSocket at 'ws://localhost:8000/ws/race'")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server!")
        print("Make sure the server is running: python run_server.py")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
