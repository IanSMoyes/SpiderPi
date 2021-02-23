# coding: utf-8
## @package MPU9250
#  This is a FaBo9Axis_MPU9250 library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

# further development by ians.moyes@gmail.com

import smbus2 as smbus
import time

## MPU6050 Default I2C slave address
SLAVE_ADDRESS        = 0x68
## AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
## Device id
DEVICE_ID            = 0x71

# MPU6050 Register Addresses
## sample rate driver
SMPLRT_DIV     = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR   = 0x1E
WOM_THR        = 0x1F
FIFO_EN        = 0x23
I2C_MST_CTRL   = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG    = 0x37
INT_ENABLE     = 0x38
INT_STATUS     = 0x3A
ACCEL_OUT      = 0x3B
TEMP_OUT       = 0x41
GYRO_OUT       = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL    = 0x69
USER_CTRL          = 0x6A
PWR_MGMT_1         = 0x6B
PWR_MGMT_2         = 0x6C
FIFO_R_W           = 0x74
WHO_AM_I           = 0x75

## Gyro Full Scale Select 250dps
GFS_250  = 0x00
## Gyro Full Scale Select 500dps
GFS_500  = 0x01
## Gyro Full Scale Select 1000dps
GFS_1000 = 0x02
## Gyro Full Scale Select 2000dps
GFS_2000 = 0x03

GFS = {GFS_250: 250.0/32768.0,
       GFS_500: 500.0/32768.0,
       GFS_1000: 1000.0/32768.0,
       GFS_2000: 2000.0/32768.0}

## Accel Full Scale Select 2G
AFS_2G   = 0x00
## Accel Full Scale Select 4G
AFS_4G   = 0x01
## Accel Full Scale Select 8G
AFS_8G   = 0x02
## Accel Full Scale Select 16G
AFS_16G  = 0x03

AFS = {AFS_2G: 2.0/32768.0,
       AFS_4G: 4.0/32768.0,
       AFS_8G: 8.0/32768.0,
       AFS_16G: 16.0/32768.0}

# AK8963 Register Addresses
AK8963_ST1        = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1      = 0x0A
AK8963_CNTL2      = 0x0B
AK8963_ASAX       = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN   = 0x00
## One shot data output
AK8963_MODE_ONE    = 0x01

## Continous data output 8Hz
AK8963_MODE_C8HZ   = 0x02
## Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
## 14bit output
AK8963_BIT_14 = 0x00
## 16bit output
AK8963_BIT_16 = 0x01

AK8963_BIT = {AK8963_BIT_14: 4912.0/8190.0, AK8963_BIT_16: 4912.0/32760.0}
              
bus = smbus.SMBus(1)

## MPU9250 I2C Control class
class MPU9250:

    ## Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address
        self.configMPU6050(GFS_250, AFS_2G)
        self.configAK8963(AK8963_MODE_C8HZ, AK8963_BIT_16)

    ## Search Device
    #  @param [in] self The object pointer.
    #  @retval true device connected
    #  @retval false device error
    def searchDevice(self):
        who_am_i = bus.read_byte_data(self.address, WHO_AM_I)
        if(who_am_i == DEVICE_ID):
            return True
        else:
            return False

    ## Configure MPU-9250
    #  @param [in] self The object pointer.
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU6050(self, gfs, afs):
        self.gres = GFS[gfs] # Set scaling
        self.ares = AFS[afs]

        # sleep off
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # DLPF_CFG
        bus.write_byte_data(self.address, CONFIG, 0x03)
        # sample rate divider
        bus.write_byte_data(self.address, SMPLRT_DIV, 0x04)
        # gyro full scale select
        bus.write_byte_data(self.address, GYRO_CONFIG, gfs << 3)
        # accel full scale select
        bus.write_byte_data(self.address, ACCEL_CONFIG, afs << 3)
        # A_DLPFCFG
        bus.write_byte_data(self.address, ACCEL_CONFIG_2, 0x03)
        # BYPASS_EN
        bus.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    ## Configure AK8963
    #  @param [in] self The object pointer.
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def configAK8963(self, mode, mfs):
        self.mres = AK8963_BIT[mfs]

        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self.magcoef = ((data[0] - 128) / 256.0 + 1.0,
                        (data[1] - 128) / 256.0 + 1.0,
                        (data[2] - 128) / 256.0 + 1.0)

        # set power down mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set scale&continous mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs<<4|mode))
        time.sleep(0.01)

    ## brief Check data ready
    #  @param [in] self The object pointer.
    #  @retval True data is ready
    #  @retval False data is not ready
    def MPU6050DataReady(self):
        drdy = bus.read_byte_data(self.address, INT_STATUS)
        if drdy & 0x01:
            return True
        else:
            return False

    ## Read accelerometer
    #  @param [in] self The object pointer.
    #  @retval output (x-axis data,y-axis data, z-axis data)
    def readAccel(self):
        data = bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        output = ()
        output += (round(self.dataConv(data[1], data[0])*self.ares,3), )
        output += (round(self.dataConv(data[3], data[2])*self.ares,3), )
        output += (round(self.dataConv(data[5], data[4])*self.ares,3), )

        return output

    ## Read gyroscope
    #  @param [in] self The object pointer.
    #  @retval output : (x-gyro data, y-gyro data, z-gyro data)
    def readGyro(self):
        data = bus.read_i2c_block_data(self.address, GYRO_OUT, 6)
        output = ()
        output += (round(self.dataConv(data[1], data[0])*self.gres, 3), )
        output += (round(self.dataConv(data[3], data[2])*self.gres, 3), )
        output += (round(self.dataConv(data[5], data[4])*self.gres, 3), )

        return output

    ## brief Check data ready
    #  @param [in] self The object pointer.
    #  @retval True data is ready
    #  @retval False data is not ready
    def AK8963DataReady(self):
        drdy = bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01:
            return True
        else:
            return False

    ## Read magnetometer
    #  @param [in] self The object pointer.
    #  @retval output : (X-magneto data, y-magneto data, Z-magneto data)
    def readMagnet(self):
        # check data ready
        '''drdy = bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01 :'''

        while self.AK8963DataReady() == False: pass
        data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

        output = ()
        # check overflow
        if (data[6] & 0x08)!=0x08:
            output += (round(self.dataConv(data[0], data[1])* self.mres * self.magcoef[0], 3), )
            output += (round(self.dataConv(data[2], data[3])* self.mres * self.magcoef[1], 3), )
            output += (round(self.dataConv(data[4], data[5])* self.mres * self.magcoef[2], 3), )

        return output

    ## Read temperature
    #  @param [out] temperature temperature(°C)
    def readTemperature(self):
        data = bus.read_i2c_block_data(self.address, TEMP_OUT, 2)
        temp = self.dataConv(data[1], data[0])

        temp = round((temp / 333.87 + 21.0), 3)
        return temp

    ## Data Convert
    # @param [in] self The object pointer.
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value

if __name__ == "__main__":

    mpu9250 = MPU9250()

    try:
        while True:
            accel = mpu9250.readAccel()
            print("Accelerometer:",accel)

            gyro = mpu9250.readGyro()
            print("Gyroscope:", gyro)

            mag = mpu9250.readMagnet()
            print("Magnetometer:", mag)

            temp = mpu9250.readTemperature()
            print("Temperature = " + str(temp) + "°C")

            time.sleep(0.25)

    except KeyboardInterrupt:
        sys.exit()
