#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# Copyright ians.moyes@gmail.com

# Programme to calculate inverse kinematics
import math

def switch_sides(coords):
    '''
    Take account of servo positions switching polarity on the other side of the hexapod
    param: coords: Tuple containing shoulder, knee & ankle servo positions
    return: Tuple containing shoulder, knee & ankle servo positions
    '''
    return (1000-coords[0], 1000-coords[1], 1000-coords[2])

def remap(angle):
    '''
    Function takes an angle and returns a servo position
    param: angle: is the joint angle in radians
    return: servo position 0-1000
    '''
    return int(((math.degrees(angle)/120)*500)+500)

def inverse_kin(leg, coords):
    '''
    Converts a XYZ coordinate into a set of servo positions using inverse kinematics
    param:leg: 0~5
    param: Coords:Tuple to store the coordinates of the foot (X, Y, Z)
    '''
    
    # Lengths of the 3 leg elements
    # The thigh length is important because the mat assumes the shoulder joint is 1, 3D joint
    thigh = 44.60 # This is the distance across the shoulder joint bracket
    calf = 75.00 # This is the length of the upper leg member
    foot = 126.50 # This is the length of the lower leg member

    x = float(coords[0]) # distance forward the new toe position is
    y = float(coords[1]) # distance out (from the shoulder joint) the new toe position is
    if y == 0: y = 1 # Avoids division by 0
    z = float(coords[2]) # distance down the new toe position is
    if z == 0: z = 1 # Avoids division by 0

    # The WZ axis is the verticle plane through the shoulder joint, toe position and knee joint
    # w = the distance along the W axis the new toe position is
    w = math.sqrt(x**2 + y**2)
    if w > thigh + calf + foot: return "Position too far" # Goal exceeds reach
    # The inverse kinematics needs to be calculated on the distance from the knee
    # joint to the toe position. So the length of the shoulder joint needs to be deducted
    w -= thigh
    if w == 0: w = 1 # Avoids division by 0

    servo_positions = (remap(math.atan(x/y)),) # shoulderjoint position in the XY plane

    # toedist = hypoteneus of the triangle made by w, x & the knee joint.
    # The distance between the nee toe position & the knee joint
    toedist = math.sqrt(w**2 + z**2)

    # kneeang = internal angle the knee joint makes between the thigh bone & the toe position
    kneeang = math.acos((toedist**2 + calf**2 - foot**2)/(2*toedist*calf))
    # kneeflex = angle between the W axis & direction to the ankle joint
    kneeflex = kneeang - math.atan(w/z)
    # kneepos = servo position to achieve kneeflex
    servo_positions += (remap(kneeflex),)

    # ankleang = internal angle between the shin bone and the thigh bone
    ankleang = math.acos((foot**2+calf**2-toedist**2)/(2*foot*calf))
    # ankleflex = external angle between straight and ankleang
    ankleflex = math.pi - ankleang
    # anklepos = servo position to achieve ankleflex
    servo_positions += (remap(ankleflex),)

    if leg > 2: return switch_sides(servo_positions)

    return servo_positions

if __name__ == '__main__':
    while True:
        leg = int(input("Which leg are we working on? "))
        x = float(input("Input x cordinate? "))
        y = float(input("Input y cordinate? "))
        z = float(input("Input z cordinate? "))

        print(inverse_kin(leg, (x,y,z)))
