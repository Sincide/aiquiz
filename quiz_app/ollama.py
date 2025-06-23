import json
import urllib.request
import urllib.error
from typing import List

OLLAMA_HOST = 'http://localhost:11434'


def list_models() -> List[str]:
    """Get list of available Ollama models"""
    try:
        with urllib.request.urlopen(f'{OLLAMA_HOST}/api/tags', timeout=10) as r:
            data = json.loads(r.read().decode())
            return [m['name'] for m in data.get('models', [])]
    except (urllib.error.URLError, json.JSONDecodeError, Exception):
        return []


def ask_model(model: str, prompt: str) -> str:
    """Ask Ollama model for explanation"""
    if not model:
        return "No model selected"
    
    req_data = {
        'model': model, 
        'prompt': prompt,
        'stream': False,
        'options': {
            'temperature': 0.7,
            'top_k': 40,
            'top_p': 0.9
        }
    }
    
    req = urllib.request.Request(
        f'{OLLAMA_HOST}/api/generate',
        data=json.dumps(req_data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 200:
                return f"Ollama API error: HTTP {r.status}"
            
            response_data = json.loads(r.read().decode('utf-8'))
            
            if 'response' in response_data:
                return response_data['response'].strip()
            elif 'error' in response_data:
                return f"Ollama error: {response_data['error']}"
            else:
                return "Received unexpected response format from Ollama"
                
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            return f"Could not connect to Ollama: {e.reason}"
        elif hasattr(e, 'code'):
            return f"Ollama HTTP error: {e.code}"
        else:
            return f"Ollama connection error: {str(e)}"
    except json.JSONDecodeError:
        return "Received invalid JSON response from Ollama"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def check_ollama_status() -> bool:
    """Check if Ollama is running and accessible"""
    try:
        with urllib.request.urlopen(f'{OLLAMA_HOST}/api/tags', timeout=5) as r:
            return r.status == 200
    except Exception:
        return False
