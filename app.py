#!/usr/bin/env python3
"""
Project Omega - Enhanced AI Chat Interface
Advanced web interface with session management, system prompts, and AI settings
"""

import os
import json
import sqlite3
import requests
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
OLLAMA_API_URL = "http://localhost:11434"
FASTAPI_URL = "http://localhost:8000"
DATABASE_PATH = "chat_sessions.db"

# Model configurations
MODEL_CONFIGS = {
    "mistral:7b-instruct": {
        "name": "Mistral 7B Instruct",
        "type": "standard",
        "supports_thinking": False,
        "default_temperature": 0.7,
        "description": "Fast and efficient general-purpose model"
    },
    "codellama:13b-instruct": {
        "name": "CodeLlama 13B Instruct", 
        "type": "standard",
        "supports_thinking": False,
        "default_temperature": 0.3,
        "description": "Specialized for code generation and programming"
    },
    "wizardlm-uncensored:13b": {
        "name": "WizardLM Uncensored 13B",
        "type": "high_reasoning",
        "supports_thinking": True,
        "default_temperature": 0.8,
        "description": "Advanced reasoning and problem-solving capabilities"
    },
    "dolphin-mistral:7b": {
        "name": "Dolphin Mistral 7B",
        "type": "high_reasoning", 
        "supports_thinking": True,
        "default_temperature": 0.6,
        "description": "Intelligent conversational model with reasoning"
    }
}

def init_database():
    """Initialize SQLite database with enhanced schema"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Enhanced chat sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT NOT NULL,
            model_name TEXT NOT NULL,
            system_prompt TEXT DEFAULT '',
            temperature REAL DEFAULT 0.7,
            thinking_mode TEXT DEFAULT 'auto',
            thinking_budget INTEGER DEFAULT 10000,
            max_tokens INTEGER DEFAULT 2048,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Enhanced chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            thinking_time REAL DEFAULT 0,
            token_count INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_available_models():
    """Get available models from Ollama API"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            # Filter to only return models we have configs for
            return [model for model in models if model in MODEL_CONFIGS]
        return list(MODEL_CONFIGS.keys())
    except:
        return list(MODEL_CONFIGS.keys())

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/models')
def api_models():
    """Get available models with configurations"""
    models = get_available_models()
    model_data = []
    for model in models:
        config = MODEL_CONFIGS.get(model, {})
        model_data.append({
            'id': model,
            'name': config.get('name', model),
            'type': config.get('type', 'standard'),
            'supports_thinking': config.get('supports_thinking', False),
            'default_temperature': config.get('default_temperature', 0.7),
            'description': config.get('description', '')
        })
    return jsonify(model_data)

@app.route('/api/sessions')
def get_sessions():
    """Get all chat sessions"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, session_name, model_name, system_prompt, temperature, 
               thinking_mode, thinking_budget, max_tokens, created_at, updated_at
        FROM chat_sessions ORDER BY updated_at DESC
    ''')
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'id': row[0],
            'name': row[1], 
            'model': row[2],
            'system_prompt': row[3],
            'temperature': row[4],
            'thinking_mode': row[5],
            'thinking_budget': row[6],
            'max_tokens': row[7],
            'created_at': row[8],
            'updated_at': row[9]
        })
    conn.close()
    return jsonify(sessions)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new chat session"""
    data = request.json
    session_name = data.get('name', f'Chat {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    model_name = data.get('model', 'mistral:7b-instruct')
    system_prompt = data.get('system_prompt', '')
    temperature = data.get('temperature', MODEL_CONFIGS.get(model_name, {}).get('default_temperature', 0.7))
    thinking_mode = data.get('thinking_mode', 'auto')
    thinking_budget = data.get('thinking_budget', 10000)
    max_tokens = data.get('max_tokens', 2048)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_sessions (session_name, model_name, system_prompt, temperature, 
                                 thinking_mode, thinking_budget, max_tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_name, model_name, system_prompt, temperature, thinking_mode, thinking_budget, max_tokens))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': session_id, 'name': session_name})

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session and all its messages"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Delete messages first (foreign key constraint)
    cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    # Delete session
    cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/sessions/<int:session_id>')
def get_session_messages(session_id):
    """Get messages for a specific session"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute('SELECT * FROM chat_sessions WHERE id = ?', (session_id,))
    session_row = cursor.fetchone()
    if not session_row:
        return jsonify({'error': 'Session not found'}), 404
    
    session_info = {
        'id': session_row[0],
        'name': session_row[1],
        'model': session_row[2],
        'system_prompt': session_row[3],
        'temperature': session_row[4],
        'thinking_mode': session_row[5],
        'thinking_budget': session_row[6],
        'max_tokens': session_row[7]
    }
    
    # Get messages
    cursor.execute('''
        SELECT role, content, thinking_time, token_count, timestamp 
        FROM chat_messages WHERE session_id = ? ORDER BY timestamp
    ''', (session_id,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'role': row[0],
            'content': row[1],
            'thinking_time': row[2],
            'token_count': row[3],
            'timestamp': row[4]
        })
    
    conn.close()
    return jsonify({'session': session_info, 'messages': messages})

@app.route('/api/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    """Update session settings"""
    data = request.json
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    update_fields = []
    values = []
    
    if 'name' in data:
        update_fields.append('session_name = ?')
        values.append(data['name'])
    if 'model' in data:
        update_fields.append('model_name = ?')
        values.append(data['model'])
    if 'system_prompt' in data:
        update_fields.append('system_prompt = ?')
        values.append(data['system_prompt'])
    if 'temperature' in data:
        update_fields.append('temperature = ?')
        values.append(data['temperature'])
    if 'thinking_mode' in data:
        update_fields.append('thinking_mode = ?')
        values.append(data['thinking_mode'])
    if 'thinking_budget' in data:
        update_fields.append('thinking_budget = ?')
        values.append(data['thinking_budget'])
    if 'max_tokens' in data:
        update_fields.append('max_tokens = ?')
        values.append(data['max_tokens'])
    
    if update_fields:
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        values.append(session_id)
        
        query = f"UPDATE chat_sessions SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

def save_message(session_id, role, content, thinking_time=0, token_count=0):
    """Save a message to the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_messages (session_id, role, content, thinking_time, token_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, role, content, thinking_time, token_count))
    
    # Update session timestamp
    cursor.execute('UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))
    
    conn.commit()
    conn.close()

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming chat messages with enhanced features"""
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    
    if not session_id or not message:
        emit('error', {'message': 'Invalid session or empty message'})
        return
    
    # Get session configuration
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT model_name, system_prompt, temperature, thinking_mode, thinking_budget, max_tokens FROM chat_sessions WHERE id = ?', (session_id,))
    session_row = cursor.fetchone()
    conn.close()
    
    if not session_row:
        emit('error', {'message': 'Session not found'})
        return
        
    model_name, system_prompt, temperature, thinking_mode, thinking_budget, max_tokens = session_row
    
    # Save user message
    save_message(session_id, 'user', message)
    
    # Emit status updates
    emit('status_update', {'status': 'thinking', 'message': 'AI is thinking...'})
    
    try:
        start_time = time.time()
        
        # Prepare conversation history
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY timestamp', (session_id,))
        history = cursor.fetchall()
        conn.close()
        
        # Build messages for API
        messages = []
        
        # Add system prompt if provided
        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        
        # Add conversation history
        for role, content in history:
            messages.append({"role": role, "content": content})
        
        # Prepare API request
        api_payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Add thinking mode settings for supported models
        model_config = MODEL_CONFIGS.get(model_name, {})
        if model_config.get('supports_thinking') and thinking_mode != 'disabled':
            api_payload["options"]["thinking_mode"] = thinking_mode
            if thinking_budget > 0:
                api_payload["options"]["thinking_budget"] = thinking_budget
        
        # Make API request
        response = requests.post(f"{OLLAMA_API_URL}/api/chat", json=api_payload, timeout=120)
        
        thinking_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('message', {}).get('content', 'No response generated')
            
            # Estimate token count (rough approximation)
            token_count = len(ai_response.split()) + len(message.split())
            
            # Save AI response
            save_message(session_id, 'assistant', ai_response, thinking_time, token_count)
            
            # Send response with metrics
            emit('ai_response', {
                'message': ai_response,
                'thinking_time': round(thinking_time, 2),
                'token_count': token_count,
                'model': model_name
            })
            
            emit('status_update', {'status': 'ready', 'message': 'Ready for next message'})
            
        else:
            error_msg = f"API Error: {response.status_code}"
            emit('error', {'message': error_msg})
            emit('status_update', {'status': 'error', 'message': error_msg})
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        emit('error', {'message': error_msg})
        emit('status_update', {'status': 'error', 'message': error_msg})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to Project Omega Enhanced'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    init_database()
    print("🚀 Starting Project Omega Enhanced Chat Interface...")
    print("📊 Features: Session Management, System Prompts, AI Settings, Status Tracking")
    print("🌐 Access via Cloudflare tunnel")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)