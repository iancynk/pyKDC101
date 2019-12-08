# %%
import serial
import time

# create a serial connection with the recommended parameters
s = serial.Serial()
s.baudrate = 115200
s.port = '/dev/ttyUSB0'
s.bytesize = serial.EIGHTBITS
s.parity = serial.PARITY_NONE
s.stopbits = serial.STOPBITS_ONE # number of stop bits
s.timeout = 5
s.rtscts = True # enable hardware (TRS/CTS) flow control
#print(s)

# open the connection
s.open()
time.sleep(0.1)
print('is open: ', s.is_open)


# %%
# identify the stage (flashes the display)
# structure:
# 23 02 = command (here: instruct hardware to identify by flashing front panel LEDs)
# 00 00 = param1 and param2 (here zero)
# 50 = dest (here: generic USB unit)
# 01 = source (here: simply means host)
string = ('23 02 00 00 50 01') # command in hex
splitstring = string.split() # separate in to list of 6 hex values
command = [int(str, 16) for str in splitstring] # convert to integer
print('sending command: ', command)
s.write(bytes(command)) # send integer in binary format to stage

# %%
# move home
string = ('43 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# get hardware info
string = ('05 00 00 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

time.sleep(0.04) # has to be at least 20 ms to work on my computer
print('bytes in queue: ', s.in_waiting)
hwinfo = ''
while s.in_waiting > 0:
    # read every single byte (converted to hex) and add whitespace
    hwinfo += s.read().hex()
    hwinfo += ' '

print('hardware info: ', hwinfo)

# %%
# get velocity parameters
string = ('14 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

time.sleep(0.04)
print('bytes in queue: ', s.in_waiting)
velparams = ''
while s.in_waiting > 0:
    velparams += s.read().hex()
    velparams += ' '

print('velocity parameters: ', velparams)
print('minvel: ', velparams[24:35])
print('maxvel: ', velparams[48:59])
print('acc: ', velparams[36:47])

# %%
# get position counter
string = ('11 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

time.sleep(0.04)
print('bytes in queue: ', s.in_waiting)
poscount = ''
while s.in_waiting > 0:
    poscount += s.read().hex()
    poscount += ' '
print('position count: ', poscount)

# %%
# get relative movement parameter
string = ('46 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

time.sleep(0.04)
print('bytes in queue: ', s.in_waiting)
relmovparam = ''
while s.in_waiting > 0:
    relmovparam += s.read().hex()
    relmovparam += ' '
print('relative movement parameter: ', relmovparam)

# %%
# set relative movement parameter (the last four bytes, inverted somewhat)
string = ('45 04 06 00 D0 01 01 00 00 70 00 00')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# move relative by predefined parameter
string = ('48 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# move relative, setting the parameter
string = ('48 04 06 00 D0 01 01 00 00 70 00 00')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# get absolute movement parameter
string = ('51 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

time.sleep(0.04)
print('bytes in queue: ', s.in_waiting)
absmovparam = ''
while s.in_waiting > 0:
    absmovparam += s.read().hex()
    absmovparam += ' '
print('absolute movement parameter: ', absmovparam)

# %%
# set absolute movement parameter (the last four bytes, inverted somewhat)
string = ('50 04 06 00 D0 01 01 00 00 70 00 00')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# move absolute by predefined parameter
string = ('53 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# move absolute, setting the parameter
string = ('53 04 06 00 D0 01 01 00 00 A0 00 00')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))
# %%
# stop
string = ('65 04 01 00 50 01')
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

time.sleep(0.04)
stopped = ''
while s.in_waiting > 0:
    stopped += s.read().hex()
    stopped += ' '
print(stopped)

# %%
# jog
string = ('6A 04 01 02 50 01') # 01 02 for forward, 01 01 for reverse rotation
splitstring = string.split()
command = [int(str, 16) for str in splitstring]
print('sending command: ', command)
s.write(bytes(command))

# %%
# close stage
s.close()
s.is_open
