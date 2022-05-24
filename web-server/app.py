from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
import cv2, time, threading
import pest_detector as pd
import gevent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, engineio_logger=True, async_mode='threading')

user_online   = False
gevent_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    global user_online
    user_online = True
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def connect():
    global user_online
    user_online = True
    print('User online: ' + str(user_online))

@socketio.on('disconnect')
def disconnect():
    global user_online
    user_online = False
    print('User online: ' + str(user_online))

def gen_frames():
    global user_online
    print(user_online)

    while user_online is True:
        frame = detector.get_frame()
        if frame is not None:
            boxes, b_center_coords, confidences, class_ids = detector.process_frame(frame)
            frame = detector.draw_bbox(frame, boxes, confidences, class_ids)

            status, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            #time.sleep(1/30)
            gevent.sleep(1/30)
        else:
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n'
            if gevent_active:
                gevent.sleep(1/30)
            else:
                time.sleep(1/30)
    user_online = False

def start_web_server():
    print('Starting webserver')
    #app.run(host='0.0.0.0', port=5000)
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)

def start_system():
    while True:
        global user_online
        if user_online is False:
            frame = detector.get_frame()
            boxes, b_center_coords, confidences, class_ids = detector.process_frame(frame)
            frame = detector.draw_bbox(frame, boxes, confidences, class_ids)
            detector.show_frame(frame)
            if gevent_active:
                gevent.sleep(1/30)
            else:
                time.sleep(1/30)
        else:
            cv2.destroyAllWindows()
            if gevent_active:
                gevent.sleep(1/30)
            else:
                time.sleep(1/30)

if __name__ == '__main__':
    detector = pd.PestDetector()

    thread = threading.Thread(target=start_system, args=())
    thread.daemon = True
    thread.start()

    start_web_server()
