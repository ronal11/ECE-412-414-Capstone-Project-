'''
This file provides all control system functions required for pest deterent system
author: Ronaldo Leon
'''
import time
import math
from get_distance import measure_distance


frame_width = 1280              # width of video frame in pixels
center_frame = (frame_width / 2) - 1
camera_FOV = 62.2               # horizontal camera FOV
alpha = camera_FOV / 2
# constants used for calculating angle to track
a = frame_width / 2
tracking_thresh = 30    # 30 pixels translates to a 1.61 degree error in aim

deg_range_p = 180
deg_range_n = -180
deg_blind = 10

deg_per_step = 3.6
last_step_cw = deg_range_p - deg_per_step
last_step_ccw = deg_range_n + deg_per_step

deg_limit_p = deg_range_p - 1
deg_limit_n = deg_range_n + 1

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
        if motor.relative_pos > last_step_cw:         # used to detect when an increment of 3.6 will bring platform over allowed range
            print(motor.relative_pos)
            degree = deg_range_p - motor.relative_pos  # calulate needed angle to bring to extrenum 
            print('greater than 176.4, degrees needed: ', degree)
            motor.rotate_stepper(degree, 'cw', delay, verbose)  # rotate to extrenum, in the case of the stepper (180 degrees clockwise)
            
        curr = motor.relative_pos       
        
        if curr > deg_limit_p:           # if current position is greater than 179
            cw = False           # start rotating stepper motor in ccw direction 
        else:
            motor.rotate_stepper(deg_per_step, 'cw', delay, verbose)   #else, rotate cw in 3.6 increments 
        
    else:                                       # if stepper is rotating ccw 
        if motor.relative_pos < last_step_ccw:
            print(motor.relative_pos)           # process same as above
            degree = deg_range_p - abs(motor.relative_pos)
            print('less than -176.4' ,degree)
            motor.rotate_stepper(degree, 'ccw', delay, verbose)
            
        curr = motor.relative_pos
        
        
        if curr < deg_limit_n:
            cw = True
        else:
            motor.rotate_stepper(deg_per_step, 'ccw', delay, verbose)
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
'''
This function takes cordinates and motor object, calculates cordinates and degree to rotate stepper appropriately 

param:

motor: an initialized motor object
servo: an initialized servo object 
delay: a numerical value for delay between steps (changes speed)
verbose: boolean value to printout info after each step command
x_cord_detected: cordinate received from CV used to calculate angle to rotate stepper

returns: nothing  
'''
def track_pest(motor, delay, verbose, x_cord_detected):   
    
   
    x_cord_detected = x_cord_detected - center_frame   # calculate x cordinate, will produce a negative or pos, which corresponds to the left or right of center cord respectivley 
    print("x_cord_detected = ", x_cord_detected)       
    abs_x_cord = abs(x_cord_detected)                  # get abs value of x cordinate, will be used to see if x cord is over threshold 
    
    k = abs_x_cord * math.tan(math.radians(alpha))     # calculation for equation to track 
    
    if (abs_x_cord < tracking_thresh):                 # if x-cord is less than threshold, don't move in hopes of preventing jittering in stepper motor             
        print("below tracking threshold")
        time.sleep(1)
    elif(x_cord_detected > 0):                         # if x-cord is > 0 move to platform to the right (big gear), this means moving stepper motor to the left(Small gear)
        dir = 'cw'
        angle_2_rotate = 2* (math.degrees(math.atan(k / a))) # calculate angle (N.B. multiplied by two because of 2:1 gear ratio)
        
        calc = motor.relative_pos + angle_2_rotate           # calculate new position that will result 
        print("calc is: ", calc)
        
        if calc > deg_range_p:                                # if new position results in stepper motor going out of range (-180 deg small gear == 90 deg big gear)
            print("angle required over {0}" .format(deg_range_p))
            if angle_2_rotate > deg_blind:
                temp = angle_2_rotate - deg_blind
                angle_2_rotate  = deg_range_p - temp
                print("changed directions to CCW")
                dir = 'ccw'
            else:
                angle_2_rotate = deg_range_p - motor.relative_pos  # calculate new angle to bring stepper motor to max range in hopes to still deter pest
            
        print("rotate {0}: {1} deg: " .format(dir, angle_2_rotate/2))
        motor.rotate_stepper(angle_2_rotate, dir, delay, verbose) # rotate stepper CCW, translates to rotating platform to the right by angle_2_rotate/2 (2:1 ratio)
        time.sleep(1)
    elif(x_cord_detected < 0):                         # if x-cord is < 0 move to platform to the left (big gear), this means moving stepper motor to the right(Small gear)
        dir = 'ccw'
        angle_2_rotate = 2*(math.degrees(math.atan(k / a)))  # calculate angle (N.B. multiplied by two because of 2:1 gear ratio)
        
        calc = motor.relative_pos - angle_2_rotate           # calculate new position that will result 
        print("calc is: ", calc)
        
        if calc < deg_range_n:                                 # if new position results in stepper motor going out of range (180 deg small gear == -90 deg big gear)
            print("angle required over {0}" .format(deg_range_n))
            if angle_2_rotate > deg_blind:
                temp = angle_2_rotate - deg_blind
                angle_2_rotate  = deg_range_p - temp
                print("changed directions to CW")
                dir = 'cw'
            else:
                angle_2_rotate = deg_range_p + motor.relative_pos  # calculate new angle to bring stepper motor to max range in hopes to still deter pest
            
        print("rotate {0}: {1} deg: " .format(dir, angle_2_rotate/2))
        motor.rotate_stepper(angle_2_rotate, dir, delay, verbose)  # rotate stepper CW, translates to rotating platform to the left by angle_2_rotate/2 (2:1 ratio)
        time.sleep(1)
