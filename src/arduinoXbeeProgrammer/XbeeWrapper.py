from array import array
import struct

class XbeeWrapper(object):
    def __init__(self, device):
        self.device = device

    def togglePin(self, target, pinNumber):

        self.device.send('tx', frame_id=b'\0', dest_addr_long=struct.pack('>Q', 0), dest_addr = target, data=b'xig://time\n') #ATDx 5 = LOW state on remote digital pin X
        frame = self.device.wait_read_frame()
        self.addrLong = frame['source_addr_long']
        self.addr = target

        #move Long Address detection after pin toggle ops

        cmd = bytearray('D' + str(pinNumber), 'latin1')
        self.device.send('remote_at', frame_id=b'\0', dest_addr = target, command=cmd, parameter=b'5') #ATDx 5 = HIGH state on remote digital pin X
        self.device.wait_read_frame()

        self.device.send('remote_at', frame_id=b'\1', dest_addr = target, command=cmd, parameter=b'4') #ATDx 4 = LOW state on remote digital pin X
        self.device.wait_read_frame()

    def sendBytes(self, *args):
        arr = bytearray()
        for arg in args:
            if isinstance(arg, bytes):
                for s in arg:
                    arr.append(s)
            else:
                 if isinstance(arg, int):
                     arr.append(arg & 0xFF)
                 else:
                     raise Exception("Unsupported arg type: " + arg)
        len(arr)           
        self.device.send("tx", dest_addr_long=self.addrLong, dest_addr = self.addr, data=arr)

    def getBytes(self):
        frame = self.device.wait_read_frame()
        return frame.data

