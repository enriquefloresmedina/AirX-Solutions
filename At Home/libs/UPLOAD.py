from libs.SCREEN import Screen
from setup import WIFI, NODE, NETWORKS
from libs.TIME import getTime
import gc
import json
import urequests

def upload(data):

    if not WIFI.status():
        if WIFI.scanForNetworks(NETWORKS, 1000): 
            WIFI.connect()

    if WIFI.status():
        
        datajson = { 
            "PM10": round(data[0]),
            "PM25": round(data[1]),
            "PM100": round(data[2]),
            "PRESS": round(data[5]),
            "ALT": round(data[6]),
            "TEMP": round((data[3] + data[7]) / 2), 
            "HUM": round(data[4]) 
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
            except: 
                Screen.disableScreens(False)
                return

        if response.status_code == 200: 
            Screen.disableScreens(False)
            return

    Screen.disableScreens(False)
    return