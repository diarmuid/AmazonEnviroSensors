import sys
sys.path.append("../")
from MiTemperature import MiTemperature2
import unittest
import logging

#logging.basicConfig(level=logging.DEBUG)


class MiTestcase(unittest.TestCase):
    def test_basic(self):
        mi = MiTemperature2.MiTemperature2(deviceAddr="a4:c1:38:1f:75:19")
        mi.temperature()


if __name__ == '__main__':
    mi = MiTemperature2.MiTemperature2(deviceAddr="a4:c1:38:1f:75:19")
    (t, h, b) = mi.reading()
    print("Temp={} Hum={} BL={}".format(t, h ,b))