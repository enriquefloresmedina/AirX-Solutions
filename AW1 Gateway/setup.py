import machine as ESP32
import dht
from libs import BMP280 as bmp
from libs import PMS5003 as pms
from libs import NETCONF as conf
from libs import PMS5003 as pms
import time
#from UPLOAD import upload
import UPLOAD

# LoRa
import gc
gc.collect()

import sx127x
gc.collect()

import config_lora 

global lora, historial, contador

SSID = "Jesus"
PASSWORD = "12345678"

WIFI = conf.WIFI(SSID, PASSWORD)
NODE = "AW1_GATEWAY_1"

_pwm = ESP32.PWM(ESP32.Pin(27))
_pwm.deinit()

BMP = bmp.BMP280(ESP32.SoftI2C(sda=ESP32.Pin(21), scl=ESP32.Pin(22), freq=100000, timeout=500000))
PMS = pms.PMS5003(ESP32.UART(1, tx=16, rx=17, baudrate=9600), reset_pin=ESP32.Pin(4, ESP32.Pin.OUT), passive_mode=True, awake=True)
DHT = dht.DHT22(ESP32.Pin(32))

readTimer = ESP32.Timer(0)
wakePMSTimer = ESP32.Timer(1)

WAKEUP_TIME_MS = 40000
READ_TIME_MS = 1 * 60000 # Must be greater than the wake up time

def startMainTimer():
    from reads import interrupt
    readTimer.init(period=READ_TIME_MS, mode=ESP32.Timer.PERIODIC, callback=interrupt)

def startTimers():
   from wakePMS import interrupt as wakeInt
   wakePMSTimer.init(period=READ_TIME_MS - WAKEUP_TIME_MS, mode=ESP32.Timer.PERIODIC, callback=wakeInt)

controller = config_lora.Controller()    
        
lora = controller.add_transceiver(sx127x.SX127x(name = 'LoRa'),
                                    pin_id_ss = config_lora.Controller.PIN_ID_FOR_LORA_SS,
                                    pin_id_RxDone = config_lora.Controller.PIN_ID_FOR_LORA_DIO0)

historial = []

def duplexCallback(lora):
    print("LoRa Duplex with callback")
    lora.onReceive(on_receive)  # register the receive callback

def sendMessage(lora, outgoing):
    lora.println(outgoing)
    print("Sending message:\n{}\n".format(outgoing))
    _pwm.init()
    _pwm.duty(920)
    time.sleep_ms(200)
    _pwm.deinit()

def on_receive(lora, payload):
    _pwm.init()
    _pwm.duty(700)
    #lora.blink_led()
                
    try:
        Trama = payload.decode()
        rssi = lora.packetRssi()
        print("*** Received message ***\n{}".format(Trama))
        print("with RSSI {}\n".format(rssi))
        _pwm.duty(0)
        
    except Exception as e:
        print(e)

    # Check the message received.
    try:
        Trama_spl = Trama.split()
        ID_Sender = Trama_spl[0]
        ID_MSG = Trama_spl[3]
        ID_history = ID_MSG + ' ' + ID_Sender
        if ID_history in historial:   # Si el ID se encuentra en el historial, se borra toda la trama de mensajes
            del Trama
            gc.collect()
            return
        else:   
            lora.receive()                 # into in mode Receiver

            data_fire = Trama_spl[2]

            UPLOAD.upload(0,0,0,data_fire.split(',')[3],data_fire.split(',')[4],data_fire.split(',')[1],data_fire.split(',')[2],data_fire.split(',')[0],NODE=Trama_spl[0])
            
            if len(historial) >= 10:
                historial.pop(0)             # Se borra el historial mas viejo
                historial.append(ID_history)         # Se añade el nuevo valor del historial
            else:
                historial.append(ID_history)
    except:
        print("Error en la trama recibida")
        
print('lora', lora)

duplexCallback(lora)