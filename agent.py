"""
agent.py - Revised main agent class that orchestrates tasks
"""
import time
from listener import OverrideDetector
from tasks import run_task_workflow
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InterveneAgent:
    def __init__(self):
        self.detector = OverrideDetector()
        self.mouse_listener, self.keyboard_listener = self.detector.start_listeners()
        logger.info("Agent initialized and listeners started")

    def run_task(self):
        logger.info("🧠 Copilot standing by...")
        time.sleep(2)  # Wait before acting

        if not self.detector.override:
            logger.info("🚀 No user detected, proceeding with workflow...")
            run_task_workflow()
        else:
            logger.info("🛑 Manual override detected. Task cancelled.")

    def shutdown(self):
        logger.info("Shutting down agent listeners")
        self.mouse_listener.stop()
        self.keyboard_listener.stop()