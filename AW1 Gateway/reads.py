from UPLOAD import upload
import machine as ESP32
import utime, urequests, json, ntptime
import gc
from setup import BMP,PMS, DHT, startTimers, lora, sendMessage, historial

# Lora
import config_lora
import random

CMD = ''

def interrupt(timer):

    if CMD == 'D' or CMD == 'd':
        timer.deinit()
        with open('/data.txt', 'w') as f: f.write('')
        return

    while not PMS.getMeasure(): pass

    state = ESP32.disable_irq()

    if CMD == 'S' or CMD == 's':
        timer.deinit()
        ESP32.enable_irq(state)
        return
    else:

        # Read BMP
        # BMP.poweron()
        BMPdata = '{!s},{!s},{!s}'.format(BMP.getTemp(), BMP.getPress(), BMP.getAltitude())
        BMP.poweroff()
        print('BMP readings: T = {!s} C, P = {!s} Pa, A = {!s} m'.format(BMPdata.split(',')[0],
                                                                         BMPdata.split(',')[1], 
                                                                         BMPdata.split(',')[2]))

        # Read DHT
        DHT.measure()
        DHTdata = '{!s},{!s}'.format(round(DHT.temperature()), round(DHT.humidity()))
        print('DHT readings: T = {!s} C, H = {!s} %'.format(DHTdata.split(',')[0], 
                                                            DHTdata.split(',')[1]))    

        # Read PMS
        PMSdata = '{!s},{!s},{!s}'.format(PMS.pm10_aqi, PMS.pm25_aqi, PMS.pm100_aqi)
        print('PMS readings: PM 1 = {!s}, PM 2.5 = {!s}, PM 10 = {!s} '.format(PMSdata.split(',')[0],
                                                                                PMSdata.split(',')[1],
                                                                                PMSdata.split(',')[2]))                                                                    
        # Concatenate data
        destination = 'Gateway1'
        My_ID = config_lora.NODE_NAME
        ID_msg = str(random.randrange(100,999,1))

        DATA = BMPdata + ',' + DHTdata# + ',' + PMSdata
        DATA_SEND = My_ID + ' ' + destination + ' ' + DATA + ' ' + ID_msg
   
        if len(historial) >= 10:
            historial.pop(0) 
            historial.append(ID_msg + ' ' + My_ID)
        else:
            historial.append(ID_msg + ' ' + My_ID)

        ESP32.enable_irq(state)

        #sendMessage(lora, DATA_SEND)
        # Into mode receiver
        lora.receive()
        #print('El historial es: {}'.format(historial))

    # Put PMS to sleep again
    PMS.sleep()

    # Restart timers for new lecture
    startTimers()

    # Upload data to txt file
    with open('/data.txt', 'a') as f: f.write(DATA + '\n')

    upload(PMSdata.split(',')[0],PMSdata.split(',')[1],PMSdata.split(',')[2],DHTdata.split(',')[0],DHTdata.split(',')[1],BMPdata.split(',')[1],BMPdata.split(',')[2],BMPdata.split(',')[0],NODE='Gateway1')