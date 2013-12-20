from abc import ABCMeta, abstractmethod
import array

class HexFileReader(object):
    """Parses out Hex File format into a byte stream"""
    def __init__(self, path):
        with open(path) as f:
            self.lines = f.readlines()
        pass

    def get_bytes(self):
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


class FileReader(metaclass=ABCMeta):
    """Abstract class representing parsers"""
    @abstractmethod
    def get_bytes(self):
        pass

FileReader.register(HexFileReader)

