#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# Copyright HiWonder.hk
# Further development by ians.moyes@gmail.com
# Translation by Google

# Library to control the hexapod using reverse kinematics of 

# lower servo values on the port side lead to
# forward positions at the shoulder
# Lifting the knee
# Dropping the ankle
# Lower servo values on the starboard side lead to
# Rearward positions at the shoulder
# Dropping the knee
# Lifting the ankle

import math # Standard library of mathematical functions
import time # Standard library of time & date functions
from LegClass import Leg # Class to define & control a hexapod leg with 3 degrees of freedom
# import PTHeadCtrl as PTH # Library to define & control a Pan & Tilt Head

SpiderPi = ()
leg_names = ("Port rear", "Port centre", "Port front", "Starboard rear", "Starboard centre", "Starboard front") 

# Define hexapod
def create_hexapod(): # Ceate the hexapod from 6 legs @ a head
    global SpiderPi # Make sure you can access the hexapod from anywhere in the code

    for id in range(6):
        SpiderPi += (Leg(id),) # Add 6 legs. 0 indexed

    PTH.inithead() # Create the pan & tilt head

    time.sleep(1) # Pause until the hexapod finishes

# Stance variables
default_pos = (100,100,-70) # Initial stnding position
sit_pos = (100.0, 100.0, 20.0) # Belly flop
lift_pos = (100, 100, -40) # Legs lifted
tall_pos = (100, 100, -120) # Stand tall

def standby(leg, position, tim):
    '''
    输入腿的编号和腿的足端坐标，控制腿的运动
    Enter the number of the leg and the coordinates of the foot to control the movement of the leg
    param:leg: 0~5
    param: position:数组，存放足端的坐标 Tuple to store the coordinates of the foot (X, Y, Z)
    param: tim: 运行该动作的速度 time to destination
    '''

    global SpiderPi # Bring the hexapod with us
    
    angle = () # Angles of the 3 elements of inverse kinematics
    output = [] # new shoulder, knee & ankle servo positions

    # Lengths of the 3 elements of inverse kinemetics
    thigh = 44.60
    calf = 75.00
    foot = 126.50

    factor = 180 / math.pi / 0.24 # Cnvert degrees to radians

    angle += (math.atan(position[1]/position[0]),) # anti tangent (Y / X)
    # Append shoulder joint angle

    L = position[1] / math.sin(angle[0]) # Y / sine (shoulder angle)

    temp = (position[2] ** 2) + ((L - thigh) ** 2) # Z squared + (L - thigh length ) squared

    ft = math.sqrt(temp) # square root of temp

    a = math.atan(position[2] / (L - thigh)) # anti tangent (Z / (L - thigh))

    b = math.acos(((calf ** 2) + (ft ** 2) - (foot ** 2)) / (2 * calf * ft))

    angle += ((a + b),) # Knee joint angle

    # Ankle joint angle
    angle += (math.acos(((ft ** 2) - (calf ** 2) - (foot ** 2)) / (2 * calf * foot)),)

    if leg < 3: # Port side of the hexapod
        output += (int(313 + angle[0] * factor), )
        output += (int(500 - angle[1] * factor), )
        output += (int(687 - angle[2] * factor - 5), )
    else: # Starboard side of the hexapod
        output += (int(687 - angle[0] * factor), )
        output += (int(500 + angle[1] * factor), )
        output += (int(313 + angle[2] * factor + 5),)

    # Move each of the servos on this leg
    SpiderPi[leg].standby_pos = (output, tim)

def trigger():
    '''
    Triggers hexapod movement
    :param:
    :return: True = success or error code
    '''

    oksofar = True
    for id in range (6):
        oksofar = SpiderPi[id].trigger
        if oksofar != True: return oksofar
    return oksofar
    
def pivot(angle, speed):
    '''
    Turn the hexapod on it's centre point. A static pivot. 
    param: angle: 为正时，右转, 为负时，左转 When +, turn right, -, turn left
                一个完整的转向周期所旋转的角度是angle*2
                The angle rotated by a complete turning cycle is angle*2
                所以检测到的角度要先除以2再传入
                So the detected angle must be divided by 2 before using it
    param: speed: 完成转向所用的毫秒数，最快建议不要小于100ms
                The number of milliseconds used to complete the turn,
                the fastest suggestion is >=100ms
    :return: True = success or error code
    '''

    if angle >= 23:
        angle = 23
        # print('R')
    elif  angle <= -23:
        angle = -23
        # print('L')

    leg0 = toe_coord(0, angle)
    leg1 = toe_coord(1, -angle)
    leg2 = toe_coord(2, angle)
    leg3 = toe_coord(3, -angle)
    leg4 = toe_coord(4, angle)
    leg5 = toe_coord(5, -angle)

    standby(0, leg0, 2 * speed)
    standby(1, lift_pos, speed)
    standby(2, leg2_pos, 2 * speed)
    standby(3, lift, speed)
    standby(4, leg4, 2 * speed)
    standby(5, lift_pos, speed)
    trigger() # Trigger the movement
    time.sleep(speed * 0.001)

    standby(1, leg1, speed)
    standby(3, leg3, speed)
    standby(5, leg5, speed)
    trigger() # Trigger the movement
    time.sleep(speed * 0.001)

    leg0 = toe_coord(0, -angle)
    leg1 = toe_coord(1, angle)
    leg2 = toe_coord(2, -angle)
    leg3 = toe_coord(3, angle)
    leg4 = toe_coord(4, -angle)
    leg5 = toe_coord(5, angle)
    
    standby(0, lift_pos, speed)
    standby(1, leg1, 2 * speed)
    standby(2, lift_pos, speed)
    standby(3, leg3, 2 * speed)
    standby(4, lift_pos, speed)
    standby(5, leg5, 2 * speed)
    trigger() # Trigger the movement
    time.sleep(speed * 0.001)
    
    standby(0, leg0, speed)
    standby(2, leg2, speed)
    standby(4, leg4, speed)
    trigger() # Trigger the movement
    time.sleep(speed * 0.001)

# angle:为正时，足端逆时针旋转 When +, the foot rotates counterclockwise
#       为负时，足端顺时针旋转 When -, the foot rotates clockwise
def toe_coord(leg, angle):
    '''
    Takes an angle in the X axis & returns X & Y coordinates for the toe
    param:leg: 0~5. 0 indexed
    param: angle: 为正时，足端逆时针旋转 为负时，足端顺时针旋转
                  turn angle + turn to port, - turn to starboard 
    '''

    # Takes an angle in the X axis &
    # converts it to X & Y coordinates a foot
    angle = angle * math.pi / 180   # 角度制转弧度制 Angle to radians
    R = 271.5
    RM = 232.5 # Middle legs just pivot, corner legs step
    base_angle_FB = 0.9465
    base_angle_M = 0.7853

    if leg == 0:
        x = R * math.cos(base_angle_FB + angle) - 58.5
        y = R * math.sin(base_angle_FB + angle) - 120.0
    elif leg == 1:
        x = RM * math.cos(base_angle_M + angle) - 64.70
        y = RM * math.sin(base_angle_M + angle) - 64.70
    elif leg == 2:
        x = R * math.sin(base_angle_FB - angle) - 120.0
        y = R * math.cos(base_angle_FB - angle) - 58.5
    elif leg == 3:
        x = R * math.cos(base_angle_FB - angle) - 58.5
        y = R * math.sin(base_angle_FB - angle) - 120.0
    elif leg == 4:
        x = RM * math.cos(base_angle_M - angle) - 64.70
        y = RM * math.sin(base_angle_M - angle) - 64.70
    elif leg == 5:
        x = R * math.sin(base_angle_FB + angle) - 120.0
        y = R * math.cos(base_angle_FB + angle) - 58.5
    else:
        x = 100
        y = 100
    return [x, y, -70] # -70 is normal stance height

def init():
    '''
    Initialise the hexapod
    param:
    :return: True = success or error code
    '''

    for leg in range(6): # For all the legs
        standby(leg, default_pos, 1000) # Move them to the default position
    trigger() # Trigger the movement

    return True

def sit():
    '''Function causes the hexapod to withdraw it's legs and rest on it's belly
    param:
    return: True = complete
    '''
    for leg in range(6): # For all legs
        standby(leg, sit_pos, 500) # Withdraw legs over 1 second
    trigger() # Trigger the movement
    time.sleep(0.5)
    unload()
    return True

def position(preset):
    '''Function causes the hexapod to adopt a preset position
    param:
    return: True = complete
    '''
    for leg in range(6): # For all legs
        standby_leg(leg, preset, 500) # Move legs over 0.5 seconds
    trigger() # Trigger the movement
    time.sleep(0.5)
    return True

def unload():
    '''
    Unload all of the servos in the hexapod
    param:
    :return: True = success or error code
    '''

    global SpiderPi # Bring the hexapod with us
    
    for leg in range(6): # For all the legs
        SpiderPi[leg].unload # Unload the leg
    time.sleep(0.5)
    return

def diag():
    global SpiderPi

    for leg in range(6): # For all the legs
        print(leg_names[leg], "leg")
        print(SpiderPi[leg].offset) # report offsets
        print(SpiderPi[leg].rotation_limits) # report rotation limits
        print(SpiderPi[leg].pos) # report position
        print(SpiderPi[leg].load_mode) # report loaded/unloaded
        print(SpiderPi[leg].vin_limits) # report vin limits
        print(SpiderPi[leg].vin) # report vin
        print(SpiderPi[leg].temp_limit) # report temperature alarm limit
        print(SpiderPi[leg].temp) # report temperature
    print("Diagnostics complete")
    return

if __name__ == '__main__':
    create_hexapod()

    print("Hexapod under test.")

    diag()
