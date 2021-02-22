
# This is just a repackaging of https://github.com/rnlgreen/thermobeacon
# The scanner works but I couldn't get the peripheral to work

from bluepy.btle import Scanner, DefaultDelegate


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


class ThermoBeacon(object):

    def __init__(self, deviceAddr):
        self.scanner = Scanner().withDelegate(ScanDelegate())
        self.addr = deviceAddr

    def temperature_and_humidity(self):
        rd_data = True
        while rd_data:
            for dev in self.scanner.scan(3):
                #print(dev.addr, self.addr)
                if dev.addr.lower() == self.addr.lower():
                    for (adtype, desc, value) in dev.getScanData():
                        #print("  %s = %s %d" % (desc, value, len(value)))
                        if desc == "Manufacturer":
                            ManuDataHex = []
                            for i, j in zip(value[::2], value[1::2]):
                                ManuDataHex.append(int(i + j, 16))
                            if len(value) == msg_len:
                                TempData = ManuDataHex[tempidx]
                                TempData += ManuDataHex[tempidx + 1] * 0x100
                                TempData = TempData * 0.0625
                                if TempData > 4000:
                                    TempData = -1 * (4096 - TempData)

                                HumidityData = ManuDataHex[humidityidx]
                                HumidityData += ManuDataHex[humidityidx + 1] * 0x100
                                HumidityData = HumidityData * 0.0625
                                return TempData, HumidityData

    def temperature(self):
        _temp, _humidity = self.temperature_and_humidity()
        return _temp

    def humidity(self):
        _temp, _humidity = self.temperature_and_humidity()
        return _humidity
