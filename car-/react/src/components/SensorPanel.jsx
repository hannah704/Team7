import { motion } from "motion/react";

function SensorPanel({ telemetry }) {
  const voltage = telemetry?.voltage ?? "--";
  const current = telemetry?.current ?? "--";
  const accel = telemetry?.accel ?? { x: 0, y: 0, z: 0 };
  const gyro = telemetry?.gyro ?? { x: 0, y: 0, z: 0 };

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


        {/* Accelerometer */}

        <div className="sensor-card imu-card">

          <div className="sensor-card-header">
            <span className="sensor-icon">◉</span>
            <span>ACCEL</span>
          </div>

          <div className="imu-values">

            <div>
              <span>X</span>
              {accel.x}
            </div>

            <div>
              <span>Y</span>
              {accel.y}
            </div>

            <div>
              <span>Z</span>
              {accel.z}
            </div>

          </div>

        </div>


        {/* Gyroscope */}

        <div className="sensor-card imu-card">

          <div className="sensor-card-header">
            <span className="sensor-icon">↻</span>
            <span>GYRO</span>
          </div>

          <div className="imu-values">

            <div>
              <span>X</span>
              {gyro.x}
            </div>

            <div>
              <span>Y</span>
              {gyro.y}
            </div>

            <div>
              <span>Z</span>
              {gyro.z}
            </div>

          </div>

        </div>

      </div>

    </motion.section>
  );
}

export default SensorPanel;