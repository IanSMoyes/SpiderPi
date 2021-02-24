#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# Copyright HiWonder.hk
# Further development by ians.moyes@gmail.com
# Translation by Google

# Library to control the hexapod

# lower servo values on the port side lead to
# forward positions at the shoulder
# Lifting the knee
# Dropping the ankle

# Lower servo values on the starboard side lead to
# Rearward positions at the shoulder
# Dropping the knee
# Lifting the ankle

# X axis is front to back
# Y axis is side to side
# Z axis is vertical

import math # Standard library of mathematical functions
import time # Standard library of time & date functions
import pigpio # Standard Raspberry Pi GPIO library
import PTHeadCtrl as PTH # Library to define & control a Pan & Tilt Head
from LegClass import Leg # Class to define and control a leg with 3 egrees of freedom (DoF)
# import HCSR04 # Library to control ultrasonic sensor
# import MPU950 # Library to read MPU9250/BM80 IMU

# Define the hexapod
pi = pigpio.pi() # Create a Raspberry Pi object
SpiderPi = () # Create a tuple to contain the hexapod
for id in range(6): # Add 6 legs
    SpiderPi +=(Leg(pi, id), )
PTH.init(pi) # Add a head
# HCSR04.init(pi) # Initialise ultrasonic sensor
# MPU92250.init(pi) # Initialise inertial measurement sensor

# Define names for the legs
leg_names = ("Port rear", "Port centre", "Port front", "Starboard rear", "Starboard centre", "Starboard front")
port_rear = 0
port_centre = 1
port_front = 2
sboard_rear = 3
sboard_centre = 4
sboard_front = 5

# Stance variables (inverse kinematics X, Y, Z coordinates)
stand_pos = (0, 100, 70) # Initial standing position
sit_pos = (0, 100, 20) # Belly flop
lift_pos = (0, 100, 40) # Legs lifted
tall_pos = (0, 100, 120) # Stand tall

def forward_step(leg, factor=1, tim=2000):
    '''
    Causes the leg to take a step
    :param: factor: Introduce step stretching
    :param: speed: How long the step should take, in milliseconds
    :return:
    '''
    global SpiderPi

    AEP = (100*factor,100,70) # (Anterior Extremity Position). Beginning of the stance phase
    PEP = (-100,100,70) # (Posterior Extremity Position). End of the stance phase
    PSP = (-50,100,40) # (Posterior Swing Position). 1/3 of the way through the swing phase
    ASP = (50,100,40) # (Anterior Swing Position). 2/3 of the way through the swing phase

    phase = leg % 2 # Even legs move forward, odd legs move back

    if phase == 0:
        SpiderPi[leg].pos = (inverse_kin(leg, PEP), tim * 0.601)
        SpiderPi[leg].pos = (inverse_kin(leg, PSP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, ASP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, AEP), tim * 0.133)
    else:
        SpiderPi[leg].pos = (inverse_kin(leg, ASP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, AEP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, PEP), tim * 0.601)
        SpiderPi[leg].pos = (inverse_kin(leg, PSP), tim * 0.133)

def backward_step(leg, factor=1, tim=2000):
    '''
    Causes the leg to take a step back
    :param: factor: Introduce step stretching
    :param: speed: How long the step should take, in milliseconds
    :return:
    '''
    global SpiderPi

    AEP = (100,100,70) # (Anterior Extremity Position). Beginning of the stance phase
    PEP = (-100*factor,100,70) # (Posterior Extremity Position). End of the stance phase
    PSP = (-50,100,40) # (Posterior Swing Position). 1/3 of the way through the swing phase
    ASP = (50,100,40) # (Anterior Swing Position). 2/3 of the way through the swing phase

    phase = leg % 2 # Even legs move forward, odd legs move back

    if phase == 0:
        SpiderPi[leg].pos = (inverse_kin(leg, AEP), tim * 0.601)
        SpiderPi[leg].pos = (inverse_kin(leg, ASP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, PSP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, PEP), tim * 0.133)
    else:
        SpiderPi[leg].pos = (inverse_kin(leg, PSP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, PEP), tim * 0.133)
        SpiderPi[leg].pos = (inverse_kin(leg, AEP), tim * 0.601)
        SpiderPi[leg].pos = (inverse_kin(leg, ASP), tim * 0.133)

def load():
    '''
    Loads all of the servos in the hexapod
    :param:
    :return:
    '''
    global SpiderPi # Import the hexapod

    for leg in range(6): # Scan the legs
        SpiderPi[leg].load=1 # Load them

def unload():
    '''
    Unloads all of the servos in the hexapod
    :param:
    :return:
    '''
    global SpiderPi # Import the hexapod

    for leg in range(6): # Scan the legs
        SpiderPi[leg].unload # Unload them

def trigger():
    '''
    Triggers hexapod movement
    :param:
    :return: True = success or error code
    '''

    global SpiderPi # Import the hexapod

    for leg in range (6): # Scan the legs
        SpiderPi[leg].trigger # Trigger the movement

def diag():
    '''
    Report hexapod status
    :param:
    :return: Multi-level tuple full of parameters
    '''
    global SpiderPi # Import the hexapod

    print("Hexapod under test.") # Print the title

    results = () # Create empty tuple
    for leg in range(6): # Scan the legs
            print(leg_names[leg], "leg") # Print the legs name
            result = (SpiderPi[leg].leg_state,) # Collect data about each leg
            print(result)
            results += result
    return results
    
if __name__ == '__main__':

    print(diag())
