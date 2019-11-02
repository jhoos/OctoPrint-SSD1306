from ssd1306 import SSD1306
from time import sleep

x = SSD1306()
x.write(0, 'Hi there')
x.commit()
sleep(1)
x.write(1, "whee")
x.commit()
sleep(1)
x.write(3, "wowee")
x.commit()
sleep(1)

