import NewKitOn
import logging
import time
logging.basicConfig(level=logging.DEBUG)

sensor = NewKitOnC.NewKiton(deviceAddr="8e:f9:00:00:00:ed")
while True:
    print("Temp={}".format(sensor.temperature()))
    time.sleep(10)
