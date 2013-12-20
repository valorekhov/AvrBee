from abc import ABCMeta, abstractmethod
import array
import struct
import binascii, os

class HexFileFormat(object):
    """Parses out Hex File format into a byte stream"""
    def __init__(self, path=None, file=None):
        self.path = path
        self.file = file
        pass

    def get_bytes(self):
        with open(self.path) as f:
            self.lines = f.readlines()

        ret = list()
        for line in self.lines:
            if not line.startswith(':'):
                raise Exception("Unsupported format")
            line = line[1:].replace('\n','')
            bytes = bytearray.fromhex(line)
            
            pageSize = bytes[0]
            memAddrHigh = bytes[1] #Big endian address as per http://en.wikipedia.org/wiki/Intel_HEX
            memAddrLow = bytes[2]
            memAddr = (memAddrHigh << 8) + memAddrLow
            eolFlag = bytes[3]

            if eolFlag == 1:
                break

            checksum = bytes[-1] 
            payload = bytes[4:4+pageSize]
            payloadsum = (pageSize + memAddrLow + memAddrHigh + eolFlag + sum(x for x in payload) + checksum ) & 0xFF
            if payloadsum != 0:
                raise Exception("Checksum mismatch")
            ret.append((memAddr,payload))
        return ret

    def save_bytes(self, data, startAddress = 0):
            f = open(self.path) if self.file == None else self.file

            pageSize = 16
            length = len(data)
            address = startAddress
            pages = length / 16 
            if pages > int(pages):
                pages = int(pages) + 1

            for i in range(0, pages):                
                slice = data[i*pageSize: i*pageSize + pageSize]
                length = len(slice)
                eol = 0 if i+1 < pages else 1
                addrLow = address & 0xFF
                addrHigh = (address >> 8) & 0xFF
                checksum = (length + addrLow + addrHigh + eol +  sum(x for x in slice) )& 0xff
                checksum = 0xff - checksum

                bytes = bytearray()
                bytes.append(length)
                bytes.extend(struct.pack(">H", address))
                bytes.append(eol)
                bytes.extend(slice)
                bytes.append(checksum)
                #struct.pack( "BiB" + str(length)+"cB" , length, address & 0xFFFF, eol, str(slice), checksum)
                f.write(':')
                f.write(str(binascii.b2a_hex( bytes )).upper())
                f.write(os.linesep)

                address += length

            if f != sys.stdout:
                f.close()

class FileFormat(metaclass=ABCMeta):
    """Abstract class representing parsers"""
    @abstractmethod
    def get_bytes(self):
        pass

    @abstractmethod
    def save_bytes(self, data):
        pass

FileFormat.register(HexFileFormat)

