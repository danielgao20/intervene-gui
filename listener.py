from pynput import mouse, keyboard

class OverrideDetector:
    def __init__(self):
        self.override = False

    def on_mouse_move(self, x, y):
        self.override = True

    def on_key_press(self, key):
        self.override = True

    def start_listeners(self):
        mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
        keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        mouse_listener.start()
        keyboard_listener.start()
        return mouse_listener, keyboard_listener
