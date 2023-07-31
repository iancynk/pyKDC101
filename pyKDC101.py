#!/bin/usr/python
# %% ---------------------------------------------------------------------------
# imports
import serial
import time
import glob
import sys

# %% ---------------------------------------------------------------------------
# KDC class
class KDC():
    # --------------------------------------------------------------------------
    # PARAMETERS (PRM1-Z8)
    PRM1_EncCnt = 1919.6418578623391 # EncCnt per degree
    PRM1_sf_vel = 42941.66 # scaling factor velocity (deg/s)
    PRM1_sf_acc = 14.66 # scaling factor acceleration (deg/s^2)
    
    # set this for more output info
    DEBUG = False
    
    # POS = EncCnt x Pos
    # VEL = EncCnt x T x 65536 x Vel
    # ACC = EncCnt x T^2 x 65536 x Acc
    # where T = 2048/6e6 (KDC101)
    # ==> VEL (PRM1-Z8) = 6.2942e4 x Vel
    # ==> ACC (PRM1-Z8) = 14.6574 x Acc
    
    def __init__ (self, port='', SN='', DEBUG=False) :
        self.ser = None
        # open serial connection
        if port:
            # with port if port is given
            self.openstage(port=port)
        elif SN:
            # with serial number if given
            self.openstage(SN=SN)
        else:
            # otherwise just pick the first found port
            self.openstage()
        self.identify()
        # more output info
        if DEBUG: self.DEBUG = True
    
    
    def __str__(self):
        return f"Is a serial instance of a KDC controller."
        self.get_info()
    
    # --------------------------------------------------------------------------
    # COMMANDS
    cmds = {
        "req_info":         "05 00 00 00 50 01", # get hardware info
        "req_enccounter":   "0A 04 01 00 50 01", # get enccounter count
        "req_poscounter":   "11 04 01 00 50 01", # get position count
        "req_velparams":    "14 04 01 00 50 01", # get the velocity parameters
        "req_jogparams":    "17 04 01 00 50 01", # get jog parameters
        "req_mmiparams":    "21 05 01 00 50 01", # get settings for top panel wheel
        "identify":         "23 02 00 00 50 01", # flashes the screen
        "req_genmoveparams":"3B 04 01 00 50 01", # get backlash settings
        "req_homeparams":   "41 04 01 00 50 01", # get home parameters
        "move_home":        "43 04 01 00 50 01", # move home
        "move_rel_set":     "45 04 06 00 D0 01 01 00", # set relative movement parameter (+4 byte)
        "req_moverelparams":"46 04 01 00 50 01", # get rel movement parameters
        "move_rel":         "48 04 01 00 50 01", # move predefined relative
        "move_rel_angle":   "48 04 06 00 D0 01 01 00", # move rel by angle (+4 byte)
        "move_abs_set":     "50 04 06 00 D0 01 01 00", # set absolute movement parameter (+4 byte)
        "req_moveabsparams":"51 04 01 00 50 01", # get abs movement parameters
        "move_abs":         "53 04 01 00 50 01", # move predefined absolute
        "move_abs_angle":   "53 04 06 00 D0 01 01 00", # move predefined absolute (+4 byte)
        "move_velocity_f":  "57 04 01 02 50 01", # move at fixed speed forward
        "move_velocity_b":  "57 04 01 01 50 01", # move at fixed speed backward
        "move_stop":        "65 04 01 00 50 01", # stop movement
        "move_jog_forward": "6A 04 01 02 50 01", # jog forward
        "move_jog_backward":"6A 04 01 01 50 01" # jog backward
    }
    # --------------------------------------------------------------------------
    # CONVERSION FUNCTIONS
    
    def convert_angle(self, angle_degree):
        """ convert an angle in degree to an increment in the requested binary format"""
        # convert angle to encoder counts
        angle_enccnt = int(angle_degree*self.PRM1_EncCnt)
        # convert to bytes (e.g. b'\xee\x76\x01\x00' (50 degree))
        angle_enccnt_bytes = angle_enccnt.to_bytes(4, byteorder='little', signed=True)
        # convert to uppercase hex string with space at the beginning and in between
        angle_enccnt_hex = ''
        for n in range(4):
            angle_enccnt_hex = f"{angle_enccnt_hex} {angle_enccnt_bytes[n]:02X}"
        if self.DEBUG: print(angle_enccnt, angle_enccnt_bytes.hex(), angle_enccnt_hex)
        return angle_enccnt_hex
    
    
    def convert_enccnt(self, enccnt):
        """ convert an enccnt value from hex to a useable angle
        e.g. ' EE 76 01 00' = 50 degree
        """
        # convert hex string to bytes, e.g. ' EE 76 01 00' to b'\xee\x76\x01\x00'
        enccnt_bytes = bytes.fromhex(enccnt)
        # convert bytes to signed integer
        enccnt_int = int.from_bytes(enccnt_bytes, byteorder='little', signed=True)
        # convert enccnts to angle
        angle = round(self.enccnt_int/self.PRM1_EncCnt, 1)
        if self.DEBUG: print(enccnt_bytes.hex(), enccnt_int, angle)
        return angle
    
    
    def hexstr_to_int(self, value_hex, signed=False):
        """convert voltage/frequency value from hex to a useable integer"""
        # convert hex string to bytes, e.g. ' EE 76 01 00' to b'\xee\x76\x01\x00'
        value_bytes = bytes.fromhex(value_hex)
        # convert bytes to signed integer, eg 'e8 03' becomes 1000 [mV/Hz]
        value_int = int.from_bytes(value_bytes, byteorder='little', signed=signed) 
        if self.DEBUG: print(value_bytes.hex(), value_int, )
        return value_int
    
    
    def int_to_hexstr(self, value_num:float, signed=True, bytenum=2):
        """ convert an integer voltage/frequency to hex strings for transmitting to KLC controller"""
        value_int = int(value_num)
        # convert to bytes (e.g. b'\xee\x76\x01\x00')
        value_bytes = value_int.to_bytes(4, byteorder='little', signed=signed)
        # convert to hex string with space at the beginning and in between
        value_hex = ''
        for n in range(bytenum):
            value_hex = f"{value_hex} {value_bytes[n]:02X}"
        if self.DEBUG: print(value_bytes.hex(), value_hex)
        return value_hex
    
    
    def hexstr_to_ascii(self, hexstr):
        """ convert a string of hex values to ASCII characters
        only used to read out the model name
        """
        # remove whitespace
        hexstr = "".join(hexstr.split())
        asciistr = ""
        for i in range(0, len(hexstr), 2):
            # extract two characters from hex string
            part = hexstr[i : i + 2]
            # change it into base 16 and typecast as character
            ch = chr(int(part, 16))
            asciistr += ch
        # strip zeros
        asciistr = asciistr.strip('\x00')
        return asciistr
    
    
    # --------------------------------------------------------------------------
    # SERIAL FUNCTIONS
    
    def openstage(self, port='', SN = ''):
        """create a serial connection with the recommended parameters to either the defined port
        or to a specified serial number SN
        """
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE # number of stop bits
        self.ser.timeout = 5
        self.ser.rtscts = True # enable hardware (TRS/CTS) flow control
        
        if not port:
            # find available ports depending on operating system
            if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                ports = glob.glob('/dev/serial/by-id/*Thorlabs_Brushed_Motor_Controller*' + SN + '*')
                if not ports:
                    print('selected SN', SN, 'not available')
                    available_ports = glob.glob('/dev/serial/by-id/*Thorlabs_Brushed_Motor_Controller*')
                    print('available SNs:')
                    print(available_ports)
            elif sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            else:
                raise EnvironmentError('Unsupported platform')
        else:
            ports = [port]
        
        # try to open the ports until one works
        if not ports:
            print('no serial port selected, aborting')
            self.ser = None
            return
        
        # try to open the ports until one works
        for port in ports:
            try:
                print('opening port', port)
                self.ser.port = port
                self.ser.open()
                time.sleep(0.1)
                break
            except:
                print('failed at port', port)
                pass
        
        if self.ser.is_open:
            print('is open: ', self.ser.is_open)
        else:
            print('could not find any serial port')
        return
    
    
    def closestage(self):
        # close serial connection
        if not self.ser.is_open: print('no serial connection'); return
        self.ser.close()
        print('is open: ', self.ser.is_open)
    
    
    def sendcmd(self, string):
        # send a command
        if not self.ser.is_open: print('no serial connection'); return
        splitstring = string.split() # separate in to list of hex values
        cmd = [int(str, 16) for str in splitstring] # convert to integer
        if self.DEBUG: print('sending command: ', cmd)
        self.ser.write(bytes(cmd)) # send integer in binary format to stage
    
    
    def recvreply(self):
        # receive and parse reply
        if not self.ser.is_open: print('no serial connection'); return
        time.sleep(0.04) # has to be at least 20 ms to work
        reply = ''
        while self.ser.in_waiting > 0:
            # read every single byte (converted to hex) and add whitespace
            reply += self.ser.read().hex()
            reply += ' '
        # print('reply: ', reply)
        return reply
    
    
    def decodereply(self, reply):
        # convert reply to readable info and split into individual messages
        # if no reply, return
        if not reply:
            message = ''
            return message
        
        mID = reply[0:5] # get the first two bytes as message ID
        header = reply[0:17] # get the first 6 bytes as header
        position = ''
        if mID == '06 00':
            # hardware info, 90 bytes (always including header)
            message = 'hardware info'
            length = 84
        elif mID == '0b 04':
            message = 'Enccounter'
            length = 6
            position = reply[24:35]
        elif mID == '12 04':
            message = 'Poscounter'
            length = 6
            position = reply[24:35]
        elif mID == '15 04':
            message = 'Velparams'
            length = 14
        elif mID == '18 04':
            message = 'Jogparams'
            length = 22
        elif mID == '22 05':
            message ='MMI parameters'
            length = 36
        elif mID == '3c 04':
            message = 'GenMoveparams'
            length = 6
        elif mID == '42 04':
            message = 'Homeparams'
            length = 14
        elif mID == '44 04':
            message = 'homed'
            length = 0
        elif mID == '47 04':
            message = 'Moverelparams'
            length = 6
        elif mID == '52 04':
            message = 'Moveabsparams'
            length = 6
        elif mID == '64 04':
            message = 'moved' #move completed
            length = 14
        elif mID == '66 04':
            message = 'stopped'
            length = 14
        else:
            print('not a recogniced message ID:', mID)
            message = ''
            length = 0
        
        # combine message plus parameter (if more than 6 bytes)
        if length > 0:
            message_params = reply[18:18+(3*length-1)]
            return message, message_params
        else:
            return message
    
    
    # --------------------------------------------------------------------------
    # CONTROLLER INFO/FUNCTIONS
    
    def identify(self):
        """flash display to indicate which controller is addressed"""
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds['identify'])
    
    
    def get_serial(self):
        """get controller serial number"""
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds['req_info'])
        reply = self.recvreply()
        message, hwinfo = self.decodereply(reply)
        sn = self.hexstr_to_int(hwinfo[0:11]) # 4 byte serial number
        return sn
    
    
    def get_info(self):
        """get hardware information, see APT protocol page 46"""
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds['req_info'])
        reply = self.recvreply()
        message, hwinfo = self.decodereply(reply)
        sn = self.hexstr_to_int(hwinfo[0:11]) # 4 byte serial number
        model_number = self.hexstr_to_ascii(hwinfo[12:35]) # 8 byte alphanumeric model number
        hw_type = self.hexstr_to_int(hwinfo[36:41]) # 2 byte describes type of hardware
        fw_minor = self.hexstr_to_int(hwinfo[42:44]) # minor firmware version (1 byte)
        fw_interim = self.hexstr_to_int(hwinfo[45:47]) # interim firmware version (1 byte)
        fw_major = self.hexstr_to_int(hwinfo[48:50]) # major firmware version (1 byte)
        fw_reserved = self.hexstr_to_int(hwinfo[51:53]) # always 00
        hw_version = self.hexstr_to_int(hwinfo[-17:-12]) # 2 byte hardware version
        hw_mod_state = self.hexstr_to_int(hwinfo[-11:-6]) # 2 byte hardware modification state
        n_channels = self.hexstr_to_int(hwinfo[-5:]) # 2 byte number of channels
        print(f"serial number:\t\t{sn}\nmodel number:\t\t{model_number}\nfirmware version:\t{fw_major}.{fw_interim}.{fw_minor}")
        print(f"hardware type:\t\t{hw_type}\nhardware version:\t{hw_version}")
        print(f"modification state:\t{hw_mod_state}\nnumber of channels:\t{n_channels}")
    
    
    def get_mmi_params(self):
        """get settings for top panel and wheel"""
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds['req_mmiparams'])
        reply = self.recvreply()
        message, mmiinfo = self.decodereply(reply)
        chan_ident = self.hexstr_to_int(mmiinfo[0:5])
        JSMode = self.hexstr_to_int(mmiinfo[6:11])
        JSMaxVel = self.hexstr_to_int(mmiinfo[12:23])
        JSAccn = self.hexstr_to_int(mmiinfo[24:35])
        DirSense = self.hexstr_to_int(mmiinfo[36:41])
        PreSetPos1 = self.hexstr_to_int(mmiinfo[42:53])
        PreSetPos2 = self.hexstr_to_int(mmiinfo[54:65])
        DispBrightness = self.hexstr_to_int(mmiinfo[66:71])
        DispTimeout = self.hexstr_to_int(mmiinfo[72:77])
        DispDimLevel = self.hexstr_to_int(mmiinfo[78:83])
        print(f"JSMode: {JSMode}\tJSMaxVel: {JSMaxVel}\tJSAccn: {JSAccn}\tDirSense:{DirSense}")
        print(f"Preset Positions:\t{PreSetPos1}\t{PreSetPos2}")
        print(f"Display Parameters: {DispBrightness}, {DispTimeout}, {DispDimLevel}")
    
    
    def get_disp_params(self):
        """get settings for display"""
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds['req_mmiparams'])
        reply = self.recvreply()
        message, mmiinfo = self.decodereply(reply)
        DispBrightness = self.hexstr_to_int(mmiinfo[66:71])
        DispTimeout = self.hexstr_to_int(mmiinfo[72:77])
        DispDimLevel = self.hexstr_to_int(mmiinfo[78:83])
        print(f"Display Brightness: {DispBrightness}%")
        if DispTimeout == 0:
            print(f"Display dimming timeout: never")
        else:
            print(f"Display dimming timeout: {DispTimeout}min")
            print(f"Display Dim level: {DispDimLevel}/10")
    
    # --------------------------------------------------------------------------
    # STAGE FUNCTIONS
    # careful, these cmds keep running until the stage is done moving!
    # they are waiting for a reply that the motor has reached its designated position
    
    def move_abs_wait(self, angle):
        # absolute movement
        if not self.ser.is_open: print('no serial connection'); return
        cmd = self.cmds["move_abs_angle"] + self.convert_angle(angle)
        self.sendcmd(cmd)
        reply = self.recvreply()
        message = self.decodereply(reply)
        while not message == 'moved':
            time.sleep(0.5)
            reply = self.recvreply()
            message = self.decodereply(reply)
        if self.DEBUG: print('movement completed')
    
    
    def move_rel_wait(self, angle):
        # relative movement
        if not self.ser.is_open: print('no serial connection'); return
        cmd = self.cmds["move_rel_angle"] + self.convert_angle(angle)
        self.sendcmd(cmd)
        reply = self.recvreply()
        message = self.decodereply(reply)
        while not message == 'moved':
            time.sleep(0.5)
            reply = self.recvreply()
            message = self.decodereply(reply)
        if self.DEBUG: print('movement completed')
    
    
    def move_home_wait(self):
        # move home
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds["move_home"])
        reply = self.recvreply()
        message = self.decodereply(reply)
        while not message == 'homed':
            time.sleep(0.5)
            reply = self.recvreply()
            message = self.decodereply(reply)
        if self.DEBUG: print('finally homed')
    
    
    # --------------------------------------------------------------------------
    # interruptible movement cmds
    
    def move_abs(self, angle):
        # absolute movement
        if not self.ser.is_open: print('no serial connection'); return
        cmd = self.cmds["move_abs_angle"] + self.convert_angle(angle)
        self.sendcmd(cmd)
    
    
    def move_rel(self, angle):
        # relative movement
        if not self.ser.is_open: print('no serial connection'); return
        cmd = self.cmds["move_rel_angle"] + self.convert_angle(angle)
        self.sendcmd(cmd)
    
    
    def move_home(self):
        # move home
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds["move_home"])
    
    
    def stop_move(self):
        # stop current move: This does NOT interrupt the above movement cmds
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds["move_stop"])
        reply = self.recvreply()
        message = self.decodereply(reply)
        while not message == 'stopped':
            time.sleep(0.5)
            reply = self.recvreply()
            message = self.decodereply(reply)
        if self.DEBUG: print('stopped')
    
    
    # --------------------------------------------------------------------------
    # read position of stage
    
    def get_pos_angle(self):
        # get position (poscnt) and return as angle
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds["req_poscounter"])
        reply = self.recvreply()
        try:
            message, position = self.decodereply(reply)
            angle = self.convert_enccnt(position)
        except:
            position = ''
            angle = ''
            print('no position found')
        return angle
    
    
    def get_enc_angle(self):
        # get encoder position (enccnt) and return as angle
        if not self.ser.is_open: print('no serial connection'); return
        self.sendcmd(self.cmds["req_enccounter"])
        reply = self.recvreply()
        try:
            message, position = self.decodereply(reply)
            angle = self.convert_enccnt(position)
        except:
            position = ''
            angle = ''
            print('no position found')
        return angle

# EOF --------------------------------------------------------------------------