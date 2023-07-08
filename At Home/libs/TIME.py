from ntptime import utime, settime
from micropython import const

GMT_SHIFT_HR = const(6)

def setTime():
    try: settime()
    except: pass

def getTime():
    time_list = utime.localtime(utime.mktime(utime.localtime()) - (GMT_SHIFT_HR * 3600))
    return "{:04d}:{:02d}:{:02d}-{:02d}:{:02d}:{:02d}".format(time_list[0], time_list[1], time_list[2], 
                                                              time_list[3], time_list[4], time_list[5])