import unittest, sys, os
from AvrBee.AvrIspFlow import AvrIspFlow
from AvrBee.XbeeWrapper import XbeeWrapper
from AvrBee.tests.Fake import *
from AvrBee.AvrConstants import *
from xbee import XBee
from array import array

class TestStkProto(unittest.TestCase):

    def test_StkSender(self):        
        xbee = FakeXBee(b'\x14\x10') #AvrConstants.STK_INSYNC, STK_OK
        adapter = XbeeWrapper(xbee)
        stk = AvrIspFlow(adapter)
        payload = B'Foo Bar'
        stk.writeRomPage(0x0010, payload)
        command, args = xbee.sentFrames[0]
        bytes = args['data']
        self.assertEqual(AvrConstants.STK_LOAD_ADDRESS, bytes[0])
        self.assertEqual(0x10, bytes[1])
        self.assertEqual(0x0, bytes[2])

        command, args = xbee.sentFrames[1]
        bytes = args['data']
        self.assertEqual(AvrConstants.STK_PROG_PAGE, bytes[0])
        self.assertEqual(0x0, bytes[1])
        self.assertEqual(len(payload), bytes[2])
        self.assertEqual(0x0, bytes[3])
        self.assertEqual(bytearray(payload), bytes[4:-1])
        self.assertEqual(AvrConstants.CRC_EOP, bytes[-1])

if __name__ == '__main__':
    unittest.main()
