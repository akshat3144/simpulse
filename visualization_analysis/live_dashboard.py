"""
Interactive Live Dashboard for Formula E Simulation
Creates an interactive web-based visualization using Plotly Dash
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
from pathlib import Path

# Load data
print("Loading race data...")
data_dir = Path(__file__).parent.parent / "backend" / "race_output"
df = pd.read_csv(data_dir / "race_timesteps.csv")

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

# Get unique cars
cars = sorted(df['car_number'].unique())

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Formula E Race Simulator - Live Dashboard"

# Define colors for cars
colors = px.colors.qualitative.Plotly

# Create the layout
app.layout = html.Div([
    html.Div([
        html.H1("🏎️ Formula E Race Simulator - Interactive Dashboard", 
                style={'textAlign': 'center', 'color': '#1e3a8a', 'marginBottom': 20}),
        html.Div([
            html.H3(f"Race Duration: {df['race_time'].max():.1f}s | Cars: {len(cars)} | Timesteps: {len(df):,}", 
                   style={'textAlign': 'center', 'color': '#475569'})
        ]),
    ], style={'padding': '20px', 'backgroundColor': '#f8fafc'}),
    
    # Control Panel
    html.Div([
        html.Div([
            html.Label("Select Car:", style={'fontWeight': 'bold', 'marginRight': 10}),
            dcc.Dropdown(
                id='car-selector',
                options=[{'label': f'Car {car}', 'value': car} for car in cars],
                value=cars[0],
                style={'width': '200px', 'display': 'inline-block'}
            ),
        ], style={'display': 'inline-block', 'marginRight': 30}),
        
        html.Div([
            html.Label("Time Range:", style={'fontWeight': 'bold', 'marginRight': 10}),
            dcc.RangeSlider(
                id='time-slider',
                min=0,
                max=df['race_time'].max(),
                value=[0, df['race_time'].max()],
                marks={i: f'{i}s' for i in range(0, int(df['race_time'].max())+1, 100)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style={'width': '60%', 'display': 'inline-block', 'marginLeft': 30}),
    ], style={'padding': '20px', 'backgroundColor': '#ffffff', 'marginBottom': 20}),
    
    # Main visualizations
    html.Div([
        # Row 1: Track position and Speed
        html.Div([
            html.Div([
                dcc.Graph(id='track-position', style={'height': '500px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                dcc.Graph(id='speed-profile', style={'height': '500px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        ]),
        
        # Row 2: Energy and Steering
        html.Div([
            html.Div([
                dcc.Graph(id='energy-management', style={'height': '450px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                dcc.Graph(id='steering-analysis', style={'height': '450px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        ]),
        
        # Row 3: Race positions and Tire degradation
        html.Div([
            html.Div([
                dcc.Graph(id='race-positions', style={'height': '450px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                dcc.Graph(id='tire-degradation', style={'height': '450px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        ]),
        
        # Row 4: Attack Mode and Statistics
        html.Div([
            html.Div([
                dcc.Graph(id='attack-mode', style={'height': '400px'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                html.Div(id='statistics-panel', style={
                    'padding': '20px',
                    'backgroundColor': '#f1f5f9',
                    'borderRadius': '10px',
                    'height': '400px',
                    'overflowY': 'auto'
                })
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        ]),
    ]),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds if needed
        n_intervals=0,
        disabled=True  # Disabled by default, enable for live updates
    )
], style={'backgroundColor': '#f8fafc', 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'})


# Callback for track position
@app.callback(
    Output('track-position', 'figure'),
    [Input('time-slider', 'value')]
)
def update_track_position(time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    
    fig = go.Figure()
    
    for i, car in enumerate(cars):
        car_data = filtered_df[filtered_df['car_number'] == car]
        fig.add_trace(go.Scatter(
            x=car_data['position_x'],
            y=car_data['position_y'],
            mode='markers',
            name=f'Car {car}',
            marker=dict(size=3, color=colors[i % len(colors)], opacity=0.6),
            hovertemplate=f'Car {car}<br>X: %{{x:.1f}}m<br>Y: %{{y:.1f}}m<extra></extra>'
        ))
    
    fig.update_layout(
        title='Track Position - Bird\'s Eye View',
        xaxis_title='Position X (m)',
        yaxis_title='Position Y (m)',
        hovermode='closest',
        showlegend=True,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        template='plotly_white'
    )
    
    return fig


# Callback for speed profile
@app.callback(
    Output('speed-profile', 'figure'),
    [Input('car-selector', 'value'),
     Input('time-slider', 'value')]
)
def update_speed_profile(selected_car, time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    car_data = filtered_df[filtered_df['car_number'] == selected_car]
    
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=('Speed Over Time', 'Speed vs Lap Distance'),
                        vertical_spacing=0.15)
    
    # Speed over time
    fig.add_trace(
        go.Scatter(x=car_data['race_time'], y=car_data['speed_kmh'],
                  mode='lines', name='Speed',
                  line=dict(color='blue', width=2),
                  hovertemplate='Time: %{x:.1f}s<br>Speed: %{y:.1f} km/h<extra></extra>'),
        row=1, col=1
    )
    
    # Speed vs lap distance
    if len(car_data) > 0:
        sample_lap = car_data[car_data['current_lap'] == car_data['current_lap'].mode()[0]] if len(car_data['current_lap'].mode()) > 0 else car_data
        fig.add_trace(
            go.Scatter(x=sample_lap['lap_distance'], y=sample_lap['speed_kmh'],
                      mode='lines', name='Speed',
                      line=dict(color='green', width=2),
                      fill='tozeroy',
                      hovertemplate='Distance: %{x:.1f}m<br>Speed: %{y:.1f} km/h<extra></extra>'),
            row=2, col=1
        )
    
    fig.update_xaxes(title_text="Race Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Lap Distance (m)", row=2, col=1)
    fig.update_yaxes(title_text="Speed (km/h)", row=1, col=1)
    fig.update_yaxes(title_text="Speed (km/h)", row=2, col=1)
    
    fig.update_layout(
        title=f'Speed Profile - Car {selected_car}',
        showlegend=False,
        template='plotly_white',
        height=500
    )
    
    return fig


# Callback for energy management
@app.callback(
    Output('energy-management', 'figure'),
    [Input('car-selector', 'value'),
     Input('time-slider', 'value')]
)
def update_energy_management(selected_car, time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    car_data = filtered_df[filtered_df['car_number'] == selected_car]
    
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Battery State of Charge', 'Battery Temperature'),
                        vertical_spacing=0.15)
    
    # Battery SOC
    fig.add_trace(
        go.Scatter(x=car_data['race_time'], y=car_data['battery_soc'],
                  mode='lines', name='SOC',
                  line=dict(color='orange', width=2),
                  fill='tozeroy',
                  hovertemplate='Time: %{x:.1f}s<br>SOC: %{y:.1f}%<extra></extra>'),
        row=1, col=1
    )
    
    # Battery temperature
    fig.add_trace(
        go.Scatter(x=car_data['race_time'], y=car_data['battery_temperature'],
                  mode='lines', name='Temperature',
                  line=dict(color='red', width=2),
                  hovertemplate='Time: %{x:.1f}s<br>Temp: %{y:.1f}°C<extra></extra>'),
        row=2, col=1
    )
    
    # Add optimal temperature line
    fig.add_hline(y=40, line_dash="dash", line_color="green", 
                  annotation_text="Optimal (40°C)", row=2, col=1)
    
    fig.update_xaxes(title_text="Race Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Race Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=1, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
    
    fig.update_layout(
        title=f'Energy Management - Car {selected_car}',
        showlegend=False,
        template='plotly_white',
        height=450
    )
    
    return fig


# Callback for steering analysis
@app.callback(
    Output('steering-analysis', 'figure'),
    [Input('car-selector', 'value'),
     Input('time-slider', 'value')]
)
def update_steering_analysis(selected_car, time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    car_data = filtered_df[filtered_df['car_number'] == selected_car]
    
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Steering Angle Over Time', 'Steering Angle Distribution'),
                        vertical_spacing=0.15)
    
    # Steering over time
    steering_deg = np.degrees(car_data['steering_angle'])
    fig.add_trace(
        go.Scatter(x=car_data['race_time'], y=steering_deg,
                  mode='lines', name='Steering',
                  line=dict(color='purple', width=1),
                  hovertemplate='Time: %{x:.1f}s<br>Angle: %{y:.2f}°<extra></extra>'),
        row=1, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
    
    # Histogram
    fig.add_trace(
        go.Histogram(x=steering_deg, nbinsx=50, name='Distribution',
                    marker_color='purple', opacity=0.7),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Race Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Steering Angle (degrees)", row=2, col=1)
    fig.update_yaxes(title_text="Angle (degrees)", row=1, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    
    fig.update_layout(
        title=f'Steering Analysis - Car {selected_car}',
        showlegend=False,
        template='plotly_white',
        height=450
    )
    
    return fig


# Callback for race positions
@app.callback(
    Output('race-positions', 'figure'),
    [Input('time-slider', 'value')]
)
def update_race_positions(time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    
    fig = go.Figure()
    
    for i, car in enumerate(cars):
        car_data = filtered_df[filtered_df['car_number'] == car]
        fig.add_trace(go.Scatter(
            x=car_data['race_time'],
            y=car_data['position'],
            mode='lines',
            name=f'Car {car}',
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'Car {car}<br>Time: %{{x:.1f}}s<br>Position: %{{y}}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Race Positions Over Time',
        xaxis_title='Race Time (s)',
        yaxis_title='Position',
        hovermode='closest',
        yaxis=dict(autorange='reversed', dtick=1),
        template='plotly_white'
    )
    
    return fig


# Callback for tire degradation
@app.callback(
    Output('tire-degradation', 'figure'),
    [Input('time-slider', 'value')]
)
def update_tire_degradation(time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    
    fig = go.Figure()
    
    for i, car in enumerate(cars):
        car_data = filtered_df[filtered_df['car_number'] == car]
        fig.add_trace(go.Scatter(
            x=car_data['race_time'],
            y=car_data['tire_degradation'] * 100,
            mode='lines',
            name=f'Car {car}',
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'Car {car}<br>Time: %{{x:.1f}}s<br>Degradation: %{{y:.2f}}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='Tire Degradation Over Time',
        xaxis_title='Race Time (s)',
        yaxis_title='Tire Degradation (%)',
        hovermode='closest',
        template='plotly_white'
    )
    
    return fig


# Callback for attack mode
@app.callback(
    Output('attack-mode', 'figure'),
    [Input('car-selector', 'value'),
     Input('time-slider', 'value')]
)
def update_attack_mode(selected_car, time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    car_data = filtered_df[filtered_df['car_number'] == selected_car]
    
    fig = go.Figure()
    
    # Attack mode active/inactive
    fig.add_trace(go.Scatter(
        x=car_data['race_time'],
        y=car_data['attack_mode_active'].astype(int),
        mode='lines',
        name='Active',
        line=dict(color='red', width=2),
        fill='tozeroy',
        hovertemplate='Time: %{x:.1f}s<br>Active: %{y}<extra></extra>'
    ))
    
    # Attack mode remaining time
    fig.add_trace(go.Scatter(
        x=car_data['race_time'],
        y=car_data['attack_mode_remaining'] / 240,  # Normalize to 0-1
        mode='lines',
        name='Remaining',
        line=dict(color='orange', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='Time: %{x:.1f}s<br>Remaining: %{y:.1%}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Attack Mode Usage - Car {selected_car}',
        xaxis_title='Race Time (s)',
        yaxis_title='Active (0/1)',
        yaxis2=dict(title='Remaining (%)', overlaying='y', side='right'),
        hovermode='closest',
        template='plotly_white'
    )
    
    return fig


# Callback for statistics panel
@app.callback(
    Output('statistics-panel', 'children'),
    [Input('car-selector', 'value'),
     Input('time-slider', 'value')]
)
def update_statistics(selected_car, time_range):
    filtered_df = df[(df['race_time'] >= time_range[0]) & (df['race_time'] <= time_range[1])]
    car_data = filtered_df[filtered_df['car_number'] == selected_car]
    
    if len(car_data) == 0:
        return html.Div("No data available for selected range")
    
    # Calculate statistics
    stats = {
        'Speed': {
            'Min': f"{car_data['speed_kmh'].min():.2f} km/h",
            'Max': f"{car_data['speed_kmh'].max():.2f} km/h",
            'Average': f"{car_data['speed_kmh'].mean():.2f} km/h",
        },
        'Position': {
            'Best': f"P{int(car_data['position'].min())}",
            'Current': f"P{int(car_data['position'].iloc[-1])}",
            'Average': f"P{car_data['position'].mean():.1f}",
        },
        'Energy': {
            'Battery SOC': f"{car_data['battery_soc'].iloc[-1]:.1f}%",
            'Battery Temp': f"{car_data['battery_temperature'].iloc[-1]:.1f}°C",
            'Temp Change': f"+{car_data['battery_temperature'].iloc[-1] - car_data['battery_temperature'].iloc[0]:.1f}°C",
        },
        'Tires': {
            'Degradation': f"{car_data['tire_degradation'].iloc[-1]*100:.2f}%",
            'Temperature': f"{car_data['tire_temperature'].iloc[-1]:.1f}°C",
        },
        'Attack Mode': {
            'Uses Left': f"{int(car_data['attack_mode_uses_left'].iloc[-1])}",
            'Currently Active': 'Yes' if car_data['attack_mode_active'].iloc[-1] else 'No',
            'Remaining': f"{car_data['attack_mode_remaining'].iloc[-1]:.1f}s",
        },
        'Lap Info': {
            'Current Lap': f"{int(car_data['current_lap'].iloc[-1])}",
            'Lap Distance': f"{car_data['lap_distance'].iloc[-1]:.1f}m",
        }
    }
    
    # Create HTML layout
    sections = []
    for section_name, section_stats in stats.items():
        section_items = [
            html.Div([
                html.Span(f"{key}: ", style={'fontWeight': 'bold'}),
                html.Span(value)
            ], style={'marginBottom': '5px'})
            for key, value in section_stats.items()
        ]
        
        sections.append(
            html.Div([
                html.H4(section_name, style={'color': '#1e3a8a', 'marginBottom': '10px'}),
                html.Div(section_items, style={'marginBottom': '15px'})
            ])
        )
    
    return html.Div([
        html.H3(f'Car {selected_car} Statistics', style={'color': '#0f172a', 'marginBottom': '20px'}),
        html.Div(sections)
    ])


# Run the app
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏎️  FORMULA E LIVE DASHBOARD")
    print("="*60)
    print("\n✓ Data loaded successfully")
    print(f"✓ {len(cars)} cars, {len(df):,} timesteps")
    print("\n🌐 Starting web server...")
    print("\n📊 Dashboard will open at: http://127.0.0.1:8050")
    print("\n💡 Features:")
    print("   - Interactive track position visualization")
    print("   - Real-time speed, energy, and steering analysis")
    print("   - Race position tracking")
    print("   - Attack mode monitoring")
    print("   - Detailed statistics per car")
    print("\n⌨️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
