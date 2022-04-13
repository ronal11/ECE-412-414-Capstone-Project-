import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
#import cv
import time
import math
from demo_get_distance import get_distance

def return_to_init_pos(motor):
    if motor.relative_pos < 0:
        time.sleep(1)
        temp = abs(motor.relative_pos)
        print(temp)
        motor.rotate_stepper(temp, 'cw', delay, verbose_sweep)
        print("back to initial from ccw")
        quit()
    elif motor.relative_pos > 0:
        time.sleep(1)
        temp = abs(motor.relative_pos)
        print(temp)
        motor.rotate_stepper(temp, 'ccw', delay, verbose_sweep)
        print("back to initial from cc")
        quit()
        
def motor_sweep(motor, delay, verbose, cw):
    
    if cw:
        if motor.relative_pos > 176.4:
            print(motor.relative_pos)
            degree = 180 - motor.relative_pos
            print('greater than 176.4, degrees needed: ', degree)
            motor.rotate_stepper(degree, 'cw', delay, verbose)
            
        curr = motor.relative_pos
        
        if curr > 179:
            cw = False
        else:
            motor.rotate_stepper(3.6, 'cw', delay, verbose)
        
    else:
        if motor.relative_pos < -176.4:
            print(motor.relative_pos)
            degree = 180 - abs(motor.relative_pos)
            print('less than -176.4' ,degree)
            motor.rotate_stepper(degree, 'ccw', delay, verbose)
            
        curr = motor.relative_pos
        
        
        if curr < -179:
            cw = True
        else:
            motor.rotate_stepper(3.6, 'ccw', delay, verbose_sweep)
    return cw

def initial_start_position(motor, delay, verbose, start):
    if start:
        motor1.rotate_stepper(180, 'ccw', delay, verbose)
        #servo1.set_angle(130)
        start = False
    return start

step_pin = 3
direc_pin = 5
servo_pin = 7
button_pin = 37
delay = .002
verbose_sweep = False
verbose_track = True

frame_width = 1920
a = frame_width / 2
camera_FOV = 60
alpha = camera_FOV / 2
center_x_frame = 0

v0 = 2
v0_2 = pow(v0, 2)
g = 9.8


#intialize stepper and servo  motor
motor1 = s.stepper(step_pin, direc_pin)                  
servo1 = ser.servo(servo_pin, 50, "servo1")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button_pin, GPIO.FALLING)


start = True
cw = True
solenoid_open = False


while True:
    if GPIO.event_detected(button_pin):
        return_to_init_pos(motor1)
    
    start = initial_start_position(motor1, delay, verbose_sweep, start)
    
    #CV code to detect pest goes here?
    x_cord_detected = 50
    pest = int(input("pest detected? "))
    
    if pest == 1:
        
        while True:
            #get some cordinates from CV and calculate a degree to have pest in center view
            
            k = x_cord_detected * math.tan(alpha)
            
            if(x_cord_detected > center_x_frame):
                angle_2_rotate = math.atan(k / a)
                print("rotate to the right: ", angle_2_rotate)
                motor1.rotate_stepper(angle_2_rotate, 'ccw', delay, verbose_track)
                #time.sleep(.3)
            elif(x_cord_detected < center_x_frame):
                angle_2_rotate = math.atan(k / a)
                print("rotate to the left:", angle_2_rotate)
                motor1.rotate_stepper(angle_2_rotate, 'cw', delay, verbose_track)
                #time.sleep(.3)
            else:
                print("already targeted")
                                      
            d = get_distance(1, False)
            if d < 0:
                while True:
                    d = get_distance(1, False)
                    if d < 0:
                        continue
                    else:
                        break
                
            print("distance measured: ",d)
            C = g * d
            needed_angle = 0.5 * math.asin(C / v0_2)
            
            if(servo1.previous_angle == needed_angle):
                if not solenoid_open:
                    #open solenoid
                    solenoid_open = True
                time.sleep(.1)
            else:
                #servo1.set_angle(needed_angle)
                if not solenoid_open:
                    #open solenoid
                    solenoid_open = True
                time.sleep(.1)
            
                
            #CV code to detect pest goes here?
            
            pest = int(input("pest detected? "))
            if pest == 1:
                continue
            else:
                #close solenoid
                solenoid_open = False
                break
    
    cw = motor_sweep(motor1, delay, verbose_sweep, cw)
