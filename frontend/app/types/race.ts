// Type definitions for race data
export interface Car {
  id: number;
  driver_name: string;
  position: number;
  current_lap: number;
  lap_distance: number;
  total_distance: number;
  battery_percentage: number;
  battery_energy: number;
  battery_temperature: number;
  tire_degradation: number;
  grip_coefficient: number;
  velocity_x: number;
  velocity_y: number;
  speed: number;
  speed_kmh: number;
  attack_mode_active: boolean;
  attack_mode_remaining: number;
  attack_mode_uses_left: number;
  last_lap_time: number;
  best_lap_time: number;
  is_active: boolean;
  gap_to_leader: number;
  gap_to_ahead: number;
  total_energy_consumed: number;
  max_speed_achieved: number;
  overtakes_made: number;
  time: number;
}

export interface RaceState {
  current_time: number;
  current_lap: number;
  cars: Car[];
  leaderboard: Car[];
  active_cars: number;
  total_cars: number;
  race_finished: boolean;
}

export interface WebSocketMessage {
  type: "initial_state" | "race_update" | "command_response";
  data: RaceState;
  timestamp?: string;
}
