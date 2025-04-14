# tools/web_agent_tool.py
from langchain.tools import Tool
from langchain_ollama import ChatOllama
from browser_use import Agent
import asyncio

# LLM for browser agent
llm = ChatOllama(model="llama3.2")


# Async wrapper to run browser agent
async def run_browser_agent_async(task: str):
    agent = Agent(task=task, llm=llm)
    result = await agent.run()
    return result


# Sync wrapper so we can use it with LangChain
def run_browser_agent(task: str) -> str:
    return asyncio.run(run_browser_agent_async(task))


# Tool definition
web_agent_tool = Tool(
    name="Web Browser Agent",
    func=run_browser_agent,
    description="Use this tool for web-based tasks that require looking something up, browsing, or comparing info online.",
)
