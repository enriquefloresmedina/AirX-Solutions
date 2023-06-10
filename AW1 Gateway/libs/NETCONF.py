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



class MQTT:
    def __init__(self, debug=True):
        self.__debug = debug
        self._certificateFile = "2f9a209bc84e9517f80f7d89d929a7d7f08d16118b7466195dd23a5ad42aadeb-certificate.pem.crt"
        self._privateKeyFile = "2f9a209bc84e9517f80f7d89d929a7d7f08d16118b7466195dd23a5ad42aadeb-private.pem.key"
        self._MQTTClientID = "esp32"
        self._MQTTPort = 8883
        self._MQTTTopic = "esp32/publish"
        self._MQTTHost = "adi9qgij6bpmb-ats.iot.us-east-2.amazonaws.com"
        try:
            with open(self._privateKeyFile, "r") as f: self._privateKey = f.read()
            with open(self._certificateFile, "r") as f: self._certificate = f.read()
            self._MQTTClient = MQTTClient(client_id=self._MQTTClientID, server=self._MQTTHost, port=self._MQTTPort, keepalive=5000, ssl=True, ssl_params={"cert":self._certificate, "key":self._privateKey, "server_side":False})

            self.connect()
        except:
            self._debug('AWS certificates and/or keys missing')
    
    def connect(self):
        try:
            self._debug('Connecting to MQTT client...')
            self._MQTTClient.connect()
            self._debug('Connected to MQTT client')
        except OSError:
            self._debug('Connect to WIFi network first')

    def publish(self, message):
        self._MQTTClient.publish(self._MQTTTopic, message)
        self._debug('Message published to ' + self._MQTTTopic)
        return True

    def disconnect(self):
        self._MQTTClient.disconnect()
        self._debug('Disconnected from MQTT client')

    def _debug(self, msg):
        if self.__debug: print(msg)