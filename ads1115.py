#
# probably going to use for 4-20mA meters
#
#
# just playing around with the module
# tryna get adc measurements directly on the rpi instead of arduino/esp -> rpi -> brewblox
# 7/3/21

import time
import Adafruit_ADS1x15

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

while True:
    for i in range(4):
        print("---------------------------------")
        print("ID:           ", i + 1)
        print("ADC:          ", get_ADC(i))
        print("Voltage:      ", get_VOLTS(i))
        print("Pressure:     ", get_PSI(i))
        print("pH:           ", get_pH(i))
        print("Conductivity: ", get_COND(i))
        print("---------------------------------")

    # sleep in between loops
    time.sleep(5)





