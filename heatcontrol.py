#!/usr/bin/env python


import time
import RPi.GPIO as GPIO
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280

print("""heatcontrol.py - humidity > 80% --> HEATWIRE ON""")




# Initialise the BME280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)


try:
    
    while True:
    
        temperature = bme280.get_temperature()
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()
    
        print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'.format(temperature, pressure, humidity))
        
    
        if humidity>85:
            GPIO.setmode(GPIO.BCM) # BCM-Nummerierung verwenden
            GPIO.setup(17, GPIO.OUT) # GPIO 17 (Pin 11) als Ausgang setzen
            GPIO.output(17, True) # GPIO 17 (Pin 11) auf HIGH setzen
            print('HEAT WIRE ON')
           
        else:
            GPIO.setmode(GPIO.BCM) # BCM-Nummerierung verwenden
            GPIO.setup(17, GPIO.OUT)
            GPIO.output(17, False)
            print('HEAT WIRE OFF')
       
        time.sleep(60)
        

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
        

