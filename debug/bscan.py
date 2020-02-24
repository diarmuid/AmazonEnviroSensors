# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# bscan.py - Simple bluetooth LE scanner and data extractor

from bluepy.btle import Scanner, DefaultDelegate
import time
import struct


# Enter the MAC address of the sensor from the lescan
SENSOR_ADDRESS = ["8e:f9:00:00:00:ed"]
SENSOR_LOCATION = ["Garage"]


class DecodeErrorException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)


scanner = Scanner().withDelegate(ScanDelegate())

ManuDataHex = []
ReadLoop = True
try:
    while (ReadLoop):
        devices = scanner.scan(2.0)
        ManuData = ""

        for dev in devices:
            entry = 0
            AcceleroData = 0
            AcceleroType = 0
            TempData = 0
            for saddr in SENSOR_ADDRESS:
                entry += 1
                if (dev.addr == saddr):
                    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                    CurrentDevAddr = saddr
                    CurrentDevLoc = SENSOR_LOCATION[entry - 1]
                    for (adtype, desc, value) in dev.getScanData():
                        print("  %s = %s" % (desc, value))
                        if (desc == "Manufacturer"):
                            ManuData = value

                    if (ManuData == ""):
                        print("No data received, end decoding")
                        continue

                    # print ManuData

                    for i, j in zip(ManuData[::2], ManuData[1::2]):
                        ManuDataHex.append(int(i + j, 16))
                    print(repr(ManuDataHex))
                    continue
                    # Start decoding the raw Manufacturer data
                    if ((ManuDataHex[0] == 0x85) and (ManuDataHex[1] == 0x00)):
                        print("Header byte 0x0085 found")
                    else:
                        print("Header byte 0x0085 not found, decoding stop")
                        #continue

                    # Skip Major/Minor
                    # Index 5 is 0x3c, indicate battery level and config #
                    if (ManuDataHex[4] == 0x3c):
                        BatteryLevel = ManuDataHex[5]
                        ConfigCounter = ManuDataHex[6]

                    idx = 7
                    # print "TotalLen: " + str(len(ManuDataHex))
                    while (idx < len(ManuDataHex)):
                        # print "Idx: " + str(idx)
                        # print "Data: " + hex(ManuDataHex[idx])

                        if (ManuDataHex[idx] == 0x41):
                            # Accerometer data
                            idx += 1
                            AcceleroType = ManuDataHex[idx]
                            AcceleroData = ManuDataHex[idx + 1]
                            idx += 2
                        elif (ManuDataHex[idx] == 0x43):
                            # Temperature data
                            idx += 1
                            TempData = ManuDataHex[idx]
                            TempData += ManuDataHex[idx + 1] * 0x100
                            TempData = TempData * 0.0625
                            idx += 2
                        else:
                            idx += 1

                    print("Device Address: " + CurrentDevAddr)
                    print("Device Location: " + CurrentDevLoc)
                    print("Battery Level: " + str(BatteryLevel) + "%")
                    print("Config Counter: " + str(ConfigCounter))
                    print("Accelero Data: " + hex(AcceleroType) + " " + hex(AcceleroData))
                    print("Temp Data: " + str(TempData))
                    ReadLoop = False

except DecodeErrorException:
    pass