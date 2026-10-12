import asyncio as asyn
import websockets as ws
import random
from row64tools.stream64 import stream64
import pandas as pd
import paho.mqtt.client as mqtt
import threading
import json
import os

class MqttCom():

    def __init__(self, broker_address):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_message
        self.client.connect(broker_address)
        threading.Thread(target=self.__run, daemon=True).start()
        self.queue = []

    def __run(self):
        self.client.loop_forever()

    # Paho callback that receives messages from the broker
    # Messages are received as bytes, not string literals
    def on_message(self, client, userdata, msg):
        
        # Testing - print payload to terminal
        print("Received message: ", msg.payload)

        # Safely attempt to parse the message string
        # msg is received as bytes, not a string
        try:
            # Convert payload to string, then split and store in list
            parts = str(msg.payload.decode("utf-8")).split(",")
            if len(parts) > 1:
                # Convert list elements to floats
                xv = float(parts[0])
                yv = float(parts[1])
                self.queue.append([msg.topic, [xv,yv]])
        except:
            print("bad message")


        # Testing
        #print("Current queue", self.queue)

        # Testing
        # parts = str(msg.payload.decode("utf-8")).split(",")
        # if len(parts) > 1:
        #     xv = float(parts[0])
        #     yv = float(parts[1])
        #     self.queue.append([msg.topic, [xv,yv]])


    def register_handler(self, topic: str):
        self.client.subscribe(topic)

async def msg_loop():

    mc = MqttCom("localhost")

    # MQTT Topic
    # Row64 location apps send messages under the topic: R64_LOCATION_UPDATE
    #mc.register_handler("example/#")
    mc.register_handler("R64_LOCATION_UPDATE/#")

    #s64 = stream64()
    s64 = stream64("ws://localhost:9002?login=api&v=2")
    s64.set_output(command="UPSERT VERBOSE", db="Examples", table="Security")

    # Row64 Server table columns
    #s64.set_columns(["Incident", "Longitude", "Latitude", "Count"])
    s64.set_columns(["Longitude","Latitude"])

    # RamDB location
    ramdb_path = os.path.join(s64.get_folder(), "Security.ramdb")

    s64.set_types_from_ramdb(ramdb_path)
    #uri = "ws://localhost:9002?login=api"
    uri = "ws://localhost:9002?login=api&v=2"

    async for w in ws.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    for topic,msg in mc.queue:
                        print(" xy: ", msg[0], "," ,msg[1])

                        # Original message - First value and last value are hard-coded for extra columns
                        # Not needed for location updates
                        #msg = s64.gen_msg([0, msg[0], msg[1], 100])
                        msg = s64.gen_msg([msg[0], msg[1]])

                        # Message for latitude and longitude
                        # This adds a new row to the table for every update
                        #msg = s64.gen_msg([msg[0], msg[1]])

                        await w.send(msg);
                        await w.recv()
                        # print((await w.recv()).decode('ascii')) # print debug feedback
                        await asyn.sleep( .05 ) # delay in seconds
                    mc.queue = []
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle
asyn.run(msg_loop())
