import time
from listener import OverrideDetector
from tasks import open_chrome_with_url

class InterveneAgent:
    def __init__(self):
        self.detector = OverrideDetector()
        self.mouse_listener, self.keyboard_listener = self.detector.start_listeners()

    def run_task(self):
        print("🧠 Copilot standing by...")
        time.sleep(2)  # Wait before acting

        if not self.detector.override:
            print("🚀 No user detected, proceeding with task...")
            open_chrome_with_url("https://llama.meta.com")
        else:
            print("🛑 Manual override detected. Task cancelled.")

    def shutdown(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
