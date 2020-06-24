import RPi.GPIO as GPIO
import time 
import sys, os
import wiringpi

def openclose(angle):
    GPIO.setmode(GPIO.BCM)

    gpout = 2
    GPIO.setup(gpout, GPIO.OUT)
    motor = GPIO.PWM(gpout, 50)
    motor.start(0.0)
    motor.ChangeDutyCycle(angle)
    time.sleep(0.5)

    GPIO.cleanup()

button_pin = 17

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(button_pin, 0)

wiringpi.pullUpDnControl(button_pin, 2)

while True:
    if(wiringpi.digitalRead(button_pin) == 0):
        print("on")
        if onor == 0:
            openclose(7.2)
            time.sleep(0.5)
        else:
            openclose(2.5)
            time.sleep(0.5)
    else:
        time.sleep(0.5)
        print("off")
