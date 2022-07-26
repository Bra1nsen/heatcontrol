#!/usr/bin/env python
import board
import time
import datetime
from datetime import date
from openpyxl import load_workbook
from bme280 import BME280
from smbus import SMBus
from adafruit_bme280 import basic as adafruit_bme280
import SI1145.SI1145 as SI1145
import adafruit_ltr390
import adafruit_veml6070  
import csv
from time import strftime, sleep
import paho.mqtt.client as mqtt
import json


def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	#print("message received: ", msg)
	#print("message topic: ", message.topic)

def on_connect(client, userdata, flags, rc):
	client.subscribe('skycam/picam2021/metrics')

# Create sensor object, default I2C bus
bus = SMBus(1)
#bme280 = BME280(i2c_dev=bus)
i2c = board.I2C()   
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
i2c = board.I2C()   
ltr = adafruit_ltr390.LTR390(i2c)
si1145 = SI1145.SI1145()
uv1 = adafruit_veml6070.VEML6070(i2c)

# open the file in the write mode
with open('/home/pi/weather/weather.csv', 'a', newline="") as log:

	writer = csv.writer(log)
	#writer.writerow(["Satellit", "", "BME280", "", "", "LTR390", "", "", "", "SI1145", "", "", "VEML6070"])
	#writer.writerow(["Datum", "Zeit", "Temperatur", "Druck", "rel_Luftfeuchtigkeit", "uv", "amblight", "UVI", "lux", "vis", "IR", "uvIndex", "uv_raw", "risk_level"])

	if True:
	
		today = date.today()
		now = datetime.datetime.now().time()
		now_format = now.strftime("%H:%M:%S")
		unix_timestamp = time.time()
		#BME280	
		
		temperature = round(bme280.temperature,1)
		pressure = round(bme280.pressure,1)
		humidity = round(bme280.relative_humidity,1)
		#temperature = round(bme280.get_temperature(),1)
		#pressure = round(bme280.get_pressure(),1)
		#humidity = round(bme280.get_humidity(),1)
		#LTR390
		uv = round(ltr.uvs,2)
		amblight = round(ltr.light,2)
		UVI = round(ltr.uvi,2)
		lux = round(ltr.lux,2)
		#SI1145
		vis = round(si1145.readVisible(),2)
		IR = round(si1145.readIR(),2)
		UV2 = round(si1145.readUV(),2)
		uvIndex = UV2 / 100.0
		#VEML6070
		uv_raw = round(uv1.uv_raw,2)
		risk_level = uv1.get_index(uv_raw)

		# Append data to the spreadsheet
		row = (today, now_format, temperature, pressure, humidity, uv, amblight, UVI, lux, vis, IR, uvIndex, uv_raw, risk_level) 
	
		# write a row to the csv file
		writer.writerow(row)
			
		print(f"Datum: {today}, Zeit: {now_format}, Temperatur:{temperature}°C, Druck:{pressure}hPa, rel_Luftfeuchtigkeit:{humidity}%, uv_LTR={uv}, lux={lux}, uv_VEML={uv_raw}")
		
		print("saved in weather.csv")
		
		BROKER_ADDRESS = "buero.easd-support.de"
		PORT = 48883
		TOPIC = 'skycam/picam2021/metrics'
		USER = "skycam"
		PW = "WDFMFkt5Dbc5uEnTR8Xz"
		
		jsonO1_Temp = { "timestamp": unix_timestamp, "urn": "Ta", "value": temperature, "unit": "°C", "source": "", "minInterval": "0", "status": "0"}
		jsonO2_Druck = { "timestamp": unix_timestamp, "urn": "Pa", "value": pressure, "unit": "hPa", "source": "", "minInterval": "0", "status": "0"}
		jsonO3_relLF = { "timestamp": unix_timestamp, "urn": "Ua", "value": humidity, "unit": "%RH", "source": "", "minInterval": "0", "status": "0"}
		jsonO4_uv = { "timestamp": unix_timestamp, "urn": "UV_AB", "value": uv, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		jsonO5_amblight = { "timestamp": unix_timestamp, "urn": "I_amb", "value": amblight, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		jsonO6_UVI = { "timestamp": unix_timestamp, "urn": "UVI", "value": UVI, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		jsonO7_lux = { "timestamp": unix_timestamp, "urn": "Ev", "value": lux, "unit": "lx", "source": "", "minInterval": "0", "status": "0"}
		jsonO8_vis = { "timestamp": unix_timestamp, "urn": "I_vis", "value": vis, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		jsonO9_IR = { "timestamp": unix_timestamp, "urn": "I_ir", "value": IR, "unit": "count", "source": "", "minInterval": "0", "status": "0"}
		jsonO10_uvIndex = { "timestamp": unix_timestamp, "urn": "UVI_raw", "value": uvIndex, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		jsonO11_uvraw = { "timestamp": unix_timestamp, "urn": "UV_AB_raw", "value": uv_raw, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		jsonO12_risklevel = { "timestamp": unix_timestamp, "urn": "UV_risk", "value": risk_level, "unit": "", "source": "", "minInterval": "0", "status": "0"}
		json_list_sensors = [jsonO1_Temp, jsonO2_Druck, jsonO3_relLF, jsonO4_uv, jsonO5_amblight, jsonO6_UVI, jsonO7_lux, jsonO8_vis, jsonO9_IR, jsonO10_uvIndex, jsonO11_uvraw, jsonO12_risklevel]
		jsonSUMsensor = json.dumps(json_list_sensors) 
		mqtt_file = { "source": "SkyCam21F19", "psk": "", "content": jsonSUMsensor, "type": "json", "sendTime": "0"}
		jsonFile = json.dumps(mqtt_file)
		rowStr = (str(temperature), str(pressure), str(humidity), str(uv), str(amblight), str(UVI), str(lux), str(vis), str(IR), str(uvIndex), str(uv_raw), risk_level)
		jsonStr = json.dumps(rowStr)
		
		client = mqtt.Client()
		client.username_pw_set(USER, PW)
		client.on_connect = on_connect
		client.on_message = on_message
		client.connect(BROKER_ADDRESS, PORT)
		client.loop_start()
		
		
		client.publish(TOPIC, jsonFile, 1)
		#msgs = [{'topic': "skycam/picam2021/metrics", 'payload': "multiple 1"}, ("skycam/picam2021/metrics", str(temperature), 1), ("skycam/picam2021/metrics", str(pressure), 1)]
		#publish.multiple(msgs, hostname="skycam/picam2021/metrics"



		print("Connected to MQTT Broker: " + BROKER_ADDRESS)

		
		
		# Wait for 30 seconds
		time.sleep(3)
		
		

