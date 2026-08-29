import { motion } from "motion/react";

function Header({ connected, warning }) {
  return (
    <motion.header
      className="header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.9 }}
    >
      <div>
        <motion.h1
          initial={{ opacity: 0 , x:-20}}
          animate={{ opacity: 1 , x: 0 }}
          transition={{ delay: 0.2, duration: 0.9 }}
        > 
        Rover Control And Mangement System
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, x:-20}}
          animate={{ opacity: 1 , x: 0 }}
          transition={{ delay: 0.4, duration: 1.5, ease: "easeInOut"}}
        >
          Mission Control Dashboard
        </motion.p>
      </div>

      <div className="header-status">
        <motion.div
          className={`connection-button ${connected ? "" : "disconnected"}`}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.9 }}
        >
          <motion.span
            className="status-dot"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [1, 0.6, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          <span>{connected ? "CONNECTED" : "DISCONNECTED"}</span>
        </motion.div>

        {warning && (
          <motion.div
            className="warning-banner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            ⚠ {warning === "LOW_VOLTAGE" ? "LOW VOLTAGE" : warning === "OVERCURRENT" ? "OVERCURRENT" : warning}
          </motion.div>
        )}
      </div>
    </motion.header>
  );
}

export default Header;