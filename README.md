# Intervene - Local LLM-Powered Automation Agent

Intervene is a local LLM-powered automation agent that can help with tasks like browser automation, spreadsheet management, and email composition without relying on cloud services. This application uses only local LLMs through Ollama for privacy and control.

## Features

- **Local LLM Integration**: Uses Llama 3.2 via locally hosted Ollama (localhost:11434) for all text processing
- **Local Vision Analysis**: Uses locally hosted LLaVA for analyzing screenshots
- **Task Automation**: Breaks down user requests into executable steps
- **API Interface**: FastAPI server for integration with other applications
- **WebSocket Support**: Real-time updates on task progress
- **Safe Automation**: Minimizes the use of dangerous automation libraries

## Requirements

- Python 3.8+
- [Ollama](https://ollama.ai/) installed locally (for running local LLMs)
- Required models:
  - llama3.2 (for task analysis)
  - llava:3 (for screenshot analysis)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/intervene.git
cd intervene
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure the application**

You can customize the application by modifying the `.env` file:

```
# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_VISION_MODEL=llava:3

# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
DEBUG=True

# Logging configuration
LOG_LEVEL=INFO
```

4. **Install Ollama**

Follow the instructions at [ollama.ai](https://ollama.ai/) to install Ollama for your platform.

5. **Start Ollama**

Make sure the Ollama server is running locally on the default port (11434):

```bash
ollama serve
```

6. **Pull required models**

In another terminal:

```bash
ollama pull llama3.2
ollama pull llava:3
```

7. **Verify Ollama is running properly**

You can test that Ollama is running and accessible with:

```bash
curl http://localhost:11434/api/tags
```

This should return a JSON list of available models.


## Usage

1. **Start the server**

```bash
python main.py
```

This will start the FastAPI server on port 8001.

2. **Use the API endpoints**

- `POST /run_request`: Execute a free-form automation request
- `POST /steps`: Execute a predefined list of steps
- `POST /tool_call`: Call a specific tool directly
- `WebSocket /step-updates`: Get real-time updates on step execution

3. **Example API request**

```bash
curl -X POST "http://localhost:8001/run_request" \
     -H "Content-Type: application/json" \
     -d '{"request": "Search for python tutorials and create a spreadsheet with the top 5 results"}'
```

## Project Structure

- `main.py`: Main application entry point and API endpoints
- `agent.py`: Core agent class that orchestrates tasks
- `tasks.py`: Task execution with safer alternatives to PyAutoGUI
- `vision_analyzer.py`: Module for analyzing screenshots using LLaVA
- `llm_task_analyzer.py`: Task analysis using llama3.2
- `listener.py`: Mouse and keyboard event listeners for override detection

## Safety Features

This application prioritizes safety in automation:

- **Safer Alternatives to PyAutoGUI**: Using platform-specific commands and safer APIs
- **Override Detection**: Detects user input to cancel automated tasks
- **Temporary Files**: Uses temporary files for data transfer between applications
- **Error Handling**: Comprehensive error handling and logging

## Requirements.txt

```
fastapi==0.109.2
uvicorn==0.27.1
pydantic==1.10.8
pynput==1.8.1
pyperclip==1.9.0
Pillow==10.2.0
python-dotenv==1.0.1
langchain==0.1.7
langchain-community==0.0.19
ollama==0.1.6
```

## Building an Executable

To build a standalone executable:

```bash
pyinstaller main.spec
```

The executable will be in the `dist` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.