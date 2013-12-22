from array import array
from AvrConstants import *
import time, struct

class AvrIspFlow(object):
    """Programs using STK500 protocol via attached XBEE in API mode"""
    def __init__(self, deviceWrapper):
        self.device = deviceWrapper

    def loadAddress(self, address):
        address = int(address / 2)
        print("loading address %X" % address)
        self.device.sendBytes(AvrConstants.STK_LOAD_ADDRESS, struct.pack("<H", address),  AvrConstants.CRC_EOP) #Address is little endian
        self.assertInSync()        

    def progPage(self, bytes):
        pageSize = len(bytes)
        #print("Writing %d bytes: %s" % (len(bytes), bytes))
        #for i in range(0, len(bytes)):
        #    bytes[i] = bytes[i] & 0x0
        self.device.sendBytes(AvrConstants.STK_PROG_PAGE, struct.pack(">H", pageSize), b'F', bytes, AvrConstants.CRC_EOP) #Length is big endian.
        self.assertInSync()

    def readPage(self, length):
        self.device.sendBytes(AvrConstants.STK_READ_PAGE, struct.pack(">H", length), b'F', AvrConstants.CRC_EOP) #Length is big endian. Following byte is EEPROM flag (E for EEPROM)
        return self.device.getBytesLong(length+2)[1:-1]

    def writeRomPage(self, address, bytes):
        if len(bytes) == 0: 
            return 
        self.loadAddress(address)
        self.progPage(bytes)

        #self.loadAddress(address)
        #page = self.readPage(len(bytes))
        #print(str(page))
        #if page != bytes:
        #    raise Exception("Attempted to write bytes %s and received page %s" % (bytes, page))

    def readRomPage(self, address, length=64):
        print("reading address=" + hex(address))
        self.loadAddress(address)
        return self.readPage(length)

    def enterProgMode(self):
        self.device.sendBytes(AvrConstants.STK_ENTER_PROGMODE, AvrConstants.CRC_EOP)
        self.assertInSync()

    def leaveProgMode(self):
        self.device.sendBytes(AvrConstants.STK_LEAVE_PROGMODE, AvrConstants.CRC_EOP) 
        self.assertInSync()

        #self.device.getBytes()

    def getTargetParameters(self):
        self.device.sendBytes(AvrConstants.STK_GET_SIGN_ON, AvrConstants.CRC_EOP)
        programmer = self.device.getBytes()
        print(programmer)

        if not programmer[0] == 0x14:
             raise Exception("Unexpected response: " + programmer)

        bootloader = str(programmer[1:], 'latin1')
        if not bootloader == 'AVR ISP':
             raise Exception("Unknown bootloader type: " + bootloader)

    def assertInSync(self):
        resp = self.device.getBytes()
        l = len(resp)
        if l < 1 or l > 2 :
            raise Exception("Out of sync on the byte stream")

        if resp[0] != AvrConstants.STK_INSYNC:
            raise Exception("Expecting an 'In Sync' response")





