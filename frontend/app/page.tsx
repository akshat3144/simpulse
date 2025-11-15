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
    <div className="min-h-screen bg-black text-white p-4 md:p-8 overflow-x-hidden">
      {/* Header */}
      <header className="mb-6 md:mb-8">
        <h1 className="text-2xl md:text-4xl font-bold mb-2">
          🏎️ Formula E Race Dashboard
        </h1>
        <p className="text-gray-400 text-sm md:text-base">
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
        <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <div className="bg-gray-900 rounded-lg p-3 md:p-4">
            <p className="text-gray-400 text-xs md:text-sm">Race Time</p>
            <p className="text-lg md:text-2xl font-bold">
              {raceState.current_time.toFixed(1)}s
            </p>
          </div>
          <div className="bg-gray-900 rounded-lg p-3 md:p-4">
            <p className="text-gray-400 text-xs md:text-sm">Current Lap</p>
            <p className="text-lg md:text-2xl font-bold">
              {raceState.current_lap}
            </p>
          </div>
          <div className="bg-gray-900 rounded-lg p-3 md:p-4">
            <p className="text-gray-400 text-xs md:text-sm">Active Cars</p>
            <p className="text-lg md:text-2xl font-bold">
              {raceState.active_cars}/{raceState.total_cars}
            </p>
          </div>
          <div className="bg-gray-900 rounded-lg p-3 md:p-4">
            <p className="text-gray-400 text-xs md:text-sm">Status</p>
            <p className="text-lg md:text-2xl font-bold">
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
