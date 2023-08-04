#!/bin/usr/python
# -----------------------------------------------------------------------------
# This code gives basic examples how to use the pyKDC101 library
# scripted by ian cynk (ian.cynk@posteo.eu) 2019
# updated 2023
# %% --------------------------------------------------------------------------
# imports
import time
# if local file:
from pyKDC101 import KDC
# if installed via pip
from pyKDC101.pyKDC101 import KDC

# %% --------------------------------------------------------------------------
# connect stage
kdc = KDC.openstage()  # open first port found
# kdc = KDC.openstage(port='/dev/ttyUSB0')  # open with specified port
# kdc = KDC.openstage(SN='12345678')  # open with specified serial number

# let the display flash
kdc.identify()

# %% --------------------------------------------------------------------------
# get info
kdc.get_info()
kdc.get_serial()
kdc.get_mmi_params()

# %% --------------------------------------------------------------------------
# movement commands (can't be interrupted)
kdc.move_abs_wait(13) # move to 13 degree
kdc.move_rel_wait(10) # move plus 10 degree
kdc.move_home_wait()

# %% --------------------------------------------------------------------------
# movement commands (interruptable)
kdc.move_abs(13)
kdc.move_rel(10)
kdc.move_home()
kdc.stop_move()

# %% --------------------------------------------------------------------------
# conversion functions to make sense of the hex blobs

enccnt = kdc.convert_angle(90)
print('EncCnt:', enccnt)
angle = kdc.convert_enccnt('DF A2 02 00')
print('Angle:', angle)

# %% --------------------------------------------------------------------------
# find current position (encoder being fixed, position could be defined)

posangle = kdc.get_pos_angle()
time.sleep(0.5)
encangle = kdc.get_enc_angle()
print(posangle, encangle)

# %% --------------------------------------------------------------------------
# disconnect stage
kdc.closestage()
