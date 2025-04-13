import subprocess
import time
import pyautogui
from pynput import keyboard
from task_templates import create_gmail_navigation_task, create_excel_setup_task
import logging


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
        pyautogui.press("j")  # Gmail shortcut for next email
        time.sleep(1)


def open_excel_with_data():
    """Open Excel and prepare it for data entry"""
    subprocess.run(["open", "-a", "Microsoft Excel"])
    time.sleep(3)  # Wait for Excel to open

    # Create a new workbook
    pyautogui.hotkey("command", "n")
    time.sleep(1)


def open_specific_email(index: int = 1):
    """Open a specific email in the inbox based on index"""
    time.sleep(3)
    y_position = 200 + (index - 1) * 60
    pyautogui.click(x=100, y=y_position)
    time.sleep(2)


def compose_email(to: str, subject: str, body: str, send: bool = False):
    """Compose a new Gmail email assuming mouse is already hovering over 'Compose'"""
    time.sleep(5)
    pyautogui.click()  # Click the compose button
    logging.info("Clicked on Compose button")
    time.sleep(2)  # Wait for compose window to appear

    pyautogui.write(to, interval=0.05)
    pyautogui.press("tab")  # Move to subject
    pyautogui.write(subject, interval=0.05)
    pyautogui.press("tab")  # Move to body
    pyautogui.write(body, interval=0.05)

    if send:
        pyautogui.hotkey("command", "enter")
    else:
        print("Email composed and saved as draft (not sent)")


def reply_to_email(reply_body: str, send: bool = False):
    """Reply to currently open email with given content"""
    pyautogui.press("r")  # Reply shortcut
    time.sleep(1)
    pyautogui.write(reply_body)

    if send:
        pyautogui.hotkey("command", "enter")
    else:
        print("💬 Reply drafted (not sent)")


def open_spam_folder():
    """Navigate to Gmail's Spam folder"""
    subprocess.run(
        ["open", "-a", "Google Chrome", "https://mail.google.com/mail/u/0/#spam"]
    )
    time.sleep(5)


def summarize_open_email():
    """Stub: Capture and 'summarize' email content on screen (placeholder)"""
    print("🔍 Summarizing open email...")
    screenshot = pyautogui.screenshot(region=(200, 200, 800, 600))  # Adjust as needed
    screenshot.save("email_screenshot.png")
    print("🖼️ Screenshot saved for manual/ML summarization: email_screenshot.png")


def run_email_excel_workflow(num_emails: int = 3):
    """Run the complete workflow using task templates"""
    print("📧 Starting email and Excel workflow...")

    # Create and execute Gmail navigation task
    gmail_task = create_gmail_navigation_task(num_emails)
    gmail_task.execute()

    # Create and execute Excel setup task
    excel_task = create_excel_setup_task()
    excel_task.execute()

    print("🎉 Workflow completed!")


def test_compose_email_to_vkadaba():
    compose_email(
        to="vkadaba@usc.edu",
        subject="Test Email from Agent",
        body="Hi Vishnu,\n\nThis is a test email sent by your local agent. 🦾\n\nBest,\nAgentBot",
    )


if __name__ == "__main__":
    test_compose_email_to_vkadaba()
