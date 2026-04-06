from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Local Chat</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        #messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 5px; }
        #input { margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Wi‑Fi Chat</h2>
    <div id="messages"></div>
    <div id="input">
        <input id="msg" autocomplete="off" placeholder="Type a message..." />
        <button onclick="sendMessage()">Send</button>
    </div>

    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"
            integrity="sha384-3xWb7xv7Y0l5f4p7fQd3vX1YQ6x8bYx5Jq1qX4m1x7x7x7x7x7x7x7x7x7x7"
            crossorigin="anonymous"></script>
    <script>
        const socket = io();

        const messagesDiv = document.getElementById('messages');
        const msgInput = document.getElementById('msg');

        socket.on('message', function(msg) {
            const p = document.createElement('p');
            p.textContent = msg;
            messagesDiv.appendChild(p);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });

        function sendMessage() {
            const text = msgInput.value.trim();
            if (text.length > 0) {
                socket.send(text);
                msgInput.value = '';
            }
        }

        msgInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@socketio.on('message')
def handle_message(msg):
    ip = request.remote_addr
    full_msg = f"{ip}: {msg}"
    print('Message:', full_msg)
    send(full_msg, broadcast=True)

if __name__ == '__main__':
    # host='0.0.0.0' makes it visible to others on the same network
    socketio.run(app, host="0.0.0.0", port=8080)
