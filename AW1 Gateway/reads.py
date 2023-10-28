from libs.UPLOAD import upload
from libs.DATA import addToBuffer, getBuffer, eraseBuffer
import machine as ESP32
import gc
from setup import BMP,PMS, DHT, startTimers, lora, historial

import config_lora
import random

def interrupt(timer):

    while not PMS.getMeasure(): pass

    state = ESP32.disable_irq()

    DHT.measure()
    PMSdata = [PMS.pm10_aqi, PMS.pm25_aqi, PMS.pm100_aqi]
    DHTdata = [round(DHT.temperature()), round(DHT.humidity())]
    BMPdata = [BMP.getPress() // 1000, BMP.getAltitude(), BMP.getTemp()]
                 
    # Concatenate data
    DEST = 'AW1_GATEWAY_1'
    My_ID = config_lora.NODE_NAME
    ID_msg = str(random.randrange(100,999,1))

    DATA = PMSdata + DHTdata + BMPdata
    DATA.append(DEST)

    addToBuffer(DATA)

    if len(historial) >= 10:
        historial.pop(0) 
        historial.append(ID_msg + ' ' + My_ID)
    else:
        historial.append(ID_msg + ' ' + My_ID)

    ESP32.enable_irq(state)

    lora.receive()

    # Put PMS to sleep again
    PMS.sleep()

    buff = getBuffer()
    while len(buff) >= 1:
        upload(buff.pop(0))

    eraseBuffer()

    gc.collect()

    startTimers()