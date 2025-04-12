import subprocess
import time
import pyautogui
from pynput import keyboard

def open_chrome_with_url(url: str):
    subprocess.run(["open", "-a", "Google Chrome", url])

def open_excel():
    subprocess.run(["open", "-a", "Microsoft Excel"])

def say_hello():
    print("👋 Hello from your local agent!")

def open_gmail():
    """Open Gmail in Chrome and wait for it to load"""
    subprocess.run(["open", "-a", "Google Chrome", "https://mail.google.com"])
    time.sleep(5)  # Wait for Gmail to load

def navigate_emails(num_emails=3):
    """Navigate through a specified number of emails"""
    # Wait for Gmail to be fully loaded
    time.sleep(3)
    
    # Click on the first email
    pyautogui.click(x=100, y=200)  # Approximate position of first email
    time.sleep(1)
    
    # Navigate through emails using keyboard
    for _ in range(num_emails - 1):
        pyautogui.press('j')  # Gmail shortcut for next email
        time.sleep(1)

def open_excel_with_data():
    """Open Excel and prepare it for data entry"""
    subprocess.run(["open", "-a", "Microsoft Excel"])
    time.sleep(3)  # Wait for Excel to open
    
    # Create a new workbook
    pyautogui.hotkey('command', 'n')
    time.sleep(1)

def run_email_excel_workflow():
    """Run the complete workflow: Open Gmail, navigate emails, then open Excel"""
    print("📧 Starting email and Excel workflow...")
    
    # Open Gmail
    open_gmail()
    print("✅ Gmail opened")
    
    # Navigate through emails
    navigate_emails()
    print("✅ Navigated through emails")
    
    # Open Excel
    open_excel_with_data()
    print("✅ Excel opened and ready")
    
    print("🎉 Workflow completed!")
