import machine as ESP32
import uasyncio as asyncio
import PMS5003 as PMSmodule
import NEO6M as GPSmodule
import NETCONF as CONF
import BMP280 as BMPmodule
import quality_mesh as qm
import time

# Adjust these parameters for each Gateway
UNIQUE_ID = 0               # Lecture ID
SENSOR_ID = 1               # Sensor ID
SSID = "Enrique's iPhone"   # WIFI SSID
PASSWORD = '12345678'       # WIFI password
READ_TIME = 15              # Time spent doing readings (s)
TIME_ZONE_DIFF = -6         # Guadalajara Time Zone (GMT-6)

CONF.wifi_init()
CONF.mqtt_init()

GPS = GPSmodule.NEO6M(ESP32.UART(1, tx=10, rx=9, baudrate=9600), TIME_ZONE_DIFF)
PMS = PMSmodule.PMS5003(ESP32.UART(2, tx=17, rx=16, baudrate=9600))
BMP = BMPmodule.BMP280(ESP32.SoftI2C(sda=ESP32.Pin(21), scl=ESP32.Pin(22)))

def avgReadings(DAT1, DAT2, DAT3, N):
    if N is not 0: 
        UNIQUE_ID = UNIQUE_ID + 1
        return str( UNIQUE_ID + int(DAT1/N)) + str(int(DAT1/N)) + ',' + str(int(DAT2/N)) + ',' + str(int(DAT3/N))
    else: return 'None'

async def main():
    global BMP

    MSG = "ID,IMEDATE,LAT,LON,UID,PM1.0,PM2.5,PM10,TEMP,PRES,ALT,AQ\n"

    while not PMS.READY:
        if PMS.NC: break
        print('Activating PMS5003...') 
        await asyncio.sleep(15)

    if PMS.NC: PMS.stop(); PMS.sleep()

    print('Starting main program...')

    while True:
        TIMEOUT = time.time() + READ_TIME

        GPS.reset()
        PMSmsg = BMPmsg = GPSmsg = 'None'
        PMScount = BMPcount = 0
        PM10 = PM25 = PM100 = 0
        TEMP = ALT = PRES = 0

        while time.time() <= TIMEOUT:
        
            if not GPS.READY: 
                GPS.checkGPS()
                if GPS.READY: GPSmsg = GPS.getData()
                else: GPSmsg = 'None'

            if not PMS.NC:
                if PMScount < 300: 
                    PMS.wakeUp()
                    if PMS.READY:
                        PM10 = PMS.pm10_env + PM10
                        PM25 = PMS.pm25_env + PM25
                        PM100 = PMS.pm100_env + PM100 
                        PMScount += 1
                PMS.sleep()

            if not BMP.NC:
                if BMPcount < 300: 
                    BMP.poweron()
                    if BMP.READY:
                        TEMP = BMP.temperature + TEMP
                        PRES = BMP.pressure + PRES
                        ALT = BMP.altitude + ALT
                        BMPcount += 1
                BMP.poweroff()
            
            if not GPS.READY: await asyncio.sleep(0.5)
            elif (BMPcount < 300 and PMScount < 300): await asyncio.sleep(0.025)
            else: await asyncio.sleep(10); ESP32.idle()

        print("PMS readings: " + str(PMScount)) # Print for debugging, will remove 
        print("BMP readings: " + str(BMPcount)) # Print for debugging, will remove 
        PMSmsg = avgReadings(PM10, PM25, PM100, PMScount)
        BMPmsg = avgReadings(TEMP, PRES, ALT, BMPcount)
        
        if GPS.READY:
            MSG = MSG + str(SENSOR_ID) + ',' + GPSmsg + ',' + PMSmsg + ',' + BMPmsg + qm.quality(PM25/PMScount) + '\n'
            try: 
                CONF.mqtt_publish(MSG)
            except:
                print(MSG) # Print for debugging, will remove
        else:
            print("Missing data:", str(SENSOR_ID) + ',' + GPSmsg + ',' + PMSmsg + ',' + BMPmsg)  # Print for debugging, will remove

        # Implement a reconnect attempt function for PMS5003

        if BMP.NC: BMP = BMPmodule.BMP280(ESP32.SoftI2C(sda=ESP32.Pin(21), scl=ESP32.Pin(22))) 
        
asyncio.run(main())
