import json
import urllib.request
from typing import List

OLLAMA_HOST = 'http://localhost:11434'


def list_models() -> List[str]:
    try:
        with urllib.request.urlopen(f'{OLLAMA_HOST}/api/tags') as r:
            data = json.loads(r.read().decode())
            return [m['name'] for m in data.get('models', [])]
    except Exception:
        return []


def ask_model(model: str, prompt: str) -> str:
    req = urllib.request.Request(
        f'{OLLAMA_HOST}/api/generate',
        data=json.dumps({'model': model, 'prompt': prompt}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read().decode())
            return resp.get('response', '')
    except Exception as e:
        return f'Ollama error: {e}'
