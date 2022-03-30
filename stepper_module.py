import time
import RPi.GPIO as GPIO

RANGE_ERR = -1
DIR_ERR = -2
MIN_DEG_ERR = -3

DEG_PER_STEP = 0.9
MAX_RANGE = 180
MIN_RANGE = -180
TOTAL_RANGE = 2 * MAX_RANGE

class stepper:
    def __init__(self, step, direc):
        self.step_pin = step
        self.dir_pin = direc
        self.relative_pos = 0
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(step, GPIO.OUT)
        GPIO.setup(direc, GPIO.OUT)
    
    def rotate_stepper(self, degrees, direction, delay = .001, verbose = False):
        if degrees < DEG_PER_STEP:
            print("minimum degrees is 0.9")
            return MIN_DEG_ERR
        steps = int(round(degrees / DEG_PER_STEP))
        temp = self.relative_pos
        i = 0
        
        if direction == 'cw':
            temp += degrees
            if temp > MAX_RANGE:
                print('angle greater than the max range of {0} (pos > {1})'.format(TOTAL_RANGE, MAX_RANGE))
                return RANGE_ERR
            else:
                self.relative_pos = temp
                GPIO.output(self.dir_pin, GPIO.HIGH)
        elif direction == 'ccw':
            temp -= degrees
            if temp < MIN_RANGE:
                print('angle greater than the max range of {0} (pos < {1})'.format(TOTAL_RANGE, MIN_RANGE))
                return RANGE_ERR
            else:
                self.relative_pos = temp
                GPIO.output(self.dir_pin, GPIO.LOW)
        else:
            print('invalid direction input')
            return DIR_ERR
        
        for i in range(0, steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)
            
        if verbose == True:
            print('relative position is: {0}'.format(self.relative_pos))
            if direction == 'cw':
                print('num of steps taken clockwise:')
                print(steps)
            else:
                print('num of steps take counterclockwise:')
                print(steps)
                
        return self.relative_pos   # new position after rotation
        
