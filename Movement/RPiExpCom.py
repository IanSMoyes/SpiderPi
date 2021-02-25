#!/usr/bin/python3
# encoding: utf-8
# Copyright HiWonder.hk
# Further development by ians.moyes@gmail.com
# Translation by Google

# Library to control the Bus Serial Servo Control Raspberry Pi expansion board

import serial # Standard library to define serial ports
import time # Standard library of time, diary & calendar functions
import ctypes # Standard library to manipulate C++ number types

SERVO_FRAME_HEADER = b'\x55\x55' # Define data frame header
TRINKET_FRAME_HEADER = b'\x25\x25' # Define data frame header

UART = serial.Serial("/dev/ttyAMA0", 115200)  # 初始化串口， 波特率为115200
                                                  # Initialize the UART, baud rate 115200

# This port is used as a switch to tell the Raspberry Pi Expansion Boad whether it should
# expect data or it is expected to send data over the UART
def portinit(pi):
    import pigpio # Standard Raspberry Pi GPIO library
    pi.set_mode(17, pigpio.OUTPUT)  # 配置RX_CON 即 GPIO17 为输出
                                    # Configure RX_CON on GPIO17 as output
    pi.write(17, 0) # Pulldown RX_CON
    pi.set_mode(27, pigpio.OUTPUT)  # 配置TX_CON 即 GPIO27 为输出
                                    # Configure TX_CON on GPIO27 as output
    pi.write(27, 1) # Pullup TX_CON

def portWrite(pi):  # 配置单线串口为输出 Switch the Raspberry Pi expansion board to read mode
    pi.write(17, 0)  # 拉低RX_CON 即 GPIO17 Pulldown RX_CON (GPIO17)
    pi.write(27, 1)  # 拉高TX_CON 即 GPIO27 Pullup TX_CON (GPIO27)

def portRead(pi):  # 配置单线串口为输入 Switch the Raspberry Pi expansion board to read mode
    pi.write(17, 1)  # 拉高RX_CON 即 GPIO17 Pullup RX_CON (GPIO17) 
    pi.write(27, 0)  # 拉低TX_CON 即 GPIO27 Pulldown TX_CON (GPIO27)

def portReset(pi): # Reset the Raspberry Pi expansion board
    time.sleep(0.1) # Pause
    UART.close() # Close the UART
    pi.write(17, 1) # GPIO17 Pullup RX_CON (GPIO17)
    pi.write(27, 1) # GPIO27 Pullup TX_CON (GPIO27)
    UART.open() # Open the UART
    time.sleep(0.1) # Pause

def portOff(pi): # Close the Raspberry Pi expansion board
    UART.close() # Close the UART
    pi.write(17, 0) # GPIO17 Pulldown RX_CON (GPIO17)
    pi.write(27, 0) # GPIO27 Pulldown TX_CON (GPIO27)

def checksum(buf):
    ''' 计算校验和 Calculate the checksum
    :param buf: data frame to be transmitted
    :param header: data frame header
    :return: checksum to be appended
    '''
    sum = 0x00
    for b in buf:  # 求和 scan the buffer
        sum += b # sum the contents of the buffer
    sum = ~sum  # 取反 Negate the sum (change the sign)
    return sum & 0xff # return the 8 least significant bits

def serial_servo_write_cmd(pi, id, w_cmd, dat1=None, dat2=None):
    '''
    写指令 Send command to the Raspberry Pi expansion board
    :param id: servo ID to be written to
    :param w_cmd: The servo command to send
    :param dat1: First servo command parameter
    :param dat2: Second servo command parameter
    :return: Error code or True = Success
    '''

    portWrite(pi) # Switch Raspberry Pi expansion board to write mode

    buf = bytearray()

    buf.append(id) # Append the servo ID

    if dat2 is not None: # 指令长度 Determine & append the data frame length
        buf.append(7)
    elif dat1 is not None:
        buf.append(4)
    else: buf.append(3)

    buf.append(w_cmd)  # 指令 Append the servo command

    # 写数据 Append the parameters
    if dat2 is not None: # If there are 2 parameters
        # Append the least significant & next least significant 8 bits of the 1st parameter
        buf.extend([(0xff & dat1), (0xff & (dat1 >> 8))])  # 分低8位 高8位 放入缓存
        # Append the least significant & next least significant 8 bits of the 2nd parameter
        buf.extend([(0xff & dat2), (0xff & (dat2 >> 8))])  # 分低8位 高8位 放入缓存
    elif dat1 is not None: # If there is 1 parameter
        buf.append(dat1 & 0xff) # Append the least significant 8 bits of the parameter

    buf.append(checksum(buf)) # 校验和 Append the checksum

    frame = bytearray(SERVO_FRAME_HEADER) + buf  # 帧头 Prepend the data frame header

    UART.write(frame)  # 发送 Transmit data frame over UART

    return True # Tell the World how clever you were

def serial_servo_read_cmd(pi, id, r_cmd):
    '''
    发送读取命令 Send request for data to the Raspberry Pi expansion board & return result
    :param id: servo_id to be interrogated
    :param r_cmd: The servo command to be responded to
    :return: 数据 Data returned from the servo
    '''

    prev = time.time() # Take a time stamp
    UART.flushInput()  # 清空接收缓存 Clear the UART receive buffer
    while time.time() < prev + 1: # Repeat for 1 second
        write_ok = serial_servo_write_cmd(pi, id, r_cmd) # Write data
        if write_ok == True: # If the write command succeeded

            time.sleep(0.00034) # Pause for an oddly specific period of time
        
            portRead(pi)  # 将单线串口配置为输入 Switch UART to read mode

            for i in range(20): # Repeat 5 times
                results = collect_serial_servo_data(r_cmd) # Read the data back
                if results != None: # If data is collected
                    return results # Send it back

    return "Comms" # If it just didn't work, report

def collect_serial_servo_data(r_cmd):
    time.sleep(0.00034) # Pause for an oddly specific period of time
    # time.sleep(0.005)  # 稍作延时，等待接收完毕 Pause while the data reception is completed
    count = UART.inWaiting() # 获取接收缓存中的字节数 Get the receive buffer length (bytes)
    if count != 0: # 如果接收到的数据不空 If the buffer is not empty
        recv_data = UART.read(count) # 读取接收到的数据 Read the buffer
        UART.flushInput() # 清空接收缓存 Clear the buffer
        try:
            data_ok = recv_data[-1] == checksum(recv_data[2:-1]) # Do the checksums match?
            data_ok = data_ok and recv_data[4] == r_cmd # Do the receive commands match?
            # Does the data have a valid header
            data_ok = data_ok and recv_data[0:2] == SERVO_FRAME_HEADER
            if data_ok:
                dat_len = recv_data[3] # Extract the length of the data (excluding frame header)
                if dat_len == 4: # 1 parameter
                    return recv_data[5] # Answer to the question we asked
                elif dat_len == 5: # 2 parameters
                    pos = 0xffff & (recv_data[5] | (0xff00 & (recv_data[6] << 8)))
                    return ctypes.c_int16(pos).value
                elif dat_len == 7: # 4 Parameters
                    pos1 = 0xffff & (recv_data[5] | (0xff00 & (recv_data[6] << 8)))
                    pos2 = 0xffff & (recv_data[7] | (0xff00 & (recv_data[8] << 8)))
                    return ctypes.c_int16(pos1).value, ctypes.c_int16(pos2).value
        except BaseException as e: # If it all went wrong
            print(e) # Print the explanation
    return None # If the data frame was empty, or corrupt

def TrinketM0_write_data(id, colour):
    '''
    Send data to the TrinketM0 via the Raspberry Pi expansion board
    :param id: LED ID to be addressed 0 ~ 11 = face lights, 12 = head/tail lights
    :param colour: the colour, or direction codes to be transmitted
    :return: Error code or True = Success
    '''

    buf = bytearray()

    buf.append(id) # Start with the LED ID

    for i in colour: buf.append(i) # Append the colour data

    buf.append(checksum(buf)) # Append the checksum

    frame = bytearray(TRINKET_FRAME_HEADER) + buf  # Prepend the data frame header

    frame += b'\n' # So that you can send a line end designated line at a time

    UART.write(frame)  # Transmit data frame over UART
    return True # Tell the World how clever you were

if __name__ == '__main__':
    import config # Environment variables
    
    # pigpio requires the pigpiod daemon to be running in the background first
    import pigpio # Standard Raspberry Pi GPIO library
    pi = pigpio.pi() # Create a Raspberry Pi object
    portinit(pi) # Initialise the read/write switch

    print(str(config.BS_num_servos), config.BS_servo_type, "servos under test.")
    portReset(pi) # Reset the Raspberry Pi expansion board
    
    for i in range(config.BS_num_servos): # For every servo
        id = i + 1 # Loops are 0 indexed, servos are 1 indexed

        print('Interrogating servo ID:', id) # Print title

        pos = serial_servo_read_cmd(pi, id, config.BS_POS_READ) # Reading servo position. Command 28
        print('Position:', pos)

        if type(pos) == int: # If a valid position returned
            # Reading servo rotation limits. Command 21
            limits = serial_servo_read_cmd(pi, id, config.BS_ANGLE_LIMIT_READ)
            print("Rotation limits:", limits)

            if pos < limits[0]: pos = limits[0] # Clamp out of range positions
            elif pos > limits[1]: pos = limits[1]

            # If the servo is near it's lower limit avoid it
            if pos < limits[0] + 20: newpos = pos + 20
            else: newpos = pos - 20

            print("Wiggling servo to new position ", newpos)
            # Move the servo. Command 1
            serial_servo_write_cmd(pi, id, config.BS_MOVE_TIME_WRITE, newpos, 500)
            time.sleep(0.6) # Wait until it finishes moving
            print("Wiggling servo to original position ", pos)
            # Move the servo back. Command 1
            serial_servo_write_cmd(pi, id, config.BS_MOVE_TIME_WRITE, pos, 500)
        print(" ")
    print(" ")
    print("Servo tests complete!")
