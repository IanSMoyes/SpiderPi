#!/usr/bin/python3
# encoding: utf-8
# Copyright https://makersportal.com/blog/2019/11/11/raspberry-pi-python-accelerometer-gyroscope-magnetometer#interfacing
# Further developement by ians.moyes@gmail.com

# Function to read:
# 1: MPU6050 (3D gyroscope, 3D accelerometer & ambient temperature)
# 2: AK8963 (3D magnetometer, )
# 3: BMP280 (barometric pressure, ambient temperature & altitude)

import smbus2 as smbus
import time

I2C = smbus.SMBus(1)

