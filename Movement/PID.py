"""Ivmech PID Controller is simple implementation of a Proportional-Integral-Derivative
(PID) Controller in the Python Programming Language.
More information about PID Controller: http://en.wikipedia.org/wiki/PID_controller
"""
# Copyright Ivmech
# Further development by ians.moyes@gmail.com

import time # Standard date & time function library

class PID: # Class to define & control a PID Controller

    def __init__(self, P=0.2, I=0.0, D=0.0, sample_time=0): # Defines P, I & D coefficients

        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.sample_time = sample_time # Period between readings
        self.current_time = time.time() # Current time
        self.last_time = self.current_time # Previous time

        self.clear() # Initialise PID controller

    def clear(self):
        """Clears PID computations and coefficients"""
        self.SetPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 20.0

        self.output = 0.0

    def update(self, feedback_value):
        """Calculates PID value for given reference feedback
        .. math::
        u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}
        .. figure:: images/pid_1.png
        :align center
        Test PID with Kp=1.2, Ki=1, Kd=0.001 (test_pid.py)
        """

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time

        if (delta_time >= self.sample_time):
            error = self.SetPoint - feedback_value
            delta_error = error - self.last_error
            self.PTerm = self.Kp * error # Set P to P coefficient * current error
            self.ITerm += error * delta_time # Set I to error * time since last set

            if (self.ITerm < -self.windup_guard): # Clamp I to the windup guard limits
                self.ITerm = -self.windup_guard
            elif (self.ITerm > self.windup_guard):
                self.ITerm = self.windup_guard

            self.DTerm = 0.0 # Reset D
            if delta_time > 0: # If time has elapsed
                self.DTerm = delta_error / delta_time # Difference in the error / difference in the time

            # Remember last time and last error for next calculation
            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

if __name__ == '__main__':
    x_pid = PID(P=0.2, I=0, D=0)
    x_pid.SetPoint = 5
    x_pid.update(10)
    out = x_pid.output
    print (out)
