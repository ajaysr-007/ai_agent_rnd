# Understanding the AI Agent

This document answers common questions about how the `local-ollama-agent` works, why it is considered an "agent", and how it differs from traditional scripts.

### 1. Are there any LLM calls happening in this?
**Yes.** Every time the code calls `ollama.chat(...)` in `agent.py` (around line 38), it is making a direct network request to the local Large Language Model (LLM) you downloaded (e.g., `llama3.2`). The LLM is the "brain" of this entire operation.

### 2. How is this fetching data and how does it work?
When you ask a question like *"What is the weather in Bangalore?"*, the script doesn't have a hardcoded `if/else` statement to handle weather. Instead:
1. It sends your exact question to the LLM.
2. The LLM reads your question and realizes it doesn't know the weather. However, because we passed the `TOOLS` list to it, the LLM knows a tool named `get_weather` exists.
3. The LLM replies back to our Python script saying: *"Hey, pause my generation and run the `get_weather` tool for the city 'Bangalore'."*
4. Our Python script (`agent.py`) catches this request, runs the python function `get_weather("Bangalore")`, gets the result, and sends that result *back* to the LLM.
5. The LLM then reads the result and formats a nice human-readable sentence for you.

### 3. Where exactly is the tool calling happening?
In `agent.py`, inside the `run_agent` loop. 
- The **LLM requests a tool call** by returning a `tool_calls` list in its response.
- The **Python script executes the tool** around line 112: `result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)`. This is where the actual code execution happens. The LLM itself **cannot run code**; it just tells Python *what* code to run.

### 4. How is this not a simple API? What makes it an "AI Agent"?
A simple API takes an input and returns a hardcoded, predictable output (e.g., a calculator API). 
An **AI Agent** is autonomous. 
- We don't tell the script *when* to use the calculator or the weather tool. 
- The LLM acts as a reasoning engine. It reads the prompt, **decides** if it needs a tool, **picks** the right tool, and **understands** the output. If you ask a question that requires multiple steps (like *"Calculate 5*5 and get the weather for that zip code"*), an agent can figure out the sequence of actions entirely on its own.

### 5. Where is the agent "planning" before executing?
This agent uses a pattern called **ReAct** (Reasoning and Acting). 
When you pass the `--verbose` flag to `agent.py`, you can see the agent "thinking". The loop in `agent.py` (`for turn in range(max_turns):`) is the environment where this planning and acting cycle happens. 
If the LLM needs 3 different tools to answer your question, it will plan to call them one by one, analyzing the result of each before deciding what to do next.

### 6. How can I use better LLMs for higher accuracy?
Local models like `llama3.2` are great because they are free and private, but they aren't always as smart as massive cloud models. If you want higher accuracy:
1. **Bigger Local Models:** If your PC has enough RAM/VRAM, you can run larger models locally. Run `ollama pull qwen2.5:14b` or `llama3.1:8b`, then use `python agent.py --model qwen2.5:14b`.
2. **Cloud Models:** You can swap out the `ollama.chat()` call with the OpenAI API to use `GPT-4o`, or the Anthropic API to use `Claude-3.5-Sonnet`. The logic of the `agent.py` loop remains exactly the same; you just change the API client sending the messages!

### 7. (Additional) What happens if a tool fails?
If a tool crashes, the `agent.py` script wraps it in a `try/except` block. Instead of crashing the whole program, the Python script sends the error message back to the LLM. Because it's an intelligent agent, the LLM reads the error, realizes what went wrong, and can attempt to fix its arguments and call the tool again!
