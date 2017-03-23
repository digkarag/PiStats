import os
import sys
import time
import glob
import signal
import RPi.GPIO as GPIO
from ubidots import ApiClient
from requests.exceptions import ConnectionError



#Signal handler for Ctrl+C to close leds
def signal_handler_Ctrl_C(signal, frame):
    print(' You pressed Ctrl+C!')
    # All Leds OFF
    GPIO.output(27,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    GPIO.output(22,GPIO.LOW)
    sys.exit(0)

def signal_handler_Ctrl_Z(signal, frame):
    print(' Logfile check: complete')
    # Blue Led OFF
    GPIO.output(23,GPIO.LOW)
    # Buzzer
    GPIO.output(25,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(25,GPIO.LOW)

signal.signal(signal.SIGINT, signal_handler_Ctrl_C)
signal.signal(signal.SIGTSTP, signal_handler_Ctrl_Z)


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
#Temp_f is optional value for fahrenheit degrees
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


#Ubidots Connection and valiable creation
try:
    api = ApiClient(token="peXr4PTbhJl1A2AEJxHc0xQGQMxVcD")
    temp = api.get_variable("58cd1a6c76254225983f07a1")

except ConnectionError as errorconn:

    print errorconn
    #LogFile entry
    file=open("logfile.txt","a")
    file.write(time.strftime("%H:%M:%S") +" , "+time.strftime("%d/%m/%Y"))
    file.write(str(errorconn)+'\n')
    file.close()

#GPIO Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(24,GPIO.OUT) # White led

# Buzzer
GPIO.output(25,GPIO.HIGH)
time.sleep(0.5)
GPIO.output(25,GPIO.LOW)

while True:

    #Green Led ON
    GPIO.output(17,GPIO.HIGH)
    time.sleep(2)

    #Read temperature from sensor
    deg_c = read_temp()

    #Sending value to Ubidots via save_value function
    try:

        temp.save_value({"value": deg_c})

        #Red Led OFF
        GPIO.output(27,GPIO.LOW)
        #Yellow Led OFF
        GPIO.output(22,GPIO.LOW)

    except  ConnectionError as ex:
        print ex

        #LogFile entry
        file=open("logfile.txt","a")
        file.write(time.strftime("%H:%M:%S") +" , "+time.strftime("%d/%m/%Y"))
        file.write(str(ex)+'\n')
        file.close()

        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)
        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)

    except ValueError as ex1:
        print ex1

        #LogFile entry
        file=open("logfile.txt","a")
        file.write(time.strftime("%H:%M:%S") +" , "+time.strftime("%d/%m/%Y"))
        file.write(str(ex1)+'\n')
        file.close()

        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)
        #Yellow Led ON
        GPIO.output(22,GPIO.HIGH)
        time.sleep(10)


    except ubidots.apiclient.UbidotsError404 as ex2:
        print ex2

        #LogFile entry
        file=open("logfile.txt","a")
        file.write(time.strftime("%H:%M:%S") +" , "+time.strftime("%d/%m/%Y"))
        file.write(str(ex2)+'\n')
        file.close()

        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)
        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)


    except upidots.apiclient.UbidotsError500 as ex3:
        print ex3

        #LogFile entry
        file=open("logfile.txt","a")
        file.write(time.strftime("%H:%M:%S") +" , "+time.strftime("%d/%m/%Y"))
        file.write(str(ex3)+'\n')
        file.close()

        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)
        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)


    #Print functions
    print( time.strftime("%d/%m/%Y") + ", " + time.strftime("%H:%M:%S") + ", "
            + 'Temperature in Celsius: ' + str(deg_c) + '\n')

    #Green Led OFF
    GPIO.output(17,GPIO.LOW)
    time.sleep(2)
