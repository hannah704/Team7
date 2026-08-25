import { useState } from "react";

import Header from "./components/Header";
import CameraFeed from "./components/CameraFeed";
import ControlPanel from "./components/ControlPanel";
import SensorPanel from "./components/SensorPanel";
import { useCarSocket } from "./hooks/useCarSocket";

import "./App.css";

function App() {
  const [mode, setMode] = useState("manual");
  const { connected, telemetry, warning, sendDrive, sendMode } = useCarSocket();

  const handleModeChange = (newMode) => {
    setMode(newMode);
    sendMode(newMode);
  };

  return (
    <div className="app">

      <Header connected={connected} warning={warning} />

      <main className="dashboard">

        <CameraFeed connected={connected} />

        <ControlPanel
          mode={mode}
          setMode={handleModeChange}
          sendDrive={sendDrive}
        />

        <SensorPanel telemetry={telemetry} />

      </main>

    </div>
  );
}

export default App;
