# import Adafruit_GPIO.SPI as SPI
from board import SCL, SDA
import adafruit_ssd1306
import busio
import os
import sys
import threading

from copy import copy
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep

# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0


def _find_resource(file):
    # Find a resource in the same parent module as this module
    guesses = []
    for p in sys.path:
        f = os.path.join(p, os.path.dirname(__file__), file)
        guesses.append(f)
        if os.path.isfile(f):
            return f
    raise ValueError('Cannot find resource {} at {}'.format(file, guesses))


class SSD1306(threading.Thread):
    daemon = True
    _y_offset = 0  # adjust as necessary for font
    _row_height = 8
    _lock = threading.Lock()
    _rows = []
    _committed_rows = []
    _stop = False

    def __init__(self):
        super(SSD1306, self).__init__()
        self._init_disp()

        # Initialize library.

        # Clear display.

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self._width = self._disp.width
        self._height = self._disp.height
        self._image = Image.new('1', (self._width, self._height))

        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)

        # Load default font.
        self._font = ImageFont.truetype(_find_resource('font/PressStart2P.ttf'), 8)

        self.clear()
        self.commit()

        self.start()

    def _init_disp(self):
        # 128x32 display with hardware I2C:
        # self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
        i2c = busio.I2C(SCL, SDA)
        self._disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        
        # 128x64 display with hardware I2C:
        # self._disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        
        # Note you can change the I2C address by passing an i2c_address parameter like:
        # self._disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
        
        # Alternatively you can specify an explicit I2C bus number, for example
        # with the 128x32 display you would use:
        # self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=2)
        
        # 128x32 display with hardware SPI:
        # self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

        # 128x64 display with hardware SPI:
        # self._disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
        
        # Alternatively you can specify a software SPI implementation by providing
        # digital GPIO pin numbers for all the required display pins.  For example
        # on a Raspberry Pi with the 128x32 display you might use:
        # self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, dc=DC, sclk=18, din=25, cs=22)

        self._disp.begin()
        self._disp.clear()

    def run(self):
        self._init_disp()

        while not self._stop:
            with self._lock:
                rows = copy(self._committed_rows)

            print(rows)
            self._clear_image()
            for (r, t) in enumerate(rows):
                self._write_text_to_image(r, t)

            self._disp.image(self._image)
            self._disp.display()

            sleep(0.5)

    def stop(self):
        self._stop = True
        self.join()
        self._disp.clear()


    def clear(self, start=0, end=None):
        """
        Draw a black filled box to clear the image.
        """
        if start == 0 and end is None:
            self._rows = [''] * (self._height / self._row_height)
        else:
            for i in range(start, end or self._height / self._row_height):
                self._rows[i] = ''

    def write(self, row, txt):
        """
        Write a single row of text, clearing whatever was on the row previously.
        """
        self._rows[row] = str(txt)

    def _clear_image(self):
        self._draw.rectangle((0, 0, self._width, self._height), outline=0, fill=0)

    def _write_text_to_image(self, row, txt):
        self._draw.text((0, row * self._row_height + self._y_offset), txt, font=self._font, fill=255)

    def commit(self):
        """
        Send the current display buffer to the device.
        """
        with self._lock:
            self._committed_rows = copy(self._rows)

