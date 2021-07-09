# 7/8/21

import json
from time import sleep
from ssl import CERT_NONE

from paho.mqtt import client as mqtt
import serial

import Adafruit_ADS1x15

#############################################################
# Websocket setup

# Host ip address
HOST = '192.168.1.17'

# Const dont change
HISTORY_TOPIC = 'brewcast/history'

# The heistory service is subscribed to all topics starting with 'brewcast/history'
# Can make more specific for debugging
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

# Convert raw_data to dc volts
# ADC fullscale mapped to 0 - 6.144 volts
voltage_factor = gain_maxv / ads_fullscale

# Converts raw data into mA
# Output range is 0-20mA mapped to 0-5vdc
milliamp_factor = voltage_factor * 4

# Converts raw data to pH
# Output range is 0-10pH mapped to 0-5vdc
pH_factor = voltage_factor * 2

# ADC -> volts DC
def get_volts(channel):
    return adc.read_adc(channel, gain=GAIN) * voltage_factor

# ADC -> volts DC
def get_ma(channel):
    return adc.read_adc(channel, gain=GAIN) * milliamp_factor
###############################################################

###############################################################
# Specific conversion
def get_ph(channel):
    return adc.read_adc(channel, gain=GAIN) * pH_factor
###############################################################

try:

    client.connect_async(host=HOST, port=443)
    client.loop_start()

    data = {}
    keys = range(4)

    while True:
        for i in keys:
            data[i] = round(get_ph(i), 2)

        value = json.dumps(data)

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




