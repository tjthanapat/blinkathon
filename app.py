from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
import cv2
from eye_blinking import detect_blink

app = Flask(__name__)

app.debug = True
app.config["SECRET_KEY"] = "supersecret!"
socketio = SocketIO(app)
cap = cv2.VideoCapture(1)


@socketio.on("connect")
def handle_connect():
    print("server and client connected")


PLAYING = False

@socketio.on("start-game")
def handle_start_game():
    global cap, PLAYING
    print("Blinkathon starts now.")

    COUNTER = 0
    TOTAL = 0
    PLAYING = True
    emit(
        "game", dict(playing=True, blinkCounter=TOTAL, status="Blinkathon starts now.")
    )

    while PLAYING:
        ret, frame = cap.read()
        if not ret:
            print("Error: cannot read a frame.")
            break

        try:
            blinked, COUNTER = detect_blink(frame, COUNTER)
            if blinked:
                TOTAL += 1
                emit(
                    "game",
                    dict(
                        playing=True,
                        blinkCounter=TOTAL,
                        status=f"Total blinks: {TOTAL}",
                    ),
                )
        except:
            emit(
                "game",
                dict(
                    playing=True,
                    blinkCounter=TOTAL,
                    error="Error in dectection.",
                    status="Blinkathon cannot detect your face.",
                ),
            )

@socketio.on("win-game")
def handle_win_game():
    global PLAYING
    PLAYING = False
    emit(
        "game",
        dict(
            playing=False,
            status="Congratulations! You win Blinkathon.",
        ),
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


def gen_frames(cap):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: cannot read a frame.")
            break

        success, frame = cv2.imencode(".jpg", frame)
        if not success:
            print("Error: cannot encode a frame.")
            break
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame.tobytes() + b"\r\n"
        )


@app.route("/video-feed")
def video_feed():
    # Set to global because we refer the video variable on global scope,
    # Or in other words outside the function
    global cap

    # Return the result on the web
    return Response(
        gen_frames(cap),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    socketio.run(app)
