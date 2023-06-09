from setup import WIFI, NODE, GMT_SHIFT_HR, NETWORKS
from libs.SCREEN import Screen
import gc
import json
import urequests
import ntptime
import utime
import _thread

def upload(pm10, pm25, pm100, temp, hum, press, alt, tempBMP):
    def setTime():
        ntptime.settime()
        timestamp = utime.mktime(utime.localtime()) - (GMT_SHIFT_HR * 3600)
        dateTime = utime.localtime(timestamp)
        return dateTime

    if not WIFI.status():
        if WIFI.scanForNetworks(NETWORKS, 2000): WIFI.connect()

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

        try: dateTime = setTime()
        except: _thread.exit()

        TIME = "{:04d}:{:02d}:{:02d}-{:02d}:{:02d}:{:02d}".format(dateTime[0], dateTime[1], dateTime[2], 
                                                                dateTime[3], dateTime[4], dateTime[5])
        URL = 'https://awair-database-default-rtdb.firebaseio.com/TEC/' + NODE + '/' + TIME + '.json'

        gc.collect()

        with open('DATA.json', 'w') as file:
            json.dump(datajson, file)

        with open('DATA.json', 'r') as file:
            data_js = file.read()
            response = urequests.put(URL, data = data_js)

        if response.status_code == 200: 
            Screen.wifiScreen(True, WIFI._ssid)
            _thread.exit()

    Screen.wifiScreen(False, WIFI._ssid)
    _thread.exit()