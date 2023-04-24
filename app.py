from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
import cv2

from blinkathon import Blinkathon


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "supersecret!"
socketio = SocketIO(app)
cap = cv2.VideoCapture(0)


@socketio.on("connect")
def handle_connect():
    global blinkathon
    print("server and client connected")
    blinkathon.stop_detect_blinks()


@socketio.on("blinkathon-status")
def handle_blinkathon_status():
    emit("game", blinkathon.status)


@socketio.on("exit")
def handle_exit():
    print("User exited the game.")


@socketio.on("start-game")
def handle_start_game():
    blinkathon.start_detect_blinks()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/video-feed")
def video_feed():
    global blinkathon
    return Response(
        blinkathon.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    socketio.run(app)
