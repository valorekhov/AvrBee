from AvrIspFlow import *
from HexFileFormat import HexFileFormat
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

        flashPageSize = 128
        self.resolveTarget()

        reader = HexFileFormat(filePath)
        lines = reader.get_bytes()

        startAddress, foo = lines[0]
        toWrite = bytearray()
        length = 0
        for (address, data) in lines:
            toWrite += data
        length = len(toWrite)


        programmer = AvrIspFlow(self.xbee)
        
        self.resetTarget()                  #do not place any other actions after resetting the target

        programmer.getTargetParameters()

        programmer.enterProgMode()
        pagesToWrite = length / flashPageSize
        if pagesToWrite > int(pagesToWrite):
            pagesToWrite = int(pagesToWrite) + 1        
        for pageNo in range(0, pagesToWrite):
            startByte = pageNo*flashPageSize
            page = toWrite[startByte:startByte+flashPageSize]
            if len(page) < flashPageSize:
                for i in range(flashPageSize - len(page)):
                    page += b'\xFF'
            programmer.writeRomPage(startAddress + startByte, page)

        programmer.leaveProgMode()

        print("Verifying %d bytes beginning with start address 0x%x" % (length, startAddress))
        readPages = bytearray()
        readPageSize = 128
        readPageNo = length / readPageSize
        readPageWholeNo = int(readPageNo) +1
        for i in range(0, readPageWholeNo):
            readPages += programmer.readRomPage(startAddress + i*readPageSize, readPageSize)

        readPages = readPages[:length]

        print(str(readPages))
        print(str(len(readPages)))

        if readPages != toWrite:
            raise Exception("Failed validation")

        self.restoreTarget()

        pass

    def download(self, startAddress, length, filePath):
        pageSize = min(248, length)
        data = bytearray()
        address = startAddress
        pages = int(length / pageSize)

        programmer = AvrIspFlow(self.xbee)
        
        self.resolveTarget()
        self.resetTarget()
        programmer.getTargetParameters()

        for i in range(0, pages):
            dataPage = programmer.readRomPage(address, pageSize)
            if len(dataPage) < pageSize:
                raise Exception("Read less bytes than the expected page size")
            data += dataPage
            address += pageSize

        if pages * pageSize < length:
            remainder = length - pages * pageSize
            print("reading remainder " + str(remainder))
            data += programmer.readRomPage(address, remainder)

        self.restoreTarget()

        writer = HexFileFormat(filePath)
        writer.save_bytes(data, startAddress)
    
