from langchain.agents import Tool, initialize_agent
from langchain_community.llms.ollama import Ollama

from task_templates import create_gmail_navigation_task, create_excel_setup_task

llm = Ollama(model="llama3.2")  # adjust based on what model is running


# --- Tool Wrappers ---
def run_gmail_task(input_str: str) -> str:
    """
    Input: string with number of emails to read, e.g., "3"
    """
    try:
        num = int(input_str.strip())
    except ValueError:
        num = 3  # default fallback
    task = create_gmail_navigation_task(num_emails=num)
    task.execute()
    return f"✅ Executed Gmail navigation for {num} emails"


def run_excel_task(_: str = "") -> str:
    task = create_excel_setup_task()
    task.execute()
    return "✅ Executed Excel setup task"


# --- Tool List ---
tools = [
    Tool(
        name="Gmail Task",
        func=run_gmail_task,
        description="Open Gmail and navigate through a number of emails. Input should be a number like '3'.",
    ),
    Tool(
        name="Excel Task",
        func=run_excel_task,
        description="Open Excel and create a new workbook.",
    ),
]

# --- Initialize Agent ---
agent = initialize_agent(
    tools=tools, llm=llm, agent="zero-shot-react-description", verbose=True
)
