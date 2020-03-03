from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import struct
import datetime
import logging
from threading import Event


RESP_OFFSET_CMD = 0x0
RESP_OFFSET_BADDR = 0x1

RESP_CMD_NEXT_ADDR = 0x1
RESP_CMD_READ_VALUES = 0x7


timeout=1.0
TenMinutes = datetime.timedelta(minutes=10)


class _NewKitonDelegate(DefaultDelegate):
    """
    Handle the callback from the Peripheral update notifications.
    """
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.last_recorded_address = 0x0
        self.readings = {}
        self.read_event = Event()

    def handleNotification(self, cHandle, data):
        read_response_len = len(data)
        if read_response_len == 20:
            responses = struct.unpack("<BHHB7H", data)
            if responses[RESP_OFFSET_CMD] == RESP_CMD_NEXT_ADDR:
                self.last_recorded_address = responses[RESP_OFFSET_BADDR] - 1
                logging.debug("Last Recorded Addr={:#0X}".format(self.last_recorded_address))
            for addr_idx in range(7):
                off = addr_idx + 4
                decimal = (responses[off] & 0xF) / 16
                integer = responses[off] >> 4
                temperature = decimal+integer
                if responses[RESP_OFFSET_CMD] == RESP_CMD_READ_VALUES:
                    self.readings[responses[RESP_OFFSET_BADDR] + addr_idx] = temperature
                logging.debug("CMD={:#0X} Addr={:#0X} Temp={}".format(responses[RESP_OFFSET_CMD], responses[RESP_OFFSET_BADDR] + addr_idx, temperature))
        self.read_event.set()
        return True


class Newkiton(object):
    """
    Class to handle accesses to the NewKiton Bluetooth sensor
    Instanciate the device with deviceAddr argument

    Call temperature to get the most recent temperature.
    Temperature is only updated very 10 minutes so the object will cache the temperature and only update every
    10 minutes

    """
    def __init__(self, deviceAddr):
        self.temperatures = {}
        self.deviceAddr = deviceAddr
        self._periph = None  # type: Peripheral
        self._most_recent_timestmap = datetime.datetime(year=2000, month=1, day=1, hour=1, minute=1, second=1)

    def _connect(self):
        self._periph = Peripheral(deviceAddr=self.deviceAddr)
        self._delagate = _NewKitonDelegate()
        self._periph.setDelegate(self._delagate)
        self.readings = self._delagate.readings

    def _disconnect(self):
        self._periph.disconnect()

    def _get_next_addr(self):
        logging.debug("Getting address of next recording")
        # This seems to trigger the update
        self._periph.writeCharacteristic(0x25, struct.pack(">H", 0x100), withResponse=True)
        if self._delagate.read_event.wait(timeout):
            self._delagate.read_event.clear()
        # Mow actually read the registers
        self._periph.writeCharacteristic(0x21, struct.pack(">BHH", 0x1, 0, 0), withResponse=True)
        if self._delagate.read_event.wait(timeout):
            self._delagate.read_event.clear()
            logging.debug("Got last add={:#0X}".format(self._delagate.last_recorded_address))
            self._most_recent_timestmap = datetime.datetime.utcnow()
            return True
        else:
            return False

    def _read_location(self, base_address):
        """
        Read the locations as defined in the base address. Does a read of 0x7 entries
        :param base_address:
        :return:
        """
        if base_address > self._delagate.last_recorded_address:
            logging.error("Don't read base the next recorded address")
            return False
        else:
            self._periph.writeCharacteristic(0x21, struct.pack("<BHHB", 0x7, base_address,  0, 0x7), withResponse=True)
            if self._delagate.read_event.wait(timeout):
                self._delagate.read_event.clear()
                logging.debug("Poplated temperatures from addr={:#0X}".format(base_address))
                return True
            else:
                return False

    def temperature(self):
        """
        Returns the most recent temperature reading
        :rtype: int
        """
        _current_time = datetime.datetime.utcnow()
        if abs(_current_time - self._most_recent_timestmap) < TenMinutes:
            logging.debug("Reading from cache")
            return self.readings[self._delagate.last_recorded_address]
        else:
            self._connect()
            self._get_next_addr()
            if self._read_location(self._delagate.last_recorded_address-6):
                self._disconnect()
                return self.readings[self._delagate.last_recorded_address]
            else:
                self._disconnect()
                return None