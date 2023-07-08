# Micropython for ESP32 using PyMakr Extension for VSCode

**1. Download the latest MicroPython firmware for ESP32**

https://micropython.org/download/esp32/ [v1.20.0 (2023-04-26) .bin] as of July, 2023

**2. Install esptool for Python**
```
pip install esptool
pip install setuptools
```
If it does not work, try using the prefix *py -m*:
```
py -m pip install --user esptool
py -m pip install --user setuptools
```
If you do not have Python, you can install the latest version here: https://www.python.org/downloads/

**3. Erase the ESP32 flash contents**
```
esptool -c esp32 -p COMXX erase_flash 
```
Or with the *py -m* prefix if it does not work:
```
py -m esptool -c esp32 -p COMXX erase_flash
```
**4. Upload the MicroPython firmware to the ESP32**

Make sure to navigate or specify the path where the firmware was installed before running the command
```
esptool -c esp32 -p COMXX -b 460800 write_flash -z 0x1000 [insert your .bin firmware file]
```
**5. Install Node.js to run the PyMakr extension**

https://nodejs.org/en [18.16.1 LTS] as of July, 2023

**6. Install the PyMakr extension for VS Code**

- Search for the extension on the VS Code explorer and install it
- If the extension does not work, downgrade to VS Code 1.56: https://code.visualstudio.com/updates/v1_56

**7. Change the PyMakr global settings**

- Add `Silicon Labs` to the `autoconnect_comport_manufacturers` if those are the drivers installed in your computer. You can check them by navigating to the device manager, and checking the Ports (COM & LPT) field
- Delete the `address` or add the COMXX to which your ESP32 is connected
- Set `auto_connect` to true only if you deleted the address

**8. Create a project and upload it to the ESP32**

- Create a folder with a *main.py* file or download the software for any of the *AirX Versions* into a folder
- Open that folder in the VS Code explorer
- Click `Upload`

The code will run after the upload is done. You can use *Ctrl+C* to stop the execution

# Micropython for ESP32 using PuTTY

**1. Follow the first four steps of the previous guide** 

These steps allow you to install the MicroPython firmware on the ESP32

**2. Install ampy**

```
pip install adafruit-ampy
```

**2. Upload/run/list/etc individual files to the ESP32 using ampy**
```
ampy -p COMXX put main.py
ampy -p COMXX run main.py
ampy -p COMXX ls
```

**3. Download and open PuTTY**

Download here: https://www.putty.org/

Select Serial, your COMXX, and a baudrate of 115200

**8. Run/debug Micropython from the terminal**

The individual files have to be uploaded using ampy, and PuTTY will be used as the serial terminal. PyMakr, on the other hand, allows you to upload multiple files at once, as well as to have an integrated terminal on VS Code.
