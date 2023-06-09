# Micropython for ESP32 using PyMakr Extension for VSCode

1. Download micropython firmware for esp32
https://micropython.org/download/esp32/  [v1.20.0 (2023-04-26) .bin as of 2023]

2. Install esptool
pip install esptool
pip install setuptools
(try "py -m esptool" if it does not work)
("py -m pip install --user esptool" if it still does not work)

3. Erase esp32 files
esptool -c esp32 -p COMXX erase_flash 

4. Upload micropython firmware for the esp32
esptool -c esp32 -p COMXX -b 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin

5. Install Node.js
https://nodejs.org/en [18.15.0 LTS as of 2023]

6. Install PyMakr extension for VS Code
Search for the extension and install it
*If the extension has errors, downgrade VS Code 1.56 (https://code.visualstudio.com/updates/v1_56)

7. Change the PyMakr global settings
Add "Silicon Labs" to the "autoconnect_comport_manufacturers" if those are the drivers you have installed
Delete the "address" or add the COMXX to which your esp32 is connected to
Set "auto_connect" to true if you deleted the address, and viceversa

8. Create a project and upload to esp32
Create a folder with main.py and boot.py files
Open that folder in the VS Code explorer
Click on upload (Ctrl+C to stop the execution of the code)

# Micropython for ESP32 using PUTTY

1. Download micropython firmware for esp32
https://micropython.org/download/esp32/ [v1.20.0 (2023-04-26) .bin as of 2023]

2. Install esptool
pip install esptool
pip install setuptools
(try "py -m esptool" if it does not work)
("py -m pip install --user esptool" if it still does not work)

3. Erase esp32 files
esptool --chip esp32 --port COMXX erase_flash 
(try py -m esptool if it does not work)

4. Upload esp32 firmware to work with micropython
esptool -c esp32 -p COMXX -b 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin

5. Install ampy
pip install adafruit-ampy

6. Upload/run/list/etc individual files to the esp32 using ampy
ampy -p COMXX put main.py
ampy -p COMXX run main.py
ampy -p COMXX ls

7. Download and open PuTTY
Select Serial, your COMXX, and baudrate of 115200

8. Run/debug Micropython from the terminal
