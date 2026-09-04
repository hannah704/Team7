import { motion } from "motion/react";

function CameraFeed() {
  return (
    <motion.section
      className="camera-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="panel-header">
        <div>
          <h2>LIVE CAMERA</h2>
          <p>Rover camera feed</p>
        </div>

        <div className="camera-status">
          <span className="camera-dot"></span>
          LIVE
        </div>
      </div>

      <div className="camera-screen">
        <img
          src="http://localhost:5000/video"
          alt="live rover camera feed"
          className="camera-stream"
        />
      </div>

      <button className="screenshot-button">
        TAKE SCREENSHOT
      </button>
    </motion.section>
  );
}

export default CameraFeed;