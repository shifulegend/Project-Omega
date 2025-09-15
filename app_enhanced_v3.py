#!/usr/bin/env python3
"""
Project Omega Enhanced v3.0.0 - Advanced AI Chat Interface
Features:
- Multiple tunnel providers (Cloudflare, ngrok, localtunnel, serveo)
- Self-learning AI with feedback system and learning logs
- Internet access for all models via web search
- Agent mode with secure RunPod terminal access
- Enhanced session management and AI settings
"""

import os
import json
import sqlite3
import requests
import time
import subprocess
import threading
import hashlib
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import re
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega-enhanced-v3-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
OLLAMA_API_URL = "http://localhost:11434"
FASTAPI_URL = "http://localhost:8000"
DATABASE_PATH = "chat_sessions.db"
LEARNINGS_DATABASE_PATH = "ai_learnings.db"
TUNNELS_DATABASE_PATH = "tunnel_providers.db"

# Active tunnels storage
ACTIVE_TUNNELS = {}
TUNNEL_PROCESSES = {}

# Model configurations with internet access capability
MODEL_CONFIGS = {
    "mistral:7b-instruct": {
        "name": "Mistral 7B Instruct",
        "type": "standard",
        "supports_thinking": False,
        "supports_internet": True,
        "default_temperature": 0.7,
        "description": "Fast and efficient general-purpose model with web search"
    },
    "codellama:13b-instruct": {
        "name": "CodeLlama 13B Instruct", 
        "type": "standard",
        "supports_thinking": False,
        "supports_internet": True,
        "default_temperature": 0.3,
        "description": "Specialized for code generation with internet access"
    },
    "wizardlm-uncensored:13b": {
        "name": "WizardLM Uncensored 13B",
        "type": "high_reasoning",
        "supports_thinking": True,
        "supports_internet": True,
        "default_temperature": 0.8,
        "description": "Advanced reasoning with web search capabilities"
    },
    "dolphin-mistral:7b": {
        "name": "Dolphin Mistral 7B",
        "type": "advanced",
        "supports_thinking": True,
        "supports_internet": True,
        "default_temperature": 0.9,
        "description": "Creative and uncensored responses with internet access"
    },
    "agent-mode": {
        "name": "RunPod Agent Mode",
        "type": "agent",
        "supports_thinking": True,
        "supports_internet": True,
        "supports_terminal": True,
        "default_temperature": 0.5,
        "description": "AI agent with full RunPod terminal access and internet"
    }
}

# Tunnel provider configurations
TUNNEL_PROVIDERS = {
    "cloudflare": {
        "name": "Cloudflare Tunnel",
        "command": ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
        "url_pattern": r"https://[\w-]+\.trycloudflare\.com",
        "priority": 1,
        "enabled": True
    },
    "ngrok": {
        "name": "ngrok",
        "command": ["ngrok", "http", "5000"],
        "url_pattern": r"https://[\w-]+\.ngrok-free\.app",
        "priority": 2,
        "enabled": True
    },
    "localtunnel": {
        "name": "LocalTunnel",
        "command": ["lt", "--port", "5000"],
        "url_pattern": r"https://[\w-]+\.loca\.lt",
        "priority": 3,
        "enabled": True
    },
    "serveo": {
        "name": "Serveo",
        "command": ["ssh", "-R", "80:localhost:5000", "serveo.net"],
        "url_pattern": r"https://[\w-]+\.serveo\.net",
        "priority": 4,
        "enabled": True
    }
}

class DatabaseManager:
    """Enhanced database manager for sessions, learnings, and tunnels"""
    
    @staticmethod
    def init_databases():
        """Initialize all databases"""
        DatabaseManager.init_sessions_db()
        DatabaseManager.init_learnings_db()
        DatabaseManager.init_tunnels_db()
    
    @staticmethod
    def init_sessions_db():
        """Initialize chat sessions database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                model TEXT NOT NULL,
                system_prompt TEXT,
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2048,
                thinking_mode BOOLEAN DEFAULT 0,
                internet_access BOOLEAN DEFAULT 1,
                agent_mode BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def init_learnings_db():
        """Initialize AI learnings database"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_correction TEXT NOT NULL,
                ai_mistake TEXT NOT NULL,
                context TEXT,
                model_used TEXT,
                learning_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learning_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                FOREIGN KEY (learning_id) REFERENCES learnings (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def init_tunnels_db():
        """Initialize tunnel providers database"""
        conn = sqlite3.connect(TUNNELS_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tunnel_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

class WebSearchManager:
    """Handle web search for internet-enabled models"""
    
    @staticmethod
    def search_web(query: str, max_results: int = 5) -> List[Dict]:
        """Search web using DuckDuckGo API"""
        try:
            # Simple web search implementation
            search_url = f"https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Extract results from DuckDuckGo response
                if 'RelatedTopics' in data:
                    for topic in data['RelatedTopics'][:max_results]:
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append({
                                'title': topic.get('Text', '')[:100],
                                'url': topic.get('FirstURL', ''),
                                'snippet': topic.get('Text', '')
                            })
                
                return results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
        
        return []
    
    @staticmethod
    def enhance_prompt_with_search(prompt: str, enable_search: bool = True) -> str:
        """Enhance user prompt with web search results if needed"""
        if not enable_search:
            return prompt
        
        # Check if user is asking for current information
        search_triggers = ['latest', 'current', 'recent', 'today', 'news', 'what is', 'tell me about']
        
        if any(trigger in prompt.lower() for trigger in search_triggers):
            # Extract search query
            search_query = prompt[:100]  # Use first 100 chars as search query
            search_results = WebSearchManager.search_web(search_query)
            
            if search_results:
                search_context = "\n\n[INTERNET SEARCH RESULTS]:\n"
                for i, result in enumerate(search_results[:3], 1):
                    search_context += f"{i}. {result['title']}\n   {result['snippet'][:200]}...\n"
                
                return prompt + search_context
        
        return prompt

class LearningManager:
    """Manage AI learning and feedback system"""
    
    @staticmethod
    def record_learning(session_id: str, user_correction: str, ai_mistake: str, 
                       context: str, model_used: str) -> int:
        """Record a new learning from user feedback"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        
        # Generate learning summary
        learning_summary = LearningManager._generate_learning_summary(
            user_correction, ai_mistake, context
        )
        
        cursor.execute('''
            INSERT INTO learnings 
            (session_id, user_correction, ai_mistake, context, model_used, learning_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_correction, ai_mistake, context, model_used, learning_summary))
        
        learning_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded learning {learning_id} for session {session_id}")
        return learning_id
    
    @staticmethod
    def _generate_learning_summary(correction: str, mistake: str, context: str) -> str:
        """Generate a concise learning summary"""
        return f"Avoid: {mistake[:100]}... | Correct approach: {correction[:100]}..."
    
    @staticmethod
    def get_relevant_learnings(prompt: str, model: str) -> List[Dict]:
        """Get relevant past learnings for current prompt"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        
        # Simple keyword matching for relevant learnings
        cursor.execute('''
            SELECT learning_summary, applied_count, effectiveness_score 
            FROM learnings 
            WHERE model_used = ? 
            ORDER BY effectiveness_score DESC, created_at DESC 
            LIMIT 5
        ''', (model,))
        
        learnings = cursor.fetchall()
        conn.close()
        
        return [
            {
                'summary': learning[0],
                'applied_count': learning[1],
                'effectiveness_score': learning[2]
            }
            for learning in learnings
        ]
    
    @staticmethod
    def get_learning_logs(limit: int = 50) -> List[Dict]:
        """Get recent learning logs for display"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, user_correction, ai_mistake, learning_summary, 
                   model_used, applied_count, effectiveness_score, created_at
            FROM learnings 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': log[0],
                'session_id': log[1],
                'user_correction': log[2],
                'ai_mistake': log[3],
                'learning_summary': log[4],
                'model_used': log[5],
                'applied_count': log[6],
                'effectiveness_score': log[7],
                'created_at': log[8]
            }
            for log in logs
        ]

class TunnelManager:
    """Manage multiple tunnel providers"""
    
    @staticmethod
    def start_all_tunnels():
        """Start all enabled tunnel providers"""
        for provider, config in TUNNEL_PROVIDERS.items():
            if config['enabled']:
                TunnelManager.start_tunnel(provider)
    
    @staticmethod
    def start_tunnel(provider: str):
        """Start a specific tunnel provider"""
        if provider in TUNNEL_PROCESSES:
            logger.info(f"Tunnel {provider} already running")
            return
        
        config = TUNNEL_PROVIDERS.get(provider)
        if not config:
            logger.error(f"Unknown tunnel provider: {provider}")
            return
        
        try:
            # Start tunnel process
            process = subprocess.Popen(
                config['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            TUNNEL_PROCESSES[provider] = process
            
            # Monitor tunnel output in separate thread
            threading.Thread(
                target=TunnelManager._monitor_tunnel,
                args=(provider, process),
                daemon=True
            ).start()
            
            logger.info(f"Started tunnel: {provider}")
            
        except Exception as e:
            logger.error(f"Failed to start tunnel {provider}: {e}")
    
    @staticmethod
    def _monitor_tunnel(provider: str, process):
        """Monitor tunnel process and extract URL"""
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    # Extract URL using regex
                    url_match = re.search(TUNNEL_PROVIDERS[provider]['url_pattern'], output)
                    if url_match:
                        url = url_match.group()
                        ACTIVE_TUNNELS[provider] = url
                        TunnelManager._save_tunnel_url(provider, url)
                        logger.info(f"Tunnel {provider} active at: {url}")
                        
                        # Emit to all connected clients
                        socketio.emit('tunnel_update', {
                            'provider': provider,
                            'url': url,
                            'status': 'active'
                        })
        
        except Exception as e:
            logger.error(f"Error monitoring tunnel {provider}: {e}")
    
    @staticmethod
    def _save_tunnel_url(provider: str, url: str):
        """Save tunnel URL to database"""
        conn = sqlite3.connect(TUNNELS_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tunnel_urls (provider, url, status) VALUES (?, ?, 'active')
        ''', (provider, url))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_active_tunnels() -> Dict[str, str]:
        """Get all active tunnel URLs"""
        return ACTIVE_TUNNELS.copy()
    
    @staticmethod
    def stop_tunnel(provider: str):
        """Stop a specific tunnel"""
        if provider in TUNNEL_PROCESSES:
            TUNNEL_PROCESSES[provider].terminate()
            del TUNNEL_PROCESSES[provider]
            if provider in ACTIVE_TUNNELS:
                del ACTIVE_TUNNELS[provider]
            logger.info(f"Stopped tunnel: {provider}")

class AgentMode:
    """Handle secure RunPod terminal access for agent mode"""
    
    @staticmethod
    def execute_command(command: str, session_id: str) -> Dict[str, str]:
        """Safely execute terminal command in agent mode"""
        try:
            # Security checks
            if not AgentMode._is_safe_command(command):
                return {
                    'success': False,
                    'output': '',
                    'error': 'Command blocked for security reasons'
                }
            
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/root'  # RunPod home directory
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Command timeout (30s limit)'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    @staticmethod
    def _is_safe_command(command: str) -> bool:
        """Check if command is safe to execute"""
        # Block dangerous commands
        dangerous_patterns = [
            r'\brm\s+-rf\s+/',  # rm -rf /
            r'\bshutdown\b',     # shutdown
            r'\breboot\b',       # reboot
            r'\bhalt\b',         # halt
            r'\bmkfs\b',         # mkfs
            r'\bddof=/dev/',     # dd of=/dev/
            r':\(\)\{.*\|\&\}:', # fork bomb
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        return True

# Initialize databases
DatabaseManager.init_databases()

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index_enhanced_v3.html', 
                         models=MODEL_CONFIGS,
                         tunnels=TunnelManager.get_active_tunnels())

@app.route('/learning_logs')
def learning_logs():
    """Learning logs interface"""
    logs = LearningManager.get_learning_logs()
    return render_template('learning_logs.html', logs=logs)

@app.route('/api/tunnels')
def api_tunnels():
    """Get active tunnel URLs"""
    return jsonify(TunnelManager.get_active_tunnels())

@app.route('/api/start_tunnel/<provider>')
def api_start_tunnel(provider):
    """Start a specific tunnel provider"""
    TunnelManager.start_tunnel(provider)
    return jsonify({'status': 'started', 'provider': provider})

@app.route('/api/learning_feedback', methods=['POST'])
def api_learning_feedback():
    """Record user feedback for AI learning"""
    data = request.get_json()
    
    learning_id = LearningManager.record_learning(
        session_id=data.get('session_id'),
        user_correction=data.get('user_correction'),
        ai_mistake=data.get('ai_mistake'),
        context=data.get('context', ''),
        model_used=data.get('model_used')
    )
    
    return jsonify({'success': True, 'learning_id': learning_id})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'msg': 'Connected to Project Omega Enhanced v3.0.0'})
    emit('tunnels_update', TunnelManager.get_active_tunnels())

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming chat messages with enhanced features"""
    session_id = data.get('session_id')
    message = data.get('message')
    model = data.get('model', 'mistral:7b-instruct')
    temperature = float(data.get('temperature', 0.7))
    max_tokens = int(data.get('max_tokens', 2048))
    thinking_mode = data.get('thinking_mode', False)
    internet_access = data.get('internet_access', True)
    agent_mode = data.get('agent_mode', False)
    system_prompt = data.get('system_prompt', '')
    
    try:
        # Handle agent mode commands
        if agent_mode and model == 'agent-mode':
            handle_agent_mode(session_id, message, data)
            return
        
        # Enhance prompt with internet search if enabled
        if internet_access and MODEL_CONFIGS.get(model, {}).get('supports_internet'):
            enhanced_message = WebSearchManager.enhance_prompt_with_search(message)
        else:
            enhanced_message = message
        
        # Get relevant learnings
        learnings = LearningManager.get_relevant_learnings(enhanced_message, model)
        
        # Add learnings context to system prompt
        if learnings:
            learning_context = "\n\n[PREVIOUS LEARNINGS]:\n"
            for learning in learnings:
                learning_context += f"- {learning['summary']}\n"
            system_prompt += learning_context
        
        # Send message to AI model
        ai_response = send_to_ollama(enhanced_message, model, temperature, max_tokens, 
                                   thinking_mode, system_prompt)
        
        # Store conversation in database
        store_message(session_id, 'user', message)
        store_message(session_id, 'assistant', ai_response)
        
        # Send response back to client
        emit('message_response', {
            'response': ai_response,
            'model': model,
            'internet_used': internet_access and 'INTERNET SEARCH RESULTS' in enhanced_message,
            'learnings_applied': len(learnings)
        })
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        emit('error', {'message': f'Error: {str(e)}'})

def handle_agent_mode(session_id: str, message: str, data: dict):
    """Handle agent mode with terminal access"""
    try:
        # Check if this is a terminal command
        if message.startswith('/cmd ') or message.startswith('/terminal '):
            command = message.split(' ', 1)[1] if ' ' in message else ''
            
            if not command:
                emit('message_response', {
                    'response': 'Please provide a command to execute. Example: /cmd ls -la',
                    'model': 'agent-mode',
                    'is_command_result': False
                })
                return
            
            # Execute command
            result = AgentMode.execute_command(command, session_id)
            
            # Format response
            response = f"**Command:** `{command}`\n\n"
            if result['success']:
                response += f"**Output:**\n```\n{result['output']}\n```"
                if result.get('error'):
                    response += f"\n\n**Stderr:**\n```\n{result['error']}\n```"
            else:
                response += f"**Error:**\n```\n{result['error']}\n```"
            
            emit('message_response', {
                'response': response,
                'model': 'agent-mode',
                'is_command_result': True,
                'command_success': result['success']
            })
            
            # Store in database
            store_message(session_id, 'user', message)
            store_message(session_id, 'assistant', response)
        
        else:
            # Regular AI conversation in agent mode
            system_prompt = data.get('system_prompt', '') + """

You are an AI agent with full access to the RunPod terminal environment. You can:
1. Execute shell commands using /cmd or /terminal prefix
2. Access the internet for current information
3. Analyze files, install software, and manage the system
4. Help with development, debugging, and system administration

When users ask for system operations, suggest the appropriate commands and execute them.
"""
            
            # Use internet-enabled response
            enhanced_message = WebSearchManager.enhance_prompt_with_search(message, True)
            ai_response = send_to_ollama(enhanced_message, 'mistral:7b-instruct', 
                                       0.7, 2048, True, system_prompt)
            
            emit('message_response', {
                'response': ai_response,
                'model': 'agent-mode',
                'is_command_result': False
            })
            
            store_message(session_id, 'user', message)
            store_message(session_id, 'assistant', ai_response)
    
    except Exception as e:
        logger.error(f"Agent mode error: {e}")
        emit('error', {'message': f'Agent mode error: {str(e)}'})

def send_to_ollama(message: str, model: str, temperature: float, max_tokens: int, 
                   thinking_mode: bool, system_prompt: str = '') -> str:
    """Send message to Ollama API with enhanced features"""
    try:
        url = f"{OLLAMA_API_URL}/api/generate"
        
        prompt = message
        if system_prompt:
            prompt = f"System: {system_prompt}\n\nUser: {message}"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', 'No response received')
        else:
            return f"Error: Ollama API returned status {response.status_code}"
    
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return f"Error communicating with Ollama: {str(e)}"

def store_message(session_id: str, role: str, content: str):
    """Store message in database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database storage error: {e}")

if __name__ == '__main__':
    # Start all tunnel providers
    logger.info("Starting Project Omega Enhanced v3.0.0...")
    TunnelManager.start_all_tunnels()
    
    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)