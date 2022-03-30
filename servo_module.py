import RPi.GPIO as GPIO
import time

MAX_RANGE = 270
MIN_RANGE = 0

class servo:
    def __init__(self, pin, freq, servoNum):
        self.pin = pin
        self.freq = freq
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        self.servoNum = GPIO.PWM(pin, freq)
        self.servoNum.start(0)
        self.previous_angle = 0

    def set_angle(self, angle, delay=0.5):
        if self.previous_angle == angle:
            print("desired angle same as previous")
        elif angle > MAX_RANGE:
            print("desired angle greater than 270")
        elif angle < MIN_RANGE:
            print("desired angle less than 0")
        else:
            self.servoNum.ChangeDutyCycle(2+(angle/27))
            print(2+(angle/27))
            time.sleep(delay)
            self.servoNum.ChangeDutyCycle(0)
            self.previous_angle = angle
