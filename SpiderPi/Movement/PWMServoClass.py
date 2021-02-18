#!/usr/bin/python3
# encoding: utf-8
# Copyright HiWonder.hk
# Further development by ians.moyes@gmail.com
# Translation by Google

# Class to control the PWM Servo

import threading # Standard multi-tasking library
import time # Standard date & time library

class PWM_Servo(object): # Class to define & control a PWM Servo
    # PWM servo parameters
    servo_type = "generic" # Manufacturer/model of the servo
    rotate_limits = (500, 2500) # Miminum & maximum number of pulses for full defection
    time_limits = (20, 5000) # Minimum & maximum time to reach destination
    offset_limits = (-300, 300) # Minimum & maximum offset values
    PWMfreq = 50 # PWM frequency
    stepTime = 20 # Time for a iteration step, in milliseconds
    default_pos = 1500 # The default position for straight ahead

    def __init__(self, pi, pin, freq=PWMfreq, min_width=rotate_limits[0], max_width=rotate_limits[1], offset=0, control_speed=False):
        self.pi = pi # Attach the servo to the Raspberry Pi
        self.SPin = pin # Channel to control servo. The GPIO pin in our case
        self.Position = PWM_Servo.default_pos # The current position, firstly the straight-ahead position
        self.positionSet = self.Position # The next position to move to
        self.Freq = freq # The PWM carrier frequency
        self.Min = min_width # Minimum PWM pulses for full deflection
        self.Max = max_width # Maximum PWM pulses for full deflection
        self.Offset = offset # Calibration offset
        self.Mintime = PWM_Servo.time_limits[0] # Minimum time to destination
        self.Maxtime = PWM_Servo.time_limits[1] # Maximum time to destination
        self.stepTime = PWM_Servo.stepTime # Time for a iteration step, in milliseconds
        self.positionInc = 0.0 # How many pulses to move in a step
        self.Time = 0 # Time duration of the movement
        self.incTimes = 1 # How many time steps to reach destination
        self.prev = time.time() # Placeholder for pause time stamp
        self.speedControl = False # Whether speed control is required

        self.pi.set_PWM_range(self.SPin, int(1000000 / self.Freq)) # Range of values for duty cycle
        self.pi.set_PWM_frequency(self.SPin, self.Freq) # Set PWM carrier frequency
        self.pi.set_PWM_dutycycle(self.SPin, self.Position + self.Offset) # Initialise position

        if self.speedControl is True: # If speed control is required start a multi-tasking thread
            t1 = threading.Thread(target=PWM_Servo.updatePosition, args=(self,))
            t1.setDaemon(True)
            t1.start()

    def setPosition(self, pos, tim=0): # Move the servo
        if pos < self.Min or pos > self.Max: # Validate the position value
            print("Invalid position value " + str(pos))
            return "pos"

        self.positionSet = pos # Set the next position flag
        
        if not self.speedControl: tim = 0 # If speed control is not required
        if tim == 0:
            self.Position = pos # Update the current position 
            self.pi.set_PWM_dutycycle(self.SPin, self.Position + self.Offset) # Move the servo
        else:
            if tim < self.Mintime: # Don't change to max/min, this is faster
                self.Time = self.Mintime # Clamp the time to the limits
            elif tim > self.Maxtime:
                self.Time = self.Maxtime
            else:
                self.Time = tim
# The multi-tasking thread will pick up that the current position doesn't match the
# desired position & activate
        return True

    def updatePosition(self): # This is the code for the multi-tasking thread
        while True: # If speed control is required
            if self.Position != self.positionSet: # If the desired position is not the current position
                self.incTimes = int(self.Time / self.stepTime)
                if self.incTimes == 0: self.incTimes = 1
                # The number of steps is time-to-destination / time-for-a-step
                self.positionInc = int((self.positionSet - self.Position) / self.incTimes)
                # Pulses per step

                for i in range (self.incTimes): # Loop to add a step increment each iteration
                    self.prev = time.time() # To the current position
                    self.Position += self.positionInc
                    self.pi.set_PWM_dutycycle(self.SPin, self.Position + self.Offset) # Move the servo
                    time.sleep(max(0, 0.02 - (time.time() - self.prev))) # Work out the pause
                
                self.Time = self.Mintime # Set the duration to the minimum to mop up the error

if __name__ == '__main__':
    import pigpio # Standard Raspberry Pi GPIO library
    pi = pigpio.pi() # Create a Raspberry Pi object

    pan = PWM_Servo(pi, 5, min_width=800, max_width=2200, offset=0) #, control_speed=True)
    tilt = PWM_Servo(pi, 6, min_width=1200, max_width=2000, offset=0) # , control_speed=True)

    tilt.setPosition(tilt.default_pos)
    pan.setPosition(pan.default_pos)
    print("Middle Middle")
    time.sleep(1)

    tilt.setPosition(tilt.Min, 500) # Full down
    print("Middle Down")
    time.sleep(1)
    tilt.setPosition(tilt.Max, 500) # Full up
    print("Middle Up")
    time.sleep(1)
    tilt.setPosition(tilt.default_pos, 500)
    print("Middle Middle")    
    time.sleep(1)

    pan.setPosition(pan.Min, 500) # Full right
    print("Right Middle")
    time.sleep(1)
    pan.setPosition(pan.Max, 500) # Full left
    print("Left Middle")
    time.sleep(1)
    print("Middle Middle")
    pan.setPosition(pan.default_pos, 500)
