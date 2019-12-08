################################################################################
# IMPORTS
################################################################################
import serial
import serial.tools.list_ports
import time
import glob
import sys

import pyKDC101 as k
################################################################################
# CODE
################################################################################
# %%
# connect stage and let display flash
s = k.openstage()
k.sendcommand(s, k.commands["identify"])
time.sleep(0.1)

# %%
# test some commands
k.move_abs(s, 13)
k.move_rel(s, 10)
k.move_home(s)
time.sleep(2)
k.sendcommand(s, commands["move_stop"])

# %% test conversion functions
enccnt = k.convert_angle(90)
angle = k.convert_enccnt('DF A2 02 00')
print('EncCnt:', enccnt, '  Angle:', angle)

# %%
k.sendcommand(s, commands["req_poscounter"])
reply = k.recvreply(s)
sendcommand(s, commands["req_enccounter"])
reply = k.recvreply(s)
k.decode_reply(reply)

# %%
k.closestage(s)
