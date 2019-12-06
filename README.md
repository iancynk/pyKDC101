# pyKDC101
Functions and examples to control Thorlabs KDC101 through serial for Python and MATLAB.
Here, the controller is used to move a Thorlabs rotation stage (PRM1-Z8).
The interfaces offered by Thorlabs do not work for unix systems (afaik). Therefore these functions use the low-level serial functionality that is documented in the `APT_Communications_Protocol.pdf`.

## Status
This is under development but I hope it will be helpful for fellow linux-users

## Commands
There are a lot of tricks in getting this to work. I try to document most of it in the code.

## MATLAB
I created basic functionalities to test it until it worked but then switched to Python. So you can use the `serial_KDC101.m`-file as guideline to build your own sequence

## Python
Working on it.
