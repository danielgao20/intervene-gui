"""
tasks.py - Task execution with safer alternatives to PyAutoGUI
"""
import subprocess
import time
import os
import logging
import json
from threading import Timer
from PIL import ImageGrab
import tempfile
from vision_analyzer import analyze_screenshot

# Configure logging
logger = logging.getLogger(__name__)

class SafeAutomation:
    """A safer alternative to PyAutoGUI that uses platform-specific commands"""
    
    @staticmethod
    def paste_text(text):
        """Paste text at current cursor position using clipboard"""
        import pyperclip
        original = pyperclip.paste()
        pyperclip.copy(text)
        
        if os.name == 'posix':  # macOS or Linux
            subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "v" using command down'])
        elif os.name == 'nt':  # Windows
            subprocess.run(["powershell", "-command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^v')"])
        
        # Restore original clipboard after short delay
        Timer(0.5, lambda: pyperclip.copy(original)).start()
        
    @staticmethod
    def press_key(key_combination):
        """Press keys with platform-specific methods"""
        if os.name == 'posix':  # macOS or Linux
            if '+' in key_combination:
                keys = key_combination.split('+')
                modifiers = []
                for mod in keys[:-1]:
                    if mod.lower() == 'cmd' or mod.lower() == 'command':
                        modifiers.append('command')
                    elif mod.lower() in ['ctrl', 'control']:
                        modifiers.append('control')
                    elif mod.lower() == 'alt':
                        modifiers.append('option')
                    elif mod.lower() == 'shift':
                        modifiers.append('shift')
                
                mod_str = ' '.join(f"{m} down" for m in modifiers)
                key = keys[-1]
                subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{key}" using {{{mod_str}}}'])
            else:
                # Single key press
                subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{key_combination}"'])
        elif os.name == 'nt':  # Windows
            # Map common keys
            key_map = {
                'command': '^',  # Control
                'cmd': '^',
                'control': '^',
                'ctrl': '^',
                'alt': '%',
                'shift': '+',
                'enter': '{ENTER}',
                'tab': '{TAB}',
                'escape': '{ESC}'
            }
            
            win_combo = key_combination
            for k, v in key_map.items():
                win_combo = win_combo.replace(k, v)
                
            subprocess.run(["powershell", "-command", f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{win_combo}')"])

    @staticmethod
    def take_screenshot():
        """Take a screenshot and save to a temporary file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        screenshot = ImageGrab.grab()
        screenshot.save(temp_file.name)
        logger.info(f"Screenshot saved to {temp_file.name}")
        return temp_file.name

def run_task_workflow():
    """Run a workflow based on LLM task analysis"""
    logger.info("Starting task workflow")
    
    # Take a screenshot to analyze the current state
    screenshot_path = SafeAutomation.take_screenshot()
    
    # Analyze screenshot with vision model
    analysis = analyze_screenshot(screenshot_path)
    logger.info(f"Screen analysis: {analysis}")
    
    # Based on analysis, perform appropriate task
    if "email" in analysis.lower():
        result = handle_email_task()
    elif "spreadsheet" in analysis.lower() or "excel" in analysis.lower():
        result = handle_spreadsheet_task()
    else:
        result = "No specific task detected"
    
    # Clean up temporary screenshot
    os.unlink(screenshot_path)
    return result

def handle_email_task(draft_text=None):
    """Handle email-related tasks safely"""
    logger.info("Handling email task")
    
    if not draft_text:
        draft_text = """Hey there,

Thanks for your message. I've looked into this and would be happy to discuss further.

Best regards,
[Your Name]"""
    
    # Open default email client instead of assuming Gmail
    if os.name == 'posix':
        subprocess.run(["open", "-a", "Mail"])
    elif os.name == 'nt':
        subprocess.run(["start", "outlook:"])
    
    time.sleep(3)  # Wait for client to open
    
    # Compose new email using keyboard shortcuts
    SafeAutomation.press_key("command+n")
    time.sleep(1)
    
    # Paste the draft text
    SafeAutomation.paste_text(draft_text)
    
    return "Email draft created"

def handle_spreadsheet_task(data=None, headers=None):
    """Handle spreadsheet tasks with safer alternatives"""
    logger.info("Handling spreadsheet task")
    
    if data is None:
        data = [["Item 1", 100], ["Item 2", 200]]
    
    if headers is None:
        headers = ["Item", "Value"]
    
    # Open spreadsheet application
    if os.name == 'posix':
        subprocess.run(["open", "-a", "Numbers"])  # Use Numbers on Mac, or change to "Microsoft Excel"
    elif os.name == 'nt':
        subprocess.run(["start", "excel"])
    
    time.sleep(3)  # Wait for application to open
    
    # For demonstration, we'll create a CSV file and open it
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        # Write headers
        f.write(','.join(headers) + '\n')
        
        # Write data rows
        for row in data:
            f.write(','.join(str(cell) for cell in row) + '\n')
        
        temp_path = f.name
    
    # Open the CSV file
    if os.name == 'posix':
        subprocess.run(["open", temp_path])
    elif os.name == 'nt':
        subprocess.run(["start", temp_path])
    
    logger.info(f"Created and opened spreadsheet: {temp_path}")
    return f"Spreadsheet created with {len(data)} rows of data"

def open_excel_with_data(data=None, headers=None):
    """
    Legacy function maintained for compatibility with API calls.
    Now uses safer alternatives to PyAutoGUI.
    """
    return handle_spreadsheet_task(data, headers)