from ntptime import utime, settime

def setTime():
    settime()

def getTime():
    return utime.localtime(utime.mktime(utime.localtime()) - (6 * 3600))