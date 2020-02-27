import unittest
import datetime
from Newkiton import Newkiton

class NewkitonTestcase(unittest.TestCase):
    def test_timestmaps(self):
        n = datetime.datetime.now()
        temps = {}
        for m in range(10):
            dt = n + datetime.timedelta(minutes=m*5)
            temps[dt] = m
        #print(repr(temps))
        nt = n + datetime.timedelta(minutes=33)
        res = min(temps.keys(), key=lambda key: abs(key - nt))
        print(res)

    def test_basic(self):
        s = Newkiton.Newkiton(deviceAddr="8e:f9:00:00:00:12")
        s.temperature()


if __name__ == '__main__':
    unittest.main()
