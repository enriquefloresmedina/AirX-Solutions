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
            "PM10":  data[0],
            "PM25":  data[1],
            "PM100": data[2],
            "TEMP":  data[3],
            "HUM":   data[4],
            "PRESS": data[5],
            "ALT":   data[6],
            "AQI" :  data[7]
        }
                                                                  
        URL = 'https://awair-database-default-rtdb.firebaseio.com/TEC/' + NODE + '/' + getTime() + '.json'

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