"use client";

import { Car } from "../types/race";

interface LeaderboardProps {
  cars: Car[];
}

export default function Leaderboard({ cars }: LeaderboardProps) {
  // Sort by position
  const sortedCars = [...cars]
    .filter((car) => car.is_active)
    .sort((a, b) => a.position - b.position)
    .slice(0, 10); // Top 10

  const getPositionColor = (position: number) => {
    if (position === 1) return "bg-yellow-400 text-black";
    if (position === 2) return "bg-gray-300 text-black";
    if (position === 3) return "bg-orange-400 text-black";
    return "bg-gray-700 text-white";
  };

  return (
    <div className="bg-gray-900 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
        🏆 Leaderboard
      </h2>
      <div className="space-y-2">
        {sortedCars.map((car) => (
          <div
            key={car.id}
            className="flex items-center gap-3 bg-gray-800 rounded-lg p-3 hover:bg-gray-750 transition-colors"
          >
            {/* Position */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${getPositionColor(
                car.position
              )}`}
            >
              {car.position}
            </div>

            {/* Driver name */}
            <div className="flex-1">
              <p className="text-white font-semibold">{car.driver_name}</p>
              <p className="text-gray-400 text-sm">
                Lap {car.current_lap} • {car.speed_kmh.toFixed(1)} km/h
              </p>
            </div>

            {/* Gap */}
            <div className="text-right">
              {car.position === 1 ? (
                <p className="text-green-400 font-semibold">Leader</p>
              ) : (
                <p className="text-gray-300">
                  +{car.gap_to_leader.toFixed(1)}s
                </p>
              )}
              <p className="text-gray-500 text-sm">
                {car.battery_percentage.toFixed(1)}% 🔋
              </p>
            </div>

            {/* Attack mode indicator */}
            {car.attack_mode_active && (
              <div className="text-purple-400 text-xl animate-pulse">⚡</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
