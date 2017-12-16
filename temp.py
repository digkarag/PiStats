import os
import sys
import time
import glob
import dht11
import signal
import datetime
import RPi.GPIO as GPIO
import requests

url = "http://things.ubidots.com/api/v1.6/devices/ZeroW/?token=A1E-ZCaNbMJodCnxdT2GPU53PIDkUSwnma"

#GPIO Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Signal handler for Ctrl+C
def signal_handler_Ctrl_C(signal, frame):
    print(' You pressed Ctrl+C!')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler_Ctrl_C)

#Read data using pin 21 DHT11
instance = dht11.DHT11(pin=21)

while True:
   #Read Data from DHT11
    result = instance.read()
    if result.is_valid():
        try:
            humidity = result.humidity
            payload ={'Humidity': humidity}
            response = requests.post(url,data=payload)
        except Exception as ex:
            time.sleep(5)
        time.sleep(1)

        #Test prints
        print response
        print result.humidity

    time.sleep(10)
