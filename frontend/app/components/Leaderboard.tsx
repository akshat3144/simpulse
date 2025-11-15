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
    if (position === 1) return { bg: "#FFBB00", color: "#041014" };
    if (position === 2) return { bg: "#C9D1D9", color: "#041014" };
    if (position === 3) return { bg: "#FF7A00", color: "#041014" };
    return { bg: "#142835", color: "#FFFFFF" };
  };

  return (
    <div
      className="rounded-lg p-3 md:p-6"
      style={{ background: "#0A1820", border: "1px solid #142835" }}
    >
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-xl md:text-2xl font-bold flex items-center gap-2"
          style={{ color: "#FFFFFF" }}
        >
          🏆 Leaderboard
        </h2>
        <span className="text-xs md:text-sm" style={{ color: "#8B949E" }}>
          {allActiveCars.length} cars
        </span>
      </div>
      <div className="space-y-2">
        {sortedCars.map((car) => {
          const posColor = getPositionColor(car.position);
          return (
            <div
              key={car.id}
              className="flex items-center gap-2 md:gap-3 rounded-lg p-2 md:p-2 transition-colors"
              style={{
                background: "#142835",
                border: "1px solid #1E3A4D",
                minHeight: "90px",
                height: "90px",
              }}
            >
              {/* Position */}
              <div
                className="w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center font-bold text-sm"
                style={{ background: posColor.bg, color: posColor.color }}
              >
                {car.position}
              </div>

              {/* Driver name & Stats */}
              <div className="flex-1 min-w-0">
                <p
                  className="font-semibold truncate text-sm md:text-base"
                  style={{ color: "#FFFFFF" }}
                >
                  {car.driver_name}
                </p>
                <div className="flex flex-wrap gap-2 md:gap-3 text-xs mt-1">
                  <span style={{ color: "#8B949E" }}>
                    Lap {car.current_lap}
                  </span>
                  <span style={{ color: "#00E5FF" }}>
                    {car.speed_kmh.toFixed(0)} km/h
                  </span>
                  <span
                    style={{
                      color:
                        car.tire_degradation > 70
                          ? "#FF3B3B"
                          : car.tire_degradation > 40
                          ? "#FF7A00"
                          : "#00FF9C",
                    }}
                  >
                    🛞 {(100 - car.tire_degradation).toFixed(0)}%
                  </span>
                  {/* SimPulse Performance Index */}
                  {car.performance_index !== undefined && (
                    <span
                      className="font-semibold"
                      style={{
                        color:
                          car.performance_index > 0.7
                            ? "#00FF9C"
                            : car.performance_index > 0.5
                            ? "#FFBB00"
                            : "#FF7A00",
                      }}
                      title="SimPulse Performance Index P_i(t)"
                    >
                      📊 {(car.performance_index * 100).toFixed(0)}
                    </span>
                  )}
                </div>
              </div>

              {/* Energy & Temperature */}
              <div className="text-center hidden md:block">
                <div className="text-xs">
                  <div
                    className="font-semibold"
                    style={{
                      color:
                        car.battery_percentage < 20
                          ? "#FF3B3B"
                          : car.battery_percentage < 40
                          ? "#FFBB00"
                          : "#00FF9C",
                    }}
                  >
                    🔋 {car.battery_percentage.toFixed(0)}%
                  </div>
                  <div
                    className="mt-0.5"
                    style={{
                      color:
                        car.battery_temperature > 45
                          ? "#FF3B3B"
                          : car.battery_temperature > 40
                          ? "#FF7A00"
                          : "#8B949E",
                    }}
                  >
                    🌡️ {car.battery_temperature.toFixed(0)}°C
                  </div>
                </div>
              </div>

              {/* Performance Stats */}
              <div className="text-right min-w-fit">
                {car.position === 1 ? (
                  <p
                    className="font-semibold text-xs md:text-sm"
                    style={{ color: "#00FF9C" }}
                  >
                    Leader
                  </p>
                ) : (
                  <>
                    <p
                      className="text-xs md:text-sm"
                      style={{ color: "#C9D1D9" }}
                    >
                      +{car.gap_to_leader.toFixed(1)}s
                    </p>
                    {car.gap_to_ahead < 1.0 && (
                      <p className="text-xs" style={{ color: "#FF7A00" }}>
                        ↑ {car.gap_to_ahead.toFixed(2)}s
                      </p>
                    )}
                  </>
                )}
                <div className="hidden sm:flex gap-2 mt-1 justify-end text-xs">
                  {car.overtakes_made > 0 && (
                    <span style={{ color: "#00E5FF" }}>
                      🏁 {car.overtakes_made}
                    </span>
                  )}
                  {car.best_lap_time > 0 && (
                    <span style={{ color: "#00E5FF" }} title="Best Lap">
                      ⏱️ {car.best_lap_time.toFixed(1)}s
                    </span>
                  )}
                </div>
              </div>

              {/* Attack mode indicator */}
              {car.attack_mode_active && (
                <div className="flex flex-col items-center">
                  <div className="text-xl" style={{ color: "#00E5FF" }}>
                    ⚡
                  </div>
                  <span className="text-xs" style={{ color: "#00E5FF" }}>
                    {car.attack_mode_remaining.toFixed(0)}s
                  </span>
                </div>
              )}
              {!car.attack_mode_active && car.attack_mode_uses_left > 0 && (
                <div className="text-xs" style={{ color: "#8B949E" }}>
                  ⚡×{car.attack_mode_uses_left}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div
          className="mt-4 pt-4 flex items-center justify-between"
          style={{ borderTop: "1px solid #142835" }}
        >
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 md:px-4 md:py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            style={{
              background: currentPage === 1 ? "#0A1820" : "#142835",
              color: "#FFFFFF",
              border: "1px solid #1E3A4D",
            }}
          >
            ← Prev
          </button>
          <div className="flex gap-1 md:gap-2">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className="w-7 h-7 md:w-9 md:h-9 rounded text-xs md:text-sm font-semibold transition-colors"
                style={{
                  background: currentPage === page ? "#00E5FF" : "#142835",
                  color: currentPage === page ? "#041014" : "#C9D1D9",
                  border: "1px solid #1E3A4D",
                }}
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
            className="px-3 py-1 md:px-4 md:py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            style={{
              background: currentPage === totalPages ? "#0A1820" : "#142835",
              color: "#FFFFFF",
              border: "1px solid #1E3A4D",
            }}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
