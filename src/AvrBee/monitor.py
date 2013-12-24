import sys, os, serial
from xbee import ZigBee
from XbeeWrapper import XbeeWrapper
from ArduinoXbeeApiModeProgrammer import ArduinoXbeeApiModeProgrammer

ser = serial.Serial('COM5', 57600)
xbee = ZigBee(ser, escaped=True)

try:
    while True:
        frame = xbee.wait_read_frame()
        if frame['id'] == 'rx':
            print(str(frame['rf_data'], 'latin1'), end='')
finally:
    ser.close()
