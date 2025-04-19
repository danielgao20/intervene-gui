from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv

load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4o")

async def run_browser_task(task: str) -> str:
    agent = Agent(
        task=task,
        llm=llm,
    )
    result = await agent.run()
    return result

if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "open google"
    import asyncio
    result = asyncio.run(run_browser_task(task))
    print(result)
