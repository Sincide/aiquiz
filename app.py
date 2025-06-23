#!/usr/bin/env python3
"""
CISSP Quiz Web Application
A modern web-based quiz tool for CISSP certification preparation
"""

import os
import json
import random
from flask import Flask, render_template, request, jsonify, session, redirect, g
from datetime import datetime
import sqlite3

# Import existing modules
from quiz_app.data import load_questions
from quiz_app.db import (init_db, save_result, is_favorite, mark_favorite, 
                         get_results_summary, get_favorite_questions)
from quiz_app.config import load_config
from quiz_app.ollama import list_models, check_ollama_status, ask_model

app = Flask(__name__)
app.secret_key = 'cissp_quiz_secret_key_change_in_production'

# Global variables
questions_data = []
db_path = ""
ollama_model = ""

def get_db():
    """Get database connection for current request"""
    if 'db' not in g:
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def close_db_context(error):
    """Close database at end of request"""
    close_db()

def init_app():
    """Initialize the application"""
    global questions_data, db_path, ollama_model
    
    cfg = load_config()
    if not os.path.exists(cfg['data_dir']):
        os.makedirs(cfg['data_dir'], exist_ok=True)
        print(f'Created data directory: {cfg["data_dir"]}')
    
    questions_data = load_questions(cfg['data_dir'])
    print(f'Loaded {len(questions_data)} questions from {len(set(q.filepath for q in questions_data))} files')
    
    # Initialize database and store path for per-request connections
    db_path = 'quiz_results.db'  # Use default path from db.py
    db_connection = init_db(db_path)
    db_connection.close()  # Close the initialization connection
    
    # Check Ollama
    if check_ollama_status():
        models = list_models()
        if models:
            ollama_model = cfg.get('ollama_model', models[0])
            if ollama_model not in models:
                ollama_model = models[0]
            print(f'Using Ollama model: {ollama_model}')
        else:
            print('Ollama running but no models found')
    else:
        print('Ollama not available - explanations will be disabled')

@app.route('/')
def index():
    """Main page with domain selection"""
    domains = sorted(set(q.domain for q in questions_data))
    domain_counts = {domain: sum(1 for q in questions_data if q.domain == domain) 
                    for domain in domains}
    
    return render_template('index.html', 
                         domains=domains, 
                         domain_counts=domain_counts,
                         total_questions=len(questions_data))

@app.route('/api/start_quiz', methods=['POST'])
def start_quiz():
    """Start a new quiz with selected domains"""
    data = request.json
    selected_domains = data.get('domains', [])
    mode = data.get('mode', 'normal')  # normal, favorites
    randomize = data.get('randomize', True)
    
    if not selected_domains and mode == 'normal':
        return jsonify({'error': 'Please select at least one domain'}), 400
    
    if mode == 'favorites':
        fav_ids = get_favorite_questions(get_db())
        if not fav_ids:
            return jsonify({'error': 'No favorite questions found'}), 400
        quiz_questions = [q for q in questions_data if q.id in fav_ids]
    else:
        quiz_questions = [q for q in questions_data if q.domain in selected_domains]
    
    if not quiz_questions:
        return jsonify({'error': 'No questions found for selected criteria'}), 400
    
    # Shuffle if randomization is enabled
    if randomize:
        random.shuffle(quiz_questions)
    
    # Clear any old session data first
    session.pop('questions', None)  # Remove old full question data if exists
    session.pop('question_ids', None)  # Remove old question_ids key if exists
    
    # Store only question IDs to avoid session cookie size limit
    session['quiz_question_ids'] = [q.id for q in quiz_questions]
    session['current_index'] = 0
    session['quiz_mode'] = mode
    session['randomized'] = randomize
    
    return jsonify({
        'success': True, 
        'total_questions': len(quiz_questions),
        'mode': mode,
        'randomized': randomize
    })

@app.route('/quiz')
def quiz():
    """Quiz interface"""
    if 'quiz_question_ids' not in session:
        return redirect('/')
    
    return render_template('quiz.html', 
                         ollama_available=bool(ollama_model))

@app.route('/api/get_question')
def get_question():
    """Get current question"""
    if 'quiz_question_ids' not in session:
        return jsonify({'error': 'No active quiz'}), 400
    
    question_ids = session['quiz_question_ids']
    index = session.get('current_index', 0)
    
    if index >= len(question_ids):
        return jsonify({'completed': True})
    
    # Find the question by ID
    current_question_id = question_ids[index]
    question_obj = next((q for q in questions_data if q.id == current_question_id), None)
    
    if not question_obj:
        return jsonify({'error': 'Question not found'}), 400
    
    # Convert to dict for JSON response
    question = question_obj.__dict__
    is_fav = is_favorite(get_db(), question['id'])
    
    return jsonify({
        'question': question,
        'index': index,
        'total': len(question_ids),
        'is_favorite': is_fav,
        'mode': session.get('quiz_mode', 'normal')
    })

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer"""
    if 'quiz_question_ids' not in session:
        return jsonify({'error': 'No active quiz'}), 400
    
    data = request.json
    user_answer = data.get('answer')
    
    question_ids = session['quiz_question_ids']
    index = session.get('current_index', 0)
    
    if index >= len(question_ids):
        return jsonify({'error': 'Quiz completed'}), 400
    
    # Find the question by ID
    current_question_id = question_ids[index]
    question_obj = next((q for q in questions_data if q.id == current_question_id), None)
    
    if not question_obj:
        return jsonify({'error': 'Question not found'}), 400
    
    question = question_obj.__dict__
    correct_answer = question['answer']
    
    # Check if answer is correct
    if question['type'] == 'mcq':
        correct = (user_answer == correct_answer)
    else:  # ordering
        correct = (user_answer == correct_answer)
    
    # Save result
    save_result(get_db(), question['id'], 
               json.dumps(user_answer), json.dumps(correct_answer), 
               correct, question['domain'])
    
    # Store user answer for AI explanation
    session['last_user_answer'] = user_answer
    session['last_answer_correct'] = correct
    
    # Move to next question
    session['current_index'] = index + 1
    
    return jsonify({
        'correct': correct,
        'correct_answer': correct_answer,
        'explanation': question.get('explanation', ''),
        'next_available': index + 1 < len(question_ids)
    })

@app.route('/api/toggle_favorite', methods=['POST'])
def toggle_favorite():
    """Toggle favorite status of current question"""
    if 'quiz_question_ids' not in session:
        return jsonify({'error': 'No active quiz'}), 400
    
    question_ids = session['quiz_question_ids']
    index = session.get('current_index', 0)
    
    if index >= len(question_ids):
        return jsonify({'error': 'No current question'}), 400
    
    # Find the question by ID
    current_question_id = question_ids[index]
    question_obj = next((q for q in questions_data if q.id == current_question_id), None)
    
    if not question_obj:
        return jsonify({'error': 'Question not found'}), 400
    
    question = question_obj.__dict__
    current_fav = is_favorite(get_db(), question['id'])
    mark_favorite(get_db(), question['id'], not current_fav)
    
    return jsonify({'is_favorite': not current_fav})

@app.route('/api/get_explanation', methods=['POST'])
def get_explanation():
    """Get AI explanation for current question"""
    if not ollama_model:
        return jsonify({'error': 'AI explanations not available'}), 400
    
    if 'quiz_question_ids' not in session:
        return jsonify({'error': 'No active quiz'}), 400
    
    question_ids = session['quiz_question_ids']
    index = session.get('current_index', 0)
    
    if index >= len(question_ids):
        return jsonify({'error': 'No current question'}), 400
    
    # Find the question by ID
    current_question_id = question_ids[index]
    question_obj = next((q for q in questions_data if q.id == current_question_id), None)
    
    if not question_obj:
        return jsonify({'error': 'Question not found'}), 400
    
    question = question_obj.__dict__
    
    # Get user's answer from session
    user_answer = session.get('last_user_answer', 'Unknown')
    was_correct = session.get('last_answer_correct', False)
    
    # Create context-aware prompt based on user's answer
    if was_correct:
        prompt = (
            "You are a CISSP expert tutor. The student answered this question CORRECTLY.\n\n"
            "Provide encouragement and reinforce their understanding:\n"
            "1. Confirm why their answer is correct\n"
            "2. Explain the key concept they demonstrated understanding of\n"
            "3. Mention why the other options were less suitable\n"
            "4. Share any additional insights about this CISSP domain\n\n"
            f"Question: {question['text']}\n\n"
            f"Options:\n"
            f"A) {question['choices'][0]}\n"
            f"B) {question['choices'][1]}\n"
            f"C) {question['choices'][2]}\n"
            f"D) {question['choices'][3]}\n\n"
            f"Student's Answer: {user_answer} ✓ CORRECT\n"
            f"Correct Answer: {question['answer']}\n\n"
            "Keep it positive and educational. Use simple formatting with numbered points."
        )
    else:
        prompt = (
            "You are a CISSP expert tutor. The student answered this question INCORRECTLY.\n\n"
            "Help them learn from their mistake:\n"
            "1. Explain why their chosen answer was incorrect\n"
            "2. Explain why the correct answer is right\n"
            "3. Identify the key concept they may have missed\n"
            "4. Provide study tips for this CISSP domain\n\n"
            f"Question: {question['text']}\n\n"
            f"Options:\n"
            f"A) {question['choices'][0]}\n"
            f"B) {question['choices'][1]}\n"
            f"C) {question['choices'][2]}\n"
            f"D) {question['choices'][3]}\n\n"
            f"Student's Answer: {user_answer} ✗ INCORRECT\n"
            f"Correct Answer: {question['answer']}\n\n"
            "Be supportive but clear about the mistake. Use simple formatting with numbered points."
        )
    
    try:
        explanation = ask_model(ollama_model, prompt)
        return jsonify({'explanation': explanation})
    except Exception as e:
        return jsonify({'error': f'Failed to get explanation: {str(e)}'}), 500

@app.route('/api/explain_question', methods=['POST'])
def explain_question():
    """Get AI explanation of what the question is asking"""
    if not ollama_model:
        return jsonify({'error': 'AI explanations not available'}), 400
    
    if 'quiz_question_ids' not in session:
        return jsonify({'error': 'No active quiz'}), 400
    
    question_ids = session['quiz_question_ids']
    index = session.get('current_index', 0)
    
    if index >= len(question_ids):
        return jsonify({'error': 'No current question'}), 400
    
    # Find the question by ID
    current_question_id = question_ids[index]
    question_obj = next((q for q in questions_data if q.id == current_question_id), None)
    
    if not question_obj:
        return jsonify({'error': 'Question not found'}), 400
    
    question = question_obj.__dict__
    
    prompt = (
        "You are a CISSP expert tutor. Help the student understand what this cybersecurity question is asking.\n\n"
        "Please explain:\n"
        "1. What the question is asking for (the key concept being tested)\n"
        "2. What domain/topic this relates to in CISSP\n"
        "3. Any important terms or concepts mentioned in the question\n"
        "4. What approach should be used to think about this type of question\n\n"
        f"Question: {question['text']}\n\n"
        f"Available Options:\n"
        f"A) {question['choices'][0]}\n"
        f"B) {question['choices'][1]}\n"
        f"C) {question['choices'][2]}\n"
        f"D) {question['choices'][3]}\n\n"
        "DO NOT reveal the correct answer. Focus on helping the student understand what's being asked "
        "and the concepts involved. This is to clarify the question, not solve it."
    )
    
    try:
        explanation = ask_model(ollama_model, prompt)
        return jsonify({'explanation': explanation})
    except Exception as e:
        return jsonify({'error': f'Failed to explain question: {str(e)}'}), 500

@app.route('/statistics')
def statistics():
    """Statistics page"""
    stats = get_results_summary(get_db())
    return render_template('statistics.html', stats=stats)

@app.route('/api/reset_statistics', methods=['POST'])
def reset_statistics():
    """Reset all statistics"""
    try:
        from quiz_app.db import clear_all_statistics
        rows_deleted = clear_all_statistics(get_db())
        return jsonify({
            'success': True, 
            'message': f'Cleared {rows_deleted} quiz results',
            'rows_deleted': rows_deleted
        })
    except Exception as e:
        return jsonify({'error': f'Failed to reset statistics: {str(e)}'}), 500

@app.route('/api/previous_question', methods=['POST'])
def previous_question():
    """Go to previous question"""
    if 'quiz_question_ids' not in session:
        return jsonify({'error': 'No active quiz'}), 400
    
    index = session.get('current_index', 0)
    if index > 0:
        session['current_index'] = index - 1
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Already at first question'}), 400

if __name__ == '__main__':
    init_app()
    print(f"Starting CISSP Quiz Web Application...")
    print(f"Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 