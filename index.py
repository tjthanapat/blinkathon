from flask import Flask, Response, render_template
import cv2

from eye_blinking import gen_blink_detect

 
app = Flask(__name__) #creating the Flask class object   

def gen(video):
    while True:
        success, frame = video.read()  # read the camera frame
        if not success:
            break
        else:

            # Setting parameter values
            t_lower = 50  # Lower Threshold
            t_upper = 150  # Upper threshold
              
            # Applying the Canny Edge filter
            edge = cv2.Canny(frame, t_lower, t_upper)

            ret, jpeg = cv2.imencode('.jpg', edge)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
@app.route('/') #decorator drfines the   
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/video-feed')
def video_feed():
		# Set to global because we refer the video variable on global scope, 
		# Or in other words outside the function
    global video

		# Return the result on the web
    return Response(gen_blink_detect(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ =='__main__':  
    video = cv2.VideoCapture(0) 
    app.run(debug = True)  