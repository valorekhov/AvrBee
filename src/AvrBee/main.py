import sys, os, serial
from xbee import ZigBee
from XbeeWrapper import XbeeWrapper
from ArduinoXbeeApiModeProgrammer import ArduinoXbeeApiModeProgrammer

ser = serial.Serial('COM5', 57600)
xbee = ZigBee(ser, escaped=True)

ser.timeout = 1
ser.read(1024)


adapter = XbeeWrapper(xbee)
prog = ArduinoXbeeApiModeProgrammer(adapter, b'\x00\x13\xa2\x00\x40\xb0\x99\xb3')
#path = os.path.join(os.path.dirname(__file__), "tests\MyBlink.cpp.hex" )
path = r'C:\Users\VAL\AppData\Local\Temp\build7501089379253165201.tmp\WeatherStation.cpp.hex'


prog.upload(path)

#prog.download(0, 1024, os.path.join(os.path.dirname(__file__), "tests\\backup.hex" ) )



ser.close()
