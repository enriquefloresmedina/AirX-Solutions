from ntptime import utime, settime
from micropython import const

GMT_SHIFT_HR = const(6)

def setTime():
    try: settime()
    except: pass

def getTime():
    return utime.localtime(utime.mktime(utime.localtime()) - (GMT_SHIFT_HR * 3600))