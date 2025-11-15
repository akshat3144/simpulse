"use client";

interface ControlPanelProps {
  isConnected: boolean;
  raceActive: boolean;
  onStart: () => void;
  onPause: () => void;
  onCreateRace: () => void;
}

export default function ControlPanel({
  isConnected,
  raceActive,
  onStart,
  onPause,
  onCreateRace,
}: ControlPanelProps) {
  return (
    <div className="bg-gray-900 rounded-lg p-3 md:p-6 shadow-lg">
      <h2 className="text-lg md:text-xl font-bold text-white mb-3 md:mb-4">
        Race Controls
      </h2>

      {/* Connection status */}
      <div className="mb-3 md:mb-4 flex items-center gap-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected ? "bg-green-500" : "bg-red-500"
          }`}
        />
        <span className="text-gray-300 text-sm md:text-base">
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>

      {/* Control buttons */}
      <div className="flex gap-2 md:gap-3 flex-wrap">
        <button
          onClick={onCreateRace}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 md:px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
          disabled={!isConnected || raceActive}
        >
          🏁 Create Race
        </button>

        <button
          onClick={onStart}
          className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 md:px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
          disabled={!isConnected || raceActive}
        >
          ▶️ Start
        </button>

        <button
          onClick={onPause}
          className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 px-4 md:px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
          disabled={!isConnected || !raceActive}
        >
          ⏸️ Pause
        </button>
      </div>

      {/* Race status */}
      {raceActive && (
        <div className="mt-3 md:mt-4 text-green-400 font-semibold animate-pulse text-sm md:text-base">
          🏎️ Race in progress...
        </div>
      )}
    </div>
  );
}
