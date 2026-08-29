import { motion } from "motion/react";
import { useState, useEffect } from "react";

function ControlPanel({ mode, setMode, sendDrive }) {
  const [motionStatus, setMotionStatus] = useState("STOPPED");
  const [speed, setSpeed] = useState("MEDIUM");

  const SPEED_VALUES = { LOW: 3, MEDIUM: 6, HIGH: 9 };

  useEffect(() => {
    fetch("http://localhost:5000/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    }).catch((err) => console.error("Failed to sync mode:", err));
  }, [mode]);

  const handleCommand = (command) => {
    console.log("Rover command:", command);

    if (command === "STOP") {
      setMotionStatus("STOPPED");
    } else {
      setMotionStatus(command);
    }

    sendDrive(command, SPEED_VALUES[speed]);
  };

  return (
    <motion.section
      className="control-panel"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >

      {/* TITLE */}

      <div className="panel-title">
        <h2>ROVER CONTROL</h2>
        <p>Movement & operating mode</p>
      </div>


      {/* MODE */}

      <div className="mode-selector">

        <button
          className={`mode-option ${
            mode === "manual" ? "active" : ""
          }`}
          onClick={() => setMode("manual")}
        >
          <motion.span
            className="mode-indicator"
            animate={
              mode === "manual"
                ? { scale: [1, 1.3, 1] }
                : { scale: 1 }
            }
            transition={{
              duration: 1.5,
              repeat: mode === "manual" ? Infinity : 0,
            }}
          />

          MANUAL
        </button>


        <button
          className={`mode-option ${
            mode === "autonomous" ? "active" : ""
          }`}
          onClick={() => setMode("autonomous")}
        >
          <motion.span
            className="mode-indicator"
            animate={
              mode === "autonomous"
                ? { scale: [1, 1.3, 1] }
                : { scale: 1 }
            }
            transition={{
              duration: 1.5,
              repeat: mode === "autonomous" ? Infinity : 0,
            }}
          />

          AUTONOMOUS
        </button>

      </div>


      {/* MOVEMENT CONTROLS */}

      <div className="direction-pad">

        <motion.button
          className="direction-button"
          whileTap={{ scale: 0.9 }}
          disabled={mode === "autonomous"}
          onClick={() => handleCommand("FORWARD")}
        >
          ↑
        </motion.button>


        <div className="middle-controls">

          <motion.button
            className="direction-button"
            whileTap={{ scale: 0.9 }}
            disabled={mode === "autonomous"}
            onClick={() => handleCommand("LEFT")}
          >
            ←
          </motion.button>


          <motion.button
            className="stop-button"
            whileTap={{ scale: 0.9 }}
            animate={{
              scale: [1, 1.05, 1],
              opacity: [1, 0.75, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
            }}
            onClick={() => handleCommand("STOP")}
          >
            ■
          </motion.button>


          <motion.button
            className="direction-button"
            whileTap={{ scale: 0.9 }}
            disabled={mode === "autonomous"}
            onClick={() => handleCommand("RIGHT")}
          >
            →
          </motion.button>

        </div>


        <motion.button
          className="direction-button"
          whileTap={{ scale: 0.9 }}
          disabled={mode === "autonomous"}
          onClick={() => handleCommand("BACKWARD")}
        >
          ↓
        </motion.button>

      </div>


      {/* MOTOR SPEED */}

      <div className="speed-section">

        <div className="section-label">
          MOTOR SPEED
        </div>

        <div className="speed-selector">

          {["LOW", "MEDIUM", "HIGH"].map((level) => (

            <button
              key={level}
              className={`speed-option ${
                speed === level ? "active" : ""
              }`}
              onClick={() => setSpeed(level)}
            >
              {level}
            </button>

          ))}

        </div>

      </div>


      {/* MOTION STATUS */}

      <div className="motion-status">

        <div className="section-label">
          MOTION STATUS
        </div>

        <div className="motion-indicator">

          <motion.span
            className="motion-dot"
            animate={{
              opacity: [1, 0.5, 1],
              scale: [1, 1.15, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
            }}
          />

          <span>{motionStatus}</span>

        </div>

      </div>

    </motion.section>
  );
}

export default ControlPanel;
