buff = bytearray(255)

class NEO6M():
    def __init__(self, uart, timeDiff):
        self._uart = uart
        self._DATA_READY = False

        if timeDiff > 13:
            self._timeDiff = 13
            print("Invalid Time Zone: Assigned GMT+13")
        elif timeDiff < -12:
            self._timeDiff = -12
            print("Invalid Time Zone: Assigned GMT-12")
        else:
            self._timeDiff = timeDiff

        self._latitude = ""
        self._longitude = ""
        self._timeDate = ""

        self._subDay = False
        self._addDay = False

    def checkGPS(self):
        self._uart.readline()
        buff = str(self._uart.readline())
        parts = buff.split(',')
        # print(parts) # Print for debugging, will remove

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
                self._longitude = 'None'
                self._latitude = 'None'

            self._DATA_READY = True

    def getData(self):
        return self._timeDate + ',' + self._latitude + ',' + self._longitude
    
    def reset(self):
        self._DATA_READY = False

    @property
    def READY(self):
        return self._DATA_READY
    
    def _getDateTime(self, hh, mm, ss, DD, MM, YY):
        hh = self._convertTimeZone(hh)

        if self._addDay: return [hh, mm, ss] + self._addDate(DD, MM, YY)
        elif self._subDay: return [hh, mm, ss] + self._subDate(DD, MM, YY)
        else: return [hh, mm, ss, DD, MM, YY] 

    def _convertTimeZone(self, hh):
        hh = int(hh) + int(self._timeDiff)
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

    def _convertToDegree(self, RawDegrees):
        RawAsFloat = float(RawDegrees)
        firstdigits = int(RawAsFloat/100) 
        nexttwodigits = RawAsFloat - float(firstdigits*100) 
        
        Converted = float(firstdigits + nexttwodigits/60.0)
        Converted = '{0:.6f}'.format(Converted) 
        return str(Converted)