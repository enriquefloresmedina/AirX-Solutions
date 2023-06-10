from libs.NETCONF import WIFI
from libs import NETCONF as conf
import gc
import json
import urequests
import ntptime
import utime

def upload( pms10, pms25, pms100, temp, hum, press, alt, tempBMP, NODE): 

    #if conf.status():

    datajson = { 
        "PM10": int(pms10),
        "PM25": int(pms25),
        "PM100": int(pms100),
        "PRESS": (int(press)//1000),
        "ALT": (int(alt)),
        "TEMP": round((int(temp) + int(tempBMP)) / 2), 
        "HUM": (int(hum)) 
    }

    # OBTENER TIEMPO Y FECHA
    ntptime.settime()
    time_tuple = utime.localtime()
    # Convert the time tuple to a timestamp
    timestamp = utime.mktime(time_tuple)
    # Calculate the timestamp 6 hours (21600 seconds) before
    timestamp_before = timestamp - (6 * 3600)
    # Convert the new timestamp to a time tuple
    time_tuple_before = utime.localtime(timestamp_before)

    year, month, day, hour, minute, second, weekday, yearday = time_tuple_before ####HAY QUE HACER QUE SIEMPRE TENGA LA MISMA CANTIDAD DE DÍGITOS
    
    # Format the time components with leading zeros
    hour = "{:02d}".format(hour)
    minute = "{:02d}".format(minute)
    second = "{:02d}".format(second)
    
    TIME = "{}:{}:{}-{}:{}:{}".format(year, month, day, hour, minute, second)
    #DEFINIR PATH
    URL = 'https://awair-database-default-rtdb.firebaseio.com/TEC/' + NODE + '/' + TIME + '.json'
    gc.collect()
    
    # CONVERTIR ESOS ACUMULADOS EN UN JSON 
    with open('DATA.json', 'w') as file:
        json.dump(datajson, file)
        
    # PUBLICAR A FIREBASE

    with open('DATA.json', 'r') as file:
        data_js =file.read()
        response = urequests.put(URL, data = data_js)
    

    if response.status_code == 200:
        print("Data uploaded successfully!")
        
    else:
        print("Error uploading data:", response.status_code)


