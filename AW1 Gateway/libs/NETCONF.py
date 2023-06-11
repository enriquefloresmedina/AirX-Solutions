from umqtt.robust import MQTTClient
from libs import BUZZER as buzz
import network

DEBUG = True

class WIFI:
    def __init__(self, SSID, PASSWORD):
        self.__debug = DEBUG
        self._wifi = network.WLAN(network.STA_IF)
        self._ssid = SSID
        self._pass = PASSWORD

        self.connect()

    def connect(self):
        if not self._wifi.isconnected():
            self._debug('Connecting to WIFI network...')
            self._wifi.active(True)
            self._wifi.connect(self._ssid, self._pass)
            while not self._wifi.isconnected():
                pass
        self._debug('Connected to WIFI network: ' + self._wifi.config('essid'))
        self._debug('IP address: ' + self._wifi.ifconfig()[0])
        buzz.successWifi()
 
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

    def _debug(self, msg):
        if self.__debug: print(msg)