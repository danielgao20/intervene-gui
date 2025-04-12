import time
import pyautogui
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    OPEN_BROWSER = "open_browser"
    NAVIGATE_URL = "navigate_url"
    CLICK = "click"
    KEY_PRESS = "key_press"
    HOTKEY = "hotkey"
    WAIT = "wait"
    OPEN_APP = "open_app"

@dataclass
class Action:
    type: ActionType
    params: Dict[str, Any]
    description: str
    wait_after: float = 1.0

class TaskTemplate:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.actions: List[Action] = []
    
    def add_action(self, action: Action) -> 'TaskTemplate':
        self.actions.append(action)
        return self
    
    def execute(self) -> None:
        print(f"🚀 Executing task: {self.name}")
        print(f"📝 {self.description}")
        
        for action in self.actions:
            print(f"⚡ Performing: {action.description}")
            self._execute_action(action)
            time.sleep(action.wait_after)
        
        print(f"✅ Task '{self.name}' completed!")

    def _execute_action(self, action: Action) -> None:
        if action.type == ActionType.OPEN_BROWSER:
            subprocess.run(["open", "-a", "Google Chrome", action.params["url"]])
        elif action.type == ActionType.NAVIGATE_URL:
            pyautogui.hotkey('command', 'l')
            pyautogui.write(action.params["url"])
            pyautogui.press('enter')
        elif action.type == ActionType.CLICK:
            pyautogui.click(x=action.params["x"], y=action.params["y"])
        elif action.type == ActionType.KEY_PRESS:
            pyautogui.press(action.params["key"])
        elif action.type == ActionType.HOTKEY:
            pyautogui.hotkey(*action.params["keys"])
        elif action.type == ActionType.WAIT:
            time.sleep(action.params["seconds"])
        elif action.type == ActionType.OPEN_APP:
            subprocess.run(["open", "-a", action.params["app_name"]])

# Example task templates
def create_gmail_navigation_task(num_emails: int = 3) -> TaskTemplate:
    task = TaskTemplate(
        name="Gmail Navigation",
        description="Opens Gmail and navigates through specified number of emails"
    )
    
    task.add_action(Action(
        type=ActionType.OPEN_BROWSER,
        params={"url": "https://mail.google.com"},
        description="Opening Gmail in Chrome",
        wait_after=5.0
    ))
    
    task.add_action(Action(
        type=ActionType.WAIT,
        params={"seconds": 3},
        description="Waiting for Gmail to load"
    ))
    
    task.add_action(Action(
        type=ActionType.CLICK,
        params={"x": 100, "y": 200},
        description="Clicking first email"
    ))
    
    for i in range(num_emails - 1):
        task.add_action(Action(
            type=ActionType.KEY_PRESS,
            params={"key": "j"},
            description=f"Navigating to next email ({i + 2}/{num_emails})"
        ))
    
    return task

def create_excel_setup_task() -> TaskTemplate:
    task = TaskTemplate(
        name="Excel Setup",
        description="Opens Excel and creates a new workbook"
    )
    
    task.add_action(Action(
        type=ActionType.OPEN_APP,
        params={"app_name": "Microsoft Excel"},
        description="Opening Excel",
        wait_after=3.0
    ))
    
    task.add_action(Action(
        type=ActionType.HOTKEY,
        params={"keys": ["command", "n"]},
        description="Creating new workbook"
    ))
    
    return task 