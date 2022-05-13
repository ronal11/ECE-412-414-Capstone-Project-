import time
import math
from get_distance import measure_distance


frame_width = 1280              # width of video frame in pixels
center_frame = (frame_width / 2) - 1
camera_FOV = 62.2               # horizontal camera FOV
alpha = camera_FOV / 2
# constants used for calculating angle to track
a = frame_width / 2
tracking_thresh = 30    #translates to a 1.61 degree error in aim
'''
This function measures distance using ultrasonic sensor 

param: none

returns: distance measured in meters

'''

def get_distance():
    Flag = True
    
    while Flag:
        d = measure_distance()         # measure distance 
        
        if d < 0 or d > 400:           # sensor max range is 400
            d = measure_distance()
        else:
            Flag = False
    
    d = d / 100   # return a distance in meters
    return d
'''
This function returns platform back to starting intial position, when a button is pressed
param:

motor: an initialized motor object
delay: a numerical value for delay between steps (changes speed)
verbose: boolean value to printout info after each step command 

returns: nothing

'''           
    
def return_to_init_pos(motor, delay, verbose):  
    if motor.relative_pos < 0:     # if position is to the left   
        time.sleep(1)
        temp = abs(motor.relative_pos)
        print(temp)
        motor.rotate_stepper(temp, 'cw', delay, verbose)    # rotate back to center according to current position 
        print("back to initial from ccw")
        quit()
    elif motor.relative_pos > 0: # if position is to the right 
        time.sleep(1)
        temp = abs(motor.relative_pos)
        print(temp)
        motor.rotate_stepper(temp, 'ccw', delay, verbose)   # rotate back to center according to current position 
        print("back to initial from cc")
        quit()
    '''
This function sweeps the platform 180 degree's back and forth, it is the passive movement of the system
(N.B. the stepper operates with a 2:1 gear ratio, so directions are reversed for stepper and main platform)
param:

motor: an initialized motor object
delay: a numerical value for delay between steps (changes speed)
verbose: boolean value to printout info after each step command
cw: boolean value for current direction

returns: current direction of sweeping motion (bool)

'''       
def motor_sweep(motor, delay, verbose, cw):
    
    if cw:                                     # if stepper motor is currently rotating clockwise (platform is rotating ccw)
        if motor.relative_pos > 176.4:         # used to detect when an increment of 3.6 will bring platform over allowed range
            print(motor.relative_pos)
            degree = 180 - motor.relative_pos  # calulate needed angle to bring to extrenum 
            print('greater than 176.4, degrees needed: ', degree)
            motor.rotate_stepper(degree, 'cw', delay, verbose)  # rotate to extrenum, in the case of the stepper (180 degrees clockwise)
            
        curr = motor.relative_pos       
        
        if curr > 179:           # if current position is greater than 179
            cw = False           # start rotating stepper motor in ccw direction 
        else:
            motor.rotate_stepper(3.6, 'cw', delay, verbose)   #else, rotate cw in 3.6 increments 
        
    else:                                       # if stepper is rotating ccw 
        if motor.relative_pos < -176.4:
            print(motor.relative_pos)           # process same as above
            degree = 180 - abs(motor.relative_pos)
            print('less than -176.4' ,degree)
            motor.rotate_stepper(degree, 'ccw', delay, verbose)
            
        curr = motor.relative_pos
        
        
        if curr < -179:
            cw = True
        else:
            motor.rotate_stepper(3.6, 'ccw', delay, verbose)
    return cw    
'''
This function sets servo and motor to an initial position, returns start variable as false, only runs at the start once
param:

motor: an initialized motor object
servo: an initialized servo object 
delay: a numerical value for delay between steps (changes speed)
verbose: boolean value to printout info after each step command
start: bool value to determine of this is the start of program

returns: start, a boolean value as false 

'''           
def initial_start_position(motor, servo, delay, verbose, start):
    if start:
        motor.rotate_stepper(180, 'ccw', delay, verbose)
        servo.set_angle(130)
        start = False
    return start
'''
This function calculates an angle to rotate the servo given a distance measured from a pest, in order for stream of water to ideally hit pest

param:

center_degree: chosen center for servo, used to calulate angle to rotate servo

returns: an angle to rotate servo 
'''
def servo_angle_needed(center_degree):
    #consant params for equation 
    v0 = 2                # velocity of water needs to be estimated
    v0_2 = pow(v0, 2)
    g = 9.8
    
    d = get_distance()    # get a distance 
          
    print("distance measured: ",d)
    C = g * d
    angle = 0.5 * math.degrees(math.asin(C / v0_2))  #might not work
    
    needed_angle = center_degree + angle             #potencial bug
    return needed_angle

def track_pest(motor, delay, verbose, x_cord_detected):   
    
    #calculate a thresh and check if it's greater than or else do nothing
    x_cord_detected = x_cord_detected - center_frame
    print("x_cord_detected = ", x_cord_detected)
    abs_x_cord = abs(x_cord_detected)
    
    k = abs_x_cord * math.tan(math.radians(alpha))
    
    if (abs_x_cord < tracking_thresh):
        print("below tracking threshold")
        time.sleep(1)
    elif(x_cord_detected > 0):
        angle_2_rotate = 2* (math.degrees(math.atan(k / a)))
        
        calc = motor.relative_pos - angle_2_rotate
        print("calc is: ", calc)
        
        if calc < -180:
            print("angle required over -180")
            angle_2_rotate = 180 + motor.relative_pos
            
        print("rotate to the right: ", angle_2_rotate/2)
        motor.rotate_stepper(angle_2_rotate, 'ccw', delay, verbose)
        time.sleep(1)
    elif(x_cord_detected < 0):
        angle_2_rotate = 2*(math.degrees(math.atan(k / a)))
        
        calc = motor.relative_pos + angle_2_rotate
        print("calc is: ", calc)
        
        if calc > 180:
            print("angle required over 180")
            angle_2_rotate = 180 - motor.relative_pos
            
        print("rotate to the left:", angle_2_rotate/2)
        motor.rotate_stepper(angle_2_rotate, 'cw', delay, verbose)
        time.sleep(1)
