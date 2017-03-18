import os
import glob
import time
from ubidots import ApiClient

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# read from w1_slave file
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

# extract and return temperature from w1_slave
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
        round(temp_c, 1)
        temp_c = ("%.1f" % temp_c)
        return float(temp_c)

# Ubidots connection
api = ApiClient(token="peXr4PTbhJl1A2AEJxHc0xQGQMxVcD")

# Create variable
temp = api.get_variable("58cd1a6c76254225983f07a1")

while True:

    # read temperature from sensor
    deg_c = read_temp()

    # save temperature and send to ubidots
    temp.save_value({"value": deg_c})

    '''
    # Print functions
    print("--------------------------------")
    print(time.strftime("%H:%M:%S"))
    print(time.strftime("%d/%m/%Y"))
    print
    print('TEMPERATURE IN CELSIUS:     ' + str(deg_c))
    print("--------------------------------")
    print
    time.sleep(0.1)
    '''
