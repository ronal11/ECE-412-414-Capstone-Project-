
import RPi.GPIO as GPIO
import time

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 3 as an output, and set servo1 as pin 3 as PWM
GPIO.setup(3,GPIO.OUT)
servo1 = GPIO.PWM(3,50) 


servo1.start(0)
print ("Waiting for 2 seconds")
time.sleep(2)



# Define variable duty
duty = 2


while duty <= 15:
    servo1.ChangeDutyCycle(duty)
    time.sleep(1)
    duty = duty + 1

# Wait a couple of seconds
time.sleep(2)


#turn back to 0 degrees
print ("Turning back to 0 degrees")
servo1.ChangeDutyCycle(2)
time.sleep(0.5)
servo1.ChangeDutyCycle(0)

servo1.stop()
GPIO.cleanup()







