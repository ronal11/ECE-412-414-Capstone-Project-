import time
import RPi.GPIO as GPIO

RANGE_ERR = -1
DIR_ERR = -2

class stepper:
    def __init__(self, step, direc):
        self.step_pin = step
        self.dir_pin = direc
        self.relative_pos = 0
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(step, GPIO.OUT)
        GPIO.setup(direc, GPIO.OUT)
    
    def rotate_stepper(self, degrees, direction, delay = .001, verbose = False):
        steps = int(round(degrees / 0.9))
        temp = self.relative_pos
        i = 0
        
        if direction == 'cw':
            temp += degrees
            if temp > 90:
                print('angle greater than the max range of 180 (pos > 90)')
                return RANGE_ERR
            else:
                self.relative_pos = temp
                GPIO.output(self.dir_pin, GPIO.LOW)
        elif direction == 'ccw':
            temp -= degrees
            if temp < -90:
                print('angle greater than the max range of 180 (pos < -90)')
                return RANGE_ERR
            else:
                self.relative_pos = temp
                GPIO.output(self.dir_pin, GPIO.HIGH)
        else:
            print('invalid direction input')
            return DIR_ERR
        
        for i in range(0, steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)
            
        if verbose == True:
            print('relative position is:')
            print(self.relative_pos)
            if direction == 'cw':
                print('num of steps taken clockwise:')
                print(steps)
            else:
                print('num of steps take counterclockwise:')
                print(steps)
