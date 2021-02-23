from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM
import logging
from collections import namedtuple
from threading import Event


Measurement = namedtuple('Measurement', ['temperature', 'humidity', 'batterylevel'])


class _MiDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.measurement = None
        self.read_event = Event()

    def handleNotification(self, cHandle, data):
        try:
            temp = int.from_bytes(data[0:2], byteorder='little', signed=True) / 100
            humidity = int.from_bytes(data[2:3], byteorder='little')
            voltage = int.from_bytes(data[3:5], byteorder='little') / 1000.
            batteryLevel = min(int(round((voltage - 2.1), 2) * 100), 100)  # 3.1 or above --> 100% 2.1 --> 0 %
            self.measurement = Measurement(temp, humidity, batteryLevel)

            logging.debug("Battery level:", batteryLevel)
            logging.debug("Temperature: " + str(temp))
            logging.debug("Humidity: " + str(humidity))
            logging.debug("Battery voltage:", voltage, "V")
            self.read_event.set()
        except Exception as e:
            logging.debug("Error={}".format(e))
            pass


class MiTemperature2(object):
    def __init__(self, deviceAddr,  addrType=ADDR_TYPE_PUBLIC, iface=0):
        self.deviceAddr = deviceAddr
        self.iface = iface
        self.addrType = addrType
        self.timeout = 3.0

    def _connect(self):
        self._periph = Peripheral(deviceAddr=self.deviceAddr, addrType=self.addrType, iface=self.iface)
        enable_notification_temp_humidity = b'\x01\x00'
        self._periph.writeCharacteristic(0x0038, enable_notification_temp_humidity, True)
        self._periph.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
        self._delagate = _MiDelegate()
        self._periph.setDelegate(self._delagate)
        self.readings = self._delagate.readings

    def _disconnect(self):
        self._periph.disconnect()

    def _reading(self):
        """
        Returns the most recent temperature reading
        :rtype: Measurement
        """

        self._connect()
        if self._delagate.read_event.wait(self.timeout):
            self._delagate.read_event.clear()
            return self._delagate.measurement
        else:
            return None

    def reading(self):
        """"
        Return the readings a tuple of temperatiure, humidity, battery level
        :rtype: (float, float, float)
        """
        measurement = self._reading()
        return measurement.temperature, measurement.humidity, measurement.batterylevel

    def temperature(self):
        measurement = self._reading()
        return measurement.temperature