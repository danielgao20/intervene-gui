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

def create_latest_email_reply_task(text: str = "") -> str:
    """Open Gmail, open the latest email, draft a reply, and save it as a draft"""
    print("📧 Starting latest email reply task")

    # Step 1: Open Gmail
    open_gmail()

    # Step 2: Wait for Gmail to fully load
    time.sleep(1)

    # Step 3: Open the latest email (assumes first email is at y=200)
    pyautogui.press("enter")
    print("📨 Opened latest email")

    # Step 4: Reply to the email
    pyautogui.press("r")
    time.sleep(1)
    print("↩️ Replying to email")

    # Step 5: Type the draft
    draft_text = """Hey Vishnu,\n\nThat sounds awesome, I've been diving into similar stuff recently and would love to jam. Let's grab lunch on Tuesday after our Algorithms class!

Looking forward,
Shubhayan"""
    pyautogui.write(draft_text, interval=0.05)
    print("📝 Draft typed")

    # Step 6: Save as draft
    pyautogui.hotkey("command", "s")
    print("💾 Draft saved")

    print("✅ Task complete")
    return "Email reply drafted and saved"

def open_excel_with_data(text: str = "") -> str:
    """Open Excel and prepare it for data entry with interaction summary"""
    subprocess.run(["open", "-a", "Microsoft Excel"])
    time.sleep(3)  # Wait for Excel to open
    
    # Create a new workbook
    pyautogui.hotkey('command', 'n')
    time.sleep(1)
    
    # Create headers
    headers = ["Metric", "Value"]
    for col, header in enumerate(headers):
        pyautogui.write(header)
        pyautogui.press('tab')
    pyautogui.press('enter')
    
    # Add data rows
    data = [
        ["Topic", "LLaMA + Agentic Workflows Discussion"],
        ["Meeting Type", "Lunch"],
        ["Time", "Tuesday after Algorithms class"],
        ["Status", "Draft saved in Gmail"],
        ["Response Time", "< 1 minute"]
    ]
    
    for row in data:
        for cell in row:
            pyautogui.write(cell)
            pyautogui.press('tab')
        pyautogui.press('enter')
    
    # Format cells (select all used range)
    pyautogui.hotkey('command', 'a')
    
    # Center align
    pyautogui.hotkey('command', 'e')
    
    return "Excel opened with interaction summary"

def run_email_excel_workflow():
    """Run the complete workflow: Open Gmail, navigate emails, then open Excel"""
    print("📧 Starting email and Excel workflow...")
    
    # Open Gmail
    create_latest_email_reply_task()
    print("WORKING")
    
    # Open Excel
    open_excel_with_data()
    print("✅ Excel opened and ready")
    
    print("🎉 Workflow completed!")
