import time

# Time to write UART messages in ms
TIME_TO_WRITE_MS = 150

# Header to send packets
HEADER = [0xB5, 0x62]

# ID for some configurations
CFG_MSG_ID = [0x06, 0x01]  # p.p. 129
CFG_RATE_ID = [0x06, 0x08] # p.p. 150
CFG_RXM_ID = [0x06, 0x011] # p.p. 153

# NMEA Standard Messages Class
NMEA_STD_CLASS = 0xF0

# NMEA Standard Message IDs
DTM = 0x0A; GBS = 0x09; GGA = 0x00
GLL = 0x01; GPQ = 0x40; GRS = 0x06
GSA = 0x02; GST = 0x07; GSV = 0x03
RMC = 0x04; THS = 0x0E; TXT = 0x41
VTG = 0x05; ZDA = 0x08

class NEO6M():
    def __init__(self, uart, timeDiffHr=0, measRateMs=1000, ecoMode=False, powerSaveMode=False, 
                 minData=False):
        self._uart = uart
        self._DATA_READY = False

        if ecoMode and not powerSaveMode:
            self._powerMode('eco')
        elif powerSaveMode and not ecoMode:
            self._powerMode('save')
        elif not ecoMode and not powerSaveMode:
            self._powerMode()
        else:
            self._powerMode()
            print("Select only one power mode - Using Max performance mode") 

        if timeDiffHr > 13:
            self._timeDiffHr = 13
            print("Invalid Time Zone: Assigned GMT+13")
        elif timeDiffHr < -12:
            self._timeDiff = -12
            print("Invalid Time Zone: Assigned GMT-12")
        else:
            self._timeDiffHrHr = timeDiffHr

        self._latitude = 'None'
        self._longitude = 'None'
        self._timeDate = 'None'

        self._subDay = False
        self._addDay = False

        self._updateFreq(measRateMs)

        if minData: self._onlyRMC()
        else: self._allNMEAMsgs()

    def checkGPS(self):
        parts = str(self._uart.readline())
        parts = parts.split(',')

        if parts[0] != 'None': print(parts)

        if parts[0] == "b'$GPRMC" and parts[1] and parts[9]:
            [hh, mm, ss, DD, MM, YY] = self._getDateTime(parts[1][0:2], parts[1][2:4], parts[1][4:6],
                                                         parts[9][0:2], parts[9][2:4], parts[9][4:6])
            self._timeDate = hh + ":" + mm + ":" + ss + "-" + DD + '/' + MM + '/' + YY

            if parts[2] == 'A':
                self._latitude = self._convertToDegree(parts[3])
                if parts[4] == 'S': self._latitude = '-' + self._latitude

                self._longitude = self._convertToDegree(parts[5])
                if parts[6] == 'W': self._longitude = '-' + self._longitude
            else:
                self._longitude = self._latitude = 'None'

            self._DATA_READY = True
            self._flush_uart()

    def getData(self):
        return self._timeDate + ',' + self._latitude + ',' + self._longitude
    
    def setTimeZone(self, timeDiffHr):
        self._timeDiffHr = timeDiffHr

    def reset(self):
        self._DATA_READY = False

    @property
    def READY(self):
        return self._DATA_READY

    def _powerMode(self, powerMode='max'):
        # Change the GPS power mode (CFG-RXM)
        length = [0x02, 0x00]

        if powerMode == 'max':
            mode = 0x00
            writeTime = TIME_TO_WRITE_MS
        elif powerMode == 'save':
            mode = 0x01
            writeTime = 25000
        elif powerMode == 'eco':
            mode = 0x04
            writeTime = TIME_TO_WRITE_MS

        payload = [0x08, mode]

        buff = CFG_RXM_ID + length + payload
        arr = bytearray(HEADER + buff + self._checkSum(buff))

        self._flush_uart()
        self._uart.write(arr)

        time.sleep_ms(writeTime)
        
    def _updateFreq(self, measRateMs):
        # Change the rate at which the GPS makes measurements (CFG-RATE)
        length = [0x06, 0x00]
        measRateMs = self._intTo2ByteHex(measRateMs)  # measRate in ms (DATL - DATH)
        payload = measRateMs + [0x01, 0x00,           # navRate (always 1)
                                0x01, 0x00]           # timeRef (0 = UTC, 1 = GPS)
    
        buff = CFG_RATE_ID + length + payload
        arr = bytearray(HEADER + buff + self._checkSum(buff))

        self._flush_uart()
        self._uart.write(arr)

        time.sleep_ms(TIME_TO_WRITE_MS)

    def _NMEAMsgEnable(self, NMEAID, enable=True):
        # Enable or disable any particular NMEA standard message (CFG-MSG)
        length = [0x08, 0x00]
        msg = [NMEA_STD_CLASS, NMEAID]  # msgClass and msgID
        if enable:
            IOtargets = [0x01, 0x01,    # DDC - Serial Port 1
                         0x01, 0x01,    # Serial Port 2 - USB
                         0x01, 0x01]    # SPI - Reserved
        else:
            IOtargets = [0x00, 0x00,    # DDC - Serial Port 1
                         0x00, 0x00,    # Serial Port 2 - USB
                         0x00, 0x00]    # SPI - Reserved
        payload = msg + IOtargets

        buff = CFG_MSG_ID + length + payload
        arr = bytearray(HEADER + buff + self._checkSum(buff))

        self._flush_uart()
        self._uart.write(arr)

        time.sleep_ms(TIME_TO_WRITE_MS)

    def _onlyRMC(self):
        # Disabling all NMEA Standard Messages, except RMC
        self._NMEAMsgEnable(DTM, False); self._NMEAMsgEnable(GBS, False) 
        self._NMEAMsgEnable(GGA, False); self._NMEAMsgEnable(GLL, False)
        self._NMEAMsgEnable(GPQ, False); self._NMEAMsgEnable(GRS, False)
        self._NMEAMsgEnable(GSA, False); self._NMEAMsgEnable(GST, False)
        self._NMEAMsgEnable(GSV, False); self._NMEAMsgEnable(RMC, True)
        self._NMEAMsgEnable(THS, False); self._NMEAMsgEnable(TXT, False)
        self._NMEAMsgEnable(VTG, False); self._NMEAMsgEnable(ZDA, False)

    def _allNMEAMsgs(self):
        # Enable all NMEA Standard Messages
        self._NMEAMsgEnable(DTM); self._NMEAMsgEnable(GBS) 
        self._NMEAMsgEnable(GGA); self._NMEAMsgEnable(GLL)
        self._NMEAMsgEnable(GPQ); self._NMEAMsgEnable(GRS)
        self._NMEAMsgEnable(GSA); self._NMEAMsgEnable(GST)
        self._NMEAMsgEnable(GSV); self._NMEAMsgEnable(RMC)
        self._NMEAMsgEnable(THS); self._NMEAMsgEnable(TXT)
        self._NMEAMsgEnable(VTG); self._NMEAMsgEnable(ZDA)

    def _intTo2ByteHex(self, num):
        # Converts an integer to a 2-byte hexadecimal
        if num > 65535 or num <= 0:
            print("Invalid int to hex - Returning 1000")
            return [0xE8, 0x03]

        # Turn number to string without 0x
        hex_num = hex(num)[2:]

        # Convert to 4 digits
        if len(hex_num) == 3:
            hex_num = '0' + hex_num
        elif len(hex_num) == 2:
            hex_num = '00' + hex_num
        elif len(hex_num) == 1:
            hex_num = '000' + hex_num

        # Divide the number into a LOW and a HIGH byte
        DATL_str = hex_num[2:] # Last two digits are the low bits
        DATH_str = hex_num[:2] # First two digits are the high bits

        # Convert the bytes into decimal numbers
        DATL = int(DATL_str, 16)
        DATH = int(DATH_str, 16)

        return [DATL, DATH]

    def _checkSum(self, buff):
        # Calculate 8-bit Fletcher Algorithm checksum
        CK_A = 0; CK_B = 0

        for i in range(len(buff)):
            CK_A = CK_A + buff[i]
            CK_B = (CK_B + CK_A) % 256
        
        return [CK_A, CK_B]
    
    def _getDateTime(self, hh, mm, ss, DD, MM, YY):
        hh = self._convertTimeZone(hh)

        if self._addDay: return [hh, mm, ss] + self._addDate(DD, MM, YY)
        elif self._subDay: return [hh, mm, ss] + self._subDate(DD, MM, YY)
        else: return [hh, mm, ss, DD, MM, YY] 

    def _convertTimeZone(self, hh):
        hh = int(hh) + int(self._timeDiffHr)
        if hh < 0:
            self._subDay = True
            self._addDay = False
            return self._doubleDigitStr(hh + 24)
        elif hh >= 24:
            self._addDay = True
            self._subDay = False
            return self._doubleDigitStr(hh - 24)
        else:
            self._subDay = False
            self._addDay = False
            return self._doubleDigitStr(hh)

    def _addDate(self, DD, MM, YY):
        DD = int(DD); MM = int(MM); YY = int(YY)
        if DD == 31:
            if MM == 12: MM = 1; YY += 1
            else: MM += 1
            DD = 1
        elif DD == 30 and MM % 2 == 0: DD = 1; MM += 1
        elif DD == 28 and MM == 2 and YY % 4 != 0: DD = 1; MM += 1
        elif DD == 29 and MM == 2: DD = 1; MM += 1
        else: DD += 1

        return [self._doubleDigitStr(DD), 
                self._doubleDigitStr(MM), 
                self._doubleDigitStr(YY)]

    def _subDate(self, DD, MM, YY):
        DD = int(DD); MM = int(MM); YY = int(YY)
        if DD == 1:
            if MM % 2 == 0: DD = 31
            elif MM == 3 and YY % 4 == 0: DD = 29
            elif MM == 3: DD = 28
            elif MM == 1: DD = 31; YY -= 1; MM = 12
            else: DD = 30
            
            if not (MM == 12 and DD == 31): MM -= 1
        else: DD -= 1

        return [self._doubleDigitStr(DD), 
                self._doubleDigitStr(MM), 
                self._doubleDigitStr(YY)]

    def _doubleDigitStr(self, num):
        if num < 10: return '0' + str(num)
        else: return str(num)

    def _convertToDegree(self, rawDegrees):
        rawAsFloat = float(rawDegrees)
        firstdigits = int(rawAsFloat/100) 
        nexttwodigits = rawAsFloat - float(firstdigits*100) 
        
        converted = float(firstdigits + nexttwodigits/60.0)
        converted = '{0:.6f}'.format(converted) 
        return str(converted)

    def _flush_uart(self):
        while self._uart.any():
            self._uart.read(self._uart.any())