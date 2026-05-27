# ============================================================
# Full Stack Integration: Calling Your Deployed Agent
# ============================================================
# This file shows how to integrate your deployed Wanderly agent
# into a real application using Flask (backend) + HTML (frontend).
#
# pip install flask boto3
#
# Run: python fullstack_integration.py
# Open: http://localhost:5000
# ============================================================

import json
import uuid
from flask import Flask, request, jsonify, render_template_string

# ============================================================
# CONFIGURATION - Set these as environment variables
# ============================================================
# 
# Option 1: Set environment variables before running:
#   Windows CMD:   set AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:123456789:runtime/wanderly_travel_agent
#   Windows PS:    $env:AGENT_RUNTIME_ARN="arn:aws:bedrock-agentcore:us-east-1:123456789:runtime/wanderly_travel_agent"
#   Linux/Mac:     export AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:123456789:runtime/wanderly_travel_agent
#
# Option 2: Create a .env file (don't commit this to git!):
#   AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:123456789:runtime/wanderly_travel_agent
#   AWS_REGION=us-east-1
#
import os

AGENT_RUNTIME_ARN = os.environ.get("AGENT_RUNTIME_ARN", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

if not AGENT_RUNTIME_ARN:
    print("\n⚠️  WARNING: AGENT_RUNTIME_ARN environment variable not set!")
    print("   Set it before running: set AGENT_RUNTIME_ARN=your-arn-here\n")

# ============================================================
# BACKEND: Flask API that calls your deployed agent
# ============================================================

app = Flask(__name__)

def invoke_wanderly(user_message: str, session_id: str = None) -> str:
    """
    Call the deployed Wanderly agent on Amazon Bedrock AgentCore.
    
    Args:
        user_message: The user's travel question
        session_id: Optional session ID for conversation continuity
    
    Returns:
        The agent's response as a string
    """
    import boto3
    
    # Create AgentCore client
    client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    
    # Generate session ID if not provided (must be 33+ characters)
    if not session_id:
        session_id = f"session-{uuid.uuid4().hex}"
    
    # Prepare the payload
    payload = json.dumps({"prompt": user_message})
    
    try:
        # Invoke the deployed agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=payload
        )
        
        # Read and parse the response
        response_body = response['response'].read()
        result = response_body.decode('utf-8')
        
        return result
        
    except Exception as e:
        return f"Error calling agent: {str(e)}"


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat messages."""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = invoke_wanderly(user_message, session_id)
    
    return jsonify({
        'response': response,
        'session_id': session_id or f"session-{uuid.uuid4().hex}"
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'agent': 'wanderly'})


# ============================================================
# FRONTEND: Simple chat interface
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wanderly - AI Travel Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            width: 100%;
            max-width: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-header h1 { font-size: 24px; margin-bottom: 5px; }
        .chat-header p { opacity: 0.8; font-size: 14px; }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
        }
        .message.user { align-items: flex-end; }
        .message.agent { align-items: flex-start; }
        .message-content {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.5;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.agent .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .message-label {
            font-size: 11px;
            color: #888;
            margin-bottom: 4px;
            padding: 0 8px;
        }
        .chat-input-container {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        .chat-input:focus { border-color: #667eea; }
        .send-button {
            margin-left: 10px;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .send-button:hover { background: #5a6fd6; }
        .send-button:disabled { background: #ccc; cursor: not-allowed; }
        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border-radius: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .typing-indicator.show { display: inline-block; }
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>Wanderly</h1>
            <p>Your AI Travel Assistant</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message agent">
                <span class="message-label">Wanderly</span>
                <div class="message-content">
                    Hello! I'm Wanderly, your travel assistant. Ask me about destinations, 
                    weather, attractions, or help planning your trip!
                </div>
            </div>
        </div>
        <div class="chat-input-container">
            <input type="text" class="chat-input" id="userInput" 
                   placeholder="Ask about your next adventure..." 
                   onkeypress="if(event.key==='Enter') sendMessage()">
            <button class="send-button" id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let sessionId = null;
        
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            const typing = showTypingIndicator();
            
            // Disable send button
            document.getElementById('sendButton').disabled = true;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, session_id: sessionId })
                });
                
                const data = await response.json();
                sessionId = data.session_id;
                
                // Remove typing indicator and add response
                typing.remove();
                addMessage(data.response, 'agent');
                
            } catch (error) {
                typing.remove();
                addMessage('Sorry, I encountered an error. Please try again.', 'agent');
            }
            
            document.getElementById('sendButton').disabled = false;
        }
        
        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.innerHTML = `
                <span class="message-label">${sender === 'user' ? 'You' : 'Wanderly'}</span>
                <div class="message-content">${text}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showTypingIndicator() {
            const messagesDiv = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message agent';
            typingDiv.innerHTML = `
                <span class="message-label">Wanderly</span>
                <div class="typing-indicator show">
                    <span></span><span></span><span></span>
                </div>
            `;
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            return typingDiv;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the chat interface."""
    return render_template_string(HTML_TEMPLATE)


# ============================================================
# RUN THE APPLICATION
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Wanderly Full Stack Demo")
    print("="*60)
    print(f"\n  Agent ARN: {AGENT_RUNTIME_ARN}")
    print(f"  Region: {AWS_REGION}")
    print("\n  IMPORTANT: Update AGENT_RUNTIME_ARN with your actual ARN!")
    print("\n  Open http://localhost:5000 in your browser")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
