# AwAir At Home Plus
AwAir At Home Plus is an update version of the AwAir At Home line. It features an Nextion nx3224t024 2.4 inch display, an ESP32-Wroom-32 SoC, a Sensirion SEN55 particulate matter, tVOC, temperature and humidity sensor, a BMP280 barometric pressure and temperature sensor, a DHT22 temperature and humidity sensor, as well as a custom PCB design.

Just as the At Home version, this system takes sensor readings every 7 seconds, and uploads data to a RealTime Database every 602 seconds. The functionality of the software system can be described by the following Finite State Machine diagram:

![AwAir At Home Plus FSM](https://github.com/enriquefloresmedina/AwAir-Sensor/blob/4cabe42b369ba62f1de1e5e241f5e9a23f68ece6/PCBs%2C%20schematics%2C%20and%20diagrams/At%20Home%20Plus/AwAir%20Software%20-%20At%20Home%20Plus.png)
