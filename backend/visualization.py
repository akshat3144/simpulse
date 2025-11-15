"""
Real-time visualization module for Formula E race simulation
Provides matplotlib-based live charts and graphs
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import numpy as np
from typing import List, Dict, Optional
from collections import deque
from .state import RaceState, CarState


class RaceVisualizer:
    """
    Real-time race visualization using matplotlib
    Creates live updating charts for position, energy, speed, etc.
    """
    
    def __init__(self, num_cars: int = 24, history_length: int = 300):
        """
        Initialize visualizer
        
        Args:
            num_cars: Number of cars to track
            history_length: Number of timesteps to keep in history
        """
        self.num_cars = num_cars
        self.history_length = history_length
        
        # Data storage
        self.time_history = deque(maxlen=history_length)
        self.position_history = {i: deque(maxlen=history_length) for i in range(num_cars)}
        self.energy_history = {i: deque(maxlen=history_length) for i in range(num_cars)}
        self.speed_history = {i: deque(maxlen=history_length) for i in range(num_cars)}
        self.lap_history = {i: [] for i in range(num_cars)}
        
        # Setup figure
        self.fig = None
        self.axes = {}
        self.lines = {}
        self.bars = {}
        
        # Color map for cars
        self.colors = plt.cm.tab20(np.linspace(0, 1, num_cars))
        
        # Animation
        self.anim = None
        self.paused = False
        
    def setup_figure(self):
        """Create matplotlib figure with multiple subplots"""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Formula E Race Simulation - Live Telemetry', 
                         fontsize=16, fontweight='bold')
        
        # Create grid layout: 2x3 subplots
        gs = GridSpec(3, 3, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # 1. Position chart (top-left, spanning 2 columns)
        self.axes['position'] = self.fig.add_subplot(gs[0, :2])
        self.axes['position'].set_title('Race Positions', fontweight='bold')
        self.axes['position'].set_xlabel('Car')
        self.axes['position'].set_ylabel('Distance (m)')
        self.axes['position'].grid(True, alpha=0.3)
        
        # 2. Energy chart (middle-left)
        self.axes['energy'] = self.fig.add_subplot(gs[1, 0])
        self.axes['energy'].set_title('Battery Energy', fontweight='bold')
        self.axes['energy'].set_xlabel('Time (s)')
        self.axes['energy'].set_ylabel('Battery (%)')
        self.axes['energy'].set_ylim([0, 105])
        self.axes['energy'].grid(True, alpha=0.3)
        
        # 3. Speed chart (middle-center)
        self.axes['speed'] = self.fig.add_subplot(gs[1, 1])
        self.axes['speed'].set_title('Speed Profile', fontweight='bold')
        self.axes['speed'].set_xlabel('Time (s)')
        self.axes['speed'].set_ylabel('Speed (km/h)')
        self.axes['speed'].grid(True, alpha=0.3)
        
        # 4. Lap times (middle-right)
        self.axes['laptimes'] = self.fig.add_subplot(gs[1, 2])
        self.axes['laptimes'].set_title('Best Lap Times', fontweight='bold')
        self.axes['laptimes'].set_xlabel('Lap Time (s)')
        self.axes['laptimes'].set_ylabel('Driver')
        
        # 5. Tire degradation (bottom-left)
        self.axes['tires'] = self.fig.add_subplot(gs[2, 0])
        self.axes['tires'].set_title('Tire Degradation', fontweight='bold')
        self.axes['tires'].set_xlabel('Car')
        self.axes['tires'].set_ylabel('Degradation (%)')
        self.axes['tires'].grid(True, alpha=0.3)
        
        # 6. Race info (bottom-center and right)
        self.axes['info'] = self.fig.add_subplot(gs[2, 1:])
        self.axes['info'].axis('off')
        
        # Initialize empty plots
        self._init_plots()
        
        # Add keyboard controls
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
        
    def _init_plots(self):
        """Initialize empty plot elements"""
        # Energy lines (show top 5 cars only for clarity)
        for i in range(min(5, self.num_cars)):
            line, = self.axes['energy'].plot([], [], 
                                             color=self.colors[i], 
                                             linewidth=2, 
                                             label=f'Car {i+1}',
                                             alpha=0.7)
            self.lines[f'energy_{i}'] = line
        self.axes['energy'].legend(loc='upper right', fontsize=8)
        
        # Speed lines (show top 5 cars only)
        for i in range(min(5, self.num_cars)):
            line, = self.axes['speed'].plot([], [], 
                                            color=self.colors[i], 
                                            linewidth=2,
                                            alpha=0.7)
            self.lines[f'speed_{i}'] = line
    
    def update(self, race_state: RaceState):
        """
        Update visualization with new race state
        
        Args:
            race_state: Current race state
        """
        # Store current time
        self.time_history.append(race_state.current_time)
        
        # Update car data
        for car in race_state.cars:
            car_id = car.car_id
            self.position_history[car_id].append(car.total_distance)
            self.energy_history[car_id].append(car.battery_percentage)
            self.speed_history[car_id].append(car.get_speed_kmh())
            
            # Store lap times
            if car.last_lap_time > 0 and len(self.lap_history[car_id]) < car.current_lap:
                self.lap_history[car_id].append(car.last_lap_time)
        
        # Update plots
        self._update_position_chart(race_state)
        self._update_energy_chart()
        self._update_speed_chart()
        self._update_lap_times(race_state)
        self._update_tire_chart(race_state)
        self._update_info_panel(race_state)
        
        # Redraw
        if self.fig:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
    
    def _update_position_chart(self, race_state: RaceState):
        """Update race position bar chart"""
        ax = self.axes['position']
        ax.clear()
        
        # Sort cars by position
        sorted_cars = sorted(race_state.cars, key=lambda c: c.position)[:10]  # Top 10
        
        # Create bars
        names = [c.driver_name for c in sorted_cars]
        distances = [c.total_distance for c in sorted_cars]
        colors = [self.colors[c.car_id] for c in sorted_cars]
        
        bars = ax.barh(names, distances, color=colors, alpha=0.7)
        
        # Color code by position
        for i, bar in enumerate(bars):
            if i == 0:
                bar.set_color('gold')
                bar.set_alpha(0.9)
            elif i == 1:
                bar.set_color('silver')
                bar.set_alpha(0.9)
            elif i == 2:
                bar.set_color('#CD7F32')  # Bronze
                bar.set_alpha(0.9)
        
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Driver')
        ax.set_title(f'Race Positions (Lap {sorted_cars[0].current_lap})', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()  # Leader at top
    
    def _update_energy_chart(self):
        """Update energy consumption line chart"""
        if len(self.time_history) < 2:
            return
        
        times = list(self.time_history)
        
        # Update lines for top 5 cars
        for i in range(min(5, self.num_cars)):
            if f'energy_{i}' in self.lines:
                energy_data = list(self.energy_history[i])
                if len(energy_data) > 0:
                    self.lines[f'energy_{i}'].set_data(times[:len(energy_data)], energy_data)
        
        # Update x-axis limits
        self.axes['energy'].set_xlim([times[0], times[-1]])
        self.axes['energy'].relim()
    
    def _update_speed_chart(self):
        """Update speed profile chart"""
        if len(self.time_history) < 2:
            return
        
        times = list(self.time_history)
        
        # Update lines for top 5 cars
        for i in range(min(5, self.num_cars)):
            if f'speed_{i}' in self.lines:
                speed_data = list(self.speed_history[i])
                if len(speed_data) > 0:
                    self.lines[f'speed_{i}'].set_data(times[:len(speed_data)], speed_data)
        
        # Update axes
        self.axes['speed'].set_xlim([times[0], times[-1]])
        self.axes['speed'].set_ylim([0, 300])
        self.axes['speed'].relim()
    
    def _update_lap_times(self, race_state: RaceState):
        """Update lap time comparison"""
        ax = self.axes['laptimes']
        ax.clear()
        
        # Get best lap times
        lap_data = []
        for car in race_state.cars:
            if car.best_lap_time != np.inf:
                lap_data.append((car.driver_name, car.best_lap_time))
        
        if not lap_data:
            return
        
        # Sort by lap time
        lap_data.sort(key=lambda x: x[1])
        lap_data = lap_data[:10]  # Top 10
        
        names = [x[0] for x in lap_data]
        times = [x[1] for x in lap_data]
        
        bars = ax.barh(names, times, color='steelblue', alpha=0.7)
        
        # Highlight fastest lap
        if bars:
            bars[0].set_color('gold')
            bars[0].set_alpha(0.9)
        
        ax.set_xlabel('Lap Time (s)')
        ax.set_ylabel('Driver')
        ax.set_title('Best Lap Times', fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
    
    def _update_tire_chart(self, race_state: RaceState):
        """Update tire degradation chart"""
        ax = self.axes['tires']
        ax.clear()
        
        # Get tire data for top 10
        sorted_cars = sorted(race_state.cars, key=lambda c: c.position)[:10]
        
        names = [c.driver_name for c in sorted_cars]
        degradation = [c.tire_degradation * 100 for c in sorted_cars]
        
        # Color based on degradation level
        colors_tire = []
        for deg in degradation:
            if deg < 30:
                colors_tire.append('green')
            elif deg < 60:
                colors_tire.append('orange')
            else:
                colors_tire.append('red')
        
        ax.bar(range(len(names)), degradation, color=colors_tire, alpha=0.7)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('Degradation (%)')
        ax.set_title('Tire Degradation', fontweight='bold')
        ax.set_ylim([0, 100])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add threshold lines
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.5, linewidth=1)
        ax.axhline(y=60, color='orange', linestyle='--', alpha=0.5, linewidth=1)
    
    def _update_info_panel(self, race_state: RaceState):
        """Update race information panel"""
        ax = self.axes['info']
        ax.clear()
        ax.axis('off')
        
        # Get leader info
        leader = None
        for car in race_state.cars:
            if car.position == 1 and car.is_active:
                leader = car
                break
        
        if not leader:
            leader = race_state.cars[0]
        
        # Create info text
        info_text = f"""
        Race Information:
        ─────────────────────────────────────────────────
        Time:              {race_state.current_time:.1f}s
        Leader:            {leader.driver_name}
        Leader Lap:        {leader.current_lap}
        Leader Speed:      {leader.get_speed_kmh():.1f} km/h
        Leader Battery:    {leader.battery_percentage:.1f}%
        Active Cars:       {len([c for c in race_state.cars if c.is_active])}/{race_state.num_cars}
        Safety Car:        {'YES' if race_state.safety_car_active else 'NO'}
        
        Controls:
        [SPACE] Pause/Resume  |  [Q] Quit
        """
        
        ax.text(0.05, 0.95, info_text, 
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    def _on_key_press(self, event):
        """Handle keyboard events"""
        if event.key == ' ':  # Space bar
            self.paused = not self.paused
            print(f"Visualization {'paused' if self.paused else 'resumed'}")
        elif event.key == 'q':
            plt.close(self.fig)
    
    def show(self, block: bool = True):
        """
        Display the visualization
        
        Args:
            block: Whether to block execution until window is closed
        """
        if self.fig is None:
            self.setup_figure()
        
        plt.show(block=block)
    
    def save_snapshot(self, filepath: str):
        """
        Save current visualization to file
        
        Args:
            filepath: Output file path (e.g., 'race_snapshot.png')
        """
        if self.fig:
            self.fig.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"Snapshot saved to {filepath}")


class LiveRaceAnimator:
    """
    Animated race visualization showing cars moving on track
    Creates a simple top-down animation
    """
    
    def __init__(self, track_length: float, num_cars: int):
        """
        Initialize animator
        
        Args:
            track_length: Total track length (meters)
            num_cars: Number of cars
        """
        self.track_length = track_length
        self.num_cars = num_cars
        
        # Setup figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim([0, track_length])
        self.ax.set_ylim([-10, 10])
        self.ax.set_xlabel('Track Position (m)')
        self.ax.set_ylabel('Lane')
        self.ax.set_title('Live Race Animation', fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Car markers
        self.car_markers = []
        colors = plt.cm.tab20(np.linspace(0, 1, num_cars))
        
        for i in range(num_cars):
            marker, = self.ax.plot([], [], 'o', markersize=10, 
                                  color=colors[i], label=f'Car {i+1}')
            self.car_markers.append(marker)
        
        self.ax.legend(loc='upper right', ncol=4, fontsize=8)
        
        # Info text
        self.info_text = self.ax.text(0.02, 0.98, '', 
                                      transform=self.ax.transAxes,
                                      verticalalignment='top',
                                      fontsize=10,
                                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def update(self, race_state: RaceState):
        """
        Update animation with new race state
        
        Args:
            race_state: Current race state
        """
        for car in race_state.cars:
            if car.car_id < len(self.car_markers):
                # Position on x-axis is lap_distance
                x = car.lap_distance
                # Y position is based on position (spread vertically)
                y = (car.position - 12.5) * 0.5  # Center around 0
                
                self.car_markers[car.car_id].set_data([x], [y])
                
                # Make inactive cars transparent
                if not car.is_active:
                    self.car_markers[car.car_id].set_alpha(0.3)
        
        # Update info
        leader = min(race_state.cars, key=lambda c: c.position if c.is_active else 999)
        info = f"Time: {race_state.current_time:.1f}s | Leader: {leader.driver_name} | Lap: {leader.current_lap}"
        self.info_text.set_text(info)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show(self):
        """Display animation"""
        plt.show(block=False)


def create_post_race_analysis(race_state: RaceState, event_log: List):
    """
    Create comprehensive post-race analysis plots
    
    Args:
        race_state: Final race state
        event_log: List of race events
    """
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Post-Race Analysis Report', fontsize=18, fontweight='bold')
    
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Final standings
    ax1 = fig.add_subplot(gs[0, :])
    sorted_cars = sorted(race_state.cars, key=lambda c: c.position)
    names = [c.driver_name for c in sorted_cars[:10]]
    laps = [c.current_lap for c in sorted_cars[:10]]
    colors = ['gold' if i == 0 else 'silver' if i == 1 else '#CD7F32' if i == 2 else 'steelblue' 
              for i in range(10)]
    ax1.barh(names, laps, color=colors, alpha=0.8)
    ax1.set_xlabel('Laps Completed')
    ax1.set_title('Final Standings', fontweight='bold')
    ax1.invert_yaxis()
    
    # 2. Energy efficiency
    ax2 = fig.add_subplot(gs[1, 0])
    efficiency = [c.get_energy_efficiency() for c in sorted_cars[:10]]
    ax2.bar(range(10), efficiency, color='green', alpha=0.7)
    ax2.set_xticks(range(10))
    ax2.set_xticklabels([c.driver_name for c in sorted_cars[:10]], rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('km/kWh')
    ax2.set_title('Energy Efficiency', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Overtakes
    ax3 = fig.add_subplot(gs[1, 1])
    overtakes = [c.overtakes_made for c in sorted_cars[:10]]
    ax3.bar(range(10), overtakes, color='orange', alpha=0.7)
    ax3.set_xticks(range(10))
    ax3.set_xticklabels([c.driver_name for c in sorted_cars[:10]], rotation=45, ha='right', fontsize=8)
    ax3.set_ylabel('Overtakes')
    ax3.set_title('Overtaking Statistics', fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Max speeds
    ax4 = fig.add_subplot(gs[1, 2])
    max_speeds = [c.max_speed_achieved * 3.6 for c in sorted_cars[:10]]
    ax4.bar(range(10), max_speeds, color='red', alpha=0.7)
    ax4.set_xticks(range(10))
    ax4.set_xticklabels([c.driver_name for c in sorted_cars[:10]], rotation=45, ha='right', fontsize=8)
    ax4.set_ylabel('Speed (km/h)')
    ax4.set_title('Maximum Speed Achieved', fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Event timeline
    ax5 = fig.add_subplot(gs[2, :])
    if event_log:
        event_types = {}
        for event in event_log:
            event_type = event.event_type if hasattr(event, 'event_type') else event.get('type', 'unknown')
            if event_type not in event_types:
                event_types[event_type] = []
            timestamp = event.timestamp if hasattr(event, 'timestamp') else event.get('time', 0)
            event_types[event_type].append(timestamp)
        
        y_pos = 0
        for event_type, times in event_types.items():
            ax5.scatter(times, [y_pos] * len(times), label=event_type, s=50, alpha=0.7)
            y_pos += 1
        
        ax5.set_xlabel('Race Time (s)')
        ax5.set_ylabel('Event Type')
        ax5.set_title('Event Timeline', fontweight='bold')
        ax5.legend(loc='upper right')
        ax5.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


class LiveRaceAnimator:
    """
    Live animation showing top-down view of cars racing on track
    Cars move in real-time as the simulation progresses
    """
    
    def __init__(self, track_length: float = 2500.0, num_cars: int = 24):
        """
        Initialize animator
        
        Args:
            track_length: Track length in meters
            num_cars: Number of cars in the race
        """
        self.track_length = track_length
        self.num_cars = num_cars
        
        # Display settings
        self.screen_margin = 100  # pixels
        self.track_start_x = self.screen_margin
        self.track_end_x = 1000 - self.screen_margin
        self.track_y = 300  # vertical position of track
        
        # Colors for cars
        self.colors = plt.cm.rainbow(np.linspace(0, 1, num_cars))
        
        # Animation state
        self.fig = None
        self.ax = None
        self.scatter = None
        self.info_text = None
        self.lap_text = None
        self.leader_text = None
        self.anim = None
        self.paused = False
        
    def setup_figure(self):
        """Create and setup the figure and track"""
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.fig.canvas.manager.set_window_title('Formula E Live Race Animation')
        
        # Setup axes
        self.ax.set_xlim(0, 1000)
        self.ax.set_ylim(0, 600)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Draw track
        self._draw_track()
        
        # Create scatter plot for cars (initially at start)
        x_positions = np.full(self.num_cars, self.track_start_x)
        y_positions = np.linspace(self.track_y - 40, self.track_y + 40, self.num_cars)
        
        self.scatter = self.ax.scatter(
            x_positions, y_positions,
            c=self.colors, s=200, marker='o',
            edgecolors='black', linewidths=2,
            alpha=0.8, zorder=10
        )
        
        # Info text panels
        self.info_text = self.ax.text(
            500, 500, '', fontsize=14, ha='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )
        
        self.lap_text = self.ax.text(
            100, 500, '', fontsize=12, ha='left',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
        )
        
        self.leader_text = self.ax.text(
            900, 500, '', fontsize=12, ha='right',
            bbox=dict(boxstyle='round', facecolor='gold', alpha=0.8)
        )
        
        # Title
        self.ax.text(500, 550, 'Formula E Race - Live Animation',
                    fontsize=18, ha='center', fontweight='bold')
        
        # Keyboard controls
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
        
    def _draw_track(self):
        """Draw the race track"""
        # Main track line
        self.ax.plot(
            [self.track_start_x, self.track_end_x],
            [self.track_y, self.track_y],
            'k-', linewidth=8, alpha=0.5, zorder=1
        )
        
        # Start line (green)
        self.ax.plot(
            [self.track_start_x, self.track_start_x],
            [self.track_y - 50, self.track_y + 50],
            'g-', linewidth=6, alpha=0.8, zorder=2
        )
        self.ax.text(
            self.track_start_x, self.track_y - 70,
            'START', fontsize=12, ha='center',
            fontweight='bold', color='green'
        )
        
        # Finish line (checkered pattern)
        for i in range(10):
            y_start = self.track_y - 50 + i * 10
            color = 'black' if i % 2 == 0 else 'white'
            self.ax.plot(
                [self.track_end_x, self.track_end_x],
                [y_start, y_start + 10],
                color=color, linewidth=6, alpha=0.8, zorder=2
            )
        self.ax.text(
            self.track_end_x, self.track_y - 70,
            'FINISH', fontsize=12, ha='center',
            fontweight='bold', color='red'
        )
        
        # Distance markers every 500m
        track_pixels = self.track_end_x - self.track_start_x
        for distance in range(0, int(self.track_length) + 1, 500):
            x_pos = self.track_start_x + (distance / self.track_length) * track_pixels
            self.ax.plot(
                [x_pos, x_pos],
                [self.track_y - 5, self.track_y + 5],
                'gray', linewidth=2, alpha=0.6, zorder=2
            )
            if distance > 0 and distance < self.track_length:
                self.ax.text(
                    x_pos, self.track_y + 15,
                    f'{distance}m', fontsize=8, ha='center',
                    color='gray'
                )
    
    def _position_to_screen_x(self, position: float, lap: int) -> float:
        """
        Convert car position (meters) to screen X coordinate
        
        Args:
            position: Distance along track (0 to track_length)
            lap: Current lap number
            
        Returns:
            X coordinate on screen
        """
        # Normalize position to 0-1 range
        normalized = (position % self.track_length) / self.track_length
        
        # Convert to screen coordinates
        track_pixels = self.track_end_x - self.track_start_x
        screen_x = self.track_start_x + normalized * track_pixels
        
        return screen_x
    
    def update(self, race_state: RaceState) -> tuple:
        """
        Update animation with new race state
        
        Args:
            race_state: Current race state
            
        Returns:
            Tuple of updated artists
        """
        if self.paused:
            return self.scatter, self.info_text, self.lap_text, self.leader_text
        
        # Get car positions
        cars = race_state.cars
        active_cars = [car for car in cars if car.is_active]
        
        if not active_cars:
            return self.scatter, self.info_text, self.lap_text, self.leader_text
        
        # Calculate screen positions
        x_positions = []
        y_positions = []
        
        # Sort by position for y-coordinate assignment
        sorted_cars = sorted(active_cars, key=lambda c: (-c.current_lap, -c.total_distance))
        
        for i, car in enumerate(sorted_cars):
            x = self._position_to_screen_x(car.lap_distance, car.current_lap)
            # Spread cars vertically based on their order
            y = self.track_y + (i - len(sorted_cars) / 2) * 3
            x_positions.append(x)
            y_positions.append(y)
        
        # Update scatter plot
        if x_positions:
            positions = np.column_stack([x_positions, y_positions])
            self.scatter.set_offsets(positions)
            
            # Update colors (highlight leader)
            colors = [self.colors[i % self.num_cars] for i in range(len(sorted_cars))]
            colors[0] = [1.0, 0.84, 0.0, 1.0]  # Gold for leader
            self.scatter.set_facecolors(colors)
        
        # Update info text
        self.info_text.set_text(
            f"Time: {race_state.current_time:.1f}s\n"
            f"Active Cars: {len(active_cars)}/{self.num_cars}"
        )
        
        # Update lap info
        if active_cars:
            leader = sorted_cars[0]
            # Calculate speed from velocity components
            speed = np.sqrt(leader.velocity_x**2 + leader.velocity_y**2)
            self.lap_text.set_text(
                f"Current Lap: {leader.current_lap}\n"
                f"Avg Speed: {speed * 3.6:.1f} km/h"
            )
            
            # Leader info
            self.leader_text.set_text(
                f"🏆 Leader\n"
                f"{leader.driver_name}\n"
                f"Battery: {leader.battery_percentage:.1f}%"
            )
        
        return self.scatter, self.info_text, self.lap_text, self.leader_text
    
    def _on_key_press(self, event):
        """Handle keyboard events"""
        if event.key == ' ':
            self.paused = not self.paused
            title = "PAUSED" if self.paused else "Formula E Race - Live Animation"
            self.ax.text(500, 550, title,
                        fontsize=18, ha='center', fontweight='bold')
            plt.draw()
        elif event.key == 'q':
            plt.close()
    
    def animate_race(self, race_engine, interval: int = 50):
        """
        Animate the race using the race engine
        
        Args:
            race_engine: FormulaERaceEngine instance
            interval: Update interval in milliseconds (default 50ms = 20 FPS)
        """
        def update_frame(frame):
            # Run simulation step
            if not race_engine.race_finished and not self.paused:
                race_engine.simulate_timestep()
            
            # Update animation
            return self.update(race_engine.race_state)
        
        # Create animation
        self.anim = animation.FuncAnimation(
            self.fig, update_frame,
            interval=interval,
            blit=True,
            cache_frame_data=False
        )
        
        plt.show()
    
    def show(self, block: bool = True):
        """Show the animation window"""
        plt.show(block=block)


