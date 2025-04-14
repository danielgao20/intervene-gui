import time
from listener import OverrideDetector
from tasks import run_email_excel_workflow

class InterveneAgent:
    def __init__(self):
        self.detector = OverrideDetector()
        self.mouse_listener, self.keyboard_listener = self.detector.start_listeners()

    def run_task(self):
        print("🧠 Copilot standing by...")
        time.sleep(2)  # Wait before acting

        if not self.detector.override:
            print("🚀 No user detected, proceeding with email and Excel workflow...")
            run_email_excel_workflow()
        else:
            print("🛑 Manual override detected. Task cancelled.")

    def shutdown(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
