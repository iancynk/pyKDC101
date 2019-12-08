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
# test movement commands (can't be interrupted)
k.move_abs(s, 13)
k.move_rel(s, 10)
k.move_home(s)

# test movement commands (interruptable)
k.move_abs2(s, 13)
k.move_rel2(s, 10)
k.move_home2(s)
k.stop_move(s)

# %% test conversion functions
enccnt = k.convert_angle(90)
angle = k.convert_enccnt('DF A2 02 00')
print('EncCnt:', enccnt, '  Angle:', angle)

# %% ask for position
posangle = k.get_pos_angle(s)
time.sleep(0.5)
encangle = k.get_enc_angle(s)

# %%
k.closestage(s)
