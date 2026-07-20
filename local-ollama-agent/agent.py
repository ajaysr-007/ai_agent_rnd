import argparse
import json
import sys
import time
from typing import Any, Dict, List

import ollama

import check_ollama
from tools import AVAILABLE_FUNCTIONS, TOOLS


def run_agent(user_query: str, model: str = "llama3.2", max_turns: int = 6, verbose: bool = False) -> str:
    """
    Runs a ReAct-style agent loop using the local ollama service.
    
    Args:
        user_query (str): The initial prompt from the user.
        model (str): The name of the model to use (default: "llama3.2").
        max_turns (int): Maximum number of iterations before forcing an exit.
        verbose (bool): Whether to log tool calls and intermediate steps.
        
    Returns:
        str: The final text answer from the assistant or a fallback message.
    """
    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": user_query}
    ]
    
    if verbose:
        print(f"\n🤖 Starting agent loop with model: {model}")
        print(f"👤 User Query: {user_query}\n")
    
    for turn in range(max_turns):
        if verbose:
            print(f"🔄 Turn {turn + 1}/{max_turns}: Waiting for model response...")
        
        max_retries = 2
        response = None
        
        # Retry loop for transient failures
        for attempt in range(max_retries + 1):
            try:
                response = ollama.chat(
                    model=model,
                    messages=messages,
                    tools=TOOLS
                )
                break  # Success, exit retry loop
            except ollama.ResponseError as e:
                # Catch specific Ollama API errors (like unsupported tools)
                error_msg = str(e).lower()
                if "tool" in error_msg or "not support" in error_msg:
                    return f"❌ Model '{model}' does not support tool calling. Please run `ollama pull llama3.2` or `ollama pull qwen2.5:3b` and try again."
                else:
                    return f"❌ Ollama API Error: {e}"
            except Exception as e:
                # Catch connection errors or other transient issues
                error_msg = str(e).lower()
                if "connection" in error_msg or "refused" in error_msg or "failed" in error_msg:
                    if attempt < max_retries:
                        if verbose:
                            print(f"⚠️ Connection error. Retrying in 1s... ({attempt+1}/{max_retries})")
                        time.sleep(1)
                        continue
                    else:
                        return "❌ Error: Could not connect to the Ollama server. Please ensure it is running by executing `ollama serve` in a separate terminal."
                else:
                    if attempt < max_retries:
                        if verbose:
                            print(f"⚠️ Transient error: {e}. Retrying in 1s... ({attempt+1}/{max_retries})")
                        time.sleep(1)
                        continue
                    return f"❌ Error communicating with Ollama: {e}"
                    
        if response is None:
            return "❌ Error: Failed to get a response from Ollama after retries."
            
        message = response.get("message", {})
        messages.append(message)
        
        tool_calls = message.get("tool_calls", [])
        
        if not tool_calls:
            if verbose:
                print("✅ Model returned final answer.")
            content = message.get("content", "")
            return content if content else "(No content returned)"
            
        if verbose:
            print(f"🛠️  Model requested {len(tool_calls)} tool call(s).")
        
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            fn_name = function.get("name", "")
            fn_args_raw = function.get("arguments", {})
            
            if verbose:
                print(f"   ▶ Calling tool: {fn_name}")
            
            # Parse arguments
            fn_args = {}
            if isinstance(fn_args_raw, str):
                try:
                    fn_args = json.loads(fn_args_raw)
                except json.JSONDecodeError:
                    if verbose:
                        print(f"   ⚠️ Warning: Failed to parse arguments as JSON: {fn_args_raw}")
            elif isinstance(fn_args_raw, dict):
                fn_args = fn_args_raw
                
            if verbose:
                print(f"   ▶ Arguments: {fn_args}")
            
            tool_result = ""
            if fn_name not in AVAILABLE_FUNCTIONS:
                tool_result = f"Error: Tool '{fn_name}' not found."
                if verbose:
                    print(f"   ❌ {tool_result}")
            else:
                try:
                    result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                    tool_result = str(result)
                    if verbose:
                        print(f"   ✔️ Result: {tool_result}")
                except Exception as e:
                    tool_result = f"Error executing tool '{fn_name}': {e}"
                    if verbose:
                        print(f"   ❌ {tool_result}")
                    
            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": tool_result
            })
            
    if verbose:
        print(f"\n🛑 Reached max_turns ({max_turns}) without completing the task.")
    return "Error: Agent could not complete the task within the maximum number of turns."

def main():
    parser = argparse.ArgumentParser(description="Local Ollama ReAct Agent")
    parser.add_argument("query", nargs="*", help="The user query to run")
    parser.add_argument("--model", type=str, default="llama3.2", help="Ollama model to use (default: llama3.2)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging of tool calls and agent thought process")
    
    args = parser.parse_args()

    # 1. Run pre-flight checks
    if args.verbose:
        print("==========================================")
        print("Running initial setup checks...")
        print("==========================================")
    
    check_ollama.check_server()
    check_ollama.check_models()
    
    if args.verbose:
        print("==========================================\n")
    
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
        print("Query cannot be empty.")
        sys.exit(1)
        
    # 3. Run the agent
    final_answer = run_agent(user_query=query, model=args.model, verbose=args.verbose)
    
    # 4. Display the final result
    print("\n" + "="*40)
    print("✨ FINAL ANSWER ✨")
    print("="*40)
    print(final_answer)
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
