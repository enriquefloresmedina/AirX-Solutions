# AwAir At Home
AwAir At Home is the most basic version of the AwAir sensor line. It features an SSD1306 display, an ESP32-Wroom-32 SoC, a PMS5003 particulate matter sensor, a BMP280 barometric pressure and temperature sensor, a DHT22 temperature and humidity sensor, as well as a custom PCB design.

The sensor makes measurements every 7 seconds, and uploads data to a RealTime Database every 602 seconds. The functionality of the software system can be described by the following Finite State Machine diagram:
