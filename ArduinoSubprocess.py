import serial
import os
import time
import numpy as np

def Process(q, o):
    while not os.path.isfile('/dev/ttyUSB0'):
        time.sleep(0.25)
    arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    arduino.write(b'so 1\n')
    while True:
        #print("Here!")
        #np.char.split(arduino.readline().decode('utf-8'))
        print(np.char.split(arduino.readline().decode('utf-8')))
        #arduino.write(b'so 1\n')
