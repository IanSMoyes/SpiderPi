#!/usr/bin/python3
# encoding: utf-8
# Copyright HiWonder.hk
# Further development by ians.moyes@gmail.com
# Translation by Google
# 配置串口舵机的参数 Configure the parameters of the serial servo
# 每次只能配置一个舵机，且树莓派扩展板只能连接一个舵机，既是一个舵机一个舵机配置参数
# Only one servo can be configured at a time,
# and only one servo can be connected to the Raspberry Pi expansion board,
# which is a servo configuration parameter for one servo

# Library to enquire and set the ID number of a SINGLE Serial Bus Servo

import serial # Standard library to define serial ports
import pigpio # Standard library to control the GPIO interface
import time # Standard library of time, diary & calendar functions

SERVO_FRAME_HEADER = 0x55 # Assign servo controller command codes

pi = pigpio.pi()  # 初始化 pigpio库 Initialize the pigpio library

BSS_UART = serial.Serial("/dev/ttyAMA0", 115200)  # 初始化串口， 波特率为115200
                                                    # Initialize the UART, baud rate 115200

# This port is used as a switch to tell the Raspberry Pi Expansion Boad whether it should
# expect data or it is expected to send data
def portInit():  # 配置用到的IO口 Configure an IO port
    pi.set_mode(17, pigpio.OUTPUT)  # 配置RX_CON 即 GPIO17 为输出
                                    # Configure RX_CON on GPIO17 as output
    pi.write(17, 0) # Pulldown RX_CON
    pi.set_mode(27, pigpio.OUTPUT)  # 配置TX_CON 即 GPIO27 为输出
                                    # Configure TX_CON on GPIO27 as output
    pi.write(27, 1) # Pullup TX_CON

portInit()

def portWrite():  # 配置单线串口为输出 Configure IO port as output
    pi.write(27, 1)  # 拉高TX_CON 即 GPIO27 Pullup TX_CON (GPIO27)
    pi.write(17, 0)  # 拉低RX_CON 即 GPIO17 Pulldown RX_CON (GPIO17)

def portRead():  # 配置单线串口为输入 Configure IO port as input
    pi.write(17, 1)  # 拉高RX_CON 即 GPIO17 Pullup RX_CON (GPIO17) 
    pi.write(27, 0)  # 拉低TX_CON 即 GPIO27 Pulldown TX_CON (GPIO27)

def portRest():
    time.sleep(0.1) # Pause
    BSS_UART.close() # Close the UART
    pi.write(17, 1) # GPIO17 Pullup RX_CON (GPIO17)
    pi.write(27, 1) # GPIO27 Pullup TX_CON (GPIO27)
    BSS_UART.open() # Open te UART
    time.sleep(0.1) # Pause

def checksum(buf):
    ''' 计算校验和 Calculate the checksum
    :param buf: data frame to be transmitted
    :return: checksum to be appended
    '''
    sum = 0x00
    for b in buf:  # 求和 scan the buffer
        sum += b # sum the contents of the buffer
    sum = sum - 0x55 - 0x55  # 去掉命令开头的两个
    # 0x55 Remove the 2 0x55 at the beginning. The frame header of the command
    sum = ~sum  # 取反 Negate the sum (change the sign)
    return sum & 0xff # return the 8 least significant bits

def serial_servo_write_ID(id, newID):
    '''
    Send change ID command to the servo controller
    :param id: servo ID to be written to
    :param newid: new servo ID
    :return: Error code or True = Success
    '''
    
    portWrite() # Configure IO port as output

    buf = bytearray(b'\x55\x55')  # 帧头 Data frame header
    
    buf.append(id) # Append the servo ID
    
    buf.append(4) # 指令长度 Append the instruction length

    buf.append(13)  # 指令 Append the command

    buf.append(newID & 0xff) # 写数据 Append the parameters

    buf.append(checksum(buf)) # 校验和 Append the checksum

    BSS_UART.write(buf)  # 发送 Transmit data frame over UART
    return True

def serial_servo_read_ID():
    '''
    发送读取命令 Send request for servo ID to the servo controller
    This was 2 functions in the original. Now combined.
    No servo ID needs to be sent as we'll be using the broadcast ID 254
    :return: 数据 Servo ID returned from the servo controller
    '''

    portWrite() # Configure IO port as output

    buf = bytearray(b'\x55\x55')  # 帧头 Data frame header
    
    buf.append(254) # Append the servo ID
    
    # 指令长度 Append the instruction length
    buf.append(3)

    buf.append(14)  # 指令 Append the command
    
    buf.append(checksum(buf)) # 校验和 Append the checksum
    
    BSS_UART.write(buf)  # 发送 Transmit data frame over UART

    time.sleep(0.00034) # Pause for an oddly specific period of time

    BSS_UART.flushInput()  # 清空接收缓存 Clear the UART receive buffer
    portRead()  # 将单线串口配置为输入 Configure IO port as input
    time.sleep(0.005)  # 稍作延时，等待接收完毕 Pause while the data reception is completed
    count = BSS_UART.inWaiting()    # 获取接收缓存中的字节数 Get the receive buffer length (bytes)
    if count != 0:  # 如果接收到的数据不空 If the buffer is not empty
        recv_data = BSS_UART.read(count)  # 读取接收到的数据 Read the buffer
        # for i in recv_data: # Scan the data
        #     print('%#x' %ord(i)) # Print the unicode integer
        # 是否是读id指令 Is it a read id command
        try:
# Does the data start with a valid header & does the command code match the expected one
            if recv_data[0] == 0x55 and recv_data[1] == 0x55 and recv_data[4] == 14:
                return recv_data[5] # Answer to the question we asked
            else:
                return None # If the data frame was corrupt
        except BaseException as e: # If it all went wrote
            print(e) # Print the explanation
    else: # If the buffer was empty
        BSS_UART.flushInput()  # 清空接收缓存 Clear the UART receive buffer
        return None

if __name__ == '__main__':
    portInit() # Clear the UART port
    
    ID = serial_servo_read_ID() # Read the current ID
    if type(ID) != int or ID < 0 or ID > 254:
        print("Servo ID read failed. Is there more than 1 servo attached to the bus?")
    else:
        print("The servo attached to the bus is ID number: " + str(ID))
    
        OK = False # Set repeat switch
        while not OK: # Repeat until satisfied
            newID = int(input("What ID number do you want to assign? ")) # Ask for the new ID

            if newID < 0 or newID > 253: print("Invalid servo ID") # Validate the new ID number
            else:
                results = serial_servo_write_ID(ID, newID) # Change the ID number
                OK = True # Set the repeat switch
                print("The result of changing the servo ID was " + str(results))
