import stepper_module as s
import time

step = 3
direc = 5

motor1 = s.stepper(step, direc)

motor1.rotate_stepper(90, 'cw',.001, True) #from inital relative pos, rotate 90 degrees cc
time.sleep(1)
motor1.rotate_stepper(180, 'ccw',.001, True)#from relative pos, rotate 180 degrees (max) 
time.sleep(1)
motor1.rotate_stepper(90, 'cw',.001, True)#rotate back to initial relative position
