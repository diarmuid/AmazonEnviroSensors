import unittest
from ThermoBeacon.ThermoBeacon import ThermoBeacon


class ThermoBeaconTestcase(unittest.TestCase):
    def test_basic(self):
        tb = ThermoBeacon("FA:AC:00:00:14:3A")
        self.assertTrue(100 > tb.temperature() > 1.0)
