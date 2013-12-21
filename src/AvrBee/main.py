import sys, os, serial
from xbee import ZigBee
from XbeeWrapper import XbeeWrapper
from ArduinoXbeeApiModeProgrammer import ArduinoXbeeApiModeProgrammer

ser = serial.Serial('COM5', 57600)
xbee = ZigBee(ser, escaped=False)
#xbee.tx(frame_id = b'\xD2', dest_addr_long=b'\x00\x13\xa2\x00\x40\xb0\x99\x66',  dest_addr=b'\x54\x6c', data=b'BOOT')
#frame = xbee.wait_read_frame()
#xbee.tx(frame_id = b'\xD3', dest_addr_long=b'\x00\x13\xa2\x00\x40\xb0\x99\x66',  dest_addr=b'\x54\x6c', data=b'ING')
#frame = xbee.wait_read_frame()
#print(frame)

adapter = XbeeWrapper(xbee)
prog = ArduinoXbeeApiModeProgrammer(adapter, 'Weather')
path = os.path.join(os.path.dirname(__file__), "tests\MyBlink.cpp.hex" )

prog.download( 0, 32*1024, os.path.join(os.path.dirname(__file__), "tests\backup.hex" ) )

#prog.upload(path)


ser.close()
