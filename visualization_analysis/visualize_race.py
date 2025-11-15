"""
Comprehensive Race Data Visualization
Analyzes and visualizes all aspects of the Formula E simulation
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load data
print("Loading race data...")
data_dir = Path(__file__).parent.parent / "backend" / "race_output"
df = pd.read_csv(data_dir / "race_timesteps.csv", encoding='latin-1')

# Rename columns for consistency
df = df.rename(columns={
    'car_id': 'car_number',
    'time': 'race_time',
    'battery_percentage': 'battery_soc',
    'battery_energy_mj': 'battery_energy'
})

# Add derived columns - proper energy calculation
df['dt'] = df.groupby('car_number')['race_time'].diff().fillna(0.05)

# Energy delta per timestep (negative = consumption, positive = regen)
df['energy_delta_mj'] = df.groupby('car_number')['battery_energy'].diff().fillna(0)

# Separate consumption and regeneration
df['energy_consumed_kwh'] = df['energy_delta_mj'].apply(lambda x: abs(x) / 3.6 if x < 0 else 0)  # Only when negative
df['energy_regen_kwh'] = df['energy_delta_mj'].apply(lambda x: x / 3.6 if x > 0 else 0)  # Only when positive

# Power output (kW)
df['power_output_kw'] = (df['energy_delta_mj'].abs() / df['dt']).fillna(0) / 1000

print(f"Loaded {len(df)} timesteps for {df['car_number'].nunique()} cars")
print(f"Time range: {df['race_time'].min():.2f}s to {df['race_time'].max():.2f}s")

# Create output directory
output_dir = Path(__file__).parent / "plots"
output_dir.mkdir(exist_ok=True)

# Get unique cars
cars = sorted(df['car_number'].unique())
car_colors = plt.cm.tab10(np.linspace(0, 1, len(cars)))

print("\n" + "="*60)
print("GENERATING VISUALIZATIONS")
print("="*60)

# ============================================================================
# 1. TRACK POSITION - 2D Bird's Eye View
# ============================================================================
print("\n1. Creating track position visualization...")
fig, ax = plt.subplots(figsize=(14, 10))

for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    # Plot position with time-based color gradient
    points = ax.scatter(car_data['position_x'], car_data['position_y'], 
                       c=car_data['race_time'], cmap='viridis', 
                       s=1, alpha=0.6, label=f'Car {car}')

# Add start/finish markers
for car in cars[:3]:  # Show first 3 cars' start positions
    car_start = df[(df['car_number'] == car) & (df['race_time'] < 1)]
    if len(car_start) > 0:
        ax.plot(car_start['position_x'].iloc[0], car_start['position_y'].iloc[0], 
               'go', markersize=10, alpha=0.7)

ax.set_xlabel('Position X (m)', fontsize=12)
ax.set_ylabel('Position Y (m)', fontsize=12)
ax.set_title('Track Layout - Bird\'s Eye View\n(Color gradient shows time progression)', 
            fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')
cbar = plt.colorbar(points, ax=ax, label='Race Time (s)')
plt.tight_layout()
plt.savefig(output_dir / '1_track_position.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 1_track_position.png")

# ============================================================================
# 2. SPEED PROFILE OVER TIME
# ============================================================================
print("\n2. Creating speed profiles...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# All cars speed over time
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    ax1.plot(car_data['race_time'], car_data['speed_kmh'], 
            label=f'Car {car}', alpha=0.7, linewidth=1)

ax1.set_xlabel('Race Time (s)', fontsize=11)
ax1.set_ylabel('Speed (km/h)', fontsize=11)
ax1.set_title('Speed Profiles - All Cars', fontsize=13, fontweight='bold')
ax1.legend(ncol=5, fontsize=8, loc='upper right')
ax1.grid(True, alpha=0.3)

# Speed vs lap_distance (one lap example)
sample_car = cars[0]
sample_lap = df[(df['car_number'] == sample_car) & 
                (df['current_lap'] == 3)].copy()  # Show lap 3 (Plaksha has longer laps)

if len(sample_lap) > 0:
    ax2.plot(sample_lap['lap_distance'], sample_lap['speed_kmh'], 
            'b-', linewidth=2, label=f'Car {sample_car} - Lap 5')
    ax2.fill_between(sample_lap['lap_distance'], sample_lap['speed_kmh'], 
                     alpha=0.3)
    ax2.set_xlabel('Lap Distance (m)', fontsize=11)
    ax2.set_ylabel('Speed (km/h)', fontsize=11)
    ax2.set_title(f'Speed vs Track Position (Car {sample_car}, Lap 5)', 
                 fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

plt.tight_layout()
plt.savefig(output_dir / '2_speed_profiles.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 2_speed_profiles.png")

# ============================================================================
# 3. STEERING ANGLE ANALYSIS
# ============================================================================
print("\n3. Creating steering analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Steering over time for sample car
sample_data = df[df['car_number'] == cars[0]]
ax1.plot(sample_data['race_time'], np.degrees(sample_data['steering_angle']), 
        'b-', linewidth=1, alpha=0.7)
ax1.set_xlabel('Race Time (s)', fontsize=11)
ax1.set_ylabel('Steering Angle (degrees)', fontsize=11)
ax1.set_title(f'Steering Angle Over Time (Car {cars[0]})', 
             fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)

# Steering angle histogram
all_steering = np.degrees(df['steering_angle'])
ax2.hist(all_steering, bins=50, edgecolor='black', alpha=0.7)
ax2.set_xlabel('Steering Angle (degrees)', fontsize=11)
ax2.set_ylabel('Frequency', fontsize=11)
ax2.set_title('Steering Angle Distribution (All Cars)', 
             fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
ax2.axvline(x=0, color='r', linestyle='--', alpha=0.5, label='Straight')
ax2.legend()

plt.tight_layout()
plt.savefig(output_dir / '3_steering_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 3_steering_analysis.png")

# ============================================================================
# 4. ENERGY MANAGEMENT
# ============================================================================
print("\n4. Creating energy management visualization...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Battery SOC over time
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    ax1.plot(car_data['race_time'], car_data['battery_soc'] * 100, 
            label=f'Car {car}', alpha=0.7, linewidth=1.5)

ax1.set_xlabel('Race Time (s)', fontsize=11)
ax1.set_ylabel('Battery SOC (%)', fontsize=11)
ax1.set_title('Battery State of Charge', fontsize=13, fontweight='bold')
ax1.legend(ncol=5, fontsize=8)
ax1.grid(True, alpha=0.3)

# Battery temperature
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    ax2.plot(car_data['race_time'], car_data['battery_temperature'], 
            label=f'Car {car}', alpha=0.7, linewidth=1.5)

ax2.set_xlabel('Race Time (s)', fontsize=11)
ax2.set_ylabel('Temperature (°C)', fontsize=11)
ax2.set_title('Battery Temperature', fontsize=13, fontweight='bold')
ax2.legend(ncol=5, fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=40, color='orange', linestyle='--', alpha=0.5, label='Optimal')

# Energy consumed vs regenerated (sample car)
sample_data = df[df['car_number'] == cars[0]].copy()
sample_data['cumulative_consumed'] = sample_data['energy_consumed_kwh'].cumsum()
sample_data['cumulative_regen'] = sample_data['energy_regen_kwh'].cumsum()

ax3.plot(sample_data['race_time'], sample_data['cumulative_consumed'], 
        'r-', linewidth=2, label='Consumed')
ax3.plot(sample_data['race_time'], sample_data['cumulative_regen'], 
        'g-', linewidth=2, label='Regenerated')
ax3.fill_between(sample_data['race_time'], 
                sample_data['cumulative_consumed'], 
                sample_data['cumulative_regen'], 
                alpha=0.3, color='orange')
ax3.set_xlabel('Race Time (s)', fontsize=11)
ax3.set_ylabel('Energy (kWh)', fontsize=11)
ax3.set_title(f'Cumulative Energy (Car {cars[0]})', fontsize=13, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Power output distribution
power_output = df['power_output_kw']
ax4.hist(power_output, bins=50, edgecolor='black', alpha=0.7)
ax4.set_xlabel('Power Output (kW)', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.set_title('Power Output Distribution', fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.axvline(x=350, color='orange', linestyle='--', alpha=0.7, label='Race Power (350kW)')
ax4.axvline(x=400, color='red', linestyle='--', alpha=0.7, label='Attack Mode (400kW)')
ax4.legend()

plt.tight_layout()
plt.savefig(output_dir / '4_energy_management.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 4_energy_management.png")

# ============================================================================
# 5. TIRE DEGRADATION
# ============================================================================
print("\n5. Creating tire degradation analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Tire degradation over time
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    ax1.plot(car_data['race_time'], car_data['tire_degradation'] * 100, 
            label=f'Car {car}', alpha=0.7, linewidth=1.5)

ax1.set_xlabel('Race Time (s)', fontsize=11)
ax1.set_ylabel('Tire Degradation (%)', fontsize=11)
ax1.set_title('Tire Degradation Over Time', fontsize=13, fontweight='bold')
ax1.legend(ncol=5, fontsize=8)
ax1.grid(True, alpha=0.3)

# Tire degradation vs distance
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    # Calculate total distance (Plaksha circuit: 2980m per lap)
    total_distance = car_data['current_lap'] * 2980 + car_data['lap_distance']
    ax2.plot(total_distance / 1000, car_data['tire_degradation'] * 100, 
            label=f'Car {car}', alpha=0.7, linewidth=1.5)

ax2.set_xlabel('Total Distance (km)', fontsize=11)
ax2.set_ylabel('Tire Degradation (%)', fontsize=11)
ax2.set_title('Tire Degradation vs Distance', fontsize=13, fontweight='bold')
ax2.legend(ncol=5, fontsize=8)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / '5_tire_degradation.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 5_tire_degradation.png")

# ============================================================================
# 6. RACE POSITION OVER TIME
# ============================================================================
print("\n6. Creating race position chart...")
fig, ax = plt.subplots(figsize=(16, 8))

for car in cars:
    car_data = df[df['car_number'] == car]
    ax.plot(car_data['race_time'], car_data['position'], 
           label=f'Car {car}', linewidth=2, alpha=0.8)

ax.set_xlabel('Race Time (s)', fontsize=11)
ax.set_ylabel('Position', fontsize=11)
ax.set_title('Race Positions Over Time', fontsize=14, fontweight='bold')
ax.legend(ncol=5, fontsize=9)
ax.grid(True, alpha=0.3)
ax.invert_yaxis()  # Position 1 at top
ax.set_yticks(range(1, len(cars) + 1))
plt.tight_layout()
plt.savefig(output_dir / '6_race_positions.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 6_race_positions.png")

# ============================================================================
# 7. ATTACK MODE USAGE
# ============================================================================
print("\n7. Creating attack mode visualization...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# Attack mode status over time
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    # Show when attack mode is active
    attack_active = car_data['attack_mode_active'].astype(int)
    ax1.plot(car_data['race_time'], attack_active + i * 1.2, 
            label=f'Car {car}', linewidth=2)

ax1.set_xlabel('Race Time (s)', fontsize=11)
ax1.set_ylabel('Attack Mode Status (offset per car)', fontsize=11)
ax1.set_title('Attack Mode Activations', fontsize=13, fontweight='bold')
ax1.legend(ncol=5, fontsize=8)
ax1.grid(True, alpha=0.3)

# Attack mode remaining time (sample car)
sample_data = df[df['car_number'] == cars[0]]
ax2.plot(sample_data['race_time'], sample_data['attack_mode_remaining'], 
        'b-', linewidth=2)
ax2.fill_between(sample_data['race_time'], sample_data['attack_mode_remaining'], 
                alpha=0.3)
ax2.set_xlabel('Race Time (s)', fontsize=11)
ax2.set_ylabel('Attack Mode Remaining (s)', fontsize=11)
ax2.set_title(f'Attack Mode Time Remaining (Car {cars[0]})', 
             fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=240, color='r', linestyle='--', alpha=0.5, label='Max Duration (240s)')
ax2.legend()

plt.tight_layout()
plt.savefig(output_dir / '7_attack_mode.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 7_attack_mode.png")

# ============================================================================
# 8. LAP TIMES COMPARISON
# ============================================================================
print("\n8. Creating lap times analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Calculate lap times for each car
lap_times = {}
for car in cars:
    car_data = df[df['car_number'] == car].copy()
    car_data = car_data.sort_values('race_time')
    
    # Find lap completion points (when current_lap increases)
    lap_completions = car_data[car_data['current_lap'].diff() > 0]
    
    if len(lap_completions) > 0:
        lap_numbers = []
        lap_durations = []
        
        prev_time = 0
        for idx, row in lap_completions.iterrows():
            lap_num = row['current_lap']
            lap_time = row['race_time'] - prev_time
            if lap_time > 0 and lap_time < 100:  # Sanity check
                lap_numbers.append(lap_num)
                lap_durations.append(lap_time)
            prev_time = row['race_time']
        
        if lap_durations:
            lap_times[car] = (lap_numbers, lap_durations)
            ax1.plot(lap_numbers, lap_durations, 'o-', label=f'Car {car}', alpha=0.7)

ax1.set_xlabel('Lap Number', fontsize=11)
ax1.set_ylabel('Lap Time (s)', fontsize=11)
ax1.set_title('Lap Times by Car', fontsize=13, fontweight='bold')
ax1.legend(ncol=5, fontsize=8)
ax1.grid(True, alpha=0.3)

# Average lap time per car
avg_lap_times = []
car_labels = []
for car in cars:
    if car in lap_times:
        avg_time = np.mean(lap_times[car][1])
        avg_lap_times.append(avg_time)
        car_labels.append(f'Car {car}')

if avg_lap_times:
    bars = ax2.bar(car_labels, avg_lap_times, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Average Lap Time (s)', fontsize=11)
    ax2.set_title('Average Lap Time Comparison', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Color bars by performance
    colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(bars)))
    sorted_indices = np.argsort(avg_lap_times)
    for i, bar in enumerate(bars):
        rank = np.where(sorted_indices == i)[0][0]
        bar.set_color(colors[rank])

plt.tight_layout()
plt.savefig(output_dir / '8_lap_times.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 8_lap_times.png")

# ============================================================================
# 9. POSITION VS LAP DISTANCE (RACE SNAPSHOT)
# ============================================================================
print("\n9. Creating race snapshot visualization...")
fig, ax = plt.subplots(figsize=(16, 8))

# Take a snapshot at mid-race
mid_time = df['race_time'].median()
snapshot = df[np.abs(df['race_time'] - mid_time) < 0.5].copy()

# Calculate total distance for proper ordering
snapshot['total_distance'] = snapshot['current_lap'] * 2500 + snapshot['lap_distance']
snapshot = snapshot.sort_values('total_distance', ascending=False)

# Plot cars on track
y_positions = range(len(snapshot))
colors_map = {car: car_colors[i] for i, car in enumerate(cars)}

for i, (idx, row) in enumerate(snapshot.iterrows()):
    color = colors_map[row['car_number']]
    ax.barh(i, row['lap_distance'], left=0, color=color, alpha=0.7, 
           edgecolor='black', linewidth=1)
    ax.text(row['lap_distance'] + 50, i, 
           f"Car {row['car_number']} (Lap {row['current_lap']})", 
           va='center', fontsize=9)

ax.set_xlabel('Lap Distance (m)', fontsize=11)
ax.set_ylabel('Position', fontsize=11)
ax.set_title(f'Race Snapshot at t={mid_time:.1f}s', fontsize=14, fontweight='bold')
ax.set_yticks(range(len(snapshot)))
ax.set_yticklabels([f"P{i+1}" for i in range(len(snapshot))])
ax.grid(True, alpha=0.3, axis='x')
ax.set_xlim(0, 2980)  # Plaksha circuit length
plt.tight_layout()
plt.savefig(output_dir / '9_race_snapshot.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 9_race_snapshot.png")

# ============================================================================
# 10. COMPREHENSIVE DASHBOARD
# ============================================================================
print("\n10. Creating comprehensive dashboard...")
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Track position
ax1 = fig.add_subplot(gs[0:2, 0:2])
for i, car in enumerate(cars):
    car_data = df[df['car_number'] == car]
    ax1.scatter(car_data['position_x'], car_data['position_y'], 
               s=0.5, alpha=0.5, label=f'Car {car}')
ax1.set_xlabel('Position X (m)')
ax1.set_ylabel('Position Y (m)')
ax1.set_title('Track Layout', fontweight='bold')
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)

# Speed profile (sample)
ax2 = fig.add_subplot(gs[0, 2])
sample = df[df['car_number'] == cars[0]]
ax2.plot(sample['race_time'], sample['speed_kmh'], 'b-', linewidth=1)
ax2.set_xlabel('Time (s)', fontsize=9)
ax2.set_ylabel('Speed (km/h)', fontsize=9)
ax2.set_title(f'Speed - Car {cars[0]}', fontweight='bold', fontsize=10)
ax2.grid(True, alpha=0.3)

# Battery SOC
ax3 = fig.add_subplot(gs[1, 2])
for car in cars:
    car_data = df[df['car_number'] == car]
    ax3.plot(car_data['race_time'], car_data['battery_soc'] * 100, 
            linewidth=1, alpha=0.7)
ax3.set_xlabel('Time (s)', fontsize=9)
ax3.set_ylabel('SOC (%)', fontsize=9)
ax3.set_title('Battery SOC', fontweight='bold', fontsize=10)
ax3.grid(True, alpha=0.3)

# Race positions
ax4 = fig.add_subplot(gs[2, :])
for car in cars:
    car_data = df[df['car_number'] == car]
    ax4.plot(car_data['race_time'], car_data['position'], 
            label=f'Car {car}', linewidth=2, alpha=0.8)
ax4.set_xlabel('Race Time (s)')
ax4.set_ylabel('Position')
ax4.set_title('Race Positions', fontweight='bold')
ax4.legend(ncol=10, fontsize=8)
ax4.invert_yaxis()
ax4.grid(True, alpha=0.3)

plt.suptitle('Formula E Race Simulation Dashboard', 
            fontsize=16, fontweight='bold', y=0.995)
plt.savefig(output_dir / '10_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: 10_dashboard.png")

# ============================================================================
# STATISTICS SUMMARY
# ============================================================================
print("\n" + "="*60)
print("GENERATING STATISTICS REPORT")
print("="*60)

stats_file = output_dir / 'race_statistics.txt'
with open(stats_file, 'w') as f:
    f.write("="*60 + "\n")
    f.write("FORMULA E SIMULATION STATISTICS\n")
    f.write("="*60 + "\n\n")
    
    # Race overview
    f.write("RACE OVERVIEW\n")
    f.write("-" * 40 + "\n")
    f.write(f"Total Race Time: {df['race_time'].max():.2f} seconds\n")
    f.write(f"Number of Cars: {len(cars)}\n")
    f.write(f"Total Timesteps: {len(df)}\n")
    f.write(f"Timesteps per Car: {len(df[df['car_number'] == cars[0]])}\n")
    f.write(f"Average dt: {df['dt'].mean():.4f} seconds\n\n")
    
    # Position statistics
    f.write("POSITION STATISTICS\n")
    f.write("-" * 40 + "\n")
    f.write(f"Position X Range: {df['position_x'].min():.2f} to {df['position_x'].max():.2f} m\n")
    f.write(f"Position Y Range: {df['position_y'].min():.2f} to {df['position_y'].max():.2f} m\n")
    f.write(f"Total Track Span: {np.sqrt((df['position_x'].max()-df['position_x'].min())**2 + (df['position_y'].max()-df['position_y'].min())**2):.2f} m\n\n")
    
    # Speed statistics
    f.write("SPEED STATISTICS\n")
    f.write("-" * 40 + "\n")
    f.write(f"Min Speed: {df['speed_kmh'].min():.2f} km/h\n")
    f.write(f"Max Speed: {df['speed_kmh'].max():.2f} km/h\n")
    f.write(f"Average Speed: {df['speed_kmh'].mean():.2f} km/h\n")
    f.write(f"Speed Std Dev: {df['speed_kmh'].std():.2f} km/h\n\n")
    
    # Steering statistics
    f.write("STEERING STATISTICS\n")
    f.write("-" * 40 + "\n")
    steering_deg = np.degrees(df['steering_angle'])
    f.write(f"Max Left Steering: {steering_deg.min():.2f}°\n")
    f.write(f"Max Right Steering: {steering_deg.max():.2f}°\n")
    f.write(f"Non-zero Steering: {(df['steering_angle'] != 0).sum()} / {len(df)} timesteps ({(df['steering_angle'] != 0).sum()/len(df)*100:.1f}%)\n\n")
    
    # Energy statistics
    f.write("ENERGY STATISTICS\n")
    f.write("-" * 40 + "\n")
    for car in cars:
        car_data = df[df['car_number'] == car]
        total_consumed = car_data['energy_consumed_kwh'].sum()
        total_regen = car_data['energy_regen_kwh'].sum()
        final_soc = car_data['battery_soc'].iloc[-1]
        f.write(f"Car {car}:\n")
        f.write(f"  Energy Consumed: {total_consumed:.3f} kWh\n")
        f.write(f"  Energy Regenerated: {total_regen:.3f} kWh\n")
        f.write(f"  Net Energy: {total_consumed - total_regen:.3f} kWh\n")
        f.write(f"  Final SOC: {final_soc*100:.1f}%\n")
    f.write("\n")
    
    # Battery temperature
    f.write("BATTERY TEMPERATURE\n")
    f.write("-" * 40 + "\n")
    f.write(f"Min Temperature: {df['battery_temperature'].min():.2f}°C\n")
    f.write(f"Max Temperature: {df['battery_temperature'].max():.2f}°C\n")
    f.write(f"Average Temperature: {df['battery_temperature'].mean():.2f}°C\n\n")
    
    # Tire degradation
    f.write("TIRE DEGRADATION\n")
    f.write("-" * 40 + "\n")
    for car in cars:
        car_data = df[df['car_number'] == car]
        final_deg = car_data['tire_degradation'].iloc[-1]
        f.write(f"Car {car}: {final_deg*100:.2f}%\n")
    f.write("\n")
    
    # Attack mode
    f.write("ATTACK MODE USAGE\n")
    f.write("-" * 40 + "\n")
    for car in cars:
        car_data = df[df['car_number'] == car]
        activations = (car_data['attack_mode_active'].astype(int).diff() > 0).sum()
        total_time = (car_data['attack_mode_active'].astype(int) * car_data['dt']).sum()
        f.write(f"Car {car}:\n")
        f.write(f"  Activations: {activations}\n")
        f.write(f"  Total Active Time: {total_time:.1f} seconds\n")
    f.write("\n")
    
    # Final positions
    f.write("FINAL CLASSIFICATION\n")
    f.write("-" * 40 + "\n")
    final_state = df[df['race_time'] == df['race_time'].max()].sort_values('position')
    for idx, row in final_state.iterrows():
        f.write(f"P{int(row['position'])}: Car {int(row['car_number'])} - {int(row['current_lap'])} laps\n")

print(f"   ✓ Saved: race_statistics.txt")

print("\n" + "="*60)
print("ALL VISUALIZATIONS COMPLETE!")
print("="*60)
print(f"\nOutput location: {output_dir.absolute()}")
print("\nGenerated files:")
print("  1. 1_track_position.png - Bird's eye view of track")
print("  2. 2_speed_profiles.png - Speed over time and distance")
print("  3. 3_steering_analysis.png - Steering behavior")
print("  4. 4_energy_management.png - Battery SOC, temp, and power")
print("  5. 5_tire_degradation.png - Tire wear over time")
print("  6. 6_race_positions.png - Position changes during race")
print("  7. 7_attack_mode.png - Attack mode usage")
print("  8. 8_lap_times.png - Lap time comparison")
print("  9. 9_race_snapshot.png - Mid-race positions")
print(" 10. 10_dashboard.png - Comprehensive overview")
print(" 11. race_statistics.txt - Detailed statistics")
print("\n" + "="*60)
