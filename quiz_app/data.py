import json
import os
from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class Question:
    id: str
    domain: str
    type: str  # 'mcq' or 'ordering'
    text: str
    choices: List[str]
    answer: Any
    explanation: str = ''
    filepath: str = ''




def load_questions(folder: str) -> List[Question]:
    """Load all questions from JSON files in folder and from quiz.json in root."""
    questions = []
    
    # Load from quiz.json in root directory first (if exists)
    quiz_json_path = 'quiz.json'
    if os.path.exists(quiz_json_path):
        print(f'Loading questions from {quiz_json_path}')
        with open(quiz_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i, q in enumerate(data):
                # Convert quiz.json format to our format
                if 'options' in q:
                    choices = [q['options'][key] for key in ['A', 'B', 'C', 'D'] if key in q['options']]
                    correct_answer = q['options'].get(q.get('correct_answer', ''), q.get('correct_answer', ''))
                else:
                    choices = q.get('choices', [])
                    correct_answer = q.get('answer', q.get('correct_answer', ''))
                
                question_text = q.get('question_text', q.get('question', q.get('text', '')))
                
                question = Question(
                    id=str(q.get('question_number', i + 1)),
                    domain=q.get('domain', 'CISSP General'),
                    type=q.get('type', 'mcq'),
                    text=question_text,
                    choices=choices,
                    answer=correct_answer,
                    explanation=q.get('explanation', ''),
                    filepath=quiz_json_path
                )
                questions.append(question)
    
    # Also load from data folder (existing format)
    for root, _, files in os.walk(folder):
        for name in files:
            if name.endswith('.json'):
                path = os.path.join(root, name)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'questions' in data:
                        items = data['questions']
                    else:
                        items = data
                    for i, q in enumerate(items):
                        question = Question(
                            id=str(q.get('id', f"{name}_{i+1}")),
                            domain=q.get('domain', 'Unknown'),
                            type=q.get('type', 'mcq'),
                            text=q.get('question', q.get('text', '')),
                            choices=q.get('choices', []),
                            answer=q.get('answer'),
                            explanation=q.get('explanation', ''),
                            filepath=path
                        )
                        questions.append(question)
    return questions
