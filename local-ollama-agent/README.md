# Local Ollama Agent

A from-scratch implementation of a ReAct-style, tool-calling agent loop in Python using the local [`ollama`](https://github.com/ollama/ollama-python) package, with zero extra dependencies beyond the standard library.

## Prerequisites

1. **Ollama**: Download and install Ollama from [ollama.com](https://ollama.com).
2. **Python**: Python 3.9 or higher.

## Setup

1. **Initialize the Environment**:
   Run the provided setup script to create a virtual environment and install the required Python packages. Ensure you navigate into the project directory first.
   ```powershell
   # On Windows
   cd local-ollama-agent
   .\setup.bat
   ```

2. **Start the Ollama Server**:
   Open a separate terminal and start the server:
   ```bash
   ollama serve
   ```

3. **Pull a Tool-Calling Model**:
   Download a model capable of tool calling, such as `llama3.2` or `qwen2.5:3b`.
   ```bash
   ollama pull llama3.2
   ```

## How to Run

Before running, make sure your virtual environment is activated (`call .venv\Scripts\activate.bat`).

### Command-Line Query
You can pass your query directly as arguments. Use the `--verbose` flag to see the agent's "thoughts" and tool calls in real-time.

```bash
python agent.py --verbose "What's the weather in Bangalore, and what's 45*12?"
```

### Interactive Mode
If you run the script without any query arguments, it will launch an interactive prompt.

```bash
python agent.py
```

### Changing Models
You can easily switch the model used by the agent via the `--model` flag:

```bash
python agent.py --model qwen2.5:3b "Calculate 15% of 850"
```

## Adding a New Tool

Adding a new capability to the agent is extremely straightforward. Open `tools.py` and follow these three steps:

1. **Write the Function**: Create a standard Python function (e.g., `def fetch_news(topic: str) -> str:`). Ensure it catches errors gracefully and returns a string (or a format the LLM can easily read).
2. **Register the Implementation**: Add your function to the `AVAILABLE_FUNCTIONS` dictionary at the bottom of the file.
3. **Define the Schema**: Add a new JSON object to the `TOOLS` list. This object follows the standard OpenAI/Ollama tool-calling format (specifying the function's name, description, and required parameters).

## Troubleshooting

- **Server Not Running (`ConnectionError`)**:
  If the agent cannot reach the server, verify that `ollama serve` is running in the background or in a separate terminal window. By default, it runs on `http://localhost:11434`.

- **Model Doesn't Support Tools**:
  If you see an error stating "Model 'xyz' does not support tool calling", you are using a model that lacks the necessary tool capabilities. Switch to a supported model like `llama3.2` or `qwen2.5:3b`.

- **Slow Responses**:
  If the model takes a very long time to respond, it is likely running solely on your CPU. Ollama will try to utilize GPU acceleration (NVIDIA, Apple Silicon, etc.) automatically if available. If a GPU isn't accessible, consider using smaller parameter models like `qwen2.5:3b` or `llama3.2:1b`.
