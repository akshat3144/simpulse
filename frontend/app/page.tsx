"use client";

import { useState, useEffect } from "react";
import useWebSocket from "./hooks/useWebSocket";
import { RaceState, WebSocketMessage } from "./types/race";
import Leaderboard from "./components/Leaderboard";
import TrackView from "./components/TrackView";
import ControlPanel from "./components/ControlPanel";

export default function Home() {
  const WS_URL = "ws://localhost:8000/ws/race";
  const { isConnected, lastMessage, sendMessage } = useWebSocket(WS_URL);

  const [raceState, setRaceState] = useState<RaceState | null>(null);
  const [raceActive, setRaceActive] = useState(false);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const message = lastMessage as WebSocketMessage;

      if (message.type === "initial_state" || message.type === "race_update") {
        setRaceState(message.data);

        // Update race active status
        if (message.data.race_finished) {
          setRaceActive(false);
        }
      }
    }
  }, [lastMessage]);

  // Create race via REST API
  const handleCreateRace = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/race/create?num_cars=12&num_laps=5",
        {
          method: "POST",
        }
      );
      const data = await response.json();
      console.log("Race created:", data);
      alert("Race created! Click Start to begin.");
    } catch (error) {
      console.error("Error creating race:", error);
      alert("Failed to create race. Make sure backend is running.");
    }
  };

  // Start race via WebSocket
  const handleStart = () => {
    sendMessage({ command: "start" });
    setRaceActive(true);
  };

  // Pause race via WebSocket
  const handlePause = () => {
    sendMessage({ command: "pause" });
    setRaceActive(false);
  };

  return (
    <div
      className="min-h-screen text-white p-4 md:p-8 overflow-x-hidden"
      style={{ background: "#041014" }}
    >
      {/* Header */}
      <header className="mb-6 md:mb-8">
        <h1
          className="text-2xl md:text-4xl font-bold mb-2"
          style={{ color: "#FFFFFF" }}
        >
          🏎️ Formula E Simulator
        </h1>
        <p className="text-sm md:text-base mb-1" style={{ color: "#C9D1D9" }}>
          A stochastic dynamics-based racing simulation framework
        </p>
        <p className="text-xs md:text-sm" style={{ color: "#8B949E" }}>
          Powered by SimPulse Engine
        </p>
      </header>

      {/* Control Panel */}
      <div className="mb-6">
        <ControlPanel
          isConnected={isConnected}
          raceActive={raceActive}
          onStart={handleStart}
          onPause={handlePause}
          onCreateRace={handleCreateRace}
        />
      </div>

      {/* Race Stats */}
      {raceState && (
        <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <div
            className="rounded-lg p-3 md:p-4"
            style={{ background: "#0A1820", border: "1px solid #142835" }}
          >
            <p className="text-xs md:text-sm" style={{ color: "#8B949E" }}>
              Race Time
            </p>
            <p
              className="text-lg md:text-2xl font-bold"
              style={{ color: "#00E5FF" }}
            >
              {raceState.current_time.toFixed(1)}s
            </p>
          </div>
          <div
            className="rounded-lg p-3 md:p-4"
            style={{ background: "#0A1820", border: "1px solid #142835" }}
          >
            <p className="text-xs md:text-sm" style={{ color: "#8B949E" }}>
              Current Lap
            </p>
            <p
              className="text-lg md:text-2xl font-bold"
              style={{ color: "#FFBB00" }}
            >
              {raceState.current_lap}
            </p>
          </div>
          <div
            className="rounded-lg p-3 md:p-4"
            style={{ background: "#0A1820", border: "1px solid #142835" }}
          >
            <p className="text-xs md:text-sm" style={{ color: "#8B949E" }}>
              Active Cars
            </p>
            <p
              className="text-lg md:text-2xl font-bold"
              style={{ color: "#00FF9C" }}
            >
              {raceState.active_cars}/{raceState.total_cars}
            </p>
          </div>
          <div
            className="rounded-lg p-3 md:p-4"
            style={{ background: "#0A1820", border: "1px solid #142835" }}
          >
            <p className="text-xs md:text-sm" style={{ color: "#8B949E" }}>
              Status
            </p>
            <p
              className="text-lg md:text-2xl font-bold"
              style={{ color: "#FFFFFF" }}
            >
              {raceState.race_finished
                ? "🏁 Finished"
                : raceActive
                ? "🏎️ Racing"
                : "⏸️ Paused"}
            </p>
          </div>
        </div>
      )}

      {/* Main Content */}
      {raceState ? (
        <div className="flex flex-col lg:grid lg:grid-cols-3 gap-4 md:gap-6">
          {/* Track View - First on mobile, Right on desktop */}
          <div className="lg:col-span-2 lg:order-2">
            <TrackView cars={raceState.cars} trackLength={2980} />
          </div>

          {/* Leaderboard - Second on mobile, Left on desktop */}
          <div className="lg:col-span-1 lg:order-1">
            <Leaderboard cars={raceState.cars} />
          </div>
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-xl mb-4" style={{ color: "#C9D1D9" }}>
            {isConnected
              ? "Click 'Create Race' to start"
              : "Connecting to server..."}
          </p>
          {!isConnected && (
            <p style={{ color: "#FF3B3B" }}>
              Make sure the backend is running on port 8000
            </p>
          )}
        </div>
      )}
    </div>
  );
}
