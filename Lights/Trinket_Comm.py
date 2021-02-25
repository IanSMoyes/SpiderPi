#!/usr/bin/python3
# encoding: utf-8
# Copyright ians.moyes@gmail.com

# Library to communicate between the Raspberry Pi & the Adafruit TrinketM0
# via the Raspberry Pi expansion board

import serial # Standard library to define serial ports
import time # Standard library of time, diary & calendar functions
from random import random

TRINKET_FRAME_HEADER = b'\x25\x25' # Define data frame header

# Set up UART port
UART = serial.Serial('/dev/ttyAMA0', 115200, timeout = 1.0, rtscts = 0)

def checksum(buf):
    '''Calculate the checksum
    :param buf: data frame to be transmitted
    :return: checksum to be appended
    '''
    sum = 0x00
    for b in buf:  # scan the buffer
        sum += b # sum the contents of the buffer
    sum = ~sum  # Negate the sum (change the sign)
    return sum & 0xff # return the 8 least significant bits

def TrinketM0_write_data(id, colour):
    '''
    Send to the TrinketM0 via the Raspberry Pi expansion board
    :param id: LED ID to be addressed 0-11 = face lights, 12 = head/tail lights
    :param colour: the colour, or direction codes to be transmitted
    :return: Error code or True = Success
    '''

    buf = bytearray()

    buf.append(id) # Start with the LED ID

    for i in colour: buf.append(i) # Append the colour data

    buf.append(checksum(buf)) # Append the checksum

    frame = bytearray(TRINKET_FRAME_HEADER) + buf  # Prepend the data frame header

    frame += b'\n' # So that you can send a line end designated line at a time

    print(frame)
    UART.write(frame)  # Transmit data frame over UART
    return True # Tell the World how clever you were

while True :
    id = int(random()*11.49)
    colour_code = ()
    if id == 12:
        colour_code += (int(random() * 2.49), )
        colour_code += (int(random() * 3.49), )
        colour_code += (0, )
    else:
        colour_code += (255, )
        colour_code += (int(random() * 255.49), )
        colour_code += (int(random() * 255.49), )
    # Transmit data
    TrinketM0_write_data(id, colour_code)
    time.sleep(0.05)
