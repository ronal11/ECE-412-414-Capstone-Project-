import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
import time

step = 3
direc = 5
servo_pin = 11
#intialize stepper and servo  motor
motor1 = s.stepper(step, direc)                  
servo1 = ser.servo(servo_pin, 50, "servo1")

GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(36, GPIO.FALLING)

start = True
pest_detected = False
cw = True


while True:
    if GPIO.event_detected(36):
        if motor1.relative_pos < 0:
            motor1.rotate_stepper(0, 'cw',.001, False)
            quit()
        elif motor1.relative_pos > 0:
            motor1.rotate_stepper(0, 'ccw',.001, False)
            quit()
    
    if start:
         motor1.rotate_stepper(90, 'ccw', .001, False)
         servo1.set_angle(130)
         start = False
         
    
    if cw:
        if motor1.relative_pos == 90:
            cw = False
        else:
            current_pos = motor1.relative_pos + 2
            if current_pos > 90:
                current_pos -= 90
                deg = current_pos
                motor1.rotate_stepper(deg, 'cw', .001, False)
            else:
                motor1.rotate_stepper(2, 'cw', .001, False)
        
    else:
        if motor1.relative_pos == -90:
            cw = True
        else:
            current_pos = motor1.relative_pos - 2
            if current_pos < -90:
                current_pos = abs(current_pos + 90)
                deg = current_pos
                motor1.rotate_stepper(deg, 'ccw', .001, False)
            else:
                motor1.rotate_stepper(2, 'ccw', .001, False)
    
    
    #CV code to detect pest goes here?
    
    
    if pest_detected:
        cord = 5
        direction = 'cw'
        while True:
            #get some cordinates from CV and calculate a degree to have pest in center view
            motor1.rotate_stepper(cord, direction, .001, False)
            #get distance and calculate angle for servo
            needed_angle = 0
            if(servo1.previous_angle == needed_angle):
                #open solenoid
            else:
                servo1.set_angle(needed_angle)
                time.sleep(.5)
                #open solenoid
                
            #CV code to detect pest goes here?
            if(pest_detected):
                continue
            else:
                break
