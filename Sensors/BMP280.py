#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MIT License

Copyright (c) 2018 Jeremie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
# further development by ians.moyes@gmail.com

import smbus2 as smbus
import time
# BMP280 default
DEVICE            = 0x76
# Register
REG_CHIPID       = 0xD0
REG_RESET        = 0xE0
REG_STATUS       = 0xF3
REG_CONFIG       = 0xF5
REG_CTRL_MEAS    = 0xF4
# Modes
MOD_SLEEP        = 0x00
MOD_FORCE        = 0x01
MOD_NORMAL       = 0x03
# Resolutions
RES_SKIP         = 0x00
RES_1            = 0x01
RES_2            = 0x02
RES_4            = 0x03
RES_8            = 0x04
RES_16           = 0x05
# Filters
FILTER_OFF       = 0x00
FILTER_2         = 0x01
FILTER_4         = 0x02
FILTER_8         = 0x03
FILTER_16        = 0x04
# Stand-By
SBT_0_5          = 0x00
SBT_62_5         = 0x01
SBT_125          = 0x02
SBT_250          = 0x03
SBT_500          = 0x04
SBT_1000         = 0x05
SBT_2000         = 0x06
SBT_4000         = 0x07
# Classe
class bmp280:
    def __init__(self, i2cbus=1, device_address=DEVICE, mode=MOD_FORCE, t_res=RES_1,
                 p_res=RES_1, f_res=FILTER_OFF, stby=SBT_1000):
        self.bus = smbus.SMBus(i2cbus)
        self.adr = device_address
        self.data = []
        # Mode
        if mode not in [MOD_SLEEP, MOD_FORCE, MOD_NORMAL]:
            raise ValueError('Unexpected mode value {0}.'.format(mode))
        self.mode = mode
        # Temp Resolution
        if t_res not in [RES_SKIP, RES_1, RES_2, RES_4, RES_8, RES_16]:
            raise ValueError('Unexpected t_res value {0}.'.format(t_res))
        self.tres = t_res
        # Pressure Resolution
        if p_res not in [RES_SKIP, RES_1, RES_2, RES_4, RES_8, RES_16]:
            raise ValueError('Unexpected p_res value {0}.'.format(p_res))
        self.pres = p_res
        # Filter Resolution
        if f_res not in [FILTER_OFF, FILTER_2, FILTER_4, FILTER_8, FILTER_16]:
            raise ValueError('Unexpected f_res value {0}.'.format(f_res))
        self.fres = f_res
        # StandBy in normal mode
        if stby not in [SBT_0_5, SBT_62_5, SBT_125, SBT_250, SBT_500, SBT_1000, SBT_2000, SBT_4000]:
            raise ValueError('Unexpected stby value {0}.'.format(stby))
        self.stby = stby
        # Write Config
        self.bus.write_byte_data(self.adr, REG_CTRL_MEAS, self._get_reg_ctrl_meas())
        self.bus.write_byte_data(self.adr, REG_CONFIG, self._get_reg_config())
        # Load Calibration
        self._load_calibration()

    def get_chip_id(self):
        self.chip_id = hex(self.bus.read_byte_data(self.adr, REG_CHIPID))
        return self.chip_id

    def reset(self):
        self.bus.write_byte_data(self.adr, REG_RESET, 0xB6)

    def is_measuring(self):
        return (self.bus.read_byte_data(self.adr, REG_STATUS) & 0x08) != 0x00

    def is_updating(self):
        return (self.bus.read_byte_data(self.adr, REG_STATUS) & 0x01) != 0x00

    def get_temperature_res(self):
        self.tres = (self.bus.read_byte_data(self.adr, REG_CTRL_MEAS) & 0xE0) >> 5
        return self.tres

    def set_temperature_res(self, temp_res):
        self.tres = temp_res
        self.bus.write_byte_data(self.adr, REG_CTRL_MEAS, self._get_reg_ctrl_meas())

    def get_pressure_res(self):
        self.pres = (self.bus.read_byte_data(self.adr, REG_CTRL_MEAS) & 0x1C) >> 2
        return self.pres

    def set_pressure_res(self, press_res):
        self.pres = press_res
        self.bus.write_byte_data(self.adr, REG_CTRL_MEAS, self._get_reg_ctrl_meas())

    def get_mode(self):
        self.mode = (self.bus.read_byte_data(self.adr, REG_CTRL_MEAS) & 0x03)
        return self.mode

    def set_mode(self, mod):
        self.mode = mod
        self.bus.write_byte_data(self.adr, REG_CTRL_MEAS, self._get_reg_ctrl_meas())

    def get_standby(self):
        self.stby = (self.bus.read_byte_data(self.adr, REG_CONFIG) & 0xE0) >> 5
        return self.stby

    def set_standby(self, timer):
        self.stby = timer
        self.bus.write_byte_data(self.adr, REG_CONFIG, self._get_reg_config())

    def get_filter(self):
        self.fres = (self.bus.read_byte_data(self.adr, REG_CONFIG) & 0x1C) >> 2
        return self.fres

    def set_filter(self, filter):
        self.fres = filter
        self.bus.write_byte_data(self.adr, REG_CONFIG, self._get_reg_config())

    def get_data(self):
        if self.mode != MOD_NORMAL:
            self.set_mode(MOD_FORCE)
            t_measure_max = 1.25 + (2.3 * self.tres) + (2.3 * self.pres + 0.575)
            time.sleep(t_measure_max/1000.0)

        self.data = []
        for i in range(0xF7, 0xF7+6):
            self.data.append(self.bus.read_byte_data(self.adr, i))

    def get_temperature(self):
        raw = ((self.data[3] << 16) | (self.data[4] << 8) | self.data[5]) >> 4
        t_fine = self._calc_t_fine(raw)
        t = self._calc_comp_t(t_fine)
        return t

    def get_pressure(self):
        raw = ((self.data[0] << 16) | (self.data[1] << 8) | self.data[2]) >> 4
        t_fine = self._calc_t_fine(((self.data[3] << 16) | (self.data[4] << 8) | self.data[5]) >> 4)
        p = self._calc_comp_p(t_fine, raw)
        return p

    def get_temp_f(self):
        temp_c = self.get_temperature()
        temp_f = (temp_c * 1.8) + 32
        return temp_f

    def get_press_mmhg(self):
        press_pa = self.get_pressure()
        press_mm = press_pa * 0.0075
        return press_mm

    def get_altitude(self, pa_sealevel=101325.0):
        press = float(self.get_pressure())
        altitude  = 44330.0 * (1.0 - pow(press / pa_sealevel, (1.0/5.255)))
        return altitude

    def get_altitude_ft(self, pa_sealevel=101325.0):
        alti = self.get_altitude(pa_sealevel)
        alti_ft = alti / 0.3048
        return alti_ft

    def get_pasealevel(self, alti=0.0):
        press = float(self.get_pressure())
        pasea = press / pow(1.0 - alti/44330.0, 5.255)
        return pasea

    def get_pasealevel_mmhg(self, alti=0.0):
        pasea = self.get_pasealevel(alti)
        pasea_mm = pasea * 0.0075
        return pasea_mm

    # Make Config Bytes
    def _get_reg_ctrl_meas(self):
        return ((self.tres & 0x07) << 5) | ((self.pres & 0x07) << 2) | self.mode

    def _get_reg_config(self):
        return ((self.stby & 0x07) << 5) | ((self.fres & 0x07) << 2) | 0x00

    # BOSCH Datasheet
    def _calc_t_fine(self, t_raw):
        var1 = (t_raw / 16384.0 - self.digT[0] / 1024.0) * self.digT[1]
        var2 = (t_raw / 131072.0 - self.digT[0] / 8192.0) * (t_raw / 131072.0 - self.digT[0] / 8192.0) * self.digT[2]
        return var1 + var2

    def _calc_comp_t(self, t_fine):
        t = t_fine / 5120.0
        return t

    def _calc_comp_p(self, t_fine, p_raw):
        var1 = (t_fine/2.0) - 64000.0
        var2 = var1 * var1 * (self.digP[5]) / 32768.0
        var2 = var2 + var1 * (self.digP[4]) * 2.0
        var2 = (var2/4.0)+(self.digP[3] * 65536.0)
        var1 = (self.digP[2] * var1 * var1 / 524288.0 + self.digP[1] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0)*self.digP[0]
        if var1 == 0.0:
            return 0
        p = 1048576.0 - p_raw
        p = (p - (var2 / 4096.0)) * 6250.0 / var1
        var1 = self.digP[8] * p * p / 2147483648.0
        var2 = p * self.digP[7] / 32768.0
        p = p + (var1 + var2 + self.digP[6]) / 16.0
        return p

    # Calibration
    def _load_calibration(self):
        # read all calibration registers
        cal_regs = []
        for i in range(0x88, 0x88+24):
            cal_regs.append(self.bus.read_byte_data(self.adr, i))
        # Temp
        self.digT = []
        self.digT.append((cal_regs[1] << 8) | cal_regs[0])
        self.digT.append((cal_regs[3] << 8) | cal_regs[2])
        self.digT.append((cal_regs[5] << 8) | cal_regs[4])
        # Press
        self.digP = []
        self.digP.append((cal_regs[7] << 8) | cal_regs[6])
        self.digP.append((cal_regs[9] << 8) | cal_regs[8])
        self.digP.append((cal_regs[11]<< 8) | cal_regs[10])
        self.digP.append((cal_regs[13]<< 8) | cal_regs[12])
        self.digP.append((cal_regs[15]<< 8) | cal_regs[14])
        self.digP.append((cal_regs[17]<< 8) | cal_regs[16])
        self.digP.append((cal_regs[19]<< 8) | cal_regs[18])
        self.digP.append((cal_regs[21]<< 8) | cal_regs[20])
        self.digP.append((cal_regs[23]<< 8) | cal_regs[22])
        # Temp
        for i in [1,2]:
            if self.digT[i] & 0x8000:
                self.digT[i] = (-self.digT[i] ^ 0xFFFF) + 1
        # Press
        for i in [1,2,3,4,5,6,7,8]:
            if self.digP[i] & 0x8000:
                self.digP[i] = (-self.digP[i] ^ 0xFFFF) + 1

if __name__ == "__main__":

    bmp = bmp280()

    try:
        while True:
            # Read Data
            bmp.get_data()
            tc = round(bmp.get_temperature(), 3)
            tf = round(bmp.get_temp_f(), 3)
            pp = round(bmp.get_pressure()/100, 3)
            ph = round(bmp.get_press_mmhg(), 3)
            am = round(bmp.get_altitude(), 3)
            af = round(bmp.get_altitude_ft(), 3)
            sp = round(bmp.get_pasealevel()/100, 3)
            sh = round(bmp.get_pasealevel_mmhg(), 3)
            chipid = bmp.get_chip_id()

            print ("Temperature: %.3f°C" % tc)
            print ("Temperature: %.3f°F" % tf)
            print ("Pressure: %.3fhPa" % pp)
            print ("Pressure: %.3fmmHg" % ph)
            print ("Altitude: %.3fm" % am)
            print ("Altitude: %.3fft" % af)
            print ("SeaLevel Pressure: %.3fhPa" % sp)
            print ("SeaLevel Pressure: %.3fmmHg" % sh)
            print ("Chip ID: {0}".format(chipid))
            print(" ")

            time.sleep(0.1)

    except KeyboardInterrupt:
        sys.exit()
