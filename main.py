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

async def execute_workflow(steps: List[str]):
    """Execute the hardcoded workflow, sending updates after each step."""
    global current_execution
    
    current_execution["is_running"] = True
    current_execution["steps"] = steps
    current_execution["current_step"] = -1
    
    # Map of execution functions for each type of step
    # In a real implementation, you would parse the steps and execute accordingly
    # Here we're hardcoding to your existing workflow
    
    try:
        # Step 1: Email workflow
        current_execution["current_step"] = 0
        await notify_clients(current_execution["current_step"], "Started email workflow")
        
        # Execute email task
        result = create_latest_email_reply_task()
        await asyncio.sleep(1)  # Simulate some processing time
        
        # Step 2: Excel workflow
        current_execution["current_step"] = 1
        await notify_clients(current_execution["current_step"], "Started Excel workflow")
        
        # Execute Excel task
        result = open_excel_with_data()
        await asyncio.sleep(1)  # Simulate some processing time
        
        # Mark remaining steps as complete (if there are more than 2 steps)
        for i in range(2, len(steps)):
            current_execution["current_step"] = i
            await notify_clients(current_execution["current_step"], f"Completed step {i+1}")
            await asyncio.sleep(0.5)  # Short delay between updates
            
    except Exception as e:
        print(f"Error executing workflow: {e}")
    finally:
        current_execution["is_running"] = False

@app.post("/steps")
async def receive_steps(request: StepsRequest):
    """Receive steps from the frontend and start execution."""
    if current_execution["is_running"]:
        return {"success": False, "message": "Execution already in progress"}
    
    # Start execution in background
    asyncio.create_task(execute_workflow(request.steps))
    
    return {"success": True, "message": "Execution started"}

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)