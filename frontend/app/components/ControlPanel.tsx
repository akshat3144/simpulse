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
    <div
      className="rounded-lg p-3 md:p-6"
      style={{ background: "#0A1820", border: "1px solid #142835" }}
    >
      <h2
        className="text-lg md:text-xl font-bold mb-3 md:mb-4"
        style={{ color: "#FFFFFF" }}
      >
        Race Controls
      </h2>

      {/* Connection status */}
      <div className="mb-3 md:mb-4 flex items-center gap-2">
        <div
          className="w-3 h-3 rounded-full"
          style={{ background: isConnected ? "#00FF9C" : "#FF3B3B" }}
        />
        <span className="text-sm md:text-base" style={{ color: "#C9D1D9" }}>
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>

      {/* Control buttons */}
      <div className="flex gap-2 md:gap-3 flex-wrap">
        <button
          onClick={onCreateRace}
          className="font-semibold py-2 px-4 md:px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
          style={{
            background: !isConnected || raceActive ? "#0A1820" : "#00E5FF",
            color: !isConnected || raceActive ? "#8B949E" : "#041014",
            border: "2px solid #00E5FF",
          }}
          disabled={!isConnected || raceActive}
        >
          🏁 Create Race
        </button>

        <button
          onClick={onStart}
          className="font-semibold py-2 px-4 md:px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
          style={{
            background: !isConnected || raceActive ? "#0A1820" : "#00FF9C",
            color: !isConnected || raceActive ? "#8B949E" : "#041014",
            border: "2px solid #00FF9C",
          }}
          disabled={!isConnected || raceActive}
        >
          ▶️ Start
        </button>

        <button
          onClick={onPause}
          className="font-semibold py-2 px-4 md:px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
          style={{
            background: !isConnected || !raceActive ? "#0A1820" : "#FFBB00",
            color: !isConnected || !raceActive ? "#8B949E" : "#041014",
            border: "2px solid #FFBB00",
          }}
          disabled={!isConnected || !raceActive}
        >
          ⏸️ Pause
        </button>
      </div>

      {/* Race status */}
      {raceActive && (
        <div
          className="mt-3 md:mt-4 font-semibold text-sm md:text-base"
          style={{ color: "#00FF9C" }}
        >
          🏎️ Race in progress...
        </div>
      )}
    </div>
  );
}
