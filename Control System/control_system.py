'''
This program aims to track and deter pests, it operates on a 350 degree range
author: Ronaldo Leon
Computer vision code written by Jacob Laws
'''

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
frame_thresh = 5

step_pin = 3                          # pin assignments 
direc_pin = 5
servo_pin = 7
button_pin = 35
solenoid_pin = 37
irrig_pin = 11
delay = .003 #.009                   # delay to control motor speed
verbose_sweep = False                 # variables for debugging 
verbose_track = True
sleep_pin = 33


#intialize stepper and servo  motor
motor1 = s.stepper(step_pin, direc_pin)                  
servo1 = ser.servo(servo_pin, 50, "servo1")
# set up GPIOs
GPIO.setmode(GPIO.BOARD)
GPIO.setup(solenoid_pin, GPIO.OUT)
GPIO.setup(sleep_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button_pin, GPIO.FALLING)

GPIO.setup(irrig_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(irrig_pin, GPIO.FALLING, bouncetime=5)
# intialize variables
started = True                 
cw = True
solenoid_open = False
Pest = False
x_cord = 0
irrigation = False
GPIO.output(sleep_pin, GPIO.HIGH)
time.sleep(.2)
GPIO.output(solenoid_pin, GPIO.LOW)
GPIO.output(solenoid_pin, GPIO.HIGH)
GPIO.output(sleep_pin, GPIO.LOW)
# start CV
class_names, net = cv.initialize()
cap = cv.toggle_camera(None, SYS_WEBCAM)
time.sleep(5)

while True:
    if GPIO.event_detected(button_pin):                      # if falling edge is detected from button
       return_to_init_pos(motor1, delay, verbose_sweep)     # return to 0 position
    '''
    if GPIO.event_detected(irrig_pin):
        if irrigation:
            irrigation = False
            print("irrigation mode ended")
            GPIO.output(solenoid_pin, GPIO.LOW)    # close solenoid
            solenoid_open = False
        else:
            irrigation = True
            print("irrigation mode started")
            GPIO.output(solenoid_pin, GPIO.HIGH)
            solenoid_open = True
    '''
    started = initial_start_position(motor1, servo1, delay, verbose_sweep, started) # turn all the way CW
    
    if not irrigation:
        if cap:
            #print("in cap")
            center_coords = cv.process_frame_for_coords(cap, net, class_names)

            if center_coords[0] != None:           # if pest is detected
                print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")
                x_cord = center_coords[0]          # assign x cordinate 
                print(x_cord)
                pest = True                        # set pest variable 
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
            print("Pest DETECTED")       # if pest is detected 
            while True:
                #get some cordinates from CV and calculate a degree to have pest in center view
                time.sleep(.5)
                track_pest(motor1, delay, verbose_track, x_cord)
            
                if not solenoid_open:       # if solenoid isn't already opened, then we open it
                    GPIO.output(sleep_pin, GPIO.LOW)
                    GPIO.output(solenoid_pin, GPIO.HIGH)
                    solenoid_open = True
                    GPIO.output(sleep_pin, GPIO.HIGH)
                '''                       
                needed_angle = servo_angle_needed(125)             #code for servo 
            
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
                #time.sleep(1.5)
                count = 0
                for i in range(0, frame_thresh):               # check if pest is still in frame
                    if cap:
                        #print("in cap")
                        center_coords = cv.process_frame_for_coords(cap, net, class_names)
                    
                        count = count + 1
                        if center_coords[0] != None:
                            print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")
                            x_cord = center_coords[0]
                            print("x_cord: ", x_cord)
                            print("count: ", count)
                            pest = True                    # if pest in detected give new x cordinate 
                        
                            # print("Detected Object Class: " + str(class_names[class_ids[0]]) + " | Confidence: " + str(round(confidences[0], 2)))
                        
                            break                          # break out of for loop to track pest 
                        else:
                            pest = False                   # else set pest to false to indicate no pest detected 
                            print("no pest detetcted")
                    print("count: ", count)
            
                if pest == True:                           # if pest is detected continue in pest deterring loop
                    print("pest still in frame")
                    continue
                
                else:                                      # otherwise exit out of loop and continue sweeping
                    GPIO.output(sleep_pin, GPIO.LOW)
                    GPIO.output(solenoid_pin, GPIO.LOW)    # close solenoid
                    print("pest not in frame anymore (presumably)")
                    solenoid_open = False
                    GPIO.output(sleep_pin, GPIO.HIGH)
                    break                         
    
    cw = motor_sweep(motor1, delay, verbose_sweep, cw) # this is the normal sweeping/irrigation motion while no pest is detected 

if cap:
    cap.release()
