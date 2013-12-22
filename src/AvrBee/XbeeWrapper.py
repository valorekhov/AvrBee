from array import array
import struct

class XbeeWrapper(object):
    def __init__(self, device):
        self.device = device
        self.counter = 1;
        self.addr = [0,0]
        self.addrLong = [0,0,0,0,0,0,0,0]

    def getFrameId(self):
        self.counter += 1
        if self.counter > 255: self.counter = 0
        return bytearray([self.counter]);

    def resolve(self, name):
        self.device.send('at', frame_id=self.getFrameId(), command=b'DN', parameter=bytearray(name, 'latin1')) 
        frame = self.device.wait_read_frame()
        bytes = frame['parameter']
        self.addr = bytes[0:2]
        self.addrLong = bytes[2:]

    def setPinMode(self, pin, mode):
        cmd = bytearray(str(pin), 'latin1')
        setting = bytearray([mode])
        self.device.remote_at(frame_id=self.getFrameId(), dest_addr_long = self.addrLong, command=cmd, parameter=setting) 
        frame = self.device.wait_read_frame()
        return frame['status'] == 0

    def sendBytes(self, *args):
        arr = bytearray()
        for arg in args:
            if isinstance(arg, bytes) or isinstance(arg, bytearray):
                for s in arg:
                    arr.append(s)
            else:
                 if isinstance(arg, int):
                     arr.append(arg & 0xFF)
                 else:
                     raise Exception("Unsupported arg type: " + str(arg))

        print(str(arr))
        packetSize = 128
        packets = len(arr) / packetSize
        wholePackets = int(packets)
        for i in range(0, wholePackets):
            startIdx = i*packetSize
            self.device.tx(frame_id = self.getFrameId(), dest_addr_long=self.addrLong, dest_addr=self.addr, data=arr[startIdx:startIdx+packetSize])
            frame = self.device.wait_read_frame()
            status = frame.get('deliver_status')
            if status != 0 and status != b'\0':
                raise Exception("Unexpected delivery status %s" % str(status))

        if packets > wholePackets:
            self.device.tx(frame_id = self.getFrameId(), dest_addr_long=self.addrLong, dest_addr=self.addr, data=arr[wholePackets*packetSize:])
            frame = self.device.wait_read_frame()
            status = frame.get('deliver_status')
            if status != 0 and status != b'\0':
                raise Exception("Unexpected delivery status %s" % str(status))


    def getBytes(self, terminatorChar=0x10):
        ret = bytearray([0])
        while not ret[-1] == terminatorChar:
            frame = self.device.wait_read_frame()
            #print(frame)
            ret += frame["rf_data"]

        return ret[1:-1]

    def getBytesLong(self, expectedBytes):
        ret = bytearray()
        while len(ret) < expectedBytes:
            frame = self.device.wait_read_frame()
            ret += frame["rf_data"]
            print(len(ret))

        return ret


