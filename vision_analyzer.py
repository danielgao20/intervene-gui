"""
llm_task_analyzer.py - Task analysis using locally hosted llama3.2
"""
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import json
import re
import logging
from config import get_ollama_config

# Configure logging
logger = logging.getLogger(__name__)

# Get Ollama configuration from environment
ollama_config = get_ollama_config()

# Initialize LLM with llama3.2 pointing to local Ollama server
llm = Ollama(
    model=ollama_config["llm_model"],
    base_url=ollama_config["base_url"]
)

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
    """
    Analyze a user request with llama3.2 and break it down into actionable steps
    
    Args:
        request (str): The user's request
        
    Returns:
        list: A list of steps to execute
    """
    try:
        logger.info(f"Analyzing request: {request}")
        
        # Prepare the prompt
        prompt = PromptTemplate.from_template(ANALYZE_PROMPT)
        
        # Invoke the LLM
        response = llm.invoke(prompt.format(request=request))
        
        # Log LLM output for debugging
        logger.info(f"LLM output: {response}")
        
        # Clean and parse the JSON response
        cleaned_response = clean_json_response(response)
        steps = json.loads(cleaned_response)
        
        logger.info(f"Parsed {len(steps)} steps from LLM response")
        return steps
        
    except Exception as e:
        logger.error(f"Error analyzing request: {str(e)}")
        # Return a fallback step in case of error
        return [{"type": "browser", "instruction": "open https://www.google.com"}]

def clean_json_response(response: str) -> str:
    """
    Clean a potentially messy JSON response from the LLM
    
    Args:
        response (str): The raw LLM response
        
    Returns:
        str: A cleaned JSON string
    """
    # Extract JSON array from response
    json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    else:
        # Fallback - try to find anything that looks like JSON
        json_str = response
    
    # Fix common JSON errors
    json_str = json_str.replace('}}', ']}')  # Fix bracket mismatch
    json_str = json_str.replace('}\n  }', ']\n  }')  # Fix nested endings
    json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)  # Remove trailing commas
    json_str = re.sub(r'\'', r'"', json_str)  # Replace single quotes with double quotes
    
    return json_str