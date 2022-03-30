import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
import time

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

step_pin = 3
direc_pin = 5
servo_pin = 11
button_pin = 36
delay = .002
verbose_sweep = False
verbose_track = True

#intialize stepper and servo  motor
motor1 = s.stepper(step_pin, direc_pin)                  
#servo1 = ser.servo(servo_pin, 50, "servo1")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button_pin, GPIO.FALLING)
GPIO.setwarnings(False)

start = True
cw = True


while True:
    if GPIO.event_detected(button_pin):
        return_to_init_pos(motor1)
    
    if start:
         motor1.rotate_stepper(180, 'ccw', delay, verbose_sweep)
         #servo1.set_angle(130)
         start = False
         
    
    if cw:
        if motor1.relative_pos > 176.4:
            print(motor1.relative_pos)
            degree = 180 - motor1.relative_pos
            print('greater than 176.4', degree)
            motor1.rotate_stepper(degree, 'cw', delay, verbose_sweep)
            
        temp = motor1.relative_pos
        
        if temp > 179:
            cw = False
        else:
            motor1.rotate_stepper(3.6, 'cw', delay, verbose_sweep)
        
    else:
        if motor1.relative_pos < -176.4:
            print(motor1.relative_pos)
            degree = 180 - abs(motor1.relative_pos)
            print('less than -176.4' ,degree)
            motor1.rotate_stepper(degree, 'ccw', delay, verbose_sweep)
            
        temp = motor1.relative_pos
        
        
        if temp < -179:
            cw = True
        else:
            motor1.rotate_stepper(3.6, 'ccw', delay, verbose_sweep)
    
    
    #CV code to detect pest goes here?
    pest = 0 #int(input("pest detected? "))
    
    if pest == 1:
        cord = 5
        direction = 'cw'
        while True:
            #get some cordinates from CV and calculate a degree to have pest in center view
            print(motor1.relative_pos)
            cord = float(input("degree?"))
            direction = input("direction?")
            motor1.rotate_stepper(cord, direction, delay, verbose_track)
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
