import asyncio as asyn
import websockets as ws
import row64tools
import os
import struct
import random

from row64tools.stream64 import stream64
# from row64tools.bytestream import bytestream as bStream
# from bytestream import bytestream as bStream
from kafka import KafkaConsumer
import json


async def msg_loop():
    
    consumer = KafkaConsumer('example_loc', bootstrap_servers=['localhost:9092'])
    
    s64 = stream64()
    s64.set_output(command="UPSERT VERBOSE", db="Examples", table="Security")
    s64.set_columns(["Incident", "Longitude", "Latitude","Count"])
    ramdb_path = os.path.join(s64.get_folder(), "Security.ramdb")
    s64.set_types_from_ramdb(ramdb_path)
    uri = "ws://localhost:9002?login=api"
    
    async for w in ws.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    for msg in consumer:
                        # print(" xy: ", msg[0],",",msg[1])
                        jmsg = json.loads(msg.value)
                        msg = s64.gen_msg([0, jmsg[0], jmsg[1], 100])
                        await w.send(msg);
                        await w.recv()
                        # print((await w.recv()).decode('ascii')) # print debug feedback
                        await asyn.sleep( .05 ) # delay in seconds
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle

    # async for ws in websockets.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=None, compression=None):
    #     try:
    #         for msg in consumer:
    #             jmsg = json.loads(msg.value)
    #             bmsg = makeBStream(jmsg)
    #             serverMsg = b"BS="+bmsg
    #             await ws.send(serverMsg)
    #             payload = await ws.recv()
    #     except websockets.exceptions.WebSocketException as err:
    #         print(" [ERROR] ******************", err)
    #         await ws.close()
    #         continue

if __name__ == "__main__":
    asyn.run(msg_loop())
