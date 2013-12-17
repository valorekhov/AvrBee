from array import array
from AvrConstants import *

class StkXbeeApiModeProgrammer(object):
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

    def writeRomPage(self, address, bytes):
        self.loadAddress(address)
        self.progPage(bytes)

    def enterProgMode(self):
        self.device.sendBytes(AvrConstants.STK_ENTER_PROGMODE, AvrConstants.CRC_EOP)
        self.assertInSync()

    def leaveProgMode(self):
        self.device.sendBytes(AvrConstants.STK_LEAVE_PROGMODE, AvrConstants.CRC_EOP, AvrConstants.STK_LEAVE_PROGMODE, AvrConstants.OK) #Send a mangled packet tail on purpose to trigger Optiboot jump to the program start
        ignore = self.device.getBytes()

    def assertInSync(self):
        resp = self.device.getBytes()
        l = len(resp)
        if l < 1 or l > 2 :
            raise Exception("Out of sync on the byte stream")

        if resp[0] != AvrConstants.STK_INSYNC:
            raise Exception("Expecting an 'In Sync' response")

        if l > 1:
            resp = resp[1:]
        else:
            resp = self.device.getBytes()

        if l < 1 or resp[0] != AvrConstants.STK_OK:
            raise Exception("Expecting an 'OK' response")





