################################################################################
# This code gives basic examples how to use the pyKDC101 library
# scripted by ian cynk (ian.cynk@posteo.eu) 2019
################################################################################
# It doesn't stop being magic just because you know how it works.
# — Terry Pratchett, The Wee Free Men
################################################################################
# IMPORTS
################################################################################
import time

import pyKDC101 as k
################################################################################
# CODE
################################################################################
# %%
# connect stage
s = k.openstage()

# %%
# to directly send commands you can use the following command structure
# let the display flash
k.sendcommand(s, k.commands["identify"])

# %%
# to use more comfortable functions, the following functions are implemented
# movement commands (can't be interrupted)
k.move_abs(s, 13) # move to 13 degree
k.move_rel(s, 10) # move plus 10 degree
k.move_home(s)

# %%
# movement commands (interruptable)
k.move_abs2(s, 13)
k.move_rel2(s, 10)
k.move_home2(s)
k.stop_move(s)

# %%
# conversion functions to make sense of the hex blobs
enccnt = k.convert_angle(90)
print('EncCnt:', enccnt)
angle = k.convert_enccnt('DF A2 02 00')
print('Angle:', angle)

# %%
# find current position (encoder being fixed, position could be defined)
posangle = k.get_pos_angle(s)
time.sleep(0.5)
encangle = k.get_enc_angle(s)

# %%
# disconnect stage
k.closestage(s)
