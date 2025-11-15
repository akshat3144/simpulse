"use client";

import { useState, useEffect } from "react";
import useWebSocket from "./hooks/useWebSocket";
import { RaceState, WebSocketMessage } from "./types/race";
import Leaderboard from "./components/Leaderboard";
import TrackView from "./components/TrackView";
import ControlPanel from "./components/ControlPanel";
import EnergyChart from "./components/EnergyChart";

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
    <div className="min-h-screen bg-black text-white p-8">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">🏎️ Formula E Race Dashboard</h1>
        <p className="text-gray-400">
          Real-time race simulation powered by FastAPI + Next.js + D3.js
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
        <div className="mb-6 grid grid-cols-4 gap-4">
          <div className="bg-gray-900 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Race Time</p>
            <p className="text-2xl font-bold">
              {raceState.current_time.toFixed(1)}s
            </p>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Current Lap</p>
            <p className="text-2xl font-bold">{raceState.current_lap}</p>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Active Cars</p>
            <p className="text-2xl font-bold">
              {raceState.active_cars}/{raceState.total_cars}
            </p>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Status</p>
            <p className="text-2xl font-bold">
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Leaderboard */}
          <div className="lg:col-span-1">
            <Leaderboard cars={raceState.cars} />
          </div>

          {/* Right Column - Visualizations */}
          <div className="lg:col-span-2 space-y-6">
            <TrackView cars={raceState.cars} trackLength={2500} />
            <EnergyChart cars={raceState.cars} />
          </div>
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-gray-400 text-xl mb-4">
            {isConnected
              ? "Click 'Create Race' to start"
              : "Connecting to server..."}
          </p>
          {!isConnected && (
            <p className="text-red-400">
              Make sure the backend is running on port 8000
            </p>
          )}
        </div>
      )}
    </div>
  );
}
