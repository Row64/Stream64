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

    def on_message(self, client, userdata, msg):
        # print("msg: ", msg.payload)
        # self.queue.append([msg.topic, msg.payload])
        self.queue.append([msg.topic, json.loads(msg.payload)])

    def register_handler(self, topic: str):
        self.client.subscribe(topic)

async def msg_loop():

    mc = MqttCom("localhost")
    mc.register_handler("example/#")

    s64 = stream64("ws://localhost:9002?login=api")
    s64.set_output(command="UPSERT", db="Examples", table="Security")
    s64.set_columns(["Incident", "Longitude", "Latitude","Count"])
    ramdb_path = os.path.join(s64.get_folder(), "include/Security.ramdb")
    s64.set_types_from_ramdb(ramdb_path)
    async for w in ws.connect(s64.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    for topic,msg in mc.queue:
                        # print(" xy: ", msg[0],",",msg[1])
                        msg = s64.gen_msg([0, msg[0], msg[1], 100])
                        await w.send(msg);
                        await w.recv()
                        # print((await w.recv()).decode('ascii')) # print debug feedback
                        await asyn.sleep( .05 ) # delay in seconds
                    mc.queue = []
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle
asyn.run(msg_loop())
