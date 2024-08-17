from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
from spellchecker import SpellChecker

app = Flask(__name__)
socketio = SocketIO(app)
spell = SpellChecker()

# Turboline API details
turboline_api_key = '7a202888c4b845b9b7c2a0a09e8850a7'
turboline_summarize_endpoint = 'https://api.turboline.ai/openai/chat/completions'


@app.route('/')
def index():
    return render_template('index.html')


# Real-time text update handling for collaborative content
@socketio.on('text_update')
def handle_text_update(data):
    emit('update_text', data, broadcast=True)


# Function to check spelling of the text
def check_spelling(text):
    misspelled = spell.unknown(text.split())
    corrections = {word: spell.correction(word) for word in misspelled}
    return corrections


# Endpoint to handle spelling check requests
@app.route('/check_spelling', methods=['POST'])
def spell_check():
    content = request.json.get('content')
    corrections = check_spelling(content)
    return jsonify(corrections=corrections)


# Function to call Turboline API for text generation (for another task)
def use_turboline_api(content):
    api_url = "https://api.turboline.ai/v1/generate"  # Example endpoint
    headers = {
        'Authorization': f'Bearer {turboline_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        api_url, json={'content': content}, headers=headers)
    return response.json()


@app.route('/turboline_generate', methods=['POST'])
def turboline_generate():
    content = request.json.get('content')
    result = use_turboline_api(content)
    return jsonify(result)


# Function to call Turboline API for text summarization
def summarize_text(content, model="gpt-4o-mini"):
    headers = {
        'X-TL-Key': turboline_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'model': model,
        "messages": [
            {
                "role": "user",
                "content": f"Summarize the following text within 150 characters:\n\n{content}"
            }
        ],
        'max_tokens': 150  # Adjust according to your needs
    }
    response = requests.post(
        turboline_summarize_endpoint, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        summary = response_data.get('choices', [])[0].get(
            'message', {}).get('content', '').strip()
        return summary
    else:
        print(f"An error occurred: {response.status_code} - {response.text}")
        return "Error in summarization"


@app.route('/summarize', methods=['POST'])
def summarize():
    content = request.json.get('content')
    summary = summarize_text(content)
    return jsonify(summary=summary)


if __name__ == '__main__':
    socketio.run(app, debug=True)
