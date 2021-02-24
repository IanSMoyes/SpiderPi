#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright HiWonder.hk
# Further development by ians.moyes@gmail.com
# Translation by Google

# Library to control the Pan & Tilt Head

import time # Standard time & date functions
from PWMServoClass import PWM_Servo # Class to control a PWM Servo

# PWM servo parameters
num_PWM_servos = 2 # Number of servos of this type on the robot
PWM_offsets = (0,0) # The PWM servos have no internal memory so the offsets have to be set here

pan = 0 # Environment variables
tilt = 1
PTHead = ()

# 9克舵机的转动范围0~180度，对应的PWM值为 500~2500
# The rotation range of 9g PTHead is 0~180 degrees = PWM 500~2500 pulses

# Create the servo objects on channels 7 & 8 on the expansion board
# PTHead rotation needs to be constrained to prevent clashing with the hexapod chassis
def init(pi):
    global PTHead
    pan_servo = PWM_Servo(pi, 5, min_width=800, max_width=2200, offset=PWM_offsets[1], control_speed=True)   # 8
    tilt_servo = PWM_Servo(pi, 6, min_width=1200, max_width=2000, offset=PWM_offsets[0], control_speed=True) # 扩展板上的7

    # 初始化云台舵机 Initialize Pan & Tilt Head
    PTHead = (pan_servo, tilt_servo) # Save Pan & Tilt Head objects

def setPWMServo(id, pos, tim=0): # Move a servo
    PTHead[id].setPosition(pos, tim)

def getPWMServo(id): # Return estimated servo position
    return PTHead[id].Position

def setPWMOffset(id, offset): # Calibaration offset
    PTHead[id].Offset = offset # Set calibration offset

def getPMWOffset(id): # Return servo calibration offset
    return PTHead[id].Offset

def setPTHpos(pan_pos, tilt_pos, tim=0): # Set the PTHead to given positions
    setPWMServo(pan, pan_pos, tim)
    setPWMServo(tilt, tilt_pos, tim)

def setPTHcentre(): # Return the PTHead to default positions
    setPWMServo(pan, PTHead[pan].default_pos)
    setPWMServo(tilt, PTHead[tilt].default_pos)

def getPTHpos(): # Return the estimated head position as a 2 element tuple
    return (PTHead[pan].Position, PTHead[tilt].Position)

def setPTHoffsets(offsets): # Calibaration offset
    setPWMOffset(pan,offsets[pan]) # Set calibration offset
    setPWMOffset(tilt, offsets[tilt]) # Set calibration offset

def getPTHoffsets(): # Return the head PWM_offsets as a 2 element tuple
    return (PTHead[pan].Offset, PTHead[tilt].Offset)

if __name__ == '__main__':
    import pigpio # Standard Raspberry Pi GPIO library
    pi = pigpio.pi() # Create a Raspberry Pi object
    init(pi) # Create Pan & Tilt Head
    
    print("Pan & Tilt Head motion tests")
    setPWMServo(pan, PTHead[pan].Min, 500)
    time.sleep(2)
    print("Pan position " + str(getPWMServo(pan)))
    setPWMServo(tilt, PTHead[tilt].Min, 500)
    time.sleep(2)
    print("Tilt position " + str(getPWMServo(tilt)))
    setPWMServo(pan, PTHead[pan].Max, 500)
    time.sleep(2)
    print("Pan position " + str(getPWMServo(pan)))
    setPWMServo(tilt, PTHead[tilt].Max, 500)
    time.sleep(2)
    print("Tilt position " + str(getPWMServo(tilt)))

    setPTHpos(PTHead[pan].Min, PTHead[tilt].Min, tim=500)
    time.sleep(2)
    print(getPTHpos())
    setPTHpos(PTHead[pan].Max, PTHead[tilt].Max, tim=500)
    time.sleep(2)
    print(getPTHpos())
    setPTHpos(PTHead[pan].Min, PTHead[tilt].Max, tim=500)
    time.sleep(2)
    print(getPTHpos())
    setPTHpos(PTHead[pan].Max, PTHead[tilt].Min, tim=500)
    time.sleep(2)
    print(getPTHpos())

    print ("Returning to default positions")
    setPTHcentre()
    time.sleep(2)
    print(getPTHpos())
    print("Pan & Tilt Head mobility tests complete!")
