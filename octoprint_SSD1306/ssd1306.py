import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import os
import sys

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


class SSD1306(object):
    y_offset = 0  # adjust as necessary for font

    def __init__(self):
        self._init_disp()

        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Load default font.
        self.font = ImageFont.truetype(_find_resource('font/PressStart2P.ttf'), 8)
        #self.font = ImageFont.load_default()

    def _init_disp(self):
        # 128x32 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
        
        # 128x64 display with hardware I2C:
        # self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        
        # Note you can change the I2C address by passing an i2c_address parameter like:
        # self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
        
        # Alternatively you can specify an explicit I2C bus number, for example
        # with the 128x32 display you would use:
        # self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=2)
        
        # 128x32 display with hardware SPI:
        # self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

        # 128x64 display with hardware SPI:
        # self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
        
        # Alternatively you can specify a software SPI implementation by providing
        # digital GPIO pin numbers for all the required display pins.  For example
        # on a Raspberry Pi with the 128x32 display you might use:
        # self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, dc=DC, sclk=18, din=25, cs=22)

    def clear(self, start=0, end=8):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, start * 8, self.width, min(end * 8, self.height) - 1), outline=0, fill=0)

    def write(self, row, txt):
        self.draw.text((0, row * 8 + self.y_offset), str(txt), font=self.font, fill=255)

    def commit(self):
        self.disp.image(self.image)
        self.disp.display()

