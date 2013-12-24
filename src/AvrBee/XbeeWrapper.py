from array import array
import struct

class XbeeWrapper(object):
    def __init__(self, device):
        self.device = device
        self.counter = 1;
        self.addr = [0,0]
        self.addrLong = [0,0,0,0,0,0,0,0]
        self.lastRxFrame = None

    def getFrameId(self):
        self.counter += 1
        if self.counter > 255: self.counter = 0
        return bytearray([self.counter]);

    def resolve(self, name):
        tries = 0
        while tries  < 3:
            fid = self.getFrameId();
            self.device.send('at', frame_id=fid, command=b'DN', parameter=bytearray(name, 'latin1')) 
            frames = 0;
            while frames < 10:
                frame = self.device.wait_read_frame()
                if frame['id'] == 'at_response' and frame['frame_id'] == fid and frame['status'] == b'\0':
                        bytes = frame['parameter']
                        self.addr = bytes[0:2]
                        self.addrLong = bytes[2:]
                        return 
                frames += 1
            tries  +=1
        raise Error("Unable to resolve target: %s" % name)

    def setPinMode(self, pin, mode):
        cmd = bytearray(str(pin), 'latin1')
        setting = bytearray([mode])
        self.device.remote_at(frame_id=self.getFrameId(), dest_addr_long = self.addrLong, command=cmd, parameter=setting) 
        frame = self.device.wait_read_frame()
        return frame['status'] == 0

    def sendAt(self, cmdTarget, command, value=None):
        cmd = bytearray(str(command), 'latin1')
        setting = None
        if value:
            setting = bytearray(value)
        tries = 0
        while tries < 5:
            fid = frame_id=self.getFrameId()
            self.device.send(cmdTarget, frame_id=fid, dest_addr_long = self.addrLong, command=cmd, parameter=setting)
            frames = 0 
            while frames < 10:
                frame = self.device.wait_read_frame()
                if (frame['id'] == 'at_response' or  frame['id'] == 'remote_at_response') and frame['frame_id'] == fid and frame['status'] == b'\0':
                    return frame.get('parameter')
                frames += 1
            tries += 1 

        raise Exception("Unxpected status while executing %s command: %s" % (cmdTarget, frame))

    def remoteAt(self, command, value=None):
        return self.sendAt("remote_at", command, value)

    def localAt(self, command, value=None):
        return self.sendAt("at", command, value)

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

        packetSize = 248
        packets = len(arr) / packetSize
        if packets != int(packets):
            packets += 1

        for i in range(0, int(packets)):
            startIdx = i*packetSize
            #print("idx:%d startIdx:%d packets:%d len:%d packetSize:%d" %(i, startIdx, packets, len(arr), packetSize))
            payload = arr[startIdx:startIdx+packetSize]
            self.device.tx(frame_id = self.getFrameId(), dest_addr_long=self.addrLong, dest_addr=self.addr, data=payload)
            while True:
                frame = self.device.wait_read_frame()

                if frame['id'] == 'rx' and frame.get('source_addr') == self.addr and frame['rf_data'][-1] == 0x10:
                    #print("storing frame %s"  %  frame)
                    self.lastRxFrame = frame
                    break

                if frame['id'] == 'tx_status':
                    status = frame.get('deliver_status')
                    if status != 0 and status != b'\0': 
                        raise Exception("Unexpected delivery status 1 %s" % frame)
                    break

                print("unexpected frame: %s" % frame)

    def getBytes(self, terminatorChar=0x10):
        if self.lastRxFrame != None and self.lastRxFrame["rf_data"][-1] == terminatorChar:
            data = self.lastRxFrame["rf_data"]
            #print("reusing last frame %s"  %  self.lastRxFrame)
            self.lastRxFrame = None
            return data[:-1]

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
            #print(len(ret))

        return ret


