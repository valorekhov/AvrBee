import select
from AvrIspFlow import *
from HexFileFormat import HexFileFormat


class ArduinoXbeeApiModeProgrammer(object):
    def __init__(self, xbee, targetName, resetPin = 'D3'):
        self.targetName = targetName
        self.resetPin = resetPin       
        self.xbee = xbee

    def resolve_target(self):
        if isinstance(self.targetName, (bytearray, bytes)):
            print("Setting remote as %s" % self.targetName)
            self.xbee.set_target_address_long(self.targetName)
        else:
            print("Resolving target %s" % self.targetName)
            self.xbee.resolve(self.targetName)
            print("Remote resolved as %s" % self.xbee.addrLong)

    def reset_target(self):
        self.xbee.setPinMode(self.resetPin, 4)  #first LOWER the pin if it was left HIGH
        time.sleep(.2)                         #wait a sec to allow the capacitor to discharge
        self.xbee.setPinMode(self.resetPin, 5)  #set the reset pin to HIGH thus triggering Arduino reset

    def restore_target(self):
        self.xbee.setPinMode(self.resetPin, 0) 

        dh = self.remoteState.get('dh')
        dl = self.remoteState.get('dl')

        if dh or dl:
            print("Restoring target prior DH/DL: %s" %( dh + dl))

            if dh:
                self.xbee.remoteAt("DH", dh)
            if dl:
                self.xbee.remoteAt("DL", dl)

            #self.xbee.remoteAt("WR")

    def configure_target(self):
        self.remoteState = dict()

        sh = self.xbee.localAt("SH")
        sl = self.xbee.localAt("SL")

#        self.reset_target()             # reset the target to take advantage of the on delay to configure sleep settings

        dh = self.xbee.remoteAt("DH")
        dl = self.xbee.remoteAt("DL")

        if dh != sh or dl != sl:
            print("Setting target to the address of the programming XBee: %s" %( sh + sl))
            self.xbee.remoteAt("DH", sh)
            self.xbee.remoteAt("DL", sl)
            #self.xbee.remoteAt("WR")
            self.remoteState['dh'] = dh
            self.remoteState['dl'] = dl

        return
        rsm = self.xbee.remoteAt("SM")
        rsp = self.xbee.remoteAt("SP")
        rspI, = struct.unpack(">H", rsp)
        rsmI = rsm[0]
        if rsmI in (1,2,3,5) or (rsmI == 4 and rspI > 10):
            print("Target is configured for sleep. Disabling this for the time of the upload...")
            if rsmI != 4:
                self.xbee.remoteAt("SM", 4)
            self.xbee.remoteAt("SP", b'\0\33')
            self.remoteState['sm'] = rsm
            self.remoteState['sp'] = rsp


    def upload(self, filePath):

        flashPageSize = 128
        self.resolve_target()


        reader = HexFileFormat(filePath)
        lines = reader.get_bytes()

        startAddress, foo = lines[0]
        toWrite = bytearray()

        for (address, data) in lines:
            toWrite += data
        length = len(toWrite)

        programmer = AvrIspFlow(self.xbee)

        print("configuring target addresses")

        self.configure_target()

        try:
            print("resetting target")
            self.reset_target()
            programmer.getTargetParameters()
            print("beginning programming sequence")
            programmer.enterProgMode()
            print("ready for upload")

            pagesToWrite = length / flashPageSize
            if pagesToWrite > int(pagesToWrite):
                pagesToWrite = int(pagesToWrite) + 1        
            for pageNo in range(0, int(pagesToWrite)):
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

            if readPages != toWrite:
                raise Exception("Failed validation")

        finally:
            self.restore_target()

        pass

    def download(self, startAddress, length, filePath):
        pageSize = min(248, length)
        data = bytearray()
        address = startAddress
        pages = int(length / pageSize)

        programmer = AvrIspFlow(self.xbee)
        
        self.resolve_target()
        self.reset_target()
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

        self.restore_target()

        writer = HexFileFormat(filePath)
        writer.save_bytes(data, startAddress)
    
