from xbee.frame import APIFrame

class FakeXBee(object):
    """
    Represents an XBee device from which data can be read.
    """
    def __init__(self, data):
        self.data = data
        self.sentFrames = list()
        
    def wait_read_frame(self):
        return {'rf_data': self.data}

    def send(self, cmd, **kwargs):
        self.sentFrames.append((cmd, kwargs))

    def tx(self, **kwargs):
        self.sentFrames.append(('tx', kwargs))

class FakeDevice(object):
    """
    Represents a fake serial port for testing purposes
    """
    def __init__(self):
        self.data = b''
        self.read_index = 0
        self.silent_on_empty = 1        

    
    def write(self, data):
        """
        Writes data to the fake port for later evaluation
        """
        self.data = data
        
    def read(self, length=1):
        """
        Read the indicated number of bytes from the port
        """
        # If too many bytes would be read, raise exception
        if self.read_index + length > len(self.data):
            if self.silent_on_empty:
                sys.exit(0)
            else:
                raise ValueError("Not enough bytes exist!")
        
        read_data = self.data[self.read_index:self.read_index + length]
        self.read_index += length
        
        return read_data

    def inWaiting(self):
        """
        Returns the number of bytes available to be read
        """
        return len(self.data) - self.read_index
