from StkXbeeApiModeProgrammer import StkXbeeApiModeProgrammer
from FileReader import HexFileReader


class ArduinoXbeeApiModeProgrammer(object):
    def __init__(self, xbee, address, resetPinNumber = 9):
        self.address = address
        self.resetPinNumber = resetPinNumber        
        self.xbee = xbee

    def resetTarget(self):
        self.xbee.togglePin(self.address, self.resetPinNumber)

    def upload(self, filePath):
        reader = HexFileReader(filePath)
        lines = reader.get_bytes()

        programmer = StkXbeeApiModeProgrammer(self.xbee)
        self.resetTarget()

        programmer.enterProgMode()

        for (address, data) in lines:
            programmer.writeRomPage(address, data)

        programmer.leaveProgMode()

        pass
    
