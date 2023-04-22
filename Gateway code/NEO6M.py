import time

buff = bytearray(255)

class NEO6M():
    def __init__(self, uart, readTime, timeDiff):
        self.uart = uart
        self.DATA_READY = False
        self.readTime = readTime
        self.timeDiff = timeDiff
        self.latitude = ""
        self.longitude = ""
        self.satellites = ""
        self.GPStime = ""

    def updateGPS(self):
        timeout = time.time() + self.readTime
        self.DATA_READY = False

        while time.time() <= timeout:
            self.uart.readline()
            buff = str(self.uart.readline())
            parts = buff.split(',')
            print(parts)

            if (parts[0] == "b'$GPGGA" and len(parts) == 15):
                if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                    
                    self.latitude = self.convertToDegree(parts[2])
                    if (parts[3] == 'S'):
                        self.latitude = '-' + self.latitude
                    self.longitude = self.convertToDegree(parts[4])
                    if (parts[5] == 'W'):
                        self.longitude = '-' + self.longitude
                    self.satellites = parts[7]
                    hrs = self.convertTimeZone(parts[1][0:2], self.timeDiff)
                    self.GPStime = hrs + ":" + parts[1][2:4] + ":" + parts[1][4:6]

                    self.DATA_READY = True
            
            time.sleep(0.5)

    def dataReady(self):
        return self.DATA_READY

    def getGPSData(self):
        return self.GPStime + ',' + self.latitude + ',' + self.longitude

    def convertTimeZone(self, hrs, plus_minus):
        hrs = int(hrs) + plus_minus
        if hrs < 10 and hrs >= 0:
            return '0' + str(hrs)
        elif hrs < 0:
            return str(24 + hrs)
        else:
            return str(hrs)
            
    def convertToDegree(self, RawDegrees):
        RawAsFloat = float(RawDegrees)
        firstdigits = int(RawAsFloat/100) 
        nexttwodigits = RawAsFloat - float(firstdigits*100) 
        
        Converted = float(firstdigits + nexttwodigits/60.0)
        Converted = '{0:.6f}'.format(Converted) 
        return str(Converted)