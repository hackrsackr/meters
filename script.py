"""
Example for reading from a serial port inside a container

Dependencies:
- pyserial
"""
import json
import serial
from ssl import CERT_NONE
from time import sleep
from paho.mqtt import client as mqtt

# This is the default serial port
PORT = '/dev/ttyUSB0'
#PORT = '/dev/ttyUSB1'
#PORT = '/dev/ttyUSB2'
#PORT = '/dev/ttyUSB3'


# 172.17.0.1 is the default IP address for the host running the Docker container
# Change this value if Brewblox is installed on a different computer
HOST = '192.168.1.6'

# This is a constant value. You never need to change it.
HISTORY_TOPIC = 'brewcast/history'

# The history service is subscribed to all topics starting with 'brewcast/history'
# We can make our topic more specific to help debugging
TOPIC = HISTORY_TOPIC + '/meterscript'

# Create a websocket MQTT client
client = mqtt.Client(transport='websockets')
client.ws_set_options(path='/eventbus')
client.tls_set(cert_reqs=CERT_NONE)
client.tls_insecure_set(True)

# You may need to further configure settings
# See the pyserial documentation for more info
# https://pythonhosted.org/pyserial/pyserial_api.html#classes
ser = serial.Serial(port=PORT,
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)

try:

    client.connect_async(host=HOST, port=443)
    client.loop_start()

    while True:
        # Read raw data from the stream
        # Convert the binary string to a normal string
        # Remove the trailing newline character
        value = ser.readline().decode().strip().strip()
        print('decoded', value)
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

finally:
    ser.close()
    client.loop_stop()

