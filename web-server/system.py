from control_functions_r import return_to_init_pos, motor_sweep, initial_start_position, servo_angle_needed, track_pest
import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
import cv2, eventlet

def system():

