# pyKDC101
Functions and examples to control Thorlabs KDC101 through serial.
Mainly for Python, additionally some basic usage for MATLAB.
Here, the controller is used to move a Thorlabs rotation stage (PRM1-Z8).
The interface offered by Thorlabs does not work for unix systems (afaik). Therefore these functions use the low-level serial functionality that is documented in [APT_Communications_Protocol.pdf](DOC/APT_Communications_Protocol.pdf).

## Status
This is under development but I hope it will be helpful for fellow linux-users. Comments and suggestions highly welcome.

## Python
Offers the most used commands (*move here*, *move there*, *go home*) in a simple structure, shown in `example.py`. Additionally offers a lower-level command structure in which you can send most basic serial commands and read the reply.

## MATLAB
I created basic functionalities to test it until it worked but then switched to Python. Still, MATLABthusiasts may find the essential bits in the [matlab_KDC101.m](DOC/matlab_KDC101.m)-file as guideline to build their own command structure.

## Commands
There are a lot of tricks in getting this to work. I try to document most of it in the code.

### Communication basics
* The address '01' is the host (usually the computer)
* The address '50' refers to generic USB device
* When using commands with parameters, '50' needs to be OR'd with '80' leading to 'D0'
* While we create the commands in hex, they are converted to integers and sent in binary format
* If you are not familiar with serial: be advised to add a delay between sending a command and receiving data (e.g. 50 ms)

### Angle to EncCnt conversion
* The position parameter structure is "weird":
* You have 4 Bytes to encode a number of increments, e.g. "64 00 10 00"
* To get the number, you have to flip the byte sequence and then convert it:
* 00 10 00 64 = 0000 0000  0001 0000  0000 0000  0110 0100 =
* 2^20 + 2^6 + 2^5 + 2^2 = 1048676
* Divide this by EncCnt/deg yields rotation in degree: 1048676/1920 = 546 degree

* Hence to calculate the needed parameter, you take your angle, multiply it with
* the EncCnt/deg, convert it to binary (filling up to 4 bytes). Then you
* flip the sequence of the four bytes.

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgement
You're welcome!
