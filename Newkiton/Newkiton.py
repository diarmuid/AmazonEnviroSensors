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
            elif responses[RESP_OFFSET_CMD] == RESP_CMD_READ_VALUES:
                for addr_idx in range(7):
                    off = addr_idx + 4
                    decimal = (responses[off] & 0xF) / 16
                    integer = responses[off] >> 4
                    temperature = decimal+integer
                    self.readings[responses[RESP_OFFSET_BADDR] + addr_idx] = temperature
                    logging.debug("Addr={:#0X} Temp={}".format(responses[RESP_OFFSET_BADDR] + addr_idx, temperature))
        self.read_event.set()
        return True


class Newkiton(Peripheral):
    """
    Class to handle accesses to the NewKiton Bluetooth sensor
    Instanciate the device with deviceAddr argument

    Call temperature to get the most recent temperature.
    Temperature is only updated very 10 minutes so the object will cache the temperature and only update every
    10 minutes

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temperatures = {}
        self._most_recent_timestmap = None
        self.delagate = _NewKitonDelegate()
        self.setDelegate(self.delagate)
        self.temperature()

    def _get_next_addr(self):
        logging.debug("Getting address of next recording")
        # This seems to trigger the update
        self.writeCharacteristic(0x25, struct.pack(">H", 0x100), withResponse=True)
        if self.delagate.read_event.wait(timeout):
            self.delagate.read_event.clear()
        # Mow actually read the registers
        self.writeCharacteristic(0x21, struct.pack(">BHH", 0x1, 0, 0), withResponse=True)
        if self.delagate.read_event.wait(timeout):
            self.delagate.read_event.clear()
            logging.debug("Got last add={:#0X}".format(self.delagate.last_recorded_address))

    def _read_location(self, base_address):
        """
        Read the locations as defined in the base address. Does a read of 0x7 entries
        :param base_address:
        :return:
        """
        if base_address > self.delagate.last_recorded_address:
            logging.error("Don't read base the next recorded address")
            return False
        else:
            self.writeCharacteristic(0x21, struct.pack("<BHHB", 0x7, base_address,  0, 0x7), withResponse=True)
            if self.delagate.read_event.wait(timeout):
                self.delagate.read_event.clear()
                logging.debug("Poplated temperatures from addr={:#0X}".format(base_address))
                return True
            else:
                return False

    def temperature(self):
        """
        Returns the most recent temperature reading
        :rtype: int
        """
        _current_time = datetime.datetime.now()
        if self._most_recent_timestmap is not None and (_current_time - self._most_recent_timestmap) < TenMinutes:
            logging.debug("Reading from cache")
            return self.delagate.readings[self.delagate.last_recorded_address]
        else:
            self._get_next_addr()
            last_set_readings_addr = self.delagate.last_recorded_address - 6
            if self._read_location(last_set_readings_addr):
                logging.debug("Readings=" + repr(self.delagate.readings))
                self._most_recent_timestmap = _current_time
                return self.delagate.readings[last_set_readings_addr+6]
            else:
                return None