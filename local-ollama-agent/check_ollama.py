import urllib.request
import urllib.error
import sys

try:
    import ollama
except ImportError:
    print("❌ The 'ollama' Python package is not installed.")
    print("Please run setup.bat first to initialize your virtual environment and install dependencies.")
    sys.exit(1)

def check_server():
    """Check if the Ollama server is running and reachable."""
    url = "http://localhost:11434"
    try:
        response = urllib.request.urlopen(url)
        if response.getcode() == 200:
            print("✅ Ollama server is reachable.")
            return True
    except (urllib.error.URLError, ConnectionError):
        pass
    
    print("❌ Ollama server is not reachable at http://localhost:11434.")
    print("Please start the server by opening a new terminal and running:")
    print("\n    ollama serve\n")
    sys.exit(1)

def check_models():
    """List local models and check for recommended tool-calling models."""
    try:
        models_response = ollama.list()
        
        # Depending on the ollama package version, it might return a dict or an object
        models = models_response.get('models', []) if isinstance(models_response, dict) else getattr(models_response, 'models', [])
        
        local_model_names = [m.get('model', '').lower() if isinstance(m, dict) else getattr(m, 'model', '').lower() for m in models]
        
        print(f"\n📦 Found {len(local_model_names)} local models:")
        for name in local_model_names:
            print(f"  - {name}")
            
        recommended_models = ["llama3.2", "qwen2.5:3b", "qwen2.5:7b"]
        
        # Check if the user has any of the recommended models (accounting for tags like :latest)
        def has_model(target):
            return any(m == target or m.startswith(target + ":") for m in local_model_names)
            
        missing_models = [m for m in recommended_models if not has_model(m)]
        present_models = [m for m in recommended_models if has_model(m)]
        
        if not present_models:
            print("\n⚠️ WARNING: None of the recommended tool-calling models are present!")
            
        if missing_models:
            print("\n💡 You can pull the missing recommended models using the following commands:")
            for m in missing_models:
                print(f"    ollama pull {m}")
        else:
            print("\n✅ All recommended tool-calling models are present.")
            
    except Exception as e:
        print(f"\n❌ Error checking models via the ollama python package: {e}")

if __name__ == "__main__":
    print("Running Ollama Pre-flight Checks...\n")
    check_server()
    check_models()
