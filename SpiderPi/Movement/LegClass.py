#!/usr/bin/python3
# encoding: utf-8
# Copyright ians.moyes@gmail.com

# Class to define a hexapod leg with 3 degrees of freedom

from SerialServoClass import Serial_Servo as Servo # Bus Serial Servo control class

class Leg():
    ''' This is a class to define a hexapod leg consisting of 3 Bus Serial Servos
    '''
    default_time = 500 # If no time is given for a movement make it 500mS

    def __init__(self, pi, leg): # Build a leg
        self.pi = pi # Attach the leg to the Raspberry Pi
        self.leg = leg # start with the index number of the leg. 0 indexed.
        self.shoulder = Servo(self.pi, (self.leg * 3) + 1) # Create a shoulder joint
        self.knee = Servo(self.pi, (self.leg * 3) + 2) # Create a knee joint
        self.ankle = Servo(self.pi, (self.leg * 3) + 3) # Create an ankle joint

    def set_pos(self, posn): # Command 1.
        '''
        Move leg to new position
        param position: tuple to define the position for leg to move to (shoulder, knee, ankle)
        param time: time to reach destination in mS
        This MAY mean the servos are travelling at different speeds
        :return:
        '''

        if len(posn) == 2: # if a time to detination was specified
            self.shoulder.pos = (posn[0][0], posn[1]) # Move shoulder joint
            self.knee.pos = (posn[0][1], posn[1]) # Move knee joint
            self.ankle.pos = (posn[0][2], posn[1]) # Move ankle joint
        else:
            self.shoulder.pos = (posn[0], Leg.default_time) # Move shoulder joint
            self.knee.pos = (posn[1], Leg.default_time) # Move knee joint
            self.ankle.pos = (posn[2], Leg.default_time) # Move ankle joint
   
    @property # Allows method to be used like a variable without ()
    def get_set_pos(self): # Command 2
        '''
        Get the last leg joint set position sent. THIS IS NOT NECESSARILY THE CURRENT POSITION
        :param:
        :return: ((Shoulder Position, Speed),(Knee Position, Speed),(Ankle Position, Speed))
        or error code
        '''

        result = (self.shoulder.get_set_pos, ) # Get shoulder (position, speed)
        result += (self.knee.get_set_pos, ) # Append knee (position, speed)
        result += (self.ankle.get_set_pos, ) # Append ankle (position, speed)
        return result
  
    def set_standby_pos(self, posn): # Command 7
        '''
        Set new position to PREPARE to move leg to.
        Nothing happens until the user transmits trigger command. Command 11.
        param position: tuple to define the position for leg to move to (shoulder, knee, ankle)
        param tim: time to reach destinations in mS
        This MAY mean the servos are travelling at different speeds
        :return:
        '''
 
        if len(posn) == 2: # if a time to detination was specified
            self.shoulder.standby_pos = (posn[0][0], posn[1]) # Move shoulder joint
            self.knee.standby_pos = (posn[0][1], posn[1]) # Move knee joint
            self.ankle.standby_pos = (posn[0][2], posn[1]) # Move ankle joint
        else:
            self.shoulder.standby_pos = (posn[0], Leg.default_time) # Standby to move shoulder joint
            self.knee.standby_pos = (posn[1], Leg.default_time) # Standby to move knee joint
            self.ankle.standby_pos = (posn[2], Leg.default_time) # Standby to move ankle joint

    standby_pos = property(fset=set_standby_pos)

    @property # Allows method to be used like a variable without ()
    def trigger(self): # Command 11
        '''
        Triggers movement to new position as defined by previously transmitted
        new_standby_pos command. Command 7.
        :return:
        '''

        self.shoulder.trigger # Trigger shoulder joint
        self.knee.trigger # Trigger knee joint
        self.ankle.trigger # Trigger ankle joint
  
    @property # Allows method to be used like a variable without ()
    def stop(self): # Command 12
        '''
        Stop leg immediately
        :return: True = successful or error code
        '''

        self.shoulder.stop # Stop shoulder joint
        self.knee.stop # Stop knee joint
        self.ankle.stop # Stop ankle joint
        
    def set_offset(self, offset=(0,0,0)): # Command 17 + 18
        """
        Set leg joint offsets and save to non-volatile memory to survive reboot
        param offset: tuple to define the offsets for leg (shoulder, knee, ankle)
        :return:
        """

        self.shoulder.offset = offset[0] # Offset shoulder joint
        self.knee.offset = offset[1] # Offset knee joint
        self.ankle.offset = offset[2] # Offset ankle joint
        
    def get_offset(self): # Command 19
        '''
        Reads offset values
        :param:
        :return: Offset values (Shoulder, Knee, Ankle) or error code
        '''

        result = (self.shoulder.offset, ) # Get shoulder offset
        result += (self.knee.offset, ) # Get knee offset
        result += (self.ankle.offset, ) # Get ankle offset
        return result

    offset = property(get_offset, set_offset)

    def set_rotation_limits(self, limits): # Command 20
        '''
        Set the leg joint rotation limits
        param limits: tuple to define the rotation limits for leg
        ((shoulder low, high), (knee low, high), (ankle low,high))
        :return:
        '''

        self.shoulder.rotation_limits = limits[0] # Set shoulder joint limits
        self.knee.rotation_limits = limits[1] # Set knee joint limits
        self.ankle.rotation_limits = limits[2] # Set ankle joint limits

    def get_rotation_limits(self): # Command 21
        '''
        Reads the leg joint rotation limits
        :return:  ((shoulder low, high), (knee low, high),(ankle low, high)) or error code
        '''

        result = (self.shoulder.rotation_limits, ) # Get shoulder limits (low, high)
        result += (self.knee.rotation_limits, ) # Append knee limits (low, high)
        result += (self.ankle.rotation_limits, ) # Append ankle limits (low, high)
        return result

    rotation_limits = property(get_rotation_limits, set_rotation_limits)

    def set_vin_limits(self, limits): # Command 22
        '''
        设置舵机转动范围 Set servo voltage-in alarm limits
        :param self.id: Servo id
        :param limits: (Lower, Upper) all joints set to the same limits
        :return: True = success or error code
        '''

        self.shoulder.vin_limits = limits # Set shoulder joint limits
        self.knee.vin_limits = limits # Set knee joint limits
        self.ankle.vin_limits = limits # Set ankle joint limits

    def get_vin_limits(self): # Command 23
        '''
        Returns leg joint voltage-in alarm limits
        :return: ((Shoulder lower, upper), (Knee lower, upper), (Ankle lower, upper))
        '''

        result = (self.shoulder.vin_limits, ) # Get shoulder limits (low, high)
        result += (self.knee.vin_limits, ) # Append knee limits (low, high)
        result += (self.ankle.vin_limits, ) # Append ankle limits (low, high)
        return result

    vin_limits = property(get_vin_limits, set_vin_limits)

    def set_temp_limits(self, limit): # Command 24
        '''
        设置舵机最高温度报警 Set servo temperature alarm value
        :param self.id: Servo id
        :param m_temp: Temperature value. Same value for all servos
        :return: Error value or True = successful
        '''

        self.shoulder.temp_limit = limit # Set shoulder joint limit
        self.knee.temp_limit = limit # Set knee joint limit
        self.ankle.temp_limit = limit # Set ankle joint limit

    def get_temp_limits(self): # Command 25
        '''
        Read leg joint temperature alarm values
        :return: Servo temperature alarm values (shoulder, knee, ankle) or error code
        '''

        result = (self.shoulder.temp_limit, ) # Get shoulder limit
        result += (self.knee.temp_limit, ) # Append knee limit
        result += (self.ankle.temp_limit, ) # Append ankle limit
        return result

    temp_limits = property(get_temp_limits, set_temp_limits)

    @property # Allows method to be used like a variable without ()
    def temp(self): # Command 26
        '''
        Read real time leg joint temperatures in °C
        :return: Temperature values (shoulder, knee, ankle) or error code
        '''

        result = (self.shoulder.temp, ) # Get shoulder temp
        result += (self.knee.temp, ) # Append knee temp
        result += (self.ankle.temp, ) # Append ankle temp
        return result

    @property # Allows method to be used like a variable without ()
    def vin(self): # Command 27
        '''
        Read real time leg joint voltages-in
        :return: Voltages-in (shoulder, knee, ankle) or error code
        '''

        result = (self.shoulder.vin, ) # Get shoulder Vin
        result += (self.knee.vin, ) # Append knee Vin
        result += (self.ankle.vin, ) # Append ankle Vin
        return result

    def get_pos(self): # Command 28
        '''
        Read real time leg joint positions
        :return: Current leg joint positions (Shoulder, Knee, Ankle) or error code
        '''

        result = (self.shoulder.pos, ) # Get shoulder position
        result += (self.knee.pos, ) # Append knee position
        result += (self.ankle.pos, ) # Append ankle position
        return result

    pos = property(get_pos, set_pos)

    def set_load(self, mode=1): # Command 31
        '''
        Set leg joints torque bearing mode
        :param mode: desired load mode. 0 = unloaded, 1 = loaded
        :return:
        '''

        self.shoulder.load = mode # Set shoulder joint loaded
        self.knee.load = mode # Set knee joint loaded
        self.ankle.load = mode # Set ankle joint loaded

    @property # Allows method to be used like a variable without ()
    def unload(self): # Command 31
        '''
        Set leg joints to torque free mode
        :return:
        '''

        self.shoulder.unload # Set shoulder joint unloaded
        self.knee.unload # Set knee joint unloaded
        self.ankle.unload # Set ankle joint unloaded

    def get_load(self): # Command 32
        '''
        Read leg joint torque/no torque modes
        :return: Return leg joint load modes (Shoulder, Knee, Ankle) or error code.
        0 for unloaded, no torque output. 1 loaded, high torque output
        '''

        result = (self.shoulder.load, ) # Get shoulder loaded/unloaded
        result += (self.knee.load, ) # Append knee loaded/unloaded
        result += (self.ankle.load, ) # Append ankle loaded/unloaded
        return result

    load = property(get_load, set_load)

    @property # Allows method to be used like a variable without ()
    def leg_state(self):
        '''
        显示信息 Display servo information
        :return: Dictionary of collected results
        '''
        results = {"leg":self.leg}
        results["rotation_limits"] = self.rotation_limits # Command 21
        results["positions"] = self.pos # Command 28
        results["temp_limits"] = self.temp_limits # Command 25
        results["temps"] = self.temp # Command 26
        results["vin_limits"] = self.vin_limits # Command 23
        results["vins"] = self.vin # Command 27
        results["offsets"] = self.offset # Command 19
        results["load"] = self.load # Command 32
        return results # Return data

if __name__ == '__main__':
    import pigpio # Standard Raspberry Pi GPIO library
    pi = pigpio.pi() # Create a Raspberry Pi object
    import SerialBusCom as Ctrl # Bus Serial Servo communication driver
    Ctrl.portinit(pi) # Initialise the read/write switch

    legs = ()
    for leg in range(6): # Create all legs
        legs += (Leg(pi, leg), )

    leg_names = ("Port rear", "Port centre", "Port front", "Starboard rear", "Starboard centre", "Starboard front")

    print("Six legs under test.")
    print(" ")

    results = ()
    for leg in range(6): # for all legs
        print("Interrogating", leg_names[leg], "leg")
        result = legs[leg].leg_state # Collect status information
        print(result)
        results += (result,)
    print(results)

    print("Leg interrogation complete!")
