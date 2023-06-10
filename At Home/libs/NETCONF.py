from libs.SCREEN import Screen
import network
import time
import ntptime

DEBUG = False

class Wifi:
    def __init__(self, networks, timeoutMS=30000):
        self.__debug = DEBUG
        self._wifi = network.WLAN(network.STA_IF)

        Screen.wifiScreen(False, 'NO SSID')
        if self.scanForNetworks(networks, timeoutMS): self.connect()
        else: self._debug('Timed out - No network found')

    def connect(self):
        if not self._wifi.isconnected():
            self._debug('Connecting to WIFI network...')
            self._wifi.active(True)
            self._wifi.connect(self._ssid, self._pass)
            while not self._wifi.isconnected(): 
                pass
        self._debug('Connected to WIFI network: ' + self._wifi.config('essid'))
        self._debug('IP address: ' + self._wifi.ifconfig()[0])
        Screen.wifiScreen(True, self._wifi.config('essid'))
        self.setTime()
 
    def disconnect(self):
        if self._wifi.isconnected(): 
            self._wifi.disconnect()
            while self._wifi.isconnected():
                pass
            self._wifi.active(False)
        self._debug('Disconnected from WIFI')

    def scan(self):
        if self.status():
            self._debug(self._wifi.scan())
        else:
            self._wifi.active(True)
            self._debug(self._wifi.scan())
            self._wifi.active(False)
  
    def status(self):
        return self._wifi.isconnected()
    
    def scanForNetworks(self, networks, timeoutMS):
        self._wifi.active(True)
        
        currTime = time.ticks_ms()
        while time.ticks_ms() - currTime < timeoutMS:
            netList = self._wifi.scan()
            for i in range(len(netList)):
                if len(str(netList[i][0])) > 3: netList[i] = str(netList[i][0])[2:-1]
                else: continue
                for key in networks.keys():
                    if netList[i] == key: 
                        self._ssid = key
                        self._pass = networks.get(key)
                        return True
        self._ssid = next(iter(networks.keys()))
        self._pass = networks.get(self._ssid)

        self._wifi.active(False)
        return False

    def setTime(self):
        try: ntptime.settime()
        except: pass

    def _debug(self, msg):
        if self.__debug: print(msg)