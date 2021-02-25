from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM
import logging
from collections import namedtuple
from threading import Event


Measurement = namedtuple('Measurement', ['temperature', 'humidity', 'batterylevel'])
logging.basicConfig(level=logging.INFO)

class _MiDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.measurement = None

    def handleNotification(self, cHandle, data):
        try:
            temp = int.from_bytes(data[0:2], byteorder='little', signed=True) / 100
            humidity = int.from_bytes(data[2:3], byteorder='little')
            voltage = int.from_bytes(data[3:5], byteorder='little') / 1000.
            batteryLevel = min(int(round((voltage - 2.1), 2) * 100), 100)  # 3.1 or above --> 100% 2.1 --> 0 %
            self.measurement = Measurement(temp, humidity, batteryLevel)

            logging.debug("Battery level: {}".format(batteryLevel))
            logging.debug("Temperature: {}".format(temp))
            logging.debug("Humidity: {}".format(humidity))
            logging.debug("Battery voltage: {} V".format(voltage))
        except Exception as e:
            logging.debug("Error={}".format(e))
            pass


class MiTemperature2(object):
    ''''
    Class to read the temperature from the MiTemp sensor from Amazon.
    Heavily based on https://github.com/JsBergbau/MiTemperature2 but refactored for my application
    '''
    def __init__(self, deviceAddr,  addrType=ADDR_TYPE_PUBLIC, iface=0):
        self.deviceAddr = deviceAddr
        self.iface = iface
        self.addrType = addrType
        self.timeout = 10.0

    def _connect(self):
        self._periph = Peripheral(deviceAddr=self.deviceAddr, addrType=self.addrType, iface=self.iface)
        enable_notification_temp_humidity = b'\x01\x00'
        self._periph.writeCharacteristic(0x0038, enable_notification_temp_humidity, True)
        self._periph.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
        self._delegate = _MiDelegate()
        self._periph.withDelegate(self._delegate)
        logging.debug("Connected to {}".format(self.deviceAddr))
        self.measurement = self._delegate.measurement

    def _disconnect(self):
        self._periph.disconnect()

    def _reading(self):
        """
        Returns the most recent temperature reading
        :rtype: Measurement
        """

        self._connect()
        result = None
        if self._periph.waitForNotifications(self.timeout):
            logging.debug("Received notification")
            result = self._delegate.measurement
        else:
            logging.error("No trigger from delegate")
        self._disconnect()
        return result

    def reading(self):
        """"
        Return the readings a tuple of temperatiure, humidity, battery level
        :rtype: (float, float, float)
        """
        measurement = self._reading()
        return measurement.temperature, measurement.humidity, measurement.batterylevel

    def temperature(self):
        measurement = self._reading()
        if measurement is None:
            return None
        else:
            return measurement.temperature


# Scanner Class

class DecodeErrorException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        pass


tempidx = 12
humidityidx = 14
msg_len = 40


class MiTemperature2Scan(object):
    ''''
    Scanner reads the broadcast messages but temperature doens't seem to be in it
    '''
    def __init__(self, deviceAddr):
        self.scanner = Scanner().withDelegate(ScanDelegate())
        self.addr = deviceAddr

    def read(self):
        rd_data = True
        while rd_data:
            for dev in self.scanner.scan(3):
                #logging.debug("DevAddr={} Add={}".format(dev.addr, self.addr))
                if dev.addr.lower() == self.addr.lower():
                    for (adtype, desc, value) in dev.getScanData():
                        logging.debug("dsc={} val={} len={}".format(desc, value, len(value)))
                        rd_data = False
