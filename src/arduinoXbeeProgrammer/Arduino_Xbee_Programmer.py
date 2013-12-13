import sys
import serial
from xbee import ZigBee

ser = serial.Serial('COM5', 19200)

xbee = ZigBee(ser, escaped=True)

while True:
    try:
        xbee.send('at', command=b'DH')
        resp = xbee.wait_read_frame()
        print(resp)
    except KeyboardInterrupt:
        break


ser.close()
