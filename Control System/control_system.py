import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
import time

step = 3
direc = 5
servo_pin = 11
#intialize stepper and servo  motor
motor1 = s.stepper(step, direc)                  
#servo1 = ser.servo(servo_pin, 50, "servo1")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(36, GPIO.FALLING)

start = True
cw = True


while True:
    if GPIO.event_detected(36):
        if motor1.relative_pos < 0:
            time.sleep(1)
            temp = abs(motor1.relative_pos)
            print(temp)
            motor1.rotate_stepper(temp, 'cw', .01, False)
            print("back to initial from ccw")
            quit()
        elif motor1.relative_pos > 0:
            time.sleep(1)
            temp = abs(motor1.relative_pos)
            print(temp)
            motor1.rotate_stepper(temp, 'ccw', .01, False)
            print("back to initial from cc")
            quit()
    
    if start:
         motor1.rotate_stepper(90, 'ccw', .01, False)
         #servo1.set_angle(130)
         start = False
         
    
    if cw:
        if motor1.relative_pos > 86.4:
            print(motor1.relative_pos)
            degree = 90 - motor1.relative_pos
            if degree < 0.9:
                print("don't rotate")
            else:
                print(degree)
                motor1.rotate_stepper(degree, 'cw', .01, False)
            
        print(motor1.relative_pos)
        temp = round(motor1.relative_pos)
        print(temp)
        
        if temp == 90:
            cw = False
        else:
            motor1.rotate_stepper(3.6, 'cw', .01, False)
        
    else:
        if motor1.relative_pos < -86.4:
            print(motor1.relative_pos)
            degree = 90 - abs(motor1.relative_pos)
            if degree < 0.9:
                print("don't rotate")
            else:
                print(degree)
                motor1.rotate_stepper(degree, 'ccw', .01, False)
            
        print(motor1.relative_pos)
        temp = round(motor1.relative_pos)
        print(temp)
        
        if temp == -90:
            cw = True
        else:
            motor1.rotate_stepper(3.6, 'ccw', .01, False)
    
    
    #CV code to detect pest goes here?
    pest = int(input("pest detected? "))
    
    if pest == 1:
        cord = 5
        direction = 'cw'
        while True:
            #get some cordinates from CV and calculate a degree to have pest in center view
            print(motor1.relative_pos)
            cord = float(input("degree?"))
            direction = input("direction?")
            motor1.rotate_stepper(cord, direction, .01, False)
            #get distance and calculate angle for servo
            needed_angle = 0
            
            #if(servo1.previous_angle == needed_angle):
            #open solenoid
                #time.sleep(.5)
            #else:
                #servo1.set_angle(needed_angle)
                #time.sleep(.5)
                #open solenoid
                
            #CV code to detect pest goes here?
            pest = int(input("pest detected? "))
            if pest == 1:
                continue
            else:
                break
