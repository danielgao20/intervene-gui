from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List, Dict, Any, Optional
import uvicorn
import time
import json
from pydantic import BaseModel

# Import your existing task functions
from tasks import run_email_excel_workflow, create_latest_email_reply_task, open_excel_with_data
from browser_use_agent import run_browser_task
from llm_task_analyzer import analyze_request_with_llm

app = FastAPI(title="Intervene Backend")

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
    steps: List[str]

class RequestString(BaseModel):
    request: str

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
                print(f"Error sending update: {e}")

def classify_query(query: str) -> str:
    """Classify the query as 'browser', 'excel', or 'other'."""
    browser_keywords = [r'open (website|google|url|chrome|browser)', r'search', r'navigate', r'browser']
    excel_keywords = [r'excel', r'spreadsheet', r'workbook', r'cell', r'column', r'row']
    for pat in browser_keywords:
        if re.search(pat, query, re.IGNORECASE):
            return 'browser'
    for pat in excel_keywords:
        if re.search(pat, query, re.IGNORECASE):
            return 'excel'
    return 'other'

async def execute_workflow(steps: list):
    """Execute the workflow, routing each step to the correct handler."""
    global current_execution
    
    current_execution["is_running"] = True
    current_execution["steps"] = steps
    current_execution["current_step"] = -1
    
    try:
        for i, step in enumerate(steps):
            current_execution["current_step"] = i
            await notify_clients(current_execution["current_step"], f"Started step {i+1}: {step['instruction']}")
            if step['type'] == 'browser':
                result = await run_browser_task(step['instruction'])
            elif step['type'] == 'excel':
                headers = step.get('headers')
                data = step.get('data')
                if headers is not None or data is not None:
                    result = open_excel_with_data(data=data or [], headers=headers or [])
                else:
                    result = open_excel_with_data()
            else:
                result = f"Unsupported query type for step: {step['instruction']}"
            await asyncio.sleep(1)
            await notify_clients(current_execution["current_step"], f"Completed step {i+1}: {result}")
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Error executing workflow: {e}")
    finally:
        current_execution["is_running"] = False

@app.post("/steps")
async def receive_steps(request: StepsRequest):
    """(Legacy) Receive explicit steps and start execution."""
    if current_execution["is_running"]:
        return {"success": False, "message": "Execution already in progress"}
    asyncio.create_task(execute_workflow(request.steps))
    return {"success": True, "message": "Execution started"}

@app.post("/run_request")
async def run_request(request: RequestString):
    """Accept a free-form user request, break it into steps, and execute them automatically."""
    if current_execution["is_running"]:
        return {"success": False, "message": "Execution already in progress"}
    steps = analyze_request_with_llm(request.request)
    asyncio.create_task(execute_workflow(steps))
    return {"success": True, "message": "Execution started", "steps": steps}

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
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.post("/test_excel")
async def test_excel():
    headers = ["Name", "Value"]
    data = [["Test1", 123], ["Test2", 456]]
    result = open_excel_with_data(data=data, headers=headers)
    return {"result": result}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)