import machine as ESP32
import PMS5003 as PMSmodule
import uasyncio as asyncio
import time

uart = ESP32.UART(2, tx=17, rx=16, baudrate=9600)
PMS = PMSmodule.PMS5003(uart)


async def main():
    PM10 = PM25 = PM100 = 0

    while True:
        buff = str(uart.readline())
        print(buff) # Print for debugging, will remove
        time.sleep(0.5)
        PMS.wakeUp()
        if PMS.READY:
            PM10 = PMS.pm10_env
            PM25 = PMS.pm25_env
            PM100 = PMS.pm100_env
        PMS.sleep()

        print("PM1.0: " + str(PM10) + ", PM2.5: " + str(PM25) + ", PM10: " + str(PM100))

        await asyncio.sleep(1)

asyncio.run(main())