import os
import tkinter as tk
from typing import List

from .data import load_questions
from .db import init_db
from .config import load_config
from .ollama import list_models
from .ui import QuizUI


def main():
    cfg = load_config()
    if not os.path.exists(cfg['data_dir']):
        os.makedirs(cfg['data_dir'], exist_ok=True)
        print('Place question JSON files in', cfg['data_dir'])
        return
    questions = load_questions(cfg['data_dir'])
    if not questions:
        print('No questions found. Add JSON files to', cfg['data_dir'])
        return
    models = list_models()
    if models:
        print('Available models:', ', '.join(models))
    model = cfg.get('ollama_model', models[0] if models else '')
    if models and model not in models:
        model = models[0]
    conn = init_db()
    root = tk.Tk()
    QuizUI(root, questions, conn, model)
    root.mainloop()


if __name__ == '__main__':
    main()
