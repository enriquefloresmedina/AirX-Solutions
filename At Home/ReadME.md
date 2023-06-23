# AirX At Home
AirX At Home is the most basic version of the AirX sensor line. It features an SSD1306 display, an ESP32-Wroom-32 SoC, a PMS5003 particulate matter sensor, a BMP280 barometric pressure and temperature sensor, a DHT22 temperature and humidity sensor, as well as a custom PCB design.

AirX At Home makes sensor readings every 6 seconds, and uploads data to a RealTime Database every 300 seconds. The functionality of the software system can be described by the following Finite State Machine diagram:

![AwAir At Home FSM](https://github.com/enriquefloresmedina/AwAir-Sensor/blob/4cabe42b369ba62f1de1e5e241f5e9a23f68ece6/PCBs%2C%20schematics%2C%20and%20diagrams/At%20Home%20Plus/AwAir%20Software%20-%20At%20Home%20Plus.png)

