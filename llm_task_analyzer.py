from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import os

llm = ChatOllama(model="llama3.2")

ANALYZE_PROMPT = """
You are an expert automation orchestrator. Given a user's request, break it down into a list of atomic, actionable steps that can be executed by either a browser automation agent or an Excel automation agent.

STRICT RULES:
- EVERY browser step must be a single, atomic, fully-specified action. Do NOT output vague, multi-stage, or incomplete browser instructions. For example, do NOT output steps like 'open google', 'search google', 'search for X', or 'go to google and search'.
- For browser steps, ALWAYS include BOTH the exact URL (e.g., 'https://www.google.com') AND the full search query in the instruction (e.g., 'open https://www.google.com and search for "LangChain"').
- For Excel steps, ALWAYS output the headers and data to enter as JSON fields: 'headers' (a list of column names) and 'data' (a list of rows, each a list of cell values). If data should be copied from browser results, explicitly specify the headers and example data.
- Do NOT ask for clarification or require any user input during execution.
- Excel steps must always be routed to the Excel automation agent (not browser automation) and must be handled by a function called 'open_excel_with_data'.
- STRICTLY output valid JSON: no trailing commas, use double quotes for all keys and string values, and do not include comments or explanations.

Respond in JSON format as follows (strictly valid JSON):
[
  {{"type": "browser", "instruction": "open https://www.google.com and search for 'LangChain'"}},
  {{"type": "excel", "instruction": "create a new spreadsheet with general information about LangChain from its homepage", "headers": ["Title", "Description", "URL"], "data": [
    ["Applications that can reason.", "Powered by LangChain.", "https://www.langchain.com"],
    ["LangChain", "The framework for developing applications powered by language models.", "https://www.langchain.com"]
  ]}}
]

User request: {request}
"""

def analyze_request_with_llm(request: str):
    prompt = ChatPromptTemplate.from_template(ANALYZE_PROMPT)
    chain = prompt | llm
    response = chain.invoke({"request": request})
    # DEBUG: Print LLM output for inspection
    print("LLM OUTPUT:\n", response.content)
    # Extract JSON from LLM response
    import json
    import re
    # CLEANUP: Fix common bracket mismatch (data: [[...}} -> data: [[...]] )
    cleaned = response.content.replace('}}', ']]').replace('}\n  }', ']\n  }')
    try:
        steps = json.loads(cleaned)
    except Exception:
        # Try to extract JSON from text
        match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if match:
            steps = json.loads(match.group(0))
        else:
            raise ValueError(f"Could not parse steps from LLM response: {response.content}")
    return steps
