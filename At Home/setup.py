import machine as ESP32
from micropython import const
from libs.BMP280 import BMP280
from libs.PMS5003 import PMS5003
from libs.NETCONF import Wifi
from libs.SSD1306 import SSD1306_I2C
from libs.SCREEN import Screen
from dht import DHT22
import gc

READ_TIME_MS = const(7400)
REF_COUNT_UPLOAD = const(6)
WIFI_TIMEOUT_MS = const(30000)
GMT_SHIFT_HR = const(6)
NODE = const("AT_HOME_2")

NETWORKS = {
    "Enrique's iPhone" : "12345678",
    "iPhone de Sebas" : "sebas123",
    "Jesus" : "12345678",
    "AB" : "12345678",
    "Wall-E" : "diego123",
    "INFINITUM5B10_2.4" : "6200370058"
}

gc.collect()
SSD = SSD1306_I2C(128, 64, ESP32.SoftI2C(scl=ESP32.Pin(22), sda=ESP32.Pin(21)))
Screen.setSSD(SSD)

WIFI = Wifi(NETWORKS, WIFI_TIMEOUT_MS)

Screen.setWIFIandTime(WIFI)

SD = ESP32.SDCard(slot = 2)
BMP = BMP280(ESP32.SoftI2C(sda=ESP32.Pin(21), scl=ESP32.Pin(22), freq=100000, timeout=500000))
DHT = DHT22(ESP32.Pin(32))
PMS = PMS5003(ESP32.UART(1, tx=17, rx=16, baudrate=9600), reset_pin=ESP32.Pin(4, ESP32.Pin.OUT), passive_mode=True)

BTN_SUM = Screen(27, mode = '+')
BTN_SUB = Screen(12, mode = '-')
BTN_ON_OFF = Screen(14, mode = 'pwr')

readTimer = ESP32.Timer(0)

def startMainTimer():
    from reads import interrupt
    readTimer.init(period=READ_TIME_MS, mode=ESP32.Timer.PERIODIC, callback=interrupt)