import gc
import json
import urequests
from ntptime import utime

GMT_SHIFT_HR = 6

def upload(actData): 

    TIME_LIST = utime.localtime(utime.mktime(utime.localtime()) - (GMT_SHIFT_HR * 3600))
    TIME = "{:04d}:{:02d}:{:02d}-{:02d}:{:02d}:{:02d}".format(TIME_LIST[0], TIME_LIST[1], TIME_LIST[2], 
                                                                    TIME_LIST[3], TIME_LIST[4], TIME_LIST[5])

    datajson = { 
            "PM10": round(actData[0]),
            "PM25": round(actData[1]),
            "PM100": round(actData[2]),
            "PRESS": round(actData[5]),
            "ALT": round(actData[6]),
            "TEMP": round((actData[3] + actData[7]) / 2), 
            "HUM": round(actData[4]) 
        }
                                                                
    URL = 'https://awair-database-default-rtdb.firebaseio.com/TEC/' + actData[8] + '/' + TIME + '.json'

    gc.collect()
    
    with open('DATA.json', 'w') as file:
        json.dump(datajson, file)

    with open('DATA.json', 'r') as file:
        datajs = file.read()
        response = urequests.put(URL, data = datajs)

    if response.status_code == 200:
        print('Data sent')
        
    return


