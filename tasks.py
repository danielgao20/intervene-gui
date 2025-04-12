import subprocess

def open_chrome_with_url(url: str):
    subprocess.run(["open", "-a", "Google Chrome", url])

def open_excel():
    subprocess.run(["open", "-a", "Microsoft Excel"])

def say_hello():
    print("👋 Hello from your local agent!")
