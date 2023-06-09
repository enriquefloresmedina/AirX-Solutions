# Fonts and images used for SSD1306 display
Using phoreglad's img_to_mono_hlsb repository: https://github.com/phoreglad/img_to_mono_hlsb/blob/main/img_to_mono_hlsb.py and Peter Hinch's micropython-font-to-py repository: https://github.com/peterhinch/micropython-font-to-py, images were converted to MONO_HSLB Framebuf format, and font files in either TTF or OTF format were converted to bytearrays. 

With this, using the Writer class in https://github.com/peterhinch/micropython-font-to-py allowed the formatting of text on the display. The transforamtion of images allowed for the use of Framebuf to easily map icons on the display.
