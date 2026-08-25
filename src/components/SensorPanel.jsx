import { motion } from "motion/react";

function SensorPanel({ telemetry }) {
  const voltage = telemetry?.voltage ?? "--";
  const current = telemetry?.current ?? "--";
  const imu = telemetry?.imu ?? { x: 0, y: 0, z: 0 };

  return (
    <motion.section
      className="sensor-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >

      <div className="sensor-title">
        <h2>SENSOR FEEDBACK</h2>
        <p>Real-time rover telemetry</p>
      </div>

      <div className="sensor-grid">

        {/* Battery */}

        <div className="sensor-card">

          <div className="sensor-card-header">
            <span className="sensor-icon">🔋</span>
            <span>BATTERY</span>
          </div>

          <div className="sensor-value">
            {voltage}
            <span> V</span>
          </div>

        </div>


        {/* Current */}

        <div className="sensor-card">

          <div className="sensor-card-header">
            <span className="sensor-icon">⚡</span>
            <span>CURRENT</span>
          </div>

          <div className="sensor-value">
            {current}
            <span> A</span>
          </div>

        </div>


        {/* IMU */}

        <div className="sensor-card imu-card">

          <div className="sensor-card-header">
            <span className="sensor-icon">◉</span>
            <span>IMU</span>
          </div>

          <div className="imu-values">

            <div>
              <span>X</span>
              {imu.x}
            </div>

            <div>
              <span>Y</span>
              {imu.y}
            </div>

            <div>
              <span>Z</span>
              {imu.z}
            </div>

          </div>

        </div>

      </div>

    </motion.section>
  );
}

export default SensorPanel;
