# %%
import serial

s = serial.Serial()
s.baudrate = 115200
s.port = '/dev/ttyUSB0'
s.bytesize = serial.EIGHTBITS
s.parity = serial.PARITY_NONE
s.stopbits = serial.STOPBITS_ONE # number of stop bits
s.timeout = 5
s.rtscts = True # enable hardware (TRS/CTS) flow control

s

s.open()

s.is_open

# %%

s.close

s.is_open
