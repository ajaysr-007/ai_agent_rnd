import argparse
import json
import logging
import sys
import time
from typing import Any, Dict, List

import ollama

import check_ollama
from tools import AVAILABLE_FUNCTIONS, TOOLS

# Set up logger for this module
logger = logging.getLogger(__name__)

def run_agent(user_query: str, model: str = "llama3.2", max_turns: int = 6) -> str:
    """
    Runs a ReAct-style agent loop using the local ollama service.
    
    Args:
        user_query (str): The initial prompt from the user.
        model (str): The name of the model to use (default: "llama3.2").
        max_turns (int): Maximum number of iterations before forcing an exit.
        
    Returns:
        str: The final text answer from the assistant or a fallback message.
    """
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "You are a helpful AI assistant. Only use tools when strictly necessary to answer the user's question. If you use multiple tools, you MUST include the results from ALL of them in your final answer. Do not ignore any tool results."},
        {"role": "user", "content": user_query}
    ]
    
    logger.info(f"Starting agent loop with model: '{model}'")
    logger.info(f"User Query: {user_query}")
    
    for turn in range(max_turns):
        logger.info(f"Turn {turn + 1}/{max_turns}: Waiting for model response...")
        
        max_retries = 2
        response = None
        
        # Retry loop for transient failures
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Calling Ollama API (Model: {model}) with {len(messages)} messages.")
                response = ollama.chat(
                    model=model,
                    messages=messages,
                    tools=TOOLS
                )
                logger.debug("Ollama API call successful.")
                break  # Success, exit retry loop
            except ollama.ResponseError as e:
                # Catch specific Ollama API errors (like unsupported tools)
                error_msg = str(e).lower()
                if "tool" in error_msg or "not support" in error_msg:
                    logger.error(f"Model '{model}' does not support tool calling.")
                    return f"❌ Model '{model}' does not support tool calling. Please run `ollama pull llama3.2` or `ollama pull qwen2.5:3b` and try again."
                else:
                    logger.error(f"Ollama API Error: {e}")
                    return f"❌ Ollama API Error: {e}"
            except Exception as e:
                # Catch connection errors or other transient issues
                error_msg = str(e).lower()
                if "connection" in error_msg or "refused" in error_msg or "failed" in error_msg:
                    if attempt < max_retries:
                        logger.warning(f"Connection error. Retrying in 1s... ({attempt+1}/{max_retries})")
                        time.sleep(1)
                        continue
                    else:
                        logger.error("Could not connect to the Ollama server.")
                        return "❌ Error: Could not connect to the Ollama server. Please ensure it is running by executing `ollama serve` in a separate terminal."
                else:
                    if attempt < max_retries:
                        logger.warning(f"Transient error: {e}. Retrying in 1s... ({attempt+1}/{max_retries})")
                        time.sleep(1)
                        continue
                    logger.error(f"Error communicating with Ollama: {e}")
                    return f"❌ Error communicating with Ollama: {e}"
                    
        if response is None:
            logger.error("Failed to get a response from Ollama after retries.")
            return "❌ Error: Failed to get a response from Ollama after retries."
            
        message = response.get("message", {})
        messages.append(message)
        
        tool_calls = message.get("tool_calls", [])
        
        if not tool_calls:
            logger.info("Model returned final answer. No further tools requested.")
            content = message.get("content", "")
            return content if content else "(No content returned)"
            
        logger.info(f"Model requested {len(tool_calls)} tool call(s).")
        
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            fn_name = function.get("name", "")
            fn_args_raw = function.get("arguments", {})
            
            logger.info(f"Calling tool: '{fn_name}'")
            
            # Parse arguments
            fn_args = {}
            if isinstance(fn_args_raw, str):
                try:
                    fn_args = json.loads(fn_args_raw)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse arguments as JSON: {fn_args_raw}")
            elif isinstance(fn_args_raw, dict):
                fn_args = fn_args_raw
                
            logger.debug(f"Tool '{fn_name}' arguments: {fn_args}")
            
            tool_result = ""
            if fn_name not in AVAILABLE_FUNCTIONS:
                tool_result = f"Error: Tool '{fn_name}' not found."
                logger.error(tool_result)
            else:
                try:
                    logger.debug(f"Executing {fn_name}(**{fn_args}) locally...")
                    result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                    tool_result = str(result)
                    logger.info(f"Tool '{fn_name}' execution successful. Result: {tool_result}")
                except Exception as e:
                    tool_result = f"Error executing tool '{fn_name}': {e}"
                    logger.error(tool_result)
                    
            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": tool_result
            })
            
    logger.warning(f"Reached max_turns ({max_turns}) without completing the task.")
    return "Error: Agent could not complete the task within the maximum number of turns."

def main():
    parser = argparse.ArgumentParser(description="Local Ollama ReAct Agent")
    parser.add_argument("query", nargs="*", help="The user query to run")
    parser.add_argument("--model", type=str, default="llama3.2", help="Ollama model to use (default: llama3.2)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging for tool calls and agent thought process")
    
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Run pre-flight checks
    logger.info("Running initial setup checks (via check_ollama.py)...")
    check_ollama.check_server()
    check_ollama.check_models()
    
    # 2. Retrieve user query
    if args.query:
        query = " ".join(args.query)
    else:
        print("Enter your query (or press Ctrl+C to exit):")
        try:
            query = input("> ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
            
    if not query.strip():
        logger.error("Query cannot be empty.")
        sys.exit(1)
        
    # 3. Run the agent
    final_answer = run_agent(user_query=query, model=args.model)
    
    # 4. Display the final result
    print("\n" + "="*60)
    print("✨ FINAL ANSWER ✨")
    print("="*60)
    print(final_answer)
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
