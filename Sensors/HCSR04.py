#!/usr/bin/python3
# encoding: utf-8
# Copyright https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
# Further development by ians.moyes@gmail.com

# Function to measure obstruction range using an HC-SR04 ultrasonic sensor

'''
=========================================================================================
THIS SENSOR OUTPUTS 5V ON THE ECHO PIN & WILL DAMAGE THE RASPBERRY PI UNLESS A
VOLTAGE DIVIDER IS EMPLOYED.

There is one fitted to the HC-SR04 on my SpiderPi.

It consists of a 100ohm resistor soldered to the ECHO pin & a 220ohm resistor soldered
to the GND pin. The echo signal is measured at the junction of those resistors NOT the
ECHO pin.
=========================================================================================
'''

import time # Standard date & time library
import math # Standard mathematical library

#set GPIO Pin functions
GPIO_TRIGGER = 12 # GPIO pin for ultrasonic trigger
GPIO_ECHO = 16  # GPIO pin for ultrasonic echo

def init(pi):
    #set GPIO direction (IN / OUT)
    pi.set_mode(GPIO_TRIGGER, pigpio.OUTPUT) # Define TRIGGER as output
    pi.set_mode(GPIO_ECHO, pigpio.INPUT) # Define ECHO as input

def distance(pi,temp=20):
    ''' Function to trigger then read the echo of the HC-SR04 ultrasonic sensor
    :param pi: Instance of the class pigpio Raspberry Pi
    :param temp: ambient temperature
    :return: Nearest obstruction range from the sensor
    '''

     # Speed of sound cm/s based upon ambient temperature in °C
    SoS = 2005 * math.sqrt(273.15 + temp) # 34329cm/s at 20°C

    # set Trigger to HIGH
    pi.write(GPIO_TRIGGER, 1) # Trigger pulse

    # set Trigger to LOW after 0.01ms
    time.sleep(0.00001) # Pulse depth is 3.43mm @ 20°C
    pi.write(GPIO_TRIGGER, 0) # Release trigger
 
    StartTime = time.time() # Initialise variables
    StopTime = time.time()
 
    # save StartTime
    while pi.read(GPIO_ECHO) == 0: pass # Wait for the echo
    StartTime = time.time() # Record when it came

    # save StopTime
    while pi.read(GPIO_ECHO) == 1: pass # Measure the duration of echo
    StopTime = time.time() # Record when it stopped
    # Duration of the echo is the difference between start & stop times
    TimeElapsed = StopTime - StartTime
    if TimeElapsed < 0: print("Sensor error!")
    # multiply by the calculated sonic speed
    return (TimeElapsed * SoS) / 2 # and divide by 2, because there & back

if __name__ == '__main__':
    import pigpio # Standard Raspberry Pi GPIO library
    pi = pigpio.pi() # Create a Raspberry Pi object
    init(pi) # Initialise ultrasonic sensor

    from MPU9250 import MPU9250 # Class to create an IMU
    IMU = MPU9250()

    try:
        dist =()
        while True: # Forever
            # Compensate for ambient temperature affecting the speed of sound
            dist += (distance(pi, IMU.readTemperature()),) # Measure the distance
            # print ("Measured Distance = %.1f cm" % dist[-1]) # print it
            time.sleep(0.01) # Snooze
            if len(dist) > 20:
                average = round(sum(dist)/len(dist),1)
                print("Averaged distance", average)
                dist = (average,)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        # GPIO.cleanup()