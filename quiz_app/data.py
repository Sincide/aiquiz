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
    """Load all questions from JSON files in folder."""
    questions = []
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
                    for q in items:
                        question = Question(
                            id=str(q.get('id', '')),
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
