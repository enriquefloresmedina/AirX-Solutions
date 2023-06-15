from setup import WIFI, NODE, NETWORKS
from libs.TIME import getTime
import gc
import json
import urequests
import _thread

def upload(pm10, pm25, pm100, temp, hum, press, alt, tempBMP):

    if not WIFI.status():
        if WIFI.scanForNetworks(NETWORKS, 1000): 
            WIFI.connect()

    if WIFI.status():
        
        datajson = { 
            "PM10": round(pm10),
            "PM25": round(pm25),
            "PM100": round(pm100),
            "PRESS": round(press),
            "ALT": round(alt),
            "TEMP": round((temp + tempBMP) / 2), 
            "HUM": round(hum) 
        }

        TIME_LIST = getTime()
        TIME = "{:04d}:{:02d}:{:02d}-{:02d}:{:02d}:{:02d}".format(TIME_LIST[0], TIME_LIST[1], TIME_LIST[2], 
                                                                  TIME_LIST[3], TIME_LIST[4], TIME_LIST[5])
                                                                  
        URL = 'https://awair-database-default-rtdb.firebaseio.com/TEC/' + NODE + '/' + TIME + '.json'

        gc.collect()

        with open('DATA.json', 'w') as file:
            json.dump(datajson, file)

        with open('DATA.json', 'r') as file:
            datajs = file.read()
            try: response = urequests.put(URL, data = datajs)
            except:_thread.exit()

        if response.status_code == 200: _thread.exit()

    _thread.exit()