from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import time
import struct
import time
import csv

# Data is memory mapped to a lineary address space
# By reading the most recent non-zero value we have the most recent sample
# What to store them as?


class TemperatureDataPoints(object):
    def __init__(self):
        self.timestamp = None
        self.value = None


class MyDelegate(DefaultDelegate):
    def __init__(self, csvfilename):
        DefaultDelegate.__init__(self)
        self.csvf = open(csvfilename, mode="w")
        self.csv = csv.writer(self.csvf)
        self.last_valid_addr = 0x0
        self.keep_scanning = True
        self.temperatures = []

    def close(self):
        self.csvf.close()

    def handleNotification(self, cHandle, data):
        read_response_len = len(data)
        if read_response_len == 20:
            responses = struct.unpack("<BHHB7H", data)
            #print("{:#0X}{:#0X}{:#0X}".format(responses[0], responses[1], responses[2]))
            for idx in range(4, 11):
                addr = responses[1]+idx-4
                decimal = (responses[idx] & 0xF) / 16
                integer = responses[idx] >> 4
                temperature = decimal+integer
                if temperature != 0.0 and addr > self.last_valid_addr:
                    self.last_valid_addr = addr
                elif temperature == 0.0 and responses[0] == 0x7 or addr >= self.last_valid_addr:
                    self.keep_scanning = False
                if temperature != 0.0:
                    self.temperatures.append(temperature)
                self.csv.writerow([responses[1], temperature])
                #if 11.0 < temperature < 12.0:
                print("Addr={:#0x}Temp{}".format(addr, temperature))
        else:
            responses = struct.unpack(">{}B".format(read_response_len), data)
            for w in responses:
                print("{:#0X}".format(w))


sensor = "8e:f9:00:00:00:ed"

perip = Peripheral(deviceAddr=sensor)
#for cst in perip.getCharacteristics():
#    print("{} {} {}".format(cst.uuid, cst.propertiesToString(), cst.getHandle()))
#    if cst.supportsRead():
#        print("\t{}".format(cst.read()))

delatate = MyDelegate("out.csv")
perip.setDelegate(delatate)

#perip.connect(sensor)
timeout=2.0
perip.writeCharacteristic(0x25, struct.pack(">H", 0x100), withResponse=True)
print(perip.waitForNotifications(timeout))
print("Writing to 21")
perip.writeCharacteristic(0x21, struct.pack(">BHH", 0x1, 0, 0), withResponse=True)
print(perip.waitForNotifications(timeout))

print("Now reading tempp")
addr = 0x300
readings=1
while delatate.keep_scanning:
    perip.writeCharacteristic(0x21, struct.pack("<BHHB", 0x7, addr,  0, 0x7), withResponse=True)
    resp= perip.waitForNotifications(timeout)
    print(resp)
    addr += 7
for t in delatate.temperatures:
    print(t)
print("{:#0X}".format(delatate.last_valid_addr))

delatate.close()