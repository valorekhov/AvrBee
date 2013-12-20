from AVR_ISP_Flow import AVR_ISP_Flow
from FileReader import HexFileReader
import time


class ArduinoXbeeApiModeProgrammer(object):
    def __init__(self, xbee, targetName, resetPin = 'D3'):
        self.targetName = targetName
        self.resetPin = resetPin       
        self.xbee = xbee

    def resolveTarget(self):
        self.xbee.resolve(self.targetName)

    def resetTarget(self):
        self.xbee.setPinMode(self.resetPin, 4) #first LOWER the pin if it was left HIGH
        time.sleep(.2)                       #wait a sec to allow the capacitor to discharge
        self.xbee.setPinMode(self.resetPin, 5) #set the reset pin to HIGH thus triggering Arduino reset
        #time.sleep(.5)

    def restoreTarget(self):
        self.xbee.setPinMode(self.resetPin, 4) 

    def upload(self, filePath):
        self.resolveTarget()

        reader = HexFileReader(filePath)
        lines = reader.get_bytes()

        programmer = AVR_ISP_Flow(self.xbee)
        
        self.resetTarget()                  #do not place any other actions after resetting the target

        programmer.getTargetParameters()

        print(programmer.readRomPage(0, 128))
        return

        programmer.enterProgMode()

#        for (address, data) in lines:
#            programmer.writeRomPage(address, data)

        programmer.leaveProgMode()
        self.restoreTarget()

        pass
    
