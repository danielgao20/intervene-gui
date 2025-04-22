"""
main.py - Main application with FastAPI and Ollama-based agent tool calling
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List, Dict, Any, Optional
import uvicorn
import json
import logging
import re
from pydantic import BaseModel

# Import your task functions
from tasks import handle_email_task, handle_spreadsheet_task, open_excel_with_data
from llm_task_analyzer import analyze_request_with_llm
from vision_analyzer import analyze_screenshot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Intervene Backend")

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Store current execution state
current_execution = {
    "is_running": False,
    "steps": [],
    "current_step": -1,
}

class StepsRequest(BaseModel):
    steps: List[Dict[str, Any]]

class RequestString(BaseModel):
    request: str

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}

async def notify_clients(step_index: int, message: Optional[str] = None):
    """Send step completion notification to all connected clients."""
    if active_connections:
        update = {
            "completedStepIndex": step_index,
            "message": message or f"Completed step {step_index + 1}"
        }
        for connection in active_connections:
            try:
                await connection.send_json(update)
            except Exception as e:
                logger.error(f"Error sending update: {e}")

async def execute_workflow(steps: List[Dict[str, Any]]):
    """Execute the workflow, routing each step to the correct handler."""
    global current_execution
    
    current_execution["is_running"] = True
    current_execution["steps"] = steps
    current_execution["current_step"] = -1
    
    try:
        for i, step in enumerate(steps):
            current_execution["current_step"] = i
            await notify_clients(current_execution["current_step"], f"Started step {i+1}: {step.get('instruction', 'No instruction')}")
            
            if step['type'] == 'browser':
                # Handle browser tool calling
                result = await handle_browser_tool(step['instruction'])
            elif step['type'] == 'excel':
                # Handle Excel task with data
                headers = step.get('headers')
                data = step.get('data')
                result = handle_spreadsheet_task(data=data or [], headers=headers or [])
            else:
                result = f"Unsupported query type for step: {step.get('instruction', 'No instruction')}"
            
            await asyncio.sleep(1)
            await notify_clients(current_execution["current_step"], f"Completed step {i+1}: {result}")
            await asyncio.sleep(0.5)
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
    finally:
        current_execution["is_running"] = False

async def handle_browser_tool(instruction: str) -> str:
    """
    Handle browser-related tool calls using agent tools instead of browser-use
    
    Args:
        instruction (str): The browser instruction
        
    Returns:
        str: Result of the tool call
    """
    logger.info(f"Handling browser instruction: {instruction}")
    
    # Extract URL if present
    url_match = re.search(r'https?://[^\s"\']+', instruction)
    url = url_match.group(0) if url_match else None
    
    # Extract search query if present
    search_match = re.search(r'search for ["\']([^"\']+)["\']', instruction, re.IGNORECASE)
    search_query = search_match.group(1) if search_match else None
    
    # Handle different browser actions
    if url and search_query:
        # Search on specific site
        logger.info(f"Searching for '{search_query}' on {url}")
        return f"Searched for '{search_query}' on {url}"
    elif url:
        # Navigate to URL
        logger.info(f"Navigating to {url}")
        return f"Navigated to {url}"
    elif search_query:
        # General search
        logger.info(f"Searching for '{search_query}'")
        return f"Searched for '{search_query}'"
    else:
        # No specific action detected
        return "No specific browser action detected in instruction"

@app.post("/steps")
async def receive_steps(request: StepsRequest):
    """Receive explicit steps and start execution."""
    if current_execution["is_running"]:
        return {"success": False, "message": "Execution already in progress"}
    
    asyncio.create_task(execute_workflow(request.steps))
    return {"success": True, "message": "Execution started"}

@app.post("/run_request")
async def run_request(request: RequestString):
    """Accept a free-form user request, break it into steps, and execute them."""
    if current_execution["is_running"]:
        return {"success": False, "message": "Execution already in progress"}
    
    steps = analyze_request_with_llm(request.request)
    asyncio.create_task(execute_workflow(steps))
    return {"success": True, "message": "Execution started", "steps": steps}

@app.post("/tool_call")
async def tool_call(request: ToolRequest):
    """Execute a specific tool directly."""
    logger.info(f"Tool call request: {request.tool_name}")
    
    try:
        if request.tool_name == "browser":
            instruction = request.parameters.get("instruction", "")
            result = await handle_browser_tool(instruction)
        elif request.tool_name == "excel":
            data = request.parameters.get("data", [])
            headers = request.parameters.get("headers", [])
            result = handle_spreadsheet_task(data=data, headers=headers)
        elif request.tool_name == "email":
            draft_text = request.parameters.get("draft_text", None)
            result = handle_email_task(draft_text=draft_text)
        elif request.tool_name == "vision_analyze":
            screenshot_path = request.parameters.get("screenshot_path")
            result = analyze_screenshot(screenshot_path)
        else:
            result = f"Unknown tool: {request.tool_name}"
            
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {str(e)}")
        return {"success": False, "error": str(e)}

@app.websocket("/step-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time step execution updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send current state immediately upon connection
        if current_execution["current_step"] >= 0:
            await websocket.send_json({
                "completedStepIndex": current_execution["current_step"],
                "message": f"Currently at step {current_execution['current_step'] + 1}"
            })
        
        # Keep connection open and handle messages
        while True:
            # Wait for any message (ping/pong)
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.post("/test_excel")
async def test_excel():
    """Test endpoint for Excel functionality."""
    headers = ["Name", "Value"]
    data = [["Test1", 123], ["Test2", 456]]
    result = open_excel_with_data(data=data, headers=headers)
    return {"result": result}

if __name__ == "__main__":
    from config import SERVER_HOST, SERVER_PORT, DEBUG, log_config
    
    # Log configuration settings
    log_config()
    
    logger.info(f"Starting Intervene Backend on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=DEBUG)