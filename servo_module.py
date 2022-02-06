import RPi.GPIO as GPIO
import time

class servo:
    def __init__(self, pin, freq, servoNum):
        self.pin = pin
        self.freq = freq
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        self.servoNum = GPIO.PWM(pin, freq)
        self.servoNum.start(0)
        self.previous_angle = 0

    def set_angle(self, angle):
        if self.previous_angle == angle:
            print('current angle same as previous')
        elif angle > 270:
            print("angle greater than 270")
        else:
            self.servoNum.ChangeDutyCycle(2+(angle/27))
            print(2+(angle/27))
            time.sleep(0.5)
            self.servoNum.ChangeDutyCycle(0)
            self.previous_angle = angle
        
        
        
        
        