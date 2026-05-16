from machine import Pin
from time import sleep

a = Pin(27, Pin.IN, Pin.PULL_UP)
b = Pin(26, Pin.IN, Pin.PULL_UP)

position = 0
last_a = a.value()

def check_encoder(pin):
    global position, last_a

    new_a = a.value()
    new_b = b.value()

    if new_a != last_a:
        if new_b != new_a:
            position -= 1
        else:
            position += 1

        print("Position:", position)

    last_a = new_a

a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=check_encoder)
b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=check_encoder)

while True:
    sleep(1)