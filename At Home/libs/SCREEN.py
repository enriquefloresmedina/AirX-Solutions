import machine as ESP32
from libs.WRITER import Writer
from libs.TIME import getTime, setTime
from fonts import arial15, arial35, arial9
from icons import drop, termometer, pressure, pm10, pm25, pm100, wifiOk, wifiErr, uploading
import framebuf
import time
import gc

COUNT = 1
POWER = True
PM10 = PM25 = PM100 = HUM = TEMP = PRESS = 0
DISABLE = False

class Screen():
    
    @staticmethod
    def setMeasurments(data):
        global PM10, PM25, PM100, HUM, TEMP, PRESS

        PM10 = data[0]; PM25 = data[1]; PM100 = data[2]
        TEMP = data[3]; HUM = data[4]; PRESS = data[5]

        Screen._update()

    @staticmethod
    def disableScreens():
        global DISABLE
        DISABLE = True

    @staticmethod
    def enableScreens():
        global DISABLE
        DISABLE = False

    @staticmethod
    def _update():
        if not DISABLE:
            if not POWER: SSD.fill(0); SSD.show()
            elif COUNT == 1: Screen.mainScreen(PM10, 'PM1.0')
            elif COUNT == 2: Screen.mainScreen(PM25, 'PM2.5')
            elif COUNT == 3: Screen.mainScreen(PM100, 'PM10')
            elif COUNT == 4: Screen.mainScreen(HUM, 'H')
            elif COUNT == 5: Screen.mainScreen(TEMP, 'T')
            elif COUNT == 6: Screen.mainScreen(PRESS, 'P')
            elif COUNT == 7: Screen.timeScreen()
            else: Screen.wifiScreen(WIFI.status(), WIFI._ssid)

    @staticmethod
    def setSSD(ssd):
        global SSD
        SSD = ssd
    
    @staticmethod
    def setWIFIandTime(wifi):
        global WIFI    
        WIFI = wifi
        setTime()
    
    def __init__(self, btn_pin, mode = '+', debounceDelayMS = 175):
        self.button = ESP32.Pin(btn_pin, ESP32.Pin.IN, ESP32.Pin.PULL_UP)
        self.lastTime = 0
        self.debounceDelayMS = debounceDelayMS
        self.mode = mode
        self.button.irq(trigger=ESP32.Pin.IRQ_RISING, handler=self._onPress)
        Screen._update()

    def _onPress(self, pin):
        global COUNT, POWER

        state = ESP32.disable_irq()
 
        if time.ticks_ms() - self.lastTime > self.debounceDelayMS:
            if self.button.value() == 1:
                if self.mode == '+' and POWER: 
                    if COUNT < 8: COUNT += 1
                    else: COUNT = 1
                elif self.mode == '-' and POWER:
                    if COUNT > 1: COUNT -= 1
                    else: COUNT = 8
                else:
                    POWER = not POWER
                Screen._update()
            self.lastTime = time.ticks_ms()

        ESP32.enable_irq(state)

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
            SSD.blit(Screen._getImage(pm100), 0, -4)
            scaledMeas = getScaledMeas(meas)
        elif mode == 'PM2.5':
            SSD.blit(Screen._getImage(pm25), 0, -4)
            scaledMeas = getScaledMeas(meas)
        else:
            SSD.blit(Screen._getImage(pm10), 0, -4)
            scaledMeas = getScaledMeas(meas)

        wri = Writer(SSD, arial35, verbose=False)
        if meas < 0:
            meas = -meas
            SSD.rect(0, SSD.height - 40, 11, 5, 1, 1)
        Writer.set_textpos(SSD, 7, 42 - len(str(meas)) * 14) 
        wri.printstring('{!s}'.format(meas))

        SSD.rect(0, SSD.height - 12, SSD.width, 12, 1, 0)
        SSD.rect(2, SSD.height - 10, scaledMeas, 8, 1, 1)

        if mode == 'PM1.0' or mode == 'PM2.5' or mode == 'PM10':
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
        SSD.fill(0)
        SSD.blit(Screen._getImage(uploading), 0, 0)
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
    def timeScreen():
        SSD.fill(0)
        
        time = getTime()
        wri = Writer(SSD, arial35, verbose=False)
        Writer.set_textpos(SSD, 15, 2) 
        wri.printstring('{:02d}:{:02d}'.format(time[3], time[4]))

        gc.collect()

        SSD.show()