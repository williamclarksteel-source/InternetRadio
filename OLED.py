from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
WIDTH =128 
HEIGHT= 32
i2c=I2C(0,scl=Pin(5),sda=Pin(4),freq=200000)
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)
while True:
    oled.fill(0)
    oled.text("Hello World", 0, 0)
    oled.text("WCS", 0, 20)
    oled.show()