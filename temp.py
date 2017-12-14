import os
import sys
import dht11
import datetime
import time
import glob
import signal
import RPi.GPIO as GPIO
import requests

from data import posturl
url = posturl

#GPIO Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()

GPIO.setup(17,GPIO.OUT) #Green Led: System Run indicator
GPIO.setup(27,GPIO.OUT) #Red Led: Connection Error
GPIO.setup(22,GPIO.OUT) #White Led: Logfile Entry
GPIO.setup(23,GPIO.OUT) #Yellow Led: Ubidots Error
GPIO.setup(25,GPIO.OUT) #Buzzer

#Signal handler for Ctrl+C to close leds
def signal_handler_Ctrl_C(signal, frame):
    #print(' You pressed Ctrl+C!')
    #All Leds OFF
    GPIO.output(27,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    GPIO.output(22,GPIO.LOW)
    GPIO.output(23,GPIO.LOW)
    GPIO.output(25,GPIO.LOW)
    sys.exit(0)


#Signal handler for Ctrl+Z for LogFile indicator clear
def signal_handler_Ctrl_Z(signal, frame):
    #print(' Logfile check: complete')
    #White Led OFF
    GPIO.output(22,GPIO.LOW)
    #Buzzer
    GPIO.output(25,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(25,GPIO.LOW)


signal.signal(signal.SIGINT, signal_handler_Ctrl_C)
signal.signal(signal.SIGTSTP, signal_handler_Ctrl_Z)

#Read data using pin 21 DHT11
instance = dht11.DHT11(pin=21)

while True:
   #Read Data from DHT11
    result = instance.read()
    if result.is_valid():
        try:
            humidity = result.humidity
            payload ={'Humidity': humidity}
            postresp = requests.post(url,data=payload)
            print postresp
        except Exception as ex:
            time.sleep(5)
        print result.humidity
        time.sleep(1)
    time.sleep(1)
