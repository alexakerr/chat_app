from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = "private_key"

socketio = SocketIO(app, cors_allowed_origins="*")

messages = []
chat_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Server has connected')
    emit('update_rooms', list(chat_rooms.keys()), broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    print('Server has disconnected')


@socketio.on('send_chat_message')
def handle_chat_message(data):
    username = data.get('username')
    message = data.get('message')
    output = f"<b>{username}</b>: {message}"
    messages.append(output)
    send(output, broadcast=True)

@socketio.on('create_room')
def handle_create_room(data):
    room = data['room']
    username = data['username']
    if room not in chat_rooms:
        chat_rooms[room] = []
        join_room(room)
        chat_rooms[room].append(username)
        emit('room_created', room, broadcast=True)
        send(f"{username} has created and entered the room {room}.", room=room)
    else:
        emit('error', f"Room {room} already exists.")

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    if room in chat_rooms:
        join_room(room)
        chat_rooms[room].append(username)
        send(f"{username} has joined the room {room}.", room=room)
    else:
        emit("error", f"Room {room} doesn't exist")

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = data['username']
    if room in chat_rooms:
        leave_room(room)
        chat_rooms[room].remove(username)
        send(f"{username} has exited {room}.", room=room)
        if not chat_rooms[room]:
            del chat_rooms[room]
            emit('room_deleted', room, broadcast=True)

@socketio.on('message')
def message(data):
    room = data['room']
    username = data['username']
    message = data['message']
    output = f"<b>{username}</b>: {message}"
    messages.append(output)
    if room in chat_rooms:
        send(output, room=room)
    else:
        emit("error", "Enter a room to chat")

if __name__ == "__main__":
    socketio.run(app, debug=True)