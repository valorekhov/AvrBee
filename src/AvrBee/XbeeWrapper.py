class XbeeWrapper(object):
    def __init__(self, device):
        self.device = device
        self.counter = 1;
        self.target_address = [0, 0]
        self.target_address_long = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_rx_frame = None

    def get_frame_id(self):
        self.counter += 1
        if self.counter > 255:
            self.counter = 0
        return bytearray([self.counter]);

    def set_target_address_long(self, address):
        self.target_address_long = address
        self.target_address = b'\0\0'

    def resolve(self, name):
        tries = 0
        while tries < 3:
            fid = self.get_frame_id();
            self.device.send('at', frame_id=fid, command=b'DN', parameter=bytearray(name, 'latin1'))
            frames = 0;
            while frames < 10:
                frame = self.device.wait_read_frame()
                if frame['id'] == 'at_response' and frame['frame_id'] == fid and frame['status'] == b'\0':
                    bytes = frame['parameter']
                    self.target_address = bytes[0:2]
                    self.target_address_long = bytes[2:]
                    return
                frames += 1
            tries += 1
        raise Exception("Unable to resolve target: %s" % name)

    def setPinMode(self, pin, mode):
        cmd = bytearray(str(pin), 'latin1')
        setting = bytearray([mode])
        self.device.remote_at(frame_id=self.get_frame_id(), dest_addr_long=self.target_address_long, command=cmd,
                              parameter=setting)
        frame = self.device.wait_read_frame()
        return frame['status'] == 0

    def sendAt(self, cmdTarget, command, value=None):
        cmd = bytearray(str(command), 'latin1')
        setting = None
        if value:
            setting = bytearray(value)
        tries = 0
        while tries < 5:
            fid =  self.get_frame_id()
            self.device.send(cmdTarget, frame_id=fid, dest_addr_long=self.target_address_long, command=cmd,
                             parameter=setting)
            frames = 0
            while frames < 10:
                frame = self.device.wait_read_frame()
                is_remote_at_resp = frame['id'] == 'remote_at_response'
                if (frame['id'] == 'at_response' or is_remote_at_resp) and \
                                frame['frame_id'] == fid:
                    if frame['status'] != b'\0':
                        raise Exception("Unexpected %s status %s" % (frame['id'], frame['status']))
                    if is_remote_at_resp and self.target_address == b'\0\0':
                        self.target_address = frame['source_addr']
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
            startIdx = i * packetSize
            #print("idx:%d startIdx:%d packets:%d len:%d packetSize:%d" %(i, startIdx, packets, len(arr), packetSize))
            payload = arr[startIdx:startIdx + packetSize]
            self.device.tx(frame_id=self.get_frame_id(), dest_addr_long=self.target_address_long,
                           dest_addr=self.target_address, data=payload)
            while True:
                frame = self.device.wait_read_frame()

                if frame['id'] == 'rx' and frame.get('source_addr') == self.target_address and frame['rf_data'][
                    -1] == 0x10:
                    #print("storing frame %s"  %  frame)
                    self.last_rx_frame = frame
                    break

                if frame['id'] == 'tx_status':
                    status = frame.get('deliver_status')
                    if status != 0 and status != b'\0':
                        raise Exception("Unexpected delivery status 1 %s" % frame)
                    break

                print("unexpected frame: %s" % frame)

    def getBytes(self, terminatorChar=0x10):
        if self.last_rx_frame != None and self.last_rx_frame["rf_data"][-1] == terminatorChar:
            data = self.last_rx_frame["rf_data"]
            #print("reusing last frame %s"  %  self.lastRxFrame)
            self.last_rx_frame = None
            return data[:-1]

        ret = bytearray([0])
        while not ret[-1] == terminatorChar:
            frame = self.device.wait_read_frame()
            if frame['id'] == "rx":
                ret += frame["rf_data"]
            else:
                print("Ignoring frame %s, state of buffer now %s" % (frame,  ret))

        return ret[1:-1]

    def getBytesLong(self, expectedBytes):
        ret = bytearray()
        while len(ret) < expectedBytes:
            frame = self.device.wait_read_frame()
            ret += frame["rf_data"]
            #print(len(ret))

        return ret


