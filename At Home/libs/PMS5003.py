import time
from libs.SCREEN import Screen

READ_IN_PASSIVE = 0xE2
CHANGE_MODE = 0xE1
SLEEP_SET = 0xE4

WAKEUP_TIME_MS = 40000 

DEBUG = False

class PMS5003: 
    def __init__(self, uart, reset_pin=None, passive_mode=False, awake=False):
        self._debug = DEBUG
        self._uart = uart
        self._passive_mode = passive_mode
        self._reset_pin = reset_pin
    
        if reset_pin != None:
            reset_pin.value(1)

        if self._passive_mode:
            self.setPassiveMode()               
        else:
            self.setActiveMode()
        
        if not awake:
            self.wakeUp()
            Screen.loadingScreen()
            self._flush_uart()

        self._resetMeasurements()

    def print(self):
        print('Standard PM (ug/m3):\n  PM1.0 = {:3.0f} | PM2.5 = {:3.0f} | PM10 = {:3.0f}'.format(
            self.pm10_std, self.pm25_std, self.pm100_std
        ))
        print('Environment PM (ug/m3):\n  PM1.0 = {:3.0f} | PM2.5 = {:3.0f} | PM10 = {:3.0f}'.format(
            self.pm10_env, self.pm25_env, self.pm100_env
        ))
        print('AQI PM:\n  PM1.0 = {:3.0f} | PM2.5 = {:3.0f} | PM10 = {:3.0f}'.format(
            self.pm10_aqi, self.pm25_aqi, self.pm100_aqi
        ))
        print('Particles (um/0.1L):\n  >0.3 = {:4.0f} | >0.5 = {:4.0f} | >1.0 =  {:4.0f}\n  >2.5 = {:4.0f} | >5.0 = {:4.0f} | >10.0 = {:4.0f}'.format(
            self.particles_03um, self.particles_05um, self.particles_10um,
            self.particles_25um, self.particles_50um, self.particles_100um
        ))
        print('--------------------------------------------')

    def getMeasure(self):
        if self._passive_mode:
            self._requestReadInPassive()
        
        available = self._uart.any()
        if available >= 32:
            self._uart.read(available - 32)
        else:
            self._resetMeasurements()
            return False

        buffer = list(self._uart.read())

        while len(buffer) >= 2 and buffer[0] != 0x42 and buffer[1] != 0x4d:
            buffer.pop(0)

        if len(buffer) > 32:
            buffer = buffer[:32]

        if (len(buffer) < 4) or (buffer[2] != 0x00 and buffer[3] != 0x1c):
            self.debug('Short UART read')
            self._resetMeasurements()
            return False

        frame = []
        for i in range(4, len(buffer), 2):
            frame.append(buffer[i] * 256 + buffer[i + 1])
        
        check_sum = sum(buffer[:-2])
        check_code = frame[-1]

        if check_code != check_sum:
            self.debug('Incorrect check sum')
            self._resetMeasurements()
            return False

        self._pm10_std = frame[0]
        self._pm25_std = frame[1]
        self._pm100_std = frame[2]

        self._pm10_env = frame[3]
        self._pm25_env = frame[4]
        self._pm100_env = frame[5]

        self._particles_03um = frame[6]
        self._particles_05um = frame[7]
        self._particles_10um = frame[8]
        self._particles_25um = frame[9]
        self._particles_50um = frame[10]
        self._particles_100um = frame[11]

        return True

    def _sendCmd(self, cmd, data):
        arr = bytearray(7)
        arr[0] = 0x42
        arr[1] = 0x4d
        arr[2] = cmd
        arr[3] = 0x00
        arr[4] = data
        s = sum(arr[:5])
        arr[5] = int(s / 256)
        arr[6] = s % 256
        self._flush_uart()
        self._uart.write(arr)
        time.sleep_ms(120)

    def _requestReadInPassive(self):
        self.debug('Requesting read for passive mode')
        self._sendCmd(READ_IN_PASSIVE, 0)

    def _resetMeasurements(self):
        self._pm10_std = self._pm25_std = self._pm100_std = 0
        self._pm10_env = self._pm25_env = self._pm100_env = 0
        self._particles_03um = self._particles_05um = self._particles_10um = 0
        self._particles_25um = self._particles_50um = self._particles_100um = 0

    def _flush_uart(self):
        while self._uart.any():
            self._uart.read(self._uart.any())

    def _checkRes(self, cmd):
        res = self._uart.read()
        if res != None:
            res = list(res)
            if res[0] == 0x42 and res[1] == 0x4d and res[4] == cmd:
                check_sum = sum(res[:-2])
                check_code = res[-2] * 256 + res[-1]
                if check_sum == check_code: return True
        self.debug('No response to command')
        return False

    def _convertToAQI(self, value, isPM100):
        if isPM100:
            if value <= 54: return int((50 / 54) * value)
            elif value <= 154: return int((49 / 99) * (value - 55) + 51)
            elif value <= 254: return int((49 / 99) * (value - 155) + 101)
            elif value <= 354: return int((49 / 99) * (value - 255) + 151)
            elif value <= 424: return int((99 / 69) * (value - 355) + 201)
            else: return int((199 / 179) * (value - 425) + 301)
        else:
            if value <= 12: return int((50 / 12) * value)
            elif value <= 35: return int((49 / 23.3) * (value - 12.1) + 51)
            elif value <= 55: return int((49 / 19.9) * (value - 35.5) + 101)
            elif value <= 150: return int((49 / 94.9) * (value - 55.5) + 151)
            elif value <= 250: return int((99 / 99.9) * (value - 150.5) + 201)
            else: return int((199 / 249.9) * (value - 250.5) + 301)

    def sleep(self):
        self._sendCmd(SLEEP_SET, 0)
        if self._checkRes(SLEEP_SET): 
            self.debug('Putting device to sleep')

    def wakeUp(self):
        self.debug('Waking up device')
        self._sendCmd(SLEEP_SET, 1)
        if self._passive_mode:
            time.sleep_ms(2300)
            self.setPassiveMode()

    def reset(self):
        if self._reset_pin != None:
            self.debug('Resetting device')
            self._reset_pin.value(0)
            time.sleep_ms(5000)
            self._reset_pin.value(1)
            self.debug('Device has been reset')
        else:
            self.debug('No reset pin defined')

    def setPassiveMode(self):
        self._sendCmd(CHANGE_MODE, 0)
        if self._checkRes(CHANGE_MODE):
            self._passive_mode = True
            self.debug('Setting device to passive mode')

    def setActiveMode(self):
        self._sendCmd(CHANGE_MODE, 1)
        if self._checkRes(CHANGE_MODE):
            self._passive_mode = False
            self.debug('Setting device to active mode')

    def debug(self, msg):
        if self._debug: print(msg)

    @property
    def pm10_std(self):
        return self._pm10_std

    @property
    def pm25_std(self):
        return self._pm25_std

    @property
    def pm100_std(self):
        return self._pm100_std

    @property
    def pm10_env(self):
        return self._pm10_env

    @property
    def pm25_env(self):
        return self._pm25_env

    @property
    def pm100_env(self):
        return self._pm100_env

    @property
    def particles_03um(self):
        return self._particles_03um

    @property
    def particles_05um(self):
        return self._particles_05um

    @property
    def particles_10um(self):
        return self._particles_10um

    @property
    def particles_25um(self):
        return self._particles_25um

    @property
    def particles_50um(self):
        return self._particles_50um

    @property
    def particles_100um(self):
        return self._particles_100um

    @property
    def pm10_aqi(self):
        return self._convertToAQI(self._pm10_env, False)

    @property
    def pm25_aqi(self):
        return self._convertToAQI(self._pm25_env, False)

    @property
    def pm100_aqi(self):
        return self._convertToAQI(self._pm100_env, True)