import servo_module as s
import time

servo1 = s.servo(3, 50, "servo1")

servo1.set_angle(0)
time.sleep(2)
print("sleep for 2 sec")
servo1.set_angle(5)
time.sleep(2)
print("sleep for 2 sec")
servo1.set_angle(10)
time.sleep(2)
print("sleep for 2 sec")
servo1.set_angle(15)
time.sleep(2)
print("sleep for 2 sec")
servo1.set_angle(270)
time.sleep(2)
print("sleep for 2 sec")
servo1.set_angle(0)





