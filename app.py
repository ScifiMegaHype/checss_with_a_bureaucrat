import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
from chess_logic import (
    initial_board,
    legal_moves,
    apply_move,
    is_in_check
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "bureaucrat-chess"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

games = {}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)

    if room not in games:
        games[room] = {
            "board": initial_board(),
            "turn": "white",
            "players": {},
        }

    emit("state", {
        "board": games[room]["board"],
        "turn": games[room]["turn"],
        "check": is_in_check(games[room]["board"], games[room]["turn"])
    }, room=room)

@socketio.on("select")
def on_select(data):
    room = data["room"]
    r, c = data["pos"]

    game = games.get(room)
    if not game:
        return

    moves = legal_moves(game["board"], r, c, game["turn"])

    emit("legal_moves", {
        "from": [r, c],
        "moves": moves
    })

@socketio.on("move")
def on_move(data):
    room = data["room"]
    sr, sc, er, ec = data["move"]

    game = games.get(room)
    if not game:
        return

    new_board, success = apply_move(
        game["board"], sr, sc, er, ec, game["turn"]
    )

    if not success:
        return

    game["board"] = new_board
    game["turn"] = "black" if game["turn"] == "white" else "white"

    emit("state", {
        "board": game["board"],
        "turn": game["turn"],
        "check": is_in_check(game["board"], game["turn"])
    }, room=room)
