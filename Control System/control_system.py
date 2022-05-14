import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
from control_functions import return_to_init_pos, motor_sweep, initial_start_position, servo_angle_needed, track_pest
import cv
import time
import cv2
import cv_test

COCO_PATH           = 'coco.names'
CUSTOM_ClASSES_PATH = 'obj.names'
SYS_WEBCAM = 0
x_cord = 0
frame_thresh = 10

step_pin = 3
direc_pin = 5
servo_pin = 7
button_pin = 37
solenoid_pin = 33
delay = .009
verbose_sweep = True
verbose_track = True


#intialize stepper and servo  motor
motor1 = s.stepper(step_pin, direc_pin)                  
servo1 = ser.servo(servo_pin, 50, "servo1")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(solenoid_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button_pin, GPIO.FALLING)

started = True
cw = True
solenoid_open = False
Pest = False


GPIO.output(solenoid_pin, GPIO.LOW)
class_names, net = cv.initialize()
cap = cv.toggle_camera(None, SYS_WEBCAM)
time.sleep(5)

while True:
    if GPIO.event_detected(button_pin):
        return_to_init_pos(motor1, delay, verbose_sweep)
    
    started = initial_start_position(motor1, servo1, delay, verbose_sweep, started)
    
    if cap:
        #print("in cap")
        center_coords = cv.process_frame_for_coords(cap, net, class_names)

        if center_coords[0] != None:
            print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")
            x_cord = center_coords[0]
            print(x_cord)
            pest = True
        else:
            pest = False
            print("no pest detetcted")
       
    '''
    key = cv2.waitKey(1)
        
    if key == 27:
        break
    elif key == 116:  # t -> Toggle the camera
        cap = cv.toggle_camera(cap, SYS_WEBCAM)
    
    '''
    
    
    if pest == True:
        print("Pest Detected")
        while True:
            #get some cordinates from CV and calculate a degree to have pest in center view
            time.sleep(1)
            track_pest(motor1, delay, verbose_track, x_cord)
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
            time.sleep(1.5)
            count = 0
            for i in range(0, frame_thresh):
                if cap:
                    #print("in cap")
                    center_coords = cv.process_frame_for_coords(cap, net, class_names)
                    count = count + 1
                    if center_coords[0] != None:
                        print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")
                        x_cord = center_coords[0]
                        print("x_cord: ", x_cord)
                        print("count: ", count)
                        pest = True
                        break
                    else:
                        pest = False
                        print("no pest detetcted")
                print("count: ", count)
            
            if pest == True:
                continue
                print("pest still in frame")
            else:
                GPIO.output(solenoid_pin, GPIO.LOW)
                print("pest not in frame anymore (presumably)")
                solenoid_open = False
                break
    
    cw = motor_sweep(motor1, delay, verbose_sweep, cw)

if cap:
        cap.release()
