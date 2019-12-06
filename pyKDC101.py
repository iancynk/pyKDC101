# %%
import serial
import serial.tools.list_ports
import time
import glob
import sys


# create a serial connection with the recommended parameters
def openstage():
    s = serial.Serial()
    s.baudrate = 115200
    s.bytesize = serial.EIGHTBITS
    s.parity = serial.PARITY_NONE
    s.stopbits = serial.STOPBITS_ONE # number of stop bits
    s.timeout = 5
    s.rtscts = True # enable hardware (TRS/CTS) flow control
    #print(s)

    # find available ports depending on operating system
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/ttyUSB*')
    elif sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    else:
        raise EnvironmentError('Unsupported platform')

    # try to open the ports until one works
    for port in ports:
        try:
            print(port)
            s.port = port
            s.open()
            time.sleep(0.1)
            break
        except:
            pass
    print('is open: ', s.is_open)
    return s


# close serial connection
def closestage(s):
    s.close()
    print('is open: ', s.is_open)


# send a command
def sendcommand(s, string):
    splitstring = string.split() # separate in to list of hex values
    command = [int(str, 16) for str in splitstring] # convert to integer
    print('sending command: ', command)
    s.write(bytes(command)) # send integer in binary format to stage


# receive and parse reply
def recvreply(s):
    time.sleep(0.04) # has to be at least 20 ms to work on my computer
    # print('bytes in queue: ', s.in_waiting)
    reply = ''
    while s.in_waiting > 0:
        # read every single byte (converted to hex) and add whitespace
        reply += s.read().hex()
        reply += ' '
    print('reply: ', reply)
    return reply


commands = {
    "identify":         "23 02 00 00 50 01", # flashes the screenA
    "move_home":        "43 04 01 00 50 01", # move home
    "req_info":         "05 00 00 00 50 01", # get hardware info
    "req_poscounter":   "11 04 01 00 50 01", # get position count
    "req_enccounter":   "0A 04 01 00 50 01", # get enccounter count
    "req_velparams":    "14 04 01 00 50 01", # get the velocity parameters
    "req_genmoveparams":"3B 04 01 00 50 01", # get backlash settings
    "req_homeparams":   "41 04 01 00 50 01", # get home parameters
    "req_moverelparams":"46 04 01 00 50 01", # get rel movement parameters
    "move_relative":    "48 04 01 00 50 01", # move predefined relative
    "req_moveabsparams":"51 04 01 00 50 01", # get abs movement parameters
    "move_absolute":    "53 04 01 00 50 01", # move predefined absolute
    "move_stop":        "65 04 01 00 50 01", # stop movement
    "req_jogparams":    "17 04 01 00 50 01", # get jog parameters
    "move_jog_forward": "6A 04 01 02 50 01", # jog forward
    "move_jog_backward":"6A 04 01 01 50 01", # jog backward
    "move_velocity_f":  "57 04 01 02 50 01", # move at fixed speed forward
    "move_velocity_b":  "57 04 01 01 50 01", # move at fixed speed backward
}

s = openstage()
sendcommand(s, commands["identify"])
time.sleep(0.1)

# %%
sendcommand(s, commands["move_stop"])
reply = recvreply(s)

# %%
closestage(s)

# %%
# about the PRM1-Z8:
# EncCnt per deg: 1919.6418578623391
# Scaling Factor
#   Velocity 42941.66 (deg/s)
#   Acceleration 14.66 (deg/s^2)
# POS = EncCnt x Pos
# VEL = EncCnt x T x 65536 x Vel
#   VEL (PRM1-Z8) = 6.2942e4 x Vel
# ACC = EncCnt x T^2 x 65536 x Acc
#   ACC (PRM1-Z8) = 14.6574 x Acc
# where T = 2048/6e6 (KDC101)
