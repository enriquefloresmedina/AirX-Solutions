from machine import RTC, UART, Pin, SoftI2C
import uasyncio as asyncio
import ntptime
import PMS5003 as PMS
import NEO6M as GPS
import NETCONF as CONF
import BMP280 as BMP

# Adjust these parameters for each Gateway
SENSOR_ID = 1             # Sensor ID
SSID = "Enrique's iPhone" # WIFI SSID
PASSWORD = '12345678'     # WIFI password
GPS_READ_TIME = 15        # Time spent waiting for GPS readings (s)
TIME_ZONE_DIFF = -6       # Guadalajara Time Zone (GMT-6)

CONF.wifi_connect(SSID, PASSWORD)
CONF.mqtt_connect()

ntptime.settime()

(YY, MM, DD, wd, hh, mm, ss, ms) = RTC().datetime()
RTC().init((YY, MM, DD, wd, hh + TIME_ZONE_DIFF, mm, ss, ms))

gpsModule = GPS.NEO6M(UART(1, tx=10, rx=9, baudrate=9600), GPS_READ_TIME, TIME_ZONE_DIFF)
pmModule = PMS.PMS5003(UART(2, tx=17, rx=16, baudrate=9600))
bmpModule = BMP.BMP280(SoftI2C(sda=Pin(21), scl=Pin(22)))

async def main():
    global SENSOR_ID

    MSG = "ID,DATE_TIME,LAT,LON,PM1.0,PM2.5,PM10,TEMP,PRES,ALT\n"
    GPSmsg = "GPS_NULL"
    PMmsg = "PM_NULL"
    BMPmsg = "BMP_NULL"
    DATEmsg = "DATE_NULL"
    
    while pmModule.readEnvPM() is None:
        print('Activating PMS5003...') 
        await asyncio.sleep(15)

    print('PMS5003 activated!')
    print('Starting main program...')

    while True:
        gpsModule.updateGPS()
        if gpsModule.dataReady():
            GPSmsg = gpsModule.getGPSData()
            GPS_READY = True
        else:
            GPSmsg = "GPS_NULL"
            GPS_READY = False

        pmModule.start()
        if pmModule.readEnvPM() is not None:
            PMmsg = pmModule.readEnvPM() 
            PMS_READY = True
        else:
            PMmsg = "PMS_NULL"
            PMS_READY = False
        pmModule.stop()

        bmpModule.poweron()
        if bmpModule.dataReady():
            BMPmsg = bmpModule.getBMPData()
            BMP_READY = True
        else:
            BMPmsg = "BMP_NULL"
            BMP_READY = False
        bmpModule.poweroff()

        DATEmsg = str(RTC().datetime()[2]) + '/' + str(RTC().datetime()[1]) + '/' + str(RTC().datetime()[0])

        if PMS_READY and GPS_READY and BMP_READY:
            MSG = MSG + str(SENSOR_ID) + ',' + DATEmsg + '-' + GPSmsg + ',' + PMmsg + ',' + BMPmsg + '\n'
            CONF.mqtt_publish(MSG)
        else:
            print("Missing data in stream:", str(SENSOR_ID) + ',' + DATEmsg + '-' + GPSmsg + ',' + PMmsg + ',' + BMPmsg)
       
        await asyncio.sleep(0.5)     
    
asyncio.run(main())