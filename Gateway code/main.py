from machine import UART, Pin, SoftI2C
import uasyncio as asyncio
import PMS5003 as PMSmodule
import NEO6M as GPSmodule
import NETCONF as CONF
import BMP280 as BMPmodule
import time

# Adjust these parameters for each Gateway
UNIQUE_ID = 0             # Lecture ID
SENSOR_ID = 1             # Sensor ID
SSID = "Enrique's iPhone" # WIFI SSID
PASSWORD = '12345678'     # WIFI password
READ_TIME = 15            # Time spent doing readings (s)
TIME_ZONE_DIFF = -6       # Guadalajara Time Zone (GMT-6)


GPS = GPSmodule.NEO6M(UART(1, tx=10, rx=9, baudrate=9600), TIME_ZONE_DIFF)
PMS = PMSmodule.PMS5003(UART(2, tx=17, rx=16, baudrate=9600))
BMP = BMPmodule.BMP280(SoftI2C(sda=Pin(21), scl=Pin(22)))

def avgReadings(DAT1, DAT2, DAT3, N):
    UNIQUE_ID = UNIQUE_ID + 1
    return str( UNIQUE_ID + int(DAT1/N)) + ',' + str(int(DAT2/N)) + ',' + str(int(DAT3/N))

async def main():
    global SENSOR_ID

    MSG = "ID,TIMEDATE,LAT,LON,PM1.0,PM2.5,PM10,TEMP,PRES,ALT\n"
    
    while not PMS.READY:
        print('Activating PMS5003...') 
        await asyncio.sleep(15)

    print('PMS5003 activated!')
    print('Starting main program...')

    while True:

        TIMEOUT = time.time() + READ_TIME

        GPS.reset()
        PMSmsg = "PM_NULL"; BMPmsg = "BMP_NULL"; GPSmsg = "GPS_NULL"
        PMScount = 0;       BMPcount = 0
        PM10 = 0; PM25 = 0; PM100 = 0
        TEMP = 0; ALT  = 0; PRES  = 0

        while time.time() <= TIMEOUT:

            if not GPS.READY: 
                GPS.checkGPS()
                if GPS.READY: GPSmsg = GPS.getData()
                else: GPSmsg = "GPS_NULL"

            if PMScount <= 300: 
                PMS.start()
                if PMS.READY:
                    PM10 = PMS.pm10_env + PM10
                    PM25 = PMS.pm25_env + PM25
                    PM100 = PMS.pm100_env + PM100 
                    PMScount += 1
            PMS.stop()

            if BMPcount <= 300: 
                BMP.poweron()
                if BMP.READY:
                    TEMP = BMP.temperature + TEMP
                    PRES = BMP.pressure + PRES
                    ALT = BMP.altitude + ALT
                    BMPcount += 1
            BMP.poweroff()

            await asyncio.sleep(0.5)

        print("PMS readings: " + str(PMScount))
        print("BMP readings: " + str(BMPcount))
        PMSmsg = avgReadings(PM10, PM25, PM100, PMScount)
        BMPmsg = avgReadings(TEMP, PRES, ALT, BMPcount)
        
        if GPS.READY and BMP.READY and PMS.READY:
            MSG = MSG + str(SENSOR_ID) + ',' + GPSmsg + ',' + PMSmsg + ',' + BMPmsg + '\n'
            CONF.wifi_connect(SSID, PASSWORD) ############################
            CONF.mqtt_connect() ####################
            CONF.mqtt_publish(MSG)
            print(MSG)  # Print for debugging, will remove
            CONF.wifi_disconnect() ############################
        else:
            print("Missing data in stream:", str(SENSOR_ID) + ',' + GPSmsg + ',' + PMSmsg + ',' + BMPmsg)  # Print for debugging, will remove 
    
asyncio.run(main())
