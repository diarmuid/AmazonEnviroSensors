# Newkiton 

I bought a temperature senson on Amazon (https://www.amazon.com/Newkiton-NK-01B-Thermometer-Temperature-Compatible/dp/B07W53L4RD) 
I wanted to integrate it into a Graphana dashboard and to do so I needed to figure out how to pull the data from it

With that in mind, I reverse engineered the protocol. At the moment I know the basic on how to get the temperatire readings 
from the device and not much more.

I am not that familar with BLE but I know wireshark so I used that to reverse engineer it. The  I just copied the 
protocol and came up with this

The device seems to store the data on a NVM with a simple address scheme. I presume it wraps around but I haven't 
run it for long enough just yet.

To use this, just instanciate a device and call the temperature method. The temperature is only updated every 10 minutes 
so call it more frequently will only return a cached version

`````python
from Newkiton import Newkiton
import time

sensor = NewKitOn.NewKiton(deviceAddr="8e:f9:00:00:00:ed")
while True:
    print("Temp={}".format(sensor.temperature()))
    time.sleep(60*10)


`````