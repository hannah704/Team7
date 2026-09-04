import { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import CameraFeed from "./components/CameraFeed";
import ControlPanel from "./components/ControlPanel";
import SensorPanel from "./components/SensorPanel";
import { useCarSocket } from "./hooks/useCarSocket";

function App() {
  const [mode, setMode] = useState("manual");
  const { connected, telemetry, warning, sendDrive, sendMode } = useCarSocket();

  const handleSetMode = (newMode) => {
    setMode(newMode);
  };

  return (
    <>
      <Header connected={connected} warning={warning} />

      <div className="dashboard">
        <div className="main-row">
          <CameraFeed />
          <ControlPanel mode={mode} setMode={handleSetMode} sendDrive={sendDrive} />
        </div>

        <SensorPanel telemetry={telemetry} />
      </div>
    </>
  );
}

export default App;
