import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai
import database as db
import prompts

load_dotenv() 
app = Flask(__name__, static_folder='static')


db.init_db()  

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now. Please try again later."

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/session', methods=['POST'])
def create_session():
    session_id = db.create_session()
    return jsonify({'session_id': session_id})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id')
    user_query = data.get('message')

    if not session_id or not user_query:
        return jsonify({'error': 'session_id and message are required'}), 400

    db.add_message_to_db(session_id, 'user', user_query)

    if 'human agent' in user_query.lower() or 'talk to a person' in user_query.lower():
        history = db.get_history(session_id)
        summary_prompt = prompts.get_summary_prompt(history)
        summary = get_gemini_response(summary_prompt)

        response_text = f"I understand. I'm escalating your request. Here is a summary for the agent:\n\n---\n{summary}"
        db.add_message_to_db(session_id, 'bot', response_text)
        return jsonify({'response': response_text})


    history = db.get_history(session_id)
    response_prompt = prompts.get_response_prompt(history, user_query)
    bot_response = get_gemini_response(response_prompt)

    db.add_message_to_db(session_id, 'bot', bot_response)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)