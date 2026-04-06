from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="eventlet")

chat_history = {
    "general": [],
    "gaming": [],
    "random": []
}

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Chat Rooms</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        #messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 5px; }
        #input { margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Chat Rooms</h2>

    <div>
        <label>Username:</label>
        <input id="username" placeholder="Enter name">
    </div>

    <div>
        <label>Room:</label>
        <select id="room">
            <option value="general">General</option>
            <option value="gaming">Gaming</option>
            <option value="random">Random</option>
        </select>
        <button onclick="joinRoom()">Join</button>
    </div>

    <hr>

    <h3 id="room-title"></h3>
    <div id="messages"></div>

    <div id="input">
        <input id="msg" autocomplete="off" placeholder="Type a message..." />
        <button onclick="sendMessage()">Send</button>
    </div>

    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io();
        let currentRoom = null;
        let username = null;

        function joinRoom() {
            username = document.getElementById("username").value.trim();
            const room = document.getElementById("room").value;

            if (!username) {
                alert("Enter a username first");
                return;
            }

            socket.emit("join", {username, room});
            currentRoom = room;
            document.getElementById("room-title").textContent = "Room: " + room;
            document.getElementById("messages").innerHTML = "";
        }

        socket.on("history", function(messages) {
            const messagesDiv = document.getElementById("messages");
            messagesDiv.innerHTML = "";
            messages.forEach(msg => {
                const p = document.createElement("p");
                p.textContent = msg;
                messagesDiv.appendChild(p);
            });
        });

        socket.on("message", function(msg) {
            const messagesDiv = document.getElementById("messages");
            const p = document.createElement("p");
            p.textContent = msg;
            messagesDiv.appendChild(p);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });

        function sendMessage() {
            const text = document.getElementById("msg").value.trim();
            if (text.length > 0 && currentRoom) {
                socket.emit("chat", {username, room: currentRoom, message: text});
                document.getElementById("msg").value = "";
            }
        }

        document.getElementById("msg").addEventListener("keyup", function(e) {
            if (e.key === "Enter") sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]

    join_room(room)
    emit("history", chat_history[room])
    join_msg = f"{username} joined the room."
    chat_history[room].append(join_msg)
    emit("message", join_msg, room=room)

@socketio.on("chat")
def on_chat(data):
    username = data["username"]
    room = data["room"]
    msg = f"{username}: {data['message']}"
    chat_history[room].append(msg)
    emit("message", msg, room=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
