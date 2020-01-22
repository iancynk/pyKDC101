################################################################################
# IMPORTS
################################################################################
import serial
import serial.tools.list_ports
import time
import glob
import sys

################################################################################
# PARAMETERS (PRM1-Z8)
################################################################################
PRM1_EncCnt = 1919.6418578623391 # EncCnt per degree
PRM1_sf_vel = 42941.66 # scaling factor velocity (deg/s)
PRM1_sf_acc = 14.66 # scaling factor acceleration (deg/s^2)

flag_debug = False
# POS = EncCnt x Pos
# VEL = EncCnt x T x 65536 x Vel
# ACC = EncCnt x T^2 x 65536 x Acc
# where T = 2048/6e6 (KDC101)
# ==> VEL (PRM1-Z8) = 6.2942e4 x Vel
# ==> ACC (PRM1-Z8) = 14.6574 x Acc

################################################################################
# COMMANDS
################################################################################
commands = {
    "identify":         "23 02 00 00 50 01", # flashes the screen
    "move_home":        "43 04 01 00 50 01", # move home
    "req_info":         "05 00 00 00 50 01", # get hardware info
    "req_poscounter":   "11 04 01 00 50 01", # get position count
    "req_enccounter":   "0A 04 01 00 50 01", # get enccounter count
    "req_velparams":    "14 04 01 00 50 01", # get the velocity parameters
    "req_genmoveparams":"3B 04 01 00 50 01", # get backlash settings
    "req_homeparams":   "41 04 01 00 50 01", # get home parameters
    "req_moverelparams":"46 04 01 00 50 01", # get rel movement parameters
    "move_rel":         "48 04 01 00 50 01", # move predefined relative
    "move_rel_angle":   "48 04 06 00 D0 01 01 00", # move rel by angle (+4 byte)
    "move_rel_set":     "45 04 06 00 D0 01 01 00", # set relative movement parameter (+4 byte)
    "req_moveabsparams":"51 04 01 00 50 01", # get abs movement parameters
    "move_abs":         "53 04 01 00 50 01", # move predefined absolute
    "move_abs_angle":   "53 04 06 00 D0 01 01 00", # move predefined absolute (+4 byte)
    "move_abs_set":     "50 04 06 00 D0 01 01 00", # set absolute movement parameter (+4 byte)
    "move_stop":        "65 04 01 00 50 01", # stop movement
    "req_jogparams":    "17 04 01 00 50 01", # get jog parameters
    "move_jog_forward": "6A 04 01 02 50 01", # jog forward
    "move_jog_backward":"6A 04 01 01 50 01", # jog backward
    "move_velocity_f":  "57 04 01 02 50 01", # move at fixed speed forward
    "move_velocity_b":  "57 04 01 01 50 01"  # move at fixed speed backward
}

################################################################################
# SERIAL FUNCTIONS
################################################################################
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
    if s.is_open:
        print('is open: ', s.is_open)
    else:
        print('could not find any serial port')
        s = ''
    return s


# close serial connection
def closestage(s):
    if not s.is_open: print('no serial connection'); return
    s.close()
    print('is open: ', s.is_open)


# send a command
def sendcommand(s, string):
    if not s.is_open: print('no serial connection'); return
    splitstring = string.split() # separate in to list of hex values
    command = [int(str, 16) for str in splitstring] # convert to integer
    if flag_debug: print('sending command: ', command)
    s.write(bytes(command)) # send integer in binary format to stage


# receive and parse reply
def recvreply(s):
    if not s.is_open: print('no serial connection'); return
    time.sleep(0.04) # has to be at least 20 ms to work on my computer
    # print('bytes in queue: ', s.in_waiting)
    reply = ''
    while s.in_waiting > 0:
        # read every single byte (converted to hex) and add whitespace
        reply += s.read().hex()
        reply += ' '
    # print('reply: ', reply)
    return reply


# convert reply to readable info and split into individual messages
def decode_reply(reply):
    # if no reply, return
    if not reply:
        message = ''
        return message

    while reply:
        mID = reply[0:5] # get the first two bytes as message ID
        header = reply[0:17] # get the first 6 bytes as header
        position = ''
        if mID == '06 00':
            # hardware info, 90 bytes (always including header)
            message = 'hardware info' + reply[17:269]
            length = 90
        elif mID == '12 04':
            message = 'Poscounter'
            length = 12
            position = reply[24:35]
        elif mID == '0b 04':
            message = 'Enccounter'
            length = 12
            position = reply[24:35]
        elif mID == '15 04':
            message = 'Velparams'
            length = 20
        elif mID == '18 04':
            message = 'Jogparams'
            length = 28
        elif mID == '3c 04':
            message = 'GenMoveparams'
            length = 12
        elif mID == '47 04':
            message = 'Moverelparams'
            length = 12
        elif mID == '52 04':
            message = 'Moveabsparams'
            length = 12
        elif mID == '42 04':
            message = 'Homeparams'
            length = 20
        elif mID == '44 04':
            message = 'homed'
            length = 6
        elif mID == '64 04':
            message = 'moved' #move completed
            length = 20
        elif mID == '66 04':
            message = 'stopped'
            length = 20

        else:
            print('not a recogniced message ID:', mID)
            message = ''
            length = 6

        # combine message plus parameter (if more than 6 bytes)
        if length > 6:
            message_params = reply[17:(3*length-1)]
            if flag_debug: print(message, message_params)
        else:
            if flag_debug: print(message)

        # remove the evaluated reply and go on with further replies
        reply = reply.replace(reply[0:3*length], '')

    if position:
        return message, position
    else:
        return message

################################################################################
# CONVERSION FUNCTIONS
################################################################################

# convert an angle in degree to an increment in the requested binary format
def convert_angle(angle_degree):
    # convert angle to encoder counts
    angle_enccnt = int(angle_degree*PRM1_EncCnt)
    # convert to binary
    angle_enccnt_bin = format(angle_enccnt, 'b')
    # fill up to 32 digits with leading zeros
    while len(angle_enccnt_bin) < 32:
        angle_enccnt_bin = '0' + angle_enccnt_bin
    # convert to 4 hex numbers (by first converting to int) AND INVERT sequence
    angle_enccnt_hex = ''
    for n in range(4):
        temp = int(angle_enccnt_bin[n*8:n*8+8], 2)
        angle_enccnt_hex = format(temp, '02X') + ' ' + angle_enccnt_hex
    # print('Degree', angle_degree, '\n', 'EncCnt', angle_enccnt, '\n',
    #       'EncCnt binary', angle_enccnt_bin, '\n', 'EncCnt hex inverted',
    #       angle_enccnt_hex)
    # add leading whitespace, remove trailing whitespace
    angle_enccnt_hex = ' ' + angle_enccnt_hex[:-1]
    return(angle_enccnt_hex)

# convert an enccnt value from hex to a useable angle
# e.g. 'DF A2 02 00' = 90 degree
def convert_enccnt(enccnt):
    encstring = enccnt.split() # separate to list of hex
    encint = 0
    # sum up converted hexvalues times their respective power
    for n in range(4):
        encint = encint + (int(encstring[n], 16) * 256**n)
    angle = round(encint/PRM1_EncCnt, 1)
    return angle

################################################################################
# STAGE FUNCTIONS
################################################################################
# careful, these commands keep running until the stage is done moving!
# absolute movement
def move_abs(s, angle):
    if not s.is_open: print('no serial connection'); return
    command = commands["move_abs_angle"] + convert_angle(angle)
    sendcommand(s, command)
    reply = recvreply(s)
    message = decode_reply(reply)
    while not message == 'moved':
        time.sleep(0.5)
        reply = recvreply(s)
        message = decode_reply(reply)
    if flag_debug: print('movement completed')


#relative movement
def move_rel(s, angle):
    if not s.is_open: print('no serial connection'); return
    command = commands["move_rel_angle"] + convert_angle(angle)
    sendcommand(s, command)
    reply = recvreply(s)
    message = decode_reply(reply)
    while not message == 'moved':
        time.sleep(0.5)
        reply = recvreply(s)
        message = decode_reply(reply)
    if flag_debug: print('movement completed')


# move home
def move_home(s):
    if not s.is_open: print('no serial connection'); return
    sendcommand(s, commands["move_home"])
    reply = recvreply(s)
    message = decode_reply(reply)
    while not message == 'homed':
        time.sleep(0.5)
        reply = recvreply(s)
        message = decode_reply(reply)
    if flag_debug: print('finally homed')


# stop current move: This does NOT interrupt the above movement commands
def stop_move(s):
    if not s.is_open: print('no serial connection'); return
    sendcommand(s, commands["move_stop"])
    reply = recvreply(s)
    message = decode_reply(reply)
    while not message == 'stopped':
        time.sleep(0.5)
        reply = recvreply(s)
        message = decode_reply(reply)
    if flag_debug: print('stopped')


# interruptible movement commands
# absolute movement
def move_abs2(s, angle):
    if not s.is_open: print('no serial connection'); return
    command = commands["move_abs_angle"] + convert_angle(angle)
    sendcommand(s, command)


#relative movement
def move_rel2(s, angle):
    if not s.is_open: print('no serial connection'); return
    command = commands["move_rel_angle"] + convert_angle(angle)
    sendcommand(s, command)


# move home
def move_home2(s):
    if not s.is_open: print('no serial connection'); return
    sendcommand(s, commands["move_home"])


# get position (poscnt) and return as angle
def get_pos_angle(s):
    if not s.is_open: print('no serial connection'); return
    sendcommand(s, commands["req_poscounter"])
    reply = recvreply(s)
    try:
        message, position = decode_reply(reply)
        angle = convert_enccnt(position)
    except:
        message = decode_reply(reply)
        position = ''
        angle = ''
        print('no position found')
    return angle

# get encoder position (enccnt) and return as angle
def get_enc_angle(s):
    if not s.is_open: print('no serial connection'); return
    sendcommand(s, commands["req_enccounter"])
    reply = recvreply(s)
    try:
        message, position = decode_reply(reply)
        angle = convert_enccnt(position)
    except:
        message = decode_reply(reply)
        position = ''
        angle = ''
        print('no position found')
    return angle
