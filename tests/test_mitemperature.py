import sys
sys.path.append("../")
from MiTemperature.MiTemperature import MiTemperature, MiTemperatureATCScan
import unittest
import logging

logging.basicConfig(level=logging.DEBUG)


class MiTestcase(unittest.TestCase):
    def test_basic(self):
        mi = MiTemperature(deviceAddr="a4:c1:38:1f:75:19")
        mi.temperature()


def connect():
    mi = MiTemperature(deviceAddr="a4:c1:38:1f:75:19")
    (t, h, b) = mi.reading()
    print("Temp={} Hum={} BL={}".format(t, h ,b))


def scan():
    mi = MiTemperatureATCScan(deviceAddr="a4:c1:38:1f:75:19")
    while True:
        try:
            (t, h, b) = mi.reading()
            print("Temp={} Hum={} BL={}".format(t, h, b))
        except:
            pass


if __name__ == '__main__':
    scan()