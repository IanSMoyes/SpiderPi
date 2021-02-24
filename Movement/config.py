'''
Copyright HiWonder

LewanSoul Bus Servo Communication Protocol
1.Summary
Using an asynchronous serial communication bus, theoretically, up to 253 robot Bus Servos can be
daisy chain connected into the bus, you can control them individually through the UART
asynchronous serial interfaces. Each Bus Servo can be set to a different node (ID) address,
and multiple Bus Servos can be grouped or controlled individually. Communicating with
the user's host computer software (micro controller or PC) through the asynchronous serial
interface, you can set the Bus Servo's parameters, control functions and movement. Sending
instructions through the asynchronous serial interface, the Bus Servo can be set to motor
control mode (continuous rotation) or position control mode (limited angle servo). In motor
control mode, the Bus Servo can be used as a DC reduction motor with adjustable speed; In
position control mode, the Bus Servo has 240° of rotation range with plus ± 30° adjustable
offset available, with high precise positional control & adjustable speed. Parameters can be read
back from the Bus Servo including servo position, input voltage, internal temperature.

Any half-duplex UART asynchronous serial interface which conforms to the protocol can
communicate with the Bus Servos and control the Bus Servos in a variety of ways.

2.UART Interface
The Bus Servo uses program code to perform the timing control to the UART asynchronous serial
interface, achieving the half-duplex asynchronous serial bus communication, the communication
baud rate is 115200bps, and the interface is simple, the protocol is equally simple.
In the users own controller design, the UART interface for communication with the Bus Servo must
be handled as shown below.

3.Command Packet
Command packet format

Table 1:

   Header  | ID number | Data Length | Command |   Parameters   | Checksum
 0x55 0x55 |    ID     |   Length    |  Cmd    | Prm 1... Prm N | Checksum

Header: Two consecutive 0x55 are received, indicating the arrival of a data packet.

ID：Each Bus Servo has an ID number. ID numbers range from 0 ~ 253, converted to hexadecimal
0x00 ~ 0xFD. Additionally, there is a broadcast ID: ID No. 254 (0xFE). If the ID number
transmitted by the controller is 254 (0xFE), all Bus Servos will receive the instruction, but
they do not perform the command nor return a response message, (except in the case
of reading the Bus Servo ID number, in that case the servo returns it's servo ID. In this case,
only 1 servo can be attached to the bus at once. Please refer to the following instructions
for details) to prevent bus conflict.

Length(data): Equal to the length of the data to be sent (including its own one byte).
That is, the length of the data plus 3 is equal to the length of this command packet,
including the header and checksum.

Command: The numeric control code to control the various instructions of the Bus Servo,
such as parameter setting, position, speed control, reading back parameters, etc.

Parameters: In addition to commands, parameters are control information that needs to be added.

Checksum: The calculation method is as follows:
             
             Checksum = ~(ID + Length + Cmd + Prm1 +...PrmN)
             
If any of the numbers in the brackets are calculated and exceeded 255, then use the
least significant byte. "~" means Negation.

4.Command type
There are two kinds of commands, write commands and read commands.

Write commands: are normally followed by parameters. Transmit the parameters of the
function to the Bus Servo to complete the corresponding action.

Read commands: are normally, not followed by parameters, when the Bus Servo receives a
read command, it will return the corresponding parameters immediately, the returned command
value is the same as the read command value that was sent to the Bus Servo. So the host
software must immediately prepare to change itself to “read mode” as soon as it sends
a read command.

The following table contains a list of the available commands for the Bus Servos. Specific
details on each command follow the table.

Table 2:
Command name            Command Length
'''
BS_MOVE_TIME_WRITE      =  1 #    7
BS_MOVE_TIME_READ       =  2 #    3
# No commands from 3 - 6
BS_MOVE_TIME_WAIT_WRITE =  7 #    7
BS_MOVE_TIME_WAIT_READ  =  8 #    3
# No commands 9 or 10
BS_MOVE_START           = 11 #    3
BS_MOVE_STOP            = 12 #    3
# BS_ID_WRITE           = 13 #    4 Too dangerous to be included
# BS_ID_READ            = 14 #    3 Useless in a multi servo environment
# No commands 15 or 16
BS_ANGLE_OFFSET_ADJUST  = 17 #    4
BS_ANGLE_OFFSET_WRITE   = 18 #    3
BS_ANGLE_OFFSET_READ    = 19 #    3
BS_ANGLE_LIMIT_WRITE    = 20 #    7
BS_ANGLE_LIMIT_READ     = 21 #    3
BS_VIN_LIMIT_WRITE      = 22 #    7
BS_VIN_LIMIT_READ       = 23 #    3
BS_TEMP_LIMIT_WRITE     = 24 #    4
BS_TEMP_LIMIT_READ      = 25 #    3
BS_TEMP_READ            = 26 #    3
BS_VIN_READ             = 27 #    3
BS_POS_READ             = 28 #    3
BS_MOTOR_MODE_WRITE     = 29 #    7
BS_MOTOR_MODE_READ      = 30 #    3
BS_LOAD_MODE_WRITE      = 31 #    4
BS_LOAD_MODE_READ       = 32 #    3
BS_LED_CTRL_WRITE       = 33 #    4
BS_LED_CTRL_READ        = 34 #    3
BS_LED_ERROR_WRITE      = 35 #    4
BS_LED_ERROR_READ       = 36 #    3
BS_num_params = (2,0,-1,-1,-1,-1,2,0,-1,-1,0,0,-1,-1,-1,-1,1,0,0,2,0,2,0,1,0,0,0,0,2,0,1,0,1,0,1,0)

'''
Command name: For easy identification, the user can also set their own according to their
preference. Command name suffix "_WRITE" which represents write command, and the
suffix "_READ" represents read command.

Command value: The command Cmd value specified in command packet of Table 1

Length: The length of the expected command packet (data length) in table 1

Detailed individual command instructions
1: Command name: BS_MOVE_TIME_WRITE. Command value: 1 Length: 7

When this command is sent to the Bus Servo, the Bus Servo will be rotated from its current angle
to a new angle specified by parameter 1 and 2, at uniform speed, to arrive within the period
specified by the interval in parameter 3 and 4. After the command reaches the Bus Servo,
the Bus Servo will rotate immediately.

Parameter 1: lower 8 bits of the new angle value.

Parameter 2: higher 8 bits of the new angle value. range 0~1000. Corresponding to Bus Servo
angles of 0 ~ 240 °, this means the minimum angle the Bus Servo can be varied by is 0.24 degree.

Parameter 3: lower 8 bits of the time interval value.

Parameter 4: higher 8 bits of the time interval value. the range of time is 0~30000ms. The Bus
Servo's have a maximum speed of rotation of 0.20sec/60°(@ VIn 11.1V).

2. Command name: BS_MOVE_TIME_READ. Command value: 2 Length: 3

When this command is sent to the Bus Servo, the Bus Servo will return the angle and time
value which was last sent by BS_MOVE_TIME_WRITE to the Bus Servo. For details of the command
packet that the Bus Servo returns to the host computer, please refer to the description
in Table 4 below.

3-6. There are no Bus Servo commands with codes between 3 and 6.

7. Command name: BS_MOVE_TIME_WAIT_WRITE. Command value: 7 Length : 7

When this command is sent to the Bus Servo, the function is similar to the BS_MOVE_TIME_WRITE
command. However, the Bus Servo will not immediately rotate when the command arrives at the
Bus Servo, the Bus Servo's rotation will be triggered by BS_MOVE_START (command code 11)
command being sent to Bus Servo (command value 11), then the Bus Servo will be rotated from
the current angle to the specified angle at uniform speed to arrive within the specified
time interval.

Parameter 1: lower 8 bits of the new angle value.

Parameter 2: higher 8 bits of the new angle value. Range 0~1000. Corresponding to Bus
Servo angles of 0 ~ 240 °, this means the minimum angle the Bus Servo can be varied by
is 0.24 degree.

Parameter 3: lower 8 bits of the time interval value. Parameter 4: higher 8 bits of the
time interval value. Range 0~30000ms. The Bus Servo's have a maximum speed of rotation
of 0.20sec/60°(@ VIn 11.1V).

8. Command name: BS_MOVE_TIME_WAIT_READ. Command value: 8 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the preset angle and
preset time value which were sent last by the BS_MOVE_TIME_WAIT_WRITE command to the
Bus Servo. For details of the command packet that the Bus Servo returns to the host computer,
please refer to the description in Table 4 below.

9-10. There are no Bus Servo commands with codes between 9 or 10.

11. Command name: BS_MOVE_START. Command value: 11 Length: 3

When this command is sent to the Bus Servo, it triggers the movement defined in the last
BS_MOVE_TIME_WAIT_WRITE (command code 7) command transmitted to the Bus Servo.

12. Command name: BS_MOVE_STOP. Command value: 12 Length: 3
When this command is sent to the Bus Servo, it will stop rotating immediately.

13. Command name: BS_ID_WRITE. Command value: 13 Length: 4

When this command is sent to the Bus Servo, it changes the ID number of the Bus Servo. Care
should be taken as it is possible to assign an ID number already assigned to another Bus Servo
attached to the UART. In this case, from this point forward, both of Bus Servos now assigned to
that ID number will respond to commands intended for either of te Bus Servos. Any attempts to
reassign the Bus Servo back to it's original ID number will ALSO affect both Bus Servo's too.
YOU SEE THE PROBLEM HERE, RIGHT? The New ID will be written to non-volatile memory and
survive powering-down.

Parameter 1: The NEW Bus Servo ID, range 0 ~ 253, the command will default to 1 if no new ID
is specified.

14. Command name: BS_ID_READ. Command value: 14 Length: 3

When this command is sent to the Bus Servo, the Bus Servo will return the servo ID. This
command is only useful in determining the ID of an unknown Bus Servo. In this case, transmit
the broadcast servo ID 254 (0xFE) and the Bus Servo will return it's own ID. This can only be
achieved with one Bus Servo attached to the UART. For the details of the command package that
the Bus Servo returns to the host computer, please refer to the description in Table 4 below.

17. Command name: BS_ANGLE_OFFSET_ADJUST. Command value: 17 Length: 4

When this command is sent to the Bus Servo, it adjusts the offset of the Bus Servo rotation.
The new value is not saved when the Bus Servo is powered-down, if you want the value to
survive powering-down follow this command with command 18 below.

Parameter 1: Bus Servo offset, range -125 ~ +125, The corresponding angle of -30 ° ~ 30 °,
when this command reaches the Bus Servo, the Bus Servo will immediately rotate to correct
for the new offset value. Because the parameter is a signed integer, and the command packets
to be sent are bytes, before sending, the parameter must be converted to unsigned data and
then appended to the command packet.

18. Command name: BS_ANGLE_OFFSET_WRITE. Command value: 18 Length: 3

When this command is sent to the Bus Servo, it saves the current offset value into non
volatile memory to survive power-down. The adjustment of the offset is achieved using
command 17, above.

19. Command name: BS_ANGLE_OFFSET_READ. Command value: 19 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the offset value. For details
of the command packet that the Bus Servo returns to the host computer, please refer to the
description in Table 4 below. Because the parameter is a signed integer, and the command
packets to be sent are bytes, after receiving, the parameter must be converted from unsigned
data when it stripped from the command packet.

20. Command name: BS_ANGLE_LIMIT_WRITE. Command value: 20 Length: 7

When this command is sent to the Bus Servo, it sets the minimum and maximum limits on the
rotation of the Bus Servo. The minimum angle value should always be less than the maximum
angle value. The values will be saved into non volatile memory to survive power-down.

Parameter 1: lower 8 bits of minimum angle

Parameter 2: higher 8 bits of minimum angle, range 0 ~ 1000

Parameter 3: lower 8 bits of maximum angle

Parameter 4: higher 8 bits of maximum angle, range 0 ~ 1000, > lower limit

21. Command name: BS_ANGLE_LIMIT_READ. Command value: 21 Length: 3

When this command is sent to the Bus Servo, the Bus Servo retunrs both of the angle limit
values of the Bus Servo, for the details of the instruction packet that the Bus Servo returns
to host computer, please refer to the description in Table 4 below.

22. Command name: BS_VIN_LIMIT_WRITE. Command value: 22 Length: 7

When this command is sent to the Bus Servo, it sets the lower and upper voltage alarm values.
Voltage supplies outside these limits will cause the Bus Servo to transmit an error code,
cause the LED to flash and alarm (if an LED alarm is set). In order to protect the Bus Servo,
the motor will switch to "unloaded", and the Bus Servo will not output torque. The values
will be saved into non volatile memory to survive power-down. The minimum input voltage
should always be less than the maximum input voltage. The working voltage range of the
HiWonder LX-824HV Bus Servo is 9-12.6 volts.

Parameter 1: lower 8 bits of minimum input voltage

Parameter 2: higher 8 bits of minimum input voltage, range 4500~12000mv

Parameter 3: lower 8 bits of maximum input voltage

Parameter 4: higher 8 bits of maximum input voltage, range 4500~12000mv, > lower limit. 

23. Command name: BS_VIN_LIMIT_READ. Command value: 23 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns both the lower and higher
voltage input limit values, for the details of the instruction packet that the Bus Servo
returns to the host computer, please refer to the description in Table 4 below.

24. Command name: BS_TEMP_LIMIT_WRITE. Command value: 24 Length: 4

When this command is sent to the Bus Servo, it sets the upper temperature alarm value.
High temperatures inside the Bus Servo are caused by the Bus Servo working against high loads.
Temperatures within the Bus Servo in excess of this limit will cause the Bus Servo to transmit
an error code, cause the LED to flash and alarm (if an LED alarm is set). In order to protect
the Bus Servo, the motor will switch to "unloaded", and the Bus Servo will not output torque
until the Bus Servo measures a temperature below this limit, then the Bus Servo will switch
back to "loaded". The value will be saved into non volatile memory to survive power-down.

Parameter 1: The maximum temperature limit inside the Bus Servo. Range 50~100°C. The default
value is 85°C.

25. Command name: BS_TEMP_LIMIT_READ. Command value: 25 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the maximum internal
temperature limit of the Bus Servo, for details of the command package that the Bus Servo
returns to the host computer, please refer to the description in Table 4 below.

26. Command name: BS_TEMP_READ. Command value: 26 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the real-time temperature
inside the Bus Servo, for details of the instruction packet that the Bus Servo returns to host
computer, please refer to the description in Table 4 below.

27. Command name: BS_VIN_READ. Command value: 27 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns real time input voltage of the
Bus Servo, for the details of the instruction packet that the SB returns to the host computer,
please refer to the description in Table 4 below.

28. Command name: BS_POS_READ. Command value: 28 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the real time angle value of
the Bus Servo, for the details of the instruction packet that the Bus Servo returns to the host
computer, please refer to the description in Table 4 below.

29. Command name: BS_MOTOR_MODE_WRITE. Command value: 29 Length: 7

When this command is sent to the Bus Servo, it switches Bus Servo between servo mode and motor
mode. In motor mode, the Bus Servo can be used as a DC reduction motor with adjustable speed;
In position control mode, the Bus Servo has 240° of rotation range with Plus ± 30° adjustable
offset available, with high precise position control & adjustable speed. Since the rotation
speed is a signed short integer, it must be forcibly to unsinged bytes before sending the
command packet.

Parameter 1: Bus Servo mode. 0 for position control (servo) mode, 1 for motor control
(continuous rotation) mode, default 0.

Parameter 2: null value

Parameter 3: lower 8 bits of rotation speed value

Parameter 4: higher 8 bits of rotation speed value. range -1000 ~ +1000, this is only valid for
motor (continuous rotation) control mode, to control the rotation speed of the motor.
Negative values represent reverse speeds, positive values represent forward speeds.
The motor mode and rotation speed do not survive power-down.

30. Command name: BS_MOTOR_MODE_READ. Command value: 30 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the motor mode and rotation
speed values of the Bus Servo. Because the rotation parameter is a signed integer, and the
command packets to be sent are bytes, after receiving, the parameter must be converted from
unsigned data when it stripped from the command packet. For the details of the command package
that the Bus Servo returns to the host computer, please refer to the description in Table 4 below.

31. Command name: BS_LOAD_MODE_WRITE. Command value: 31 Length: 4

When this command is sent to the Bus Servo, it sets the Bus Servo to unloaded (no torque output)
or loaded (high torque output).

Parameter 1: Range 0 or 1. 0 represents unloaded, the Bus Servo has no torque output.
1 represents loaded, the Bus Servo has high torque output, the default value is 0. The
loaded mode does not survive power-down.

32. Command name: BS_LOAD_MODE_READ Command value: 32 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the load state of the
Bus Servo. For details of the command package that the Bus Servo returns to host computer,
please refer to the description of Table 4 below.

33. Command name: BS_LED_CTRL_WRITE. Command value: 33 Length: 4

When this command is sent to the Bus Servo, it switches the status of the LED.

Parameter 1: LED light/off state. Range 0 or 1. 0 represents LED always on. 1 represents
LED off. The default is 0. The value will be saved into non volatile memory to
survive power-down.

34. Command name: BS_LED_CTRL_READ Command value: 34 Length: 3

When this command is sent to the Bus Servo, the Bus Servo returns the state of the LED. Range
0 or 1. 0 represents LED always on. 1 represents LED off. For the details of the command packet
that the Bus Servo returns to host computer, please refer to the description of Table 4 below.

35. Command name: BS_LED_ERROR_WRITE Command value: 35 Length: 4

When this command is sent to the Bus Servo, it determines what faults will cause the LED to
flash alarm.

Parameter 1: Range 0~7 There are three types of faults that cause the LED to flash and alarm,
regardless of whether the LED is in or off mode. The first fault is that internal temperature
of the Bus Servo exceeds the maximum temperature limit (this value is set with command 24, the
limit is read with command 25 and the real time value is read with command 26). The second
fault is that the Bus Servo input voltage exceeds the limit values (this value is set with
command 22, the limit is read with command 23 and the real time value is read with command 27).
The third fault is when the Bus Servo rotor becomes locked. The fault codes are as shown below:

Table 3:
      0      No alarm
      1      Over temperature
      2      Over voltage
      3      Over temperature and over voltage
      4      ocked_rotor
      5      Over temperature and ocked_rotor
      6      Over voltage and ocked_rotor
      7      Over temperature , over voltage and locked_rotor

36. Command name: BS_LED_ERROR_READ command value: 36 Length: 3

Read the Bus Servo fault alarm value. The values are as above. For the details of the
command packet that the Bus Servo returns to thehost computer, please refer to the
description of Table 4 below.

List of read commands:
Table 4:
Command name           Command Length
BS_MOVE_TIME_READ         2       7
BS_MOVE_TIME_WAIT_READ    8       7
BS_ID_READ               14       4
BS_ANGLE_OFFSET_READ     19       4
BS_ANGLE_LIMIT_READ      21       7
BS_VIN_LIMIT_READ        23       7
BS_TEMP_LIMIT_READ       25       4
BS_TEMP_READ             26       4
BS_VIN_READ              27       5
BS_POS_READ              28       5
BS_MOTOR_MODE_READ       30       7
BS_LOAD_MODE_READ        32       4
BS_LED_CTRL_READ         34       4
BS_LED_ERROR_READ        36       4
'''

BS_inactive_rcmds = (1,3,4,5,6,7,9,10,11,12,13,15,16,17,18,20,22,24,29,31,33,35)

'''
Table 4 lists the commands that the Bus Servo returns to the host computer. These commands
will only be returned when the host computer has sent a read command to the Bus Servo.
What’s more, the returned command value is consistent with the read command that the host
computer sent to the Bus Servo. The difference is that the returned command has parameters.
The format of the returned data command packet is the same as the command package that
the host computer sent to Bus Servo, as in Table 1.

Detailed individual command instructions
2. Command name: BS_MOVE_TIME_READ. Command value: 2 Length: 7

The Bus Servo returns the angle and time value which was last sent by BS_MOVE_TIME_WRITE to the
host computer.

Parameter 1: lower 8 bits of angle value

Parameter 2: higher 8 bits of angle, range 0 ~ 1000

Parameter 3: lower 8 bits of time value

Parameter 4: higher 8 bits of time value, range 0 ~ 30000ms

8. Command name: BS_MOVE_TIME_WAIT_READ. Command value: 8 Length: 7

The Bus Servo returns the preset angle and preset time value which were sent last by the
BS_MOVE_TIME_WAIT_WRITE command to the host computer.

Parameter 1: lower 8 bits of preset angle value

Parameter 2: higher 8 bits of preset angle, range 0 ~ 1000

Parameter 3: lower 8 bits of preset time value

Parameter 4: higher 8 bits of preset time value, range 0 ~ 30000ms

14. Command name: BS_ID_READ. Command value: 14 Length: 4

The Bus Servo returns the servo ID. ID read is a little bit special compared with other read
commands. If the command packet ID is the broadcast ID 254 (0xFE), the Bus Servo will return
the response information. Other read commands will not respond when the ID is the broadcast ID.
The purpose of this design is to acquire the Bus Servo ID number of Bus Servos whose ID is
unknown. However the limit is that the bus can only be attached to a single Bus Servo, or it
will cause a bus conflict.

Parameter 1: Bus Servo ID value

19. Command name: BS_ANGLE_OFFSET_READ. Command value: 19 Length: 4

The Bus Servo returns the offset value. Because the parameter is a signed integer, and the
command packets to be sent are bytes, after receiving, the parameter must be converted from
unsigned data when it stripped from the command packet.

Parameter 1: The offset set by the Bus Servo, range -125 ~ +125

21. Command name: BS_ANGLE_LIMIT_READ. Command value: 21 Length: 7

The Bus Servo returns both of the angle limit values of the Bus Servo.

Parameter 1: lower 8 bits of minimum angle value

Parameter 2: higher 8 bits of minimum angle, range 0 ~ 1000

Parameter 3: lower 8 bits of maximum angle value

Parameter 4: higher 8 bits of maximum angle value, range 0 ~ 1000

23. Command name: BS_VIN_LIMIT_READ. Command value: 23 Length: 7

The Bus Servo returns both the lower and upper voltage input limit values.

Parameter 1: lower 8 bits of input voltage value

Parameter 2: higher 8 bits of input voltage value ,range 4500~12000mv

Parameter 3: lower 8 bits of maximum input voltage value

Parameter 4: higher 8 bits of maximum input voltage value,range 4500~12000mv

25. Command name: BS_TEMP_LIMIT_READ. Command value: 25 Length: 4

The Bus Servo returns the maximum internal temperature limit of the Bus Servo.

Parameter 1: The maximum temperature limit inside the Bus Servo, range 50~100°C

26. Command name: BS_TEMP_READ. Command value: 26 Length: 4

The Bus Servo returns the real-time temperature inside the Bus Servo.

Parameter 1: The real time temperature inside the Bus Servo

27. Command name: BS_VIN_READ. Command value: 27 Length: 5

The Bus Servo returns real time input voltage of the Bus Servo.

Parameter 1: lower 8 bits of current input voltage value

Parameter 2: higher 8 bits of current input voltage value, no default

28. Command name BS_POS_READ. Command value: 28 Length: 5

The Bus Servo returns the real time angle value of the Bus Servo.

Parameter 1: lower 8 bits of current Bus Servo position value

Parameter 2: higher 8 bits of current Bus Servo position value

30. Command name: BS_MOTOR_MODE_READ Command value: 30 Length: 7

The Bus Servo returns the motor mode and rotation speed values of the Bus Servo.
Because the rotation parameter is a signed integer, and the command packets to be sent are
bytes, after receiving, the parameter must be converted from unsigned data when it stripped
from the command packet.

Parameter 1: The current mode of the Bus Servo, 0 for the position control (servo) mode,
1 for the motor control (continuous rotation) mode, the default 0

Parameter 2: Null, set to 0

Parameter 3: lower 8 bits of rotation speed value

Parameter 4: higher 8 bits of rotation speed value. Range -1000 ~ +1000. Only valid in motor
control mode. Negative values represent reverse rotation, positive values represent forward
rotation.

32. Command name: BS_LOAD_MODE_READ. Command value: 32 Length: 4

The Bus Servo returns the load state of the Bus Servo.

Parameter 1: Whether the Bus Servo is loaded/unloaded. Range 0 or 1. 0 represents unloaded,
no torque output. 1 represents loaded, high torque output.

34. Command name: BS_LED_CTRL_READ. Command value: 34 Length: 4

The Bus Servo returns the state of the LED. Range 0 or 1. 0 represents LED always on. 1
represents LED off.

Parameter 1: LED light on/off state.

36. Command name: BS_LED_ERROR_READ. Command value: 36 Length: 4

The Bus Servo returns the fault alarm code. The values are as below.

Parameter 1: What faults in the Bus Servo are causing the LED to flash and alarm, range 0~7.
'''
BS_no_alarm = 0
BS_over_temp_alarm = 1
BS_over_volt_alarm = 2
BS_over_temp_volt_alarm = 3
BS_locked_rotor_alarm = 4
BS_over_temp_locked_rotor_alarm = 5
BS_over_voltage_locked_rotor_alarm = 6
BS_over_temp_volt_locked_rotor = 7
'''
The corresponding relationship between the numerical value and the faults are shown in table 3.'''

# Bus Servo parameters
BS_servo_type = "LX-224HV" # Manufacturer/model of the servo
BS_num_servos = 18 # Number of servos of this type on the robot
BS_rotate_limits = (0, 1000) # Miminum & maximum values for full defection
BS_cont_speed = (-1000, 1000) # Range of continuous rotation speeds
BS_max_speed = 1250
# HiWonder LX-824HV Bus Servos have a maximum speed of rotation of 0.20sec/60°(@ VIn 11.1V).
# With a maximum rotation of 0 ~ 240° defined as a range of 1-1000.
BS_time_limits = (0, 30000) # Minimum & maximum time durations
BS_offset_limits = (-125, 125)  # Minimum & maximum offset values
# Offsets can be set between angles of -30 ° ~ 30 °
BS_Vin_limits = (9000, 12600) # Voltage limits specified in mV
# Servos allow voltage limits to be set from 4500mV to 14000mV but the operating voltage of the
# servos is  9-12.6V
BS_temp_limits = (50, 85) # Temperature limit in °C. The limit can be set between 50 ~ 100°C.
BS_default_pos = 500 # The default position for 50% rotation

# PWM servo parameters
PWM_servo_type = "PWM_generic" # Manufacturer/model of the servo
PWM_num_servos = 2 # Number of servos of this type on the robot
PWM_rotate_limits = (500, 2500) # Miminum & maximum number of pulses for full defection
PWM_time_limits = (20, 5000) # Minimum & maximum time to reach destination
PWM_offset_limits = (-300, 300) # Minimum & maximum offset values
PWM_offsets = (0,0) # The PWM servos have no internal memory so the offsets have to be set here
PWM_freq = 50 # PWM frequency
PWM_default_pos = 1500 # The default position for straight ahead


if __name__ == '__main__':
    print("This file just contains environment variables. It doesn't do anything")
