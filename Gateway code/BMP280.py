from micropython import const

BMP280_I2C_ADDR = const(0x76)

class BMP280():
    def __init__(self, i2c):
        try:
            self.i2c = i2c
            self.tb = bytearray(1)
            self.rb = bytearray(1)
            self.dig_T1 = self.get2Reg(0x88)
            self.dig_T2 = self.short(self.get2Reg(0x8A))
            self.dig_T3 = self.short(self.get2Reg(0x8C))
            self.dig_P1 = self.get2Reg(0x8E)
            self.dig_P2 = self.short(self.get2Reg(0x90))
            self.dig_P3 = self.short(self.get2Reg(0x92))
            self.dig_P4 = self.short(self.get2Reg(0x94))
            self.dig_P5 = self.short(self.get2Reg(0x96))
            self.dig_P6 = self.short(self.get2Reg(0x98))
            self.dig_P7 = self.short(self.get2Reg(0x9A))
            self.dig_P8 = self.short(self.get2Reg(0x9C))
            self.dig_P9 = self.short(self.get2Reg(0x9E))
            self.mode = 3
            self.osrs_p = 3
            self.osrs_t = 1
            self.setReg(0xF4, 0x2F)
            self.setReg(0xF5, 0x0C)
            self.filter = 3
            self.T = 0
            self.P = 0
            
            self.version = '1.0'
            self.NC = False
        except:
            self.NC = True
            print('No response from BMP280')

    def	short(self,	dat):
        if dat > 32767:
            return dat - 65536
        else:
            return dat

    # set reg
    def	setReg(self, reg, dat):
        try:
            self.tb[0] = dat
            self.i2c.writeto_mem(BMP280_I2C_ADDR, reg, self.tb)
        except:
            self.NC = True

    # get reg
    def	getReg(self, reg): 
        try:
            self.i2c.readfrom_mem_into(BMP280_I2C_ADDR, reg, self.rb)

        # The ETIMEDOUT error means that the request took more time than the webserver 
        # configuration allows and the connection has been closed by the server. 
        # A connect or send request failed because the connected party did not properly respond after a period of time. 
        # Usually encountered by HTTP or net. Often a sign that a socket. end() was not properly called.
            return self.rb[0]
        except:
            self.NC = True

    # get two reg
    def	get2Reg(self, reg):
        return self.getReg(reg) + self.getReg(reg+1) * 256

    def get(self):
        try:
            adc_T = (self.getReg(0xFA) << 12) + (self.getReg(0xFB) << 4) + (self.getReg(0xFC) >> 4)
            var1 = (((adc_T >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
            var2 = (((((adc_T >> 4) - self.dig_T1) * ((adc_T>>4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
            t = var1 + var2
            self.T = ((t * 5 + 128) >> 8) / 100
            var1 = (t >> 1) - 64000
            var2 = (((var1 >> 2) * (var1 >> 2)) >> 11 ) * self.dig_P6
            var2 = var2 + ((var1 * self.dig_P5) << 1)
            var2 = (var2 >> 2) + (self.dig_P4 << 16)
            var1 = (((self.dig_P3 * ((var1 >> 2) * (var1 >> 2)) >> 13) >> 3) + (((self.dig_P2) * var1) >> 1)) >> 18
            var1 = ((32768+var1)*self.dig_P1)>>15
            if var1 == 0:
                self.T = -1
                self.P = -1
                return [self.T, self.P] # avoid exception caused by division by zero, throw error code
            adc_P = (self.getReg(0xF7)<<12) + (self.getReg(0xF8)<<4) + (self.getReg(0xF9)>>4)
            p=((1048576-adc_P)-(var2>>12))*3125
            if p < 0x80000000:
                p = (p << 1) // var1
            else:
                p = (p // var1) * 2
            var1 = (self.dig_P9 * (((p>>3)*(p>>3))>>13))>>12
            var2 = (((p>>2)) * self.dig_P8)>>13
            self.P = p + ((var1 + var2 + self.dig_P7) >> 4)
            return [self.T, self.P]
        except:
            self.NC = True

    # get Temperature in Celsius
    @property
    def temperature(self):
        self.get()
        return self.T

    # get Pressure in Pa
    @property
    def pressure(self):
        self.get()
        return self.P

    # Calculating absolute altitude
    @property
    def	altitude(self):
        return 44330*(1-(self.pressure/101325)**(1/5.255))

    # sleep mode
    def poweroff(self):
        self.setReg(0xF4, 0)

    # normal mode
    def poweron(self):
        self.setReg(0xF4, 0x2F)

    @property
    def READY(self):
        self.get()
        if self.T == -1 and self.P == -1: return False 
        else: return True
