import subprocess
import time
import pyautogui
from pynput import keyboard
from task_templates import create_gmail_navigation_task, create_excel_setup_task
import logging
import requests
import base64
from PIL import Image
import io


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


def capture_screen():
    """Capture the current screen and return as base64"""
    screenshot = pyautogui.screenshot()
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def analyze_screen_with_ollama(prompt: str):
    """Use Ollama to analyze the screen and return coordinates"""
    screenshot = capture_screen()
    
    # Prepare the request to Ollama
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "images": [screenshot],
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"]
    except Exception as e:
        print(f"Error analyzing screen with Ollama: {e}")
        return None


def test_ollama_connection():
    """Test if Ollama is running and responding"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama is running and responding")
            return True
        else:
            print("❌ Ollama is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama. Make sure it's running with 'ollama run llama3.2'")
        return False


def find_and_click_element(element_description: str, verify_position: bool = True):
    """Find and click an element based on its description"""
    prompt = f"""Analyze this screenshot and find the coordinates of the {element_description}.
    Return the coordinates in the format 'x,y' where x and y are integers.
    Only return the coordinates, nothing else."""
    
    coordinates = analyze_screen_with_ollama(prompt)
    if coordinates:
        try:
            x, y = map(int, coordinates.split(','))
            
            if verify_position:
                print(f"\nMoving to coordinates: ({x}, {y})")
                print("Press Ctrl+C to stop position display")
                # Display mouse position for 3 seconds before clicking
                try:
                    for _ in range(3):
                        current_x, current_y = pyautogui.position()
                        print(f"Current mouse position: ({current_x}, {current_y})")
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nPosition verification interrupted")
                    return False
                
            pyautogui.click(x, y)
            return True
        except:
            print(f"Could not parse coordinates: {coordinates}")
    return False


def navigate_emails(num_emails=3):
    """Navigate through a specified number of emails"""
    # First verify Ollama is running
    if not test_ollama_connection():
        return
        
    time.sleep(3)  # Wait for Gmail to load
    
    # Find and click first email
    if not find_and_click_element("first email in the inbox", verify_position=True):
        print("Could not find first email")
        return
    
    time.sleep(1)
    
    # Navigate through remaining emails
    for _ in range(num_emails - 1):
        if not find_and_click_element("next email in the list", verify_position=True):
            print("Could not find next email")
            break
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
    # First verify Ollama is running
    if not test_ollama_connection():
        return
        
    if not find_and_click_element("reply button in the email view", verify_position=True):
        print("Could not find reply button")
        return
    
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
    open_gmail()
    compose_email(
        to="vkadaba@usc.edu",
        subject="Test Email from Agent",
        body="Hi Vishnu,\n\nThis is a test email sent by your local agent. 🦾\n\nBest,\nAgentBot",
    )


if __name__ == "__main__":
    # Test Ollama connection when script starts
    test_ollama_connection()
    # Run the test email function
    test_compose_email_to_vkadaba()
