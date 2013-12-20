from array import array
from AvrBee.AvrConstants import *
import time

class AvrIspFlow(object):
    """Programs using STK500 protocol via attached XBEE in API mode"""
    def __init__(self, deviceWrapper):
        self.device = deviceWrapper

    def loadAddress(self, address):
        addressLow = address & 0xFF
        addressHigh = (address >> 8) & 0xFF

        self.device.sendBytes(AvrConstants.STK_LOAD_ADDRESS, addressLow, addressHigh, AvrConstants.CRC_EOP)
        self.assertInSync()        

    def progPage(self, bytes):
        self.device.sendBytes(AvrConstants.STK_PROG_PAGE, 0, len(bytes), 0, bytes, AvrConstants.CRC_EOP)
        self.assertInSync()

    def readPage(self, length):
        self.device.sendBytes(AvrConstants.STK_READ_PAGE, 0, length & 0xff, 0, AvrConstants.CRC_EOP)
        return self.device.getBytes()[1:]

    def writeRomPage(self, address, bytes):
        self.loadAddress(address)
        self.progPage(bytes)

    def readRomPage(self, address, length=64):
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





