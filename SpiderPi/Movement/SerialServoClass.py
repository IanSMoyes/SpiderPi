#!/usr/bin/python3
# encoding: utf-8
# Copyright HiWonder.hk
# Copyright ians.moyes@gmail.com
# Further development by ians.moyes@gmail.com
# Translation by Google

# Class to define a serial bus servo motor

import SerialBusCom as Ctrl # Bus Serial Servo communication driver

class Serial_Servo():
    ''' This is a class to define & therefore control a Bus Serial Servo motor
    '''
    # Set class variables

    # Bus Serial Servo command codes
    MOVE_TIME_WRITE      =  1 #    7
    MOVE_TIME_READ       =  2 #    3
    # No commands from      3 - 6
    MOVE_TIME_WAIT_WRITE =  7 #    7
    MOVE_TIME_WAIT_READ  =  8 #    3
    # No commands           9 or 10
    MOVE_START           = 11 #    3
    MOVE_STOP            = 12 #    3
    # ID_WRITE           = 13 #    4 Too dangerous to be included
    # ID_READ            = 14 #    3 Useless in a multi servo environment
    # No commands          15 or 16
    ANGLE_OFFSET_ADJUST  = 17 #    4
    ANGLE_OFFSET_WRITE   = 18 #    3
    ANGLE_OFFSET_READ    = 19 #    3
    ANGLE_LIMIT_WRITE    = 20 #    7
    ANGLE_LIMIT_READ     = 21 #    3
    VIN_LIMIT_WRITE      = 22 #    7
    VIN_LIMIT_READ       = 23 #    3
    TEMP_LIMIT_WRITE     = 24 #    4
    TEMP_LIMIT_READ      = 25 #    3
    TEMP_READ            = 26 #    3
    VIN_READ             = 27 #    3
    POS_READ             = 28 #    3
    MOTOR_MODE_WRITE     = 29 #    7
    MOTOR_MODE_READ      = 30 #    3
    LOAD_MODE_WRITE      = 31 #    4
    LOAD_MODE_READ       = 32 #    3
    LED_CTRL_WRITE       = 33 #    4
    LED_CTRL_READ        = 34 #    3
    LED_ERROR_WRITE      = 35 #    4
    LED_ERROR_READ       = 36 #    3
    # Numbers of arguments for each command
    # -1 means inactive command. Tuple is 0 indexed. commands are 1 indexed.
    num_params = (2,0,-1,-1,-1,-1,2,0,-1,-1,0,0,-1,-1,-1,-1,1,0,0,2,0,2,0,1,0,0,0,0,2,0,1,0,1,0,1,0)
    # Bus Servo parameters
    servo_type = "LX-224HV" # Manufacturer/model of the servo
    num_servos = 18 # Number of servos of this type on the robot
    rotate_limits = (0, 1000) # Miminum & maximum values for full defection
    cont_speed = (-1000, 1000) # Range of continuous rotation speeds
    max_speed = 1250 # Maximum rotation speed in positions per second
    # HiWonder LX-224HV Bus Servos have a maximum speed of rotation of 0.20sec/60°(@ VIn 11.1V).
    # With a maximum rotation of 0 ~ 240° defined as a range of 1-1000.
    time_limits = (0, 30000) # Minimum & maximum time durations
    offset_limits = (-125, 125)  # Minimum & maximum offset values
    # Offsets can be set between angles of -30 ° ~ 30 °
    Vin_limits = (9000, 12600) # Voltage limits specified in mV
    # Controller allows voltage limits to be set from 4500mV to 14000mV but the operating
    # voltage of the LX-224HV is 9-12.6V
    temp_limits = (50, 85) # Temperature alarm limit in °C.
    # The limit can be set between 50 ~ 100°C.
    default_pos = 500 # The default position for 50% rotation

    def __init__(self, pi, id):
        self.pi = pi # Attach the servo to the Raspberry Pi
        self.id = id # The ID number of the Bus Serial Servo to control

    def set_pos(self, posn): # Command 1
        '''
        Move servo to new position
        param self.id: Servo id
        param pos: position for servo to move to
        param tim: time to reach destination in mS
        :return: True or error code
        '''
        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.MOVE_TIME_WRITE, posn[0], posn[1])

    @property # Allows method to be used like a variable without ()
    def get_set_pos(self): # Command 2
        '''
        Read the last servo set position sent.
        THIS IS NOT NECESSARILY THE CURRENT POSITION, it's the last REQUESTED position
        :param self.id: Servo id
        :return: (Position, Speed) or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.MOVE_TIME_READ) # Send data request
        if type(msg) == str: print("Get set position error", msg)
        return msg # Return value once received

    # There are no commands 3 - 6

    def set_standby_pos(self, posn): # Command 7
        '''
        Prepare to move servo to new position.
        Nothing happens until the user transmits trigger. Command 11.
        param self.id: Servo id
        param posn: position for servo to move to
        param tim: time to reach destination in mS
        :return: True = successful or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.MOVE_TIME_WAIT_WRITE, posn[0], posn[1])

    # For some reason, this one doesn't work gets locked in endless loop
    def get_standby_pos(self): # Command 8
        '''
        Read the last servo set standby position sent.
        THIS IS NOT THE SET POSITION until triggered
        :param self.id: Servo id
        :return: Requested servo position or error code
        '''

        '''msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.MOVE_TIME_WAIT_READ) # Send data request
        return msg # Return value once received
        if type(msg) == str: print("Standby position read error", msg)
        else: print("Last standby position for servo number", self.id, "is", msg)
        return msg # Return value once received'''
        pass

    standby_pos = property(get_standby_pos, set_standby_pos)

    @property # Allows method to be used like a variable without ()
    def trigger(self): # Command 11
        '''
        Triggers movement to new position as defined by previously transmitted
        new_standby_pos. Command 7.
        param self.id: Servo id
        :return: True = successful or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.MOVE_START)

    @property # Allows method to be used like a variable without ()
    def stop(self): # Command 12
        '''
        停止舵机运行 Stop servo immediately
        :param self.id: Servo id
        :return: True = successful or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.MOVE_STOP)

    #ID_WRITE. # Command 13 is too dangerous for general use
    #ID_READ. # Command 14 is no use in a multi servo configuration
    # There are no commands 15 - 16

    def set_offset(self, offset=0): # Command 17 + 18
        """
        配置偏差，掉电保护 Set servo offset and save to non-volatile memory to survive reboot
        :param self.id: 舵机 id Servo id
        :param offset: 偏差 Offset value
        :return: True = Successful or Error code
        """

        # 设置偏差 Set offset
        result = Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.ANGLE_OFFSET_ADJUST, offset)
        if type(result) == str: return result
        # 设置为掉电保护 Save to non-volatile memory
        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.ANGLE_OFFSET_WRITE)

    def get_offset(self): # Command 19
        '''
        读取偏差值 Read offset value
        :param self.id: 舵机号 Servo id
        :return: Offset value or error code
        '''

        # 发送读取偏差指令 Send read offset command
        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.ANGLE_OFFSET_READ) # Send data request
        if type(msg) == str: print("Get offset read error",  msg)
        return msg # Return value once received

    offset = property(get_offset, set_offset)

    def set_rotation_limits(self, limits=rotate_limits): # Command 20
        '''
        设置舵机转动范围 Set the servo rotation limits
        :param self.id: Servo id
        :param limits: (Lower, Upper)
        :return: True = successful or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.ANGLE_LIMIT_WRITE, limits[0], limits[1])

    def get_rotation_limits(self): # Command 21
        '''
        读取舵机转动范围 Read the servo rotation limits
        :param self.id: Servo id
        :return: 返回元祖 0： 低位  1： 高位 (Lower limit, Upper limit) or error code
        '''

        # 发送读取偏差指令 Send read rotation limits command
        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.ANGLE_LIMIT_READ) # Send data request
        if type(msg) == str: print("Get rotation limits error", msg)
        return msg # Return value once received

    rotation_limits = property(get_rotation_limits, set_rotation_limits)

    def set_vin_limits(self, limits=Vin_limits): # Command 22
        '''
        设置舵机转动范围 Set servo voltage-in alarm limits
        :param self.id: Servo id
        :param limits: (Lower, Upper)
        :return: True = success or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.VIN_LIMIT_WRITE, limits[0], limits[1])

    def get_vin_limits(self): # Command 23
        '''
        读取舵机转动范围 Read servo voltage-in alarm limits
        :param id: Servo id
        :return: 返回元祖 0： 低位  1： 高位 0: (Lower limit, Upper limit) or error code
        '''

        # 发送读取偏差指令 Send read offset command
        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.VIN_LIMIT_READ) # Send data request
        if type(msg) == str: print("Voltage-in limits read error", msg)
        return msg # Return value once received

    vin_limits = property(get_vin_limits, set_vin_limits)

    def set_temp_limit(self, m_temp=temp_limits[1]): # Command 24
        '''
        设置舵机最高温度报警 Set servo temperature alarm value
        :param self.id: Servo id
        :param m_temp: Temperature value
        :return: Error value or True = successful
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.TEMP_LIMIT_WRITE, m_temp)

    def get_temp_limit(self): # Command 25
        '''
        读取舵机温度报警范围 Read servo temperature alarm value
        :param id: Servo id
        :return: Servo temperature alarm value or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.TEMP_LIMIT_READ) # Send data request
        if type(msg) == str: print("Temperature limit read error", msg)
        return msg # Return value once received

    temp_limit = property(get_temp_limit, set_temp_limit)

    @property # Allows method to be used like a variable without ()
    def temp(self): # Command 26
        '''
        读取舵机温度 Read real time servo temperature
        :param self.id: Servo id
        :return: Temperature value or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.TEMP_READ) # Send data request
        if type(msg) == str: print("Current temperature read error", msg)
        return msg # Return value once received

    @property # Allows method to be used like a variable without ()
    def vin(self): # Command 27
        '''
        读取舵机温度 Read real time servo voltage-in
        :param self.id: Servo id
        :return: Servo voltage-in or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.VIN_READ) # Send data request
        if type(msg) == str: print("Input voltage read read error", msg)
        return msg # Return value once received

    def get_pos(self): # Command 28
        '''
        读取舵机当前位置 Read real time servo position
        :param self.id: Servo id
        :return: Current servo position or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.POS_READ) # Send data request
        if type(msg) == str: print("Current position read error", msg)
        return msg # Return value once received

    pos = property(get_pos, set_pos)

    @property # Allows method to be used like a variable without ()
    def servo_mode(self): # Command 29
        '''
        Set limited angle servo mode
        :param self.id: Servo id
        :return: Success = True or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.MOTOR_MODE_WRITE, 0)

    @property # Allows method to be used like a variable without ()
    def motor_mode(self): # Command 30
        '''
        读取舵机当前位置 Read servo motor mode
        :param self.id: Servo id
        :return: Return motor mode or error code (mode, speed)
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.MOTOR_MODE_READ) # Send data request
        if type(msg) == str: print("Motor mode read error", msg)
        return msg # Return value once received

    def set_load(self, mode = 1): # Command 31
        '''
        Set torque bearing mode
        :param mode: desired load mode. 0 = unlaoded, 1 = loaded
        :return: True = success or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.LOAD_MODE_WRITE, mode)

    @property # Allows method to be used like a variable without ()
    def unload(self): # Command 31
        '''
        Set torque free mode
        :param self.id: servo id
        :return: True = success or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.LOAD_MODE_WRITE, 0)

    def get_load_mode(self): # Command 32
        '''
        Read torque/no torque mode
        :param self.id: Servo id
        :return: Return motor load mode or error code.
        0 for unloaded, no torque output. 1 loaded, high torque output
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.LOAD_MODE_READ) # Send data request
        if type(msg) == str: print("Motor mode read error", msg)
        return msg # Return value once received

    load = property(get_load_mode, set_load)

    def set_LED_mode(self, mode=1): # Command 33
        '''
        Set LED state
        :param self.id: Servo id
        :param mode: LED mode. 0 LED always on. 1 LED off.
        :return:
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.LED_CTRL_WRITE, mode)

    def get_LED_mode(self): # Command 34
        '''
        Read LED state
        :param self.id: Servo id
        :return: Return LED mode or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.LED_CTRL_READ) # Send data request
        if type(msg) == str: print("LED mode read error", msg)
        return msg # Return value once received

    LED_mode = property(get_LED_mode, set_LED_mode)

    def set_LED_err(self, mode=7): # Command 35
        '''
        Set LED error mode
        :param self.id: Servo id
        :param mode: LED error mode. Range 0 to 7
          0      No alarm
          1      Over temperature
          2      Over voltage
          3      Over temperature and over voltage
          4      locked_rotor
          5      Over temperature and locked_rotor
          6      Over voltage and locked_rotor
          7      Over temperature , over voltage and locked_rotor
        :return: True = success or error code
        '''

        return Ctrl.serial_servo_write_cmd(self.pi, self.id, Serial_Servo.LED_ERROR_WRITE, mode)

    def get_LED_err(self): # Command 36
        '''
        Read LED error code
        :param self.id: Servo id
        :return: Return LED error code (above) or error code
        '''

        msg = Ctrl.serial_servo_read_cmd(self.pi, self.id, Serial_Servo.LED_ERROR_READ) # Send data request
        if type(msg) == str: print("LED error mode read error", msg)
        return msg # Return value once received

    LED_err = property(get_LED_err, set_LED_err)

    @property # Allows method to be used like a variable without ()
    def servo_state(self):
        '''
        显示信息 Display servo information
        :return: Dictionary of collected results
        '''
        results = {"id":self.id}
        results["rotation_limits"] = self.rotation_limits # Command 21
        results["position"] = self.pos # Command 28
        results["temp_limit"] = self.temp_limit # Command 25
        results["temp"] = self.temp # Command 26
        results["vin_limits"] = self.vin_limits # Command 23
        results["vin"] = self.vin # Command 27
        results["offset"] = self.offset # Command 19
        results["load"] = self.load # Command 32
        results["LED_mode"] = self.LED_mode # Command 34
        results["LED_err"] = self.LED_err # Command 36
        
        print(" ")
        print(" ")
        return results # Return data

if __name__ == '__main__':
    import pigpio # Standard Raspberry Pi GPIO library
    pi = pigpio.pi() # Create a Raspberry Pi object
    Ctrl.portinit(pi) # Initialise the read/write switch

    servos = ()
    for id in range(Serial_Servo.num_servos): # Create all servos
        servos += (Serial_Servo(pi, id+1),) # tuples are 0 indexed, servos 1 indexed

    print(Serial_Servo.num_servos, Serial_Servo.servo_type, " servos under test.")

    results=()
    for id in range(Serial_Servo.num_servos): # for all servos
        result = servos[id].servo_state # Collect status information
        print(result)
        results += (result, )

    print(results)
    print(" ")
    print("Servo interrogation complete!")
