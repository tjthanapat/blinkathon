from flask import Flask, session, render_template
from flask_session import Session
from flask_socketio import SocketIO, emit
import cv2
import numpy as np

import dataurl_utilities as dataurl_utils

from blinkathon import Blinkathon


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "supersecret!"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

socketio = SocketIO(app, manage_session=False)


@socketio.on("connect")
def handle_connect():
    print("client connected")
    session["blinkathon"] = Blinkathon()


@socketio.on("stream")
def handle_stream(data):
    frame = dataurl_utils.decode_dataurl_to_frame(data)
    blinkathon = session.get("blinkathon")
    blinkathon, frame = blinkathon.process_frame(frame)
    session["blinkathon"] = blinkathon
    game_status = blinkathon.get_status()
    frame_encoded = dataurl_utils.encode_frame(frame)
    emit(
        "blinkathon",
        dict(
            message="sent from server!!",
            frame=frame_encoded,
            **game_status
        ),
    )

@socketio.on("start-game")
def handle_start_game():
    blinkathon = session.get("blinkathon")
    blinkathon = blinkathon.start_detect_blink()
    session["blinkathon"] = blinkathon


@socketio.on("end-game")
def handle_end_game():
    blinkathon = session.get("blinkathon")
    blinkathon = blinkathon.start_detect_blink()
    session["blinkathon"] = blinkathon 


@app.route("/")
def index():
    return render_template("index2.html")


@app.route("/about")
def about():
    return render_template("about.html")



if __name__ == "__main__":
    socketio.run(app)
