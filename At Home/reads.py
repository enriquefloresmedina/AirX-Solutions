import machine as ESP32
from setup import BMP, PMS, DHT, SD, REF_COUNT_UPLOAD
from libs.UPLOAD import upload
from libs.SCREEN import Screen
import os
import gc

COUNTER = 0
PM10 = PM25 = PM100 = HUM = TEMP = PRESS = ALT = TEMPBMP = 0

def interrupt(timer):
    global COUNTER
    
    while not PMS.getMeasure(): pass

    state = ESP32.disable_irq()

    COUNTER += 1

    DHT.measure()
    PMSdata = [PMS.pm10_aqi, PMS.pm25_aqi, PMS.pm100_aqi]
    DHTdata = [round(DHT.temperature()), round(DHT.humidity())]
    BMPdata = [BMP.getPress() // 1000, BMP.getAltitude(), BMP.getTemp()]

    DATA = PMSdata + DHTdata + BMPdata

    ESP32.enable_irq(state)

    Screen.setMeasurments(DATA[:6])

    DATA_S = ','.join(map(str, DATA))

    try: writeToSD(DATA_S)
    except: pass

    if average(DATA):
        Screen.disableScreens(True)
        if Screen.power(): Screen.uploadingScreen()
        upload(DATA)

    gc.collect()
        
def average(data):
    global PM10, PM25, PM100, HUM, TEMP, PRESS, ALT, TEMPBMP, COUNTER
    
    if COUNTER == 1:
        PM10 = PM25 = PM100 = HUM = TEMP = PRESS = ALT = TEMPBMP = 0

    PM10 += data[0]; PM25 += data[1]; PM100 += data[2]
    TEMP += data[3]; HUM += data[4]; PRESS += data[5]
    ALT += data[6]; TEMPBMP += data[7]

    if COUNTER >= REF_COUNT_UPLOAD:
        PM10 /= REF_COUNT_UPLOAD; PM25 /= REF_COUNT_UPLOAD; PM100 /= REF_COUNT_UPLOAD
        TEMP /= REF_COUNT_UPLOAD; HUM /= REF_COUNT_UPLOAD; PRESS /= REF_COUNT_UPLOAD
        ALT /= REF_COUNT_UPLOAD; TEMPBMP /= REF_COUNT_UPLOAD
        COUNTER = 0; 
        return True

    return False

def writeToSD(data):
    os.mount(SD, '/sd')
    with open('/sd/historic.txt', 'a') as f:
        f.write(data + '\n')
    os.umount('/sd')