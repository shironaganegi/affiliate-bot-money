import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    print(f"Checking models from: {url.replace(api_key, 'HIDDEN_KEY')}")
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== Available Models ===")
            if "models" in data:
                for model in data["models"]:
                    print(f"- Name: {model.get('name')}")
                    print(f"  Version: {model.get('version')}")
                    print(f"  Methods: {model.get('supportedGenerationMethods')}")
                    print("-" * 20)
            else:
                print("No 'models' key in response.")
                print(json.dumps(data, indent=2))
        else:
            print(f"\nAPI Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_available_models()
