import sys
from xbee import ZigBee
import serial

ser = serial.Serial('COM5', 19200)

xbee = ZigBee(ser)

while True:
    try:
        xbee.send('at', command=b'DH')
        resp = xbee.wait_read_frame()
        print(resp)
    except KeyboardInterrupt:
        break


ser.close()
