import machine as ESP32
import time

_pwm = ESP32.PWM(ESP32.Pin(27))
_pwm.deinit()

_max_duty = 1023
_max_freq = 40000

def stop():
    _pwm.duty(0)
    _pwm.deinit()

def successWifi():
    _pwm.init()
    duty_cycle = int(_max_duty * 0.9)

    _pwm.duty(duty_cycle)
    time.sleep_ms(200)
    _pwm.duty(0) 
    time.sleep_ms(150)
    _pwm.duty(duty_cycle) 
    time.sleep_ms(700)

    _pwm.deinit()
