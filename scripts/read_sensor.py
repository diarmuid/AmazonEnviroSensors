import sys
sys.path.append(".")
from Newkiton import Newkiton
import logging
import time

# Debug option here
logging.basicConfig(level=logging.DEBUG)

sensor = Newkiton.Newkiton(deviceAddr="8e:f9:00:00:00:ed")
while True:
    print("Temp={}".format(sensor.temperature()))
    time.sleep(60*10)
