import machine as ESP32
from setup import BMP, PMS, DHT, SD, REF_COUNT_UPLOAD
from libs.UPLOAD import upload
from libs.SCREEN import Screen
import os
import gc

COUNTER = 0
PM10 = PM25 = PM100 = TEMP = HUM = PRESS = ALT = AQI = 0

def interrupt(timer):
    global COUNTER
    
    while not PMS.getMeasure(): pass

    state = ESP32.disable_irq()

    COUNTER += 1
    DATA = readSensors()

    ESP32.enable_irq(state)

    Screen.setMeasurments(DATA)

    if average(DATA):
        Screen.disableScreens(True)
        if Screen.power(): Screen.uploadingScreen()
        UP_DATA = [PM10, PM25, PM100, TEMP, HUM, PRESS, ALT, AQI]
        upload(UP_DATA)

        try: writeToSD(','.join(map(str, UP_DATA)))
        except: pass

    gc.collect()
        
def average(data):
    global PM10, PM25, PM100, TEMP, HUM, PRESS, ALT, AQI, COUNTER
    
    if COUNTER == 1:
        PM10 = PM25 = PM100 = TEMP = HUM = PRESS = ALT = AQI = 0

    PM10 += data[0]; PM25 += data[1]; PM100 += data[2]
    TEMP += data[3]; HUM += data[4]; PRESS += data[5]
    ALT += data[6]; AQI += data[7]

    if COUNTER >= REF_COUNT_UPLOAD:
        PM10 /= REF_COUNT_UPLOAD; PM25 /= REF_COUNT_UPLOAD; PM100 /= REF_COUNT_UPLOAD
        TEMP /= REF_COUNT_UPLOAD; HUM /= REF_COUNT_UPLOAD;  PRESS /= REF_COUNT_UPLOAD
        ALT /= REF_COUNT_UPLOAD;  AQI /= REF_COUNT_UPLOAD;  COUNTER = 0
        return True

    return False

def readSensors():
    pm10 = PMS.pm10_env; pm25 = PMS.pm25_env; pm100 = PMS.pm100_env
    aqi = PMS.pm_aqi; mainPoll = PMS.main_pollutant
    DHT.measure()
    temp = round((DHT.temperature() + BMP.getTemp()) / 2)
    hum = round(DHT.humidity()); press = round(BMP.getPress() / 1000); 
    alt = round(BMP.getAltitude() / 100) / 10

    return [pm10, pm25, pm100, temp, hum, press, alt, aqi, mainPoll]

def writeToSD(data):
    os.mount(SD, '/sd')
    with open('/sd/historic.txt', 'a') as f:
        f.write(data + '\n')
    os.umount('/sd')