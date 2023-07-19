from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import requests
import json
import uuid
import constants

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Crie um identificador de sessão único para este cliente, se ainda não existir um.
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@socketio.on('message')
def handle_message(data):
    # Enviar os dados para a API de chat e retornar a resposta.
    response = requests.post(constants.API, json={'session_id': session['session_id'], 'query': data})
    response_data = response.json()
    emit('response', response_data['answer'])

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)

