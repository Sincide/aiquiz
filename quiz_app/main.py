import os
import tkinter as tk
from typing import List

from .data import load_questions
from .db import init_db
from .config import load_config
from .ollama import list_models, check_ollama_status
from .ui import QuizUI


def main():
    cfg = load_config()
    if not os.path.exists(cfg['data_dir']):
        os.makedirs(cfg['data_dir'], exist_ok=True)
        print(f'Created data directory: {cfg["data_dir"]}')
        print('Place question JSON files in', cfg['data_dir'])
        return
        
    questions = load_questions(cfg['data_dir'])
    if not questions:
        print('No questions found. Add JSON files to', cfg['data_dir'])
        print('Sample JSON format:')
        print('[{"id": "1", "domain": "Security Management", "type": "mcq", "question": "...", "choices": [...], "answer": "..."}]')
        return
        
    print(f'Loaded {len(questions)} questions from {len(set(q.filepath for q in questions))} files')
    
    # Check Ollama availability
    model = ''
    if check_ollama_status():
        models = list_models()
        if models:
            print('Available Ollama models:', ', '.join(models))
            model = cfg.get('ollama_model', models[0])
            if model not in models:
                model = models[0]
            print(f'Using model: {model}')
        else:
            print('Ollama is running but no models found')
    else:
        print('Ollama not available - explanations will be disabled')
    
    conn = init_db()
    root = tk.Tk()
    
    try:
        QuizUI(root, questions, conn, model)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nQuiz application closed")
    except Exception as e:
        print(f"Error running quiz application: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
