from gpiozero import LED
from time import sleep

led1 = LED(21)
led2 = LED(26)
led3 = LED(19)

while True:
        led1.on()
        sleep(0.1)
        led1.off()
        led2.on()
        sleep(0.1)
        led2.off()
        led3.on()
        sleep(0.1)
        led3.off()
