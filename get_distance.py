import sys
import os
import time
import RPi.GPIO as GPIO
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance as Board

board = Board()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, GPIO.LOW)

def print_distance(dis):
  d = 0
  if board.last_operate_status == board.STA_OK:
    print(dis)
    d = dis
    return d
  elif board.last_operate_status == board.STA_ERR_CHECKSUM:
    print("ERROR")
    d = -1
    return d
  elif board.last_operate_status == board.STA_ERR_SERIAL:
    print("Serial open failed!")
    d = -2
    return d
  elif board.last_operate_status == board.STA_ERR_CHECK_OUT_LIMIT:
    print("Above the upper limit: %d" %dis)
    d = -3
    return d
  elif board.last_operate_status == board.STA_ERR_CHECK_LOW_LIMIT:
    print("Below the lower limit: %d" %dis)
    d = -4
    return d
  elif board.last_operate_status == board.STA_ERR_DATA:
    print("No data!")
    d = -5
    return d


  #Minimum ranging threshold: 0mm
  dis_min = 0 
  #Highest ranging threshold: 4500mm  
  dis_max = 4500 
  board.set_dis_range(dis_min, dis_max)

def get_distance(samples, convertft):
  i = 0
  prev_valid_val = 0 
  for i in range(0, samples):
    temp = board.getDistance()
    distance = print_distance(temp)
    if distance >= 0:
      prev_valid_val = distance
    else:
      distance = prev_valid_val 
    #Delay time < 0.6s
    time.sleep(0.3) 
  if convertft:
    distance = distance / 305       #convert to ft
  else:
    distance = distance / 1000      #convert to meters
  return distance
