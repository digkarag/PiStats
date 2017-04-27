import os
import sys
import time
import glob
import logging
import signal
import ubidots
import RPi.GPIO as GPIO
from requests.exceptions import ConnectionError

#Sleep for autorun feature, waiting for OS loading time
time.sleep(30)


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


#GPIO Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)


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


#Signal handler for Ctrl+C to close leds
def signal_handler_Ctrl_C(signal, frame):
    print(' You pressed Ctrl+C!')
    #All Leds OFF
    GPIO.output(27,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    GPIO.output(22,GPIO.LOW)
    GPIO.output(24,GPIO.LOW)
    sys.exit(0)


#Signal handler for Ctrl+Z for LogFile indicator clear
def signal_handler_Ctrl_Z(signal, frame):
    print(' Logfile check: complete')
    #Blue Led OFF
    GPIO.output(23,GPIO.LOW)
    #Buzzer
    GPIO.output(25,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(25,GPIO.LOW)


signal.signal(signal.SIGINT, signal_handler_Ctrl_C)
signal.signal(signal.SIGTSTP, signal_handler_Ctrl_Z)


#LogFile Function
def logFile(error):
    #I tried with logging python
    logging.basicConfig(filename='logfile.txt',level=logging.ERROR);
    logging.warnign(str(error) + '\n');


    try:

        file=open("logfile.txt","a+")
        file.write(time.strftime("%H:%M:%S") +" , "+time.strftime("%d/%m/%Y")+" , ")
        file.write(str(error)+'\n')
        file.close()

        #Blue Led ON
        GPIO.output(23,GPIO.HIGH)

    except Exception as error:

        print error
        sys.exit(0)


#Ubidots Connection and valiable creation
try:
    api = ubidots.ApiClient(token="peXr4PTbhJl1A2AEJxHc0xQGQMxVcD")
    temp = api.get_variable("58cd1a6c76254225983f07a1")

    #White LED OFF
    GPIO.output(24,GPIO.LOW)

except Exception as error:

    print error
    #White Led ON
    GPIO.output(24,GPIO.HIGH)
    time.sleep(10)

    #LogFile entry
    logFile(error)

    #Red Led ON
    GPIO.output(27,GPIO.HIGH)
    time.sleep(10)


#Buzzer, single beep at program startup
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
        #White Led OFF
        GPIO.output(24,GPIO.LOW)

    except ConnectionError as ex:
        print("Connection error"+"\n")
        print ex
        sys.stdout.flush()

        #LogFile entry
        logFile(ex)

        #Yellow Led ON
        GPIO.output(22,GPIO.HIGH)
        time.sleep(10)

    except ValueError as ex1:
        print("ValueError"+"\n")
        print ex1
        sys.stdout.flush()

        #LogFile entry
        logFile(ex1)

        #Yellow Led ON
        GPIO.output(22,GPIO.HIGH)
        time.sleep(10)

    except ubidots.UbidotsError500 as ex2:
        print("Ubidots Error 500"+"\n")
        print ex2
        sys.stdout.flush()

        #LogFile entry
        logFile(ex2)

        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)

    except ubidots.UbidotsError404 as ex3:
        print("Ubidots Error 404"+"\n")
        print ex3
        sys.stdout.flush()

        #LogFile entry
        logFile(ex3)

        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)

    except ubidots.UbidotsError400 as ex4:
        print("Ubidots Error 400"+"\n")
        print ex4
        sys.stdout.flush()

        #LogFile entry
        logFile(ex4)

        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)

    except Exception as ex5:
        print("General Exception"+"\n")
        print ex5
        sys.stdout.flush()

        #LogFile entry
        logFile(ex5)

        #Red Led ON
        GPIO.output(27,GPIO.HIGH)
        time.sleep(10)


    #Print functions
    print( time.strftime("%d/%m/%Y") + ", " + time.strftime("%H:%M:%S") + ", "
            + 'Temperature in Celsius: ' + str(deg_c) + '\n')
    sys.stdout.flush()

    #Green Led OFF
    GPIO.output(17,GPIO.LOW)
    time.sleep(2)
