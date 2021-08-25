from flask import Response, Flask, render_template, request
import threading
import argparse
import datetime
import imutils
import glob
import time
import cv2 

path="./data/processor/static/gstreamer/0/*"
last_file = "video_00000.ts"

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

@app.route("/") 
def home(): 
    return render_template('s3_streaming.html') 

@app.route("/templates/getCharts.html", methods=["GET","POST"])
def getCharts():
    param = str(request.args["key"])
    return render_template('getCharts.html', param=param)

@app.route("/templates/s3_streaming.html")
def back():
    return render_template('s3_streaming.html')

@app.route("/templates/video_streaming.html")
def streamHtml():
    return render_template('video_streaming.html')

def stream():
    global outputFrame, lock, path, last_file
    while (True):
        file_list =glob.glob(path)
        file_list_ts = [file for file in file_list if file.endswith(".ts")]
        file_list_ts.sort()
        if last_file == file_list_ts[-2]:
            #print("the file hasn't been updated yet")
            time.sleep(1)
            continue
        last_file = file_list_ts[-2]
        #print("last file : {}".format(last_file))

        cap = cv2.VideoCapture(last_file)
        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) #current frames count
        flag_stm = True

        while(flag_stm): 
            flag1, frame = cap.read() 
            if frame is None:
                print("frame is none")
                time.sleep(1)
                continue
            if flag1: 
                # The frame is ready and already captured 
                #cv2.imshow('video', frame) 
                pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) 
                #print (str(pos_frame)+" frames" )
            else: 
                # The next frame is not ready, so we try to read it again 
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1) 
                print ("frame is not ready")
                # It is better to wait for a while for the next frame to be ready 
                cv2.waitKey(1000) 
    
            with lock:
                outputFrame = frame.copy()

            if cv2.waitKey(30) == 27: 
                break 
            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT): # CAP_PROP_FRAME_COUNT : total frames count
                # If the number of captured frames is equal to the total number of frames, 
                # we stop 
                flag_stm = False


#This function is a python generator used to encode our outputFrame as JPEG data.
def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag2, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag2:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
	# start a thread that will perform motion detection
	t = threading.Thread(target=stream)
	t.daemon = True
	t.start()
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)







    
