from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
import cv2, time, threading, eventlet, gevent, system, sys
import RPi.GPIO as GPIO
import pest_detector as pd
import control_system as cs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, engineio_logger=True, async_mode='eventlet')

user_online   = False
eventlet_active = True
max_fps = 1/30
frame_thresh = 10

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def connect():
    global user_online
    user_online = True
    print('User online: ' + str(user_online), file=sys.stderr)

@socketio.on('disconnect')
def disconnect():
    global user_online
    user_online = False
    print('User online: ' + str(user_online), file=sys.stderr)

def gen_frames():
    eventlet.sleep(2)
    global user_online
    while user_online is True:
        frame = detector.get_frame()
        if frame is not None:
            boxes, b_center_coords, confidences, class_ids = detector.process_frame(frame)
            frame = detector.draw_bbox(frame, boxes, confidences, class_ids)

            status, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            eventlet.sleep(max_fps)
        else:
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n'
            eventlet.sleep(max_fps)

def start_web_server():
    print('Starting webserver')
    socketio.run(app)

# FOR TESTING CAMERA/WEBSERVER ONLY - WILL BE REMOVED IN FINAL BUILD
def start_system():
    while True:
        global user_online
        if user_online is False:
            frame = detector.get_frame()
            boxes, b_center_coords, confidences, class_ids = detector.process_frame(frame)
            frame = detector.draw_bbox(frame, boxes, confidences, class_ids)
            detector.show_frame(frame)
            eventlet.sleep(1/30)
        else:
            cv2.destroyAllWindows()
            eventlet.sleep(max_fps)

def run_system():
    control_system.initial_start_position()  # Move to the initial starting position

    while True:
        global user_online
        pest = False
        if user_online is False:
            # if GPIO.event_detected(button_pin):
            #     return_to_init_pos(motor1, delay, verbose_sweep)

            frame = detector.get_frame()
            center_coords = detector.process_frame_coords()

            if center_coords[0] is not None:
                print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")
                control_system.set_x_cord(center_coords[0])
                print(control_system.get_x_cord())
                pest = True
            else:
                pest = False
                print("no pest detetcted")

            if pest is True:
                eventlet.sleep(1)
                control_system.track_pest(control_system.get_x_cord())
                control_system.solenoid_open()
                '''                       
                needed_angle = servo_angle_needed(130)

                if(servo1.previous_angle == needed_angle):
                    if not solenoid_open:
                        GPIO.output(solenoid_pin, GPIO.HIGH)
                        solenoid_open = True

                else:
                    #servo1.set_angle(needed_angle)
                    if not solenoid_open:
                        GPIO.output(solenoid_pin, GPIO.HIGH)
                        solenoid_open = True
                '''
                # eventlet.sleep(1.5)
                count = 0
                for i in range(0, frame_thresh):
                    frame = detector.get_frame()
                    center_coords = detector.process_frame_coords()
                    count += 1
                    if center_coords[0] is not None:
                        print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")
                        control_system.set_x_cord(center_coords[0])
                        print("x_cord: ", control_system.get_x_cord())
                        print("count: ", count)
                        pest = True
                        break
                    else:
                        pest = False
                        print("no pest detetcted")
                print("count: ", count)

                if pest is True:
                    print("pest still in frame")
                    continue
                else:
                    control_system.close_solenoid()
                    print("pest not in frame anymore (presumably)")
                    solenoid_open = False
                    break
            cw = control_system.motor_sweep()
        else:
            eventlet.sleep(max_fps)

if __name__ == '__main__':
    detector       = pd.PestDetector()
    control_system = cs.ControlSystem(1280)
    eventlet.sleep(5) # Give both systems a few seconds to initialize

    # thread = threading.Thread(target=start_system, args=())
    thread = threading.Thread(target=run_system, args=())
    thread.daemon = True
    thread.start()

    start_web_server()
