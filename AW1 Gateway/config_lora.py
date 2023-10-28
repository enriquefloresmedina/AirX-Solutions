import time
          
# Node Name
import machine
import ubinascii 
uuid = ubinascii.hexlify(machine.unique_id()).decode()  
    
NODE_NAME = 'ESP32_'        
import esp
    
NODE_NAME = NODE_NAME + uuid

millisecond = time.ticks_ms

SOFT_SPI = None
from controller_esp import Controller