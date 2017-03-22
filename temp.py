import os
import glob
import time
import RPi.GPIO as GPIO
from ubidots import ApiClient
from requests.exceptions import ConnectionError

import signal
import sys

#Signal handler for Ctrl+C to close leds
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    GPIO.output(27,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    GPIO.output(22,GPIO.LOW)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#Read from w1_slave file
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#Extract and return temperature from w1_slave
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        temp_c = round(temp_c, 1)
        return temp_c

try:
    #Ubidots connection
    api = ApiClient(token="peXr4PTbhJl1A2AEJxHc0xQGQMxVcD")
    #Create variable
    temp = api.get_variable("58cd1a6c76254225983f07a1")
except ConnectionError as e:
    print e

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)

while True:

    #Green Led ON
    GPIO.output(17,GPIO.HIGH)
    time.sleep(1)

    #Read temperature from sensor
    deg_c = read_temp()

    try:
        #Save temperature and send to ubidots
        temp.save_value({"value": deg_c})
        #Red Led OFF
        GPIO.output(27,GPIO.LOW)
        #Yellow Led OFF
        GPIO.output(22,GPIO.LOW)

    except  ConnectionError as ex:
        print ex
        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
    except ValueError as ex:
        print ex1
        #Yellow Led ON
        GPIO.output(23,GPIO.HIGH
                )
    except ubidots.apiclient.UbidotsError404 as ex2:
        print ex2
        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)

    except upidots.apiclient.UbidotsError500 as ex3:
        print ex3
        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)

    #Print functions
    print
    print(time.strftime("%H:%M:%S") +" , " + time.strftime("%d/%m/%Y"))
    print('Temperature in Celsius: ' + str(deg_c))
    print

    #Green Led OFF
    GPIO.output(17,GPIO.LOW)
    time.sleep(1)
