from machine import UART, Pin, SoftI2C
import uasyncio as asyncio
import PMS5003 as PMSmodule
import NETCONF as CONF
import time 
import WhatsApp_bot as wb


# Adjust these parameters for each Gateway
UNIQUE_ID = 0             # ID for each lecture
SENSOR_ID = 1             # Sensor ID
SSID = "Wall-E"           # WIFI SSID
PASSWORD = 'diego123'     # WIFI password
READ_TIME = 16            # Time spent doing readings (s)

phone_number = 5213318635546 #Your phone number in international format
api_key = 3344572 #Your callmebot API key


PMS = PMSmodule.PMS5003(UART(2, tx=17, rx=16, baudrate=9600))

async def main():
    
    while not PMS.READY:
        print('Activating PMS5003...') 
        await asyncio.sleep(15)

    print('PMS5003 activated!')
    print('Starting main program...')
    
    while True:
        PM25 = 0
        PMScount = 0
        
        TIMEOUT = time.time() + READ_TIME
        
        while time.time() <= TIMEOUT:
            if PMScount <= 300: 
                PMS.wakeUp()
                if PMS.READY:
                    PM25 = PMS.pm25_env + PM25
                    PMS.print()
                    PMScount += 1
                    
                time.sleep(0.05)
            PMS.sleep()
        
        AVG_PM25 = PM25/(PMScount)
        print(AVG_PM25) #For debugging
        
        if AVG_PM25 > 10:
            CONF.wifi_connect(SSID, PASSWORD)
            message = "Concentración_peligrosa_de_PM2.5:__" + str(AVG_PM25) + "__"
            print('SENDING MESSAGE')
            wb.send_message(phone_number, message, api_key) # agregar un sleep?
        
        await asyncio.sleep(0.025)
asyncio.run(main())
