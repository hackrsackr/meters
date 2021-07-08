# 7/8/21

import json
from time import sleep
from ssl import CERT_NONE

from paho.mqtt import client as mqtt
import serial

import Adafruit_ADS1x15

# Host ip address
HOST = '192.168.1.17'
# Const dont change
HISTORY_TOPIC = 'brewcast/history'

TOPIC = HISTORY_TOPIC + '/meterscript'

# Create a websocket MQTT client
client = mqtt.Client(transport='websockets')
client.ws_set_options(path='/eventbus')
client.tls_set(cert_reqs=CERT_NONE)
client.tls_insecure_set(True)

#############################################################
# ADS1115 stuff

adc = Adafruit_ADS1x15.ADS1115()

# Gain  ->  0 - gain_maxv
# 2/3   ->  0 - 6.144v    1 bit = 3.000 mV
# 1     ->  0 - 4.096v    1 bit = 2.000 mV
# 2     ->  0 - 2.048v    1 bit = 1.000 mV
# 4     ->  0 - 1.024v    1 bit = 0.500 mV
# 8     ->  0 - 0.512v    1 bit = 0.250 mV
# 16    ->  0 - 0.256v    1 bit = 0.125 mV

# Set gain of ads1115
GAIN = 2/3

# Max readable volts based on gain setting
gain_maxv = 4.096 / GAIN

# 15-bit resolution 65535 bytes for 0 +/- 32768 each direction
ads_fullscale = 32768

# Convert read_adc to dc volts
voltage_factor = gain_maxv / ads_fullscale
###############################################################

###############################################################
# Sensor stuff

# Sensor VDD
sensor_voltage = 5

# Max pressure rating in PSI
pressure_rating = 60

# Bits at .5v or sensor zero state
sensor_offset = 2656

# Converts adc to psi
pressure_factor = pressure_rating / sensor_voltage
###############################################################

###############################################################
# Conversions

# Converts volts to mA
milliamp_factor = voltage_factor * 4

# Converts volts to pH
pH_factor = voltage_factor * 2

# Converts volts to microsiemens
conductivity_factor = voltage_factor * 10
###############################################################
# Do things
def get_ADC(channel):
    return adc.read_adc(channel, gain=GAIN)

def get_VOLTS(channel):
    return adc.read_adc(channel, gain=GAIN) * voltage_factor

def get_mA(channel):
    return adc.read_adc(channel, gain=GAIN) * milliamp_factor

def get_PSI(channel):
    return (adc.read_adc(channel, gain=GAIN) - sensor_offset) * pressure_factor

def get_pH(channel):
    return adc.read_adc(channel, gain=GAIN) * pH_factor

def get_COND(channel):
    return adc.read_adc(channel, gain=GAIN) * conductivity_factor
###############################################################
try:

    client.connect_async(host=HOST, port=443)
    client.loop_start()
    
    dict = {}
    keys = range(4)
    
    while True:
        for i in keys:
            dict[i] = round(get_pH(i), 2)
        
        value = json.dumps(dict)
        
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            continue
        
        print('json', value)

        message = {
                'key': 'meterscript',
                'data': value
        }
        client.publish(TOPIC, json.dumps(message))
        sleep(5)

finally:
    client.loop_stop()




