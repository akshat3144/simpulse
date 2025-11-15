"use client";

import { useState, useMemo } from "react";
import { Car } from "../types/race";

interface LeaderboardProps {
  cars: Car[];
}

export default function Leaderboard({ cars }: LeaderboardProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const carsPerPage = 10;

  // Sort by position
  const allActiveCars = useMemo(
    () =>
      [...cars]
        .filter((car) => car.is_active)
        .sort((a, b) => a.position - b.position),
    [cars]
  );

  const totalPages = Math.ceil(allActiveCars.length / carsPerPage);
  const startIndex = (currentPage - 1) * carsPerPage;
  const sortedCars = allActiveCars.slice(startIndex, startIndex + carsPerPage);

  const getPositionColor = (position: number) => {
    if (position === 1) return "bg-yellow-400 text-black";
    if (position === 2) return "bg-gray-300 text-black";
    if (position === 3) return "bg-orange-400 text-black";
    return "bg-gray-700 text-white";
  };

  return (
    <div className="bg-gray-900 rounded-lg p-3 md:p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2">
          🏆 Leaderboard
        </h2>
        <span className="text-xs md:text-sm text-gray-400">
          {allActiveCars.length} cars
        </span>
      </div>
      <div className="space-y-2">
        {sortedCars.map((car) => (
          <div
            key={car.id}
            className="flex items-center gap-2 md:gap-3 bg-gray-800 rounded-lg p-2 md:p-3 hover:bg-gray-750 transition-colors"
          >
            {/* Position */}
            <div
              className={`w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center font-bold text-sm ${getPositionColor(
                car.position
              )}`}
            >
              {car.position}
            </div>

            {/* Driver name & Stats */}
            <div className="flex-1 min-w-0">
              <p className="text-white font-semibold truncate text-sm md:text-base">
                {car.driver_name}
              </p>
              <div className="flex flex-wrap gap-2 md:gap-3 text-xs mt-1">
                <span className="text-gray-400">Lap {car.current_lap}</span>
                <span className="text-blue-400">
                  {car.speed_kmh.toFixed(0)} km/h
                </span>
                <span
                  className={`${
                    car.tire_degradation > 70
                      ? "text-red-400"
                      : car.tire_degradation > 40
                      ? "text-orange-400"
                      : "text-green-400"
                  }`}
                >
                  🛞 {(100 - car.tire_degradation).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Energy & Temperature */}
            <div className="text-center hidden md:block">
              <div className="text-xs">
                <div
                  className={`font-semibold ${
                    car.battery_percentage < 20
                      ? "text-red-400"
                      : car.battery_percentage < 40
                      ? "text-yellow-400"
                      : "text-green-400"
                  }`}
                >
                  🔋 {car.battery_percentage.toFixed(0)}%
                </div>
                <div
                  className={`text-gray-400 mt-0.5 ${
                    car.battery_temperature > 45
                      ? "text-red-400"
                      : car.battery_temperature > 40
                      ? "text-orange-400"
                      : ""
                  }`}
                >
                  🌡️ {car.battery_temperature.toFixed(0)}°C
                </div>
              </div>
            </div>

            {/* Performance Stats */}
            <div className="text-right min-w-fit">
              {car.position === 1 ? (
                <p className="text-green-400 font-semibold text-xs md:text-sm">
                  Leader
                </p>
              ) : (
                <>
                  <p className="text-gray-300 text-xs md:text-sm">
                    +{car.gap_to_leader.toFixed(1)}s
                  </p>
                  {car.gap_to_ahead < 1.0 && (
                    <p className="text-orange-400 text-xs">
                      ↑ {car.gap_to_ahead.toFixed(2)}s
                    </p>
                  )}
                </>
              )}
              <div className="hidden sm:flex gap-2 mt-1 justify-end text-xs">
                {car.overtakes_made > 0 && (
                  <span className="text-purple-400">
                    🏁 {car.overtakes_made}
                  </span>
                )}
                {car.best_lap_time > 0 && (
                  <span className="text-blue-300" title="Best Lap">
                    ⏱️ {car.best_lap_time.toFixed(1)}s
                  </span>
                )}
              </div>
            </div>

            {/* Attack mode indicator */}
            {car.attack_mode_active && (
              <div className="flex flex-col items-center">
                <div className="text-purple-400 text-xl animate-pulse">⚡</div>
                <span className="text-purple-300 text-xs">
                  {car.attack_mode_remaining.toFixed(0)}s
                </span>
              </div>
            )}
            {!car.attack_mode_active && car.attack_mode_uses_left > 0 && (
              <div className="text-gray-500 text-xs">
                ⚡×{car.attack_mode_uses_left}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 pt-4 border-t border-gray-700 flex items-center justify-between">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 md:px-4 md:py-2 bg-gray-800 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors text-sm"
          >
            ← Prev
          </button>
          <div className="flex gap-1 md:gap-2">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`w-7 h-7 md:w-9 md:h-9 rounded text-xs md:text-sm font-semibold transition-colors ${
                  currentPage === page
                    ? "bg-blue-500 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                }`}
              >
                {page}
              </button>
            ))}
          </div>
          <button
            onClick={() =>
              setCurrentPage(Math.min(totalPages, currentPage + 1))
            }
            disabled={currentPage === totalPages}
            className="px-3 py-1 md:px-4 md:py-2 bg-gray-800 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors text-sm"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
