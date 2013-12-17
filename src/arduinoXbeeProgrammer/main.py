import sys, os, serial
from xbee import ZigBee
from XbeeWrapper import XbeeWrapper
from ArduinoXbeeApiModeProgrammer import ArduinoXbeeApiModeProgrammer

ser = serial.Serial('COM5', 9600)
xbee = ZigBee(ser, escaped=True)
adapter = XbeeWrapper(xbee)
prog = ArduinoXbeeApiModeProgrammer(adapter, b'\xFF\xFE')
path = os.path.join(os.path.dirname(__file__), "tests\MyBlink.cpp.hex" )
prog.upload(path)


while True:
    try:        
        xbee.send('at', command=b'DH')
        
        resp = xbee.wait_read_frame()
        print(resp)
    except KeyboardInterrupt:
        break


ser.close()
