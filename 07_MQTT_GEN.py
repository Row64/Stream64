import asyncio
import websockets
import logging
import row64tools
import os
import struct
import random
import threading
import time
import random
import paho.mqtt.client as mqtt
import math

class MqttCom():

	def __init__(self, broker_address):
		self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
		self.client.on_message = self.on_message
		self.client.connect(broker_address)
		threading.Thread(target=self.__run, daemon=True).start()
		self.queue = []

	def __run(self):
		self.client.loop_forever()

	def on_message(self, client, userdata, msg):
		self.queue.append([msg.topic, msg.payload])

	def publish(self, topic, payload):
		self.client.publish(topic, payload=payload)

	def register_handler(self, topic: str):
		self.client.subscribe(topic)

def main():
	
	print("MGen - MQTT Circle Movement Test")
	mc = MqttCom("localhost")
	mc.register_handler("example/#")
	M_2PI = 6.28318530718
	circleDiv = 256
	aStep = M_2PI / circleDiv
	cx = -97.29451
	cy = 39.908065
	rad = 9.4 
	ang = 0
	while True:
		xp = cx+rad*math.cos(ang)
		yp = cy+rad*math.sin(ang)
		val = "["  + str(xp) + ","+str(yp)+"]"
		mc.publish("example/id1/loc",val)
		time.sleep(.015) # update rate in seconds
		ang += aStep

main()