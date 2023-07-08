import machine as ESP32
from libs.WRITER import Writer
from libs.TIME import getTime
from fonts import arial15, arial35, arial9
from icons import drop, termometer, pressure, pm10, pm25, pm100, wifiOk, wifiErr
from icons import aqi1, aqi2, aqi3, aqi4, aqi5, aqi6, altitude
import framebuf
import time
import gc

NUM_SCREENS = 11
POWER = True
DISABLE = False
PM10 = PM25 = PM100 = TEMP = HUM = PRESS = ALT = AQI = COUNT = 0
POLLUTANT = ''

class Screen():
    
    @staticmethod
    def setMeasurments(data):
        global PM10, PM25, PM100, TEMP, HUM, PRESS, ALT, AQI, POLLUTANT

        PM10 = data[0]; PM25 = data[1]; PM100 = data[2]
        TEMP = data[3]; HUM =  data[4]; PRESS = data[5]; 
        ALT =  data[6]; AQI =  data[7]; POLLUTANT = data[8]

        Screen._update()

    @staticmethod
    def _update():
        if not DISABLE:
            if not POWER: SSD.fill(0); SSD.show()
            elif COUNT == 0: Screen.mainScreen(PM10, 'PM1.0')
            elif COUNT == 1: Screen.mainScreen(PM25, 'PM2.5')
            elif COUNT == 2: Screen.mainScreen(PM100, 'PM10')
            elif COUNT == 3: Screen.mainScreen(AQI, 'AQI')
            elif COUNT == 4: Screen.mainScreen(HUM, 'H')
            elif COUNT == 5: Screen.mainScreen(TEMP, 'T')
            elif COUNT == 6: Screen.mainScreen(PRESS, 'P')
            elif COUNT == 7: Screen.mainScreen(ALT, 'A')
            elif COUNT == 8: Screen.timeScreen()
            elif COUNT == 9: Screen.dateScreen()
            else: Screen.wifiScreen(WIFI.status(), WIFI._ssid)

    @staticmethod
    def setSSD(ssd):
        global SSD
        SSD = ssd
    
    @staticmethod
    def setWIFI(wifi):
        global WIFI    
        WIFI = wifi
    
    def __init__(self, btn_pin, mode = '+', debounceDelayMS = 175):
        self.button = ESP32.Pin(btn_pin, ESP32.Pin.IN, ESP32.Pin.PULL_UP)
        self.lastTime = 0
        self.debounceDelayMS = debounceDelayMS
        self.mode = mode
        self.button.irq(trigger=ESP32.Pin.IRQ_RISING, handler=self._onPress)
        Screen._update()

    def _onPress(self, pin):
        global COUNT, POWER, NUM_SCREENS

        state = ESP32.disable_irq()
 
        if time.ticks_ms() - self.lastTime > self.debounceDelayMS:
            if self.button.value() == 1:
                if self.mode == '+' and POWER: 
                    COUNT += 1
                elif self.mode == '-' and POWER:
                    COUNT -= 1
                else:
                    POWER = not POWER
                COUNT = (COUNT + NUM_SCREENS) % NUM_SCREENS
                Screen._update()
            self.lastTime = time.ticks_ms()

        ESP32.enable_irq(state)

    @staticmethod
    def disableScreens(val):
        global DISABLE
        DISABLE = val

    @staticmethod
    def power():
        return POWER

    @staticmethod
    def _getImage(imgPy):
        return framebuf.FrameBuffer(imgPy.img, imgPy.width, imgPy.height, framebuf.MONO_HLSB)

    @staticmethod
    def mainScreen(meas, mode):
        SSD.fill(0)

        wri = Writer(SSD, arial15, verbose=False)

        def getScaledMeas(meas):
            slotLen = SSD.width / 6
            if meas <= 200:
                return int((meas * 4 * slotLen) / 200)
            elif meas <= 300:
                return int((slotLen / 100) * (meas - 200) + (4 * slotLen))
            else:
                return int((slotLen / 200) * (meas - 300) + (5 * slotLen))
        
        def addPMtext(txt):
            wri = Writer(SSD, arial9, verbose=False)
            if txt == 'PM10':
                Writer.set_textpos(SSD, 40, 95)
                wri.printstring(txt[:2])
                Writer.set_textpos(SSD, 40, 111)
                wri.printstring(txt[2:])
            else:
                Writer.set_textpos(SSD, 40, 93)
                wri.printstring(txt[:2])
                Writer.set_textpos(SSD, 40, 109)
                wri.printstring(txt[2:])

        if mode == 'H':
            SSD.blit(Screen._getImage(drop), 20, -6)
            scaledMeas = int(meas * 128 / 100)
            text = '%'
            Writer.set_textpos(SSD, 7, 72)
            wri.printstring(text)
        elif mode == 'T':
            SSD.blit(Screen._getImage(termometer), 20, -4)
            scaledMeas = int(meas * (64/45) + 128 / 3)
            text = 'ºC'
            Writer.set_textpos(SSD, 7, 71)
            wri.printstring(text)
        elif mode == 'P':
            SSD.blit(Screen._getImage(pressure), 18, -4)
            scaledMeas = int((64 / 29) * (meas - 50))
            text = 'kPa'
            Writer.set_textpos(SSD, 7, 91)
            wri.printstring(text)
        elif mode == 'PM10':
            SSD.blit(Screen._getImage(pm100), 0, 0)
            scaledMeas = getScaledMeas(meas)
            addPMtext(mode)
        elif mode == 'PM2.5':
            SSD.blit(Screen._getImage(pm25), 0, 0)
            scaledMeas = getScaledMeas(meas)
            addPMtext(mode)
        elif mode == 'PM1.0':
            SSD.blit(Screen._getImage(pm10), 0, 0)
            scaledMeas = getScaledMeas(meas)
            addPMtext(mode)
        elif mode == 'AQI':
            if meas <= 50:
                SSD.blit(Screen._getImage(aqi1), 0, 0)
            elif meas <= 100:
                SSD.blit(Screen._getImage(aqi2), 0, 0)
            elif meas <= 150:
                SSD.blit(Screen._getImage(aqi3), 0, 0)
            elif meas <= 200:
                SSD.blit(Screen._getImage(aqi4), 0, 0)
            elif meas <= 300:
                SSD.blit(Screen._getImage(aqi5), 0, 0)
            else:
                SSD.blit(Screen._getImage(aqi6), 0, 0)
            addPMtext(POLLUTANT)
            scaledMeas = getScaledMeas(meas)
        else:
            SSD.blit(Screen._getImage(altitude), 18, -4)
            text = 'kM'
            Writer.set_textpos(SSD, 7, 94)
            wri.printstring(text)
            scaledMeas = int(meas * 128 / 3.7)

        wri = Writer(SSD, arial35, verbose=False)
        if meas < 0:
            meas = -meas
            SSD.rect(0, SSD.height - 40, 11, 5, 1, 1)
        if mode == 'A': Writer.set_textpos(SSD, 7, 9) 
        else: Writer.set_textpos(SSD, 7, 42 - len(str(meas)) * 14) 
        wri.printstring('{!s}'.format(meas))

        SSD.rect(0, SSD.height - 12, SSD.width, 12, 1, 0)
        SSD.rect(2, SSD.height - 10, scaledMeas, 8, 1, 1)

        if mode == 'PM1.0' or mode == 'PM2.5' or mode == 'PM10' or mode == 'AQI':
            for i in range(1, 6):
                delta = 5
                side = (SSD.width - delta * 5) // 6
                x = i * side + delta * (i - 1)
                SSD.rect(x, SSD.height - 12, delta, 12,  1, 1)
                SSD.line(x - 1, SSD.height - 11, x - 1, SSD.height - 2, 0)
                SSD.rect(x + 1, SSD.height - 12, delta - 2, 12, 0, 1)
                SSD.line(x + delta, SSD.height - 11, x + delta, SSD.height - 2, 0)
        
        SSD.show()

    @staticmethod
    def wifiScreen(wifi, ssid):
        SSD.fill(0)
        
        if wifi: SSD.blit(Screen._getImage(wifiOk), 0, 0)
        else: SSD.blit(Screen._getImage(wifiErr), 0, 0)
        
        wri = Writer(SSD, arial9, verbose=False)
        Writer.set_textpos(SSD, 54, 2) 
        wri.printstring((ssid.upper()).replace(" ", "_"))
        SSD.show()

    @staticmethod
    def uploadingScreen():
        SSD.ellipse(4, 12, 3, 3, 1, 1)
        SSD.ellipse(4, 24, 3, 3, 1, 1)
        SSD.ellipse(4, 36, 3, 3, 1, 1)
        SSD.show()

    @staticmethod
    def loadingScreen():
        SSD.fill(0)
        SSD.rect(10, 10, 110, 43, 1)

        sum = 12
        x_pos = [12]
        for i in range(20):
            sum += 4.8
            x_pos.append(round(sum))

        percentages = [0]
        sum = 0
        for i in range(20):
            sum += 5 
            percentages.append(sum / 100)

        for i in range(20):
            if x_pos[i] == 0:
                continue
            SSD.fill_rect(x_pos[i],12,5,39,1)
            SSD.fill_rect(0, 56, 128, 40, 0)
            SSD.text("{:.0%}".format(percentages[i]), 58, 56)
            SSD.show()
            time.sleep_ms(2000)
            
        SSD.show()

    @staticmethod
    def dateScreen():
        SSD.fill(0)

        month = int(getTime()[5:7])
        day = getTime()[8:10]
        year = getTime()[:4]

        if month == 1: month = 'JAN'
        elif month == 2: month = 'FEB'
        elif month == 3: month = 'MAR'
        elif month == 4: month = 'APR'
        elif month == 5: month = 'MAY'
        elif month == 6: month = 'JUN'
        elif month == 7: month = 'JUL'
        elif month == 8: month = 'AUG'
        elif month == 9: month = 'SEP'
        elif month == 10: month = 'OCT'
        elif month == 11: month = 'NOV'
        elif month == 12: month = 'DEC'

        wri = Writer(SSD, arial35, verbose=False)
        Writer.set_textpos(SSD, 15, 10)
        wri.printstring(day)
        wri = Writer(SSD, arial15, verbose=False)
        Writer.set_textpos(SSD, 15, 75)
        wri.printstring(month)
        Writer.set_textpos(SSD, 35, 75)
        wri.printstring(year)

        gc.collect()

        SSD.show()

    @staticmethod
    def timeScreen():
        SSD.fill(0)
        
        wri = Writer(SSD, arial35, verbose=False)
        Writer.set_textpos(SSD, 15, 2) 
        wri.printstring(getTime()[11:16])

        gc.collect()

        SSD.show()