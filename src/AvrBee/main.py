import sys, os, serial
from xbee import ZigBee
from XbeeWrapper import XbeeWrapper
from ArduinoXbeeApiModeProgrammer import ArduinoXbeeApiModeProgrammer

ser = serial.Serial('COM5', 57600)
xbee = ZigBee(ser, escaped=True)

ser.timeout = 1
ser.read(1024)



adapter = XbeeWrapper(xbee)
prog = ArduinoXbeeApiModeProgrammer(adapter, 'Weather')
#path = os.path.join(os.path.dirname(__file__), "tests\MyBlink.cpp.hex" )
path = r'C:\Users\val\AppData\Local\Temp\build3481126681594866832.tmp\WeatherStation.cpp.hex'

prog.upload(path)

#prog.download(0, 1024, os.path.join(os.path.dirname(__file__), "tests\\backup.hex" ) )



ser.close()
