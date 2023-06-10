import machine as ESP32
from setup import PMS

def interrupt(timer):
    state = ESP32.disable_irq()

    timer.deinit()
    
    ESP32.enable_irq(state)

    PMS.wakeUp()
