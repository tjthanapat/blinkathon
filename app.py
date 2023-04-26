from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
import cv2
import numpy as np

import dataurl_utilities as dataurl_utils

from blinkathon import Blinkathon


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "supersecret!"
socketio = SocketIO(app)

# cap = cv2.VideoCapture(0)
# blinkathon = Blinkathon(cap)


@socketio.on("connect")
def handle_connect():
    # global blinkathon
    print("client connected")
    # blinkathon.stop_detect_blinks()


@socketio.on("stream")
def handle_stream(data):
    frame = dataurl_utils.decode_dataurl_to_frame(data)
    color = np.random.randint(0, 256, 3).tolist()
    cv2.putText(
        frame,
        "Blinkathon",
        (50, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        color,
        2,
    )
    frame_encoded = dataurl_utils.encode_frame(frame)
    emit(
        "blinkathon",
        dict(
            message="sent from server!!",
            frame=frame_encoded,
        ),
    )


# @socketio.on("blinkathon-status")
# def handle_blinkathon_status():
#     emit("game", blinkathon.status)


@socketio.on("exit")
def handle_exit():
    print("User exited the game.")


# @socketio.on("start-game")
# def handle_start_game():
#     blinkathon.start_detect_blinks()


@app.route("/")
def index():
    return render_template("index2.html")


@app.route("/about")
def about():
    return render_template("about.html")



if __name__ == "__main__":
    socketio.run(app)
