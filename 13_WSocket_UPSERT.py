import asyncio as asyn
import websockets as ws
import random
from include.stream64 import stream64
import threading
import json
import os
from websockets.asyncio.server import serve
import websockets



#----------------------- port 9005: remote devices send messages into here ----------------------

class Signal_IN():
    
    def __init__(self, in_uri):
        self.uri = in_uri
        threading.Thread(target=self.init_server, daemon=True).start()
        self.queue = []

    async def handler(self, websocket):
        async for msg in websocket:
            self.queue.append(json.loads(msg))

    async def server_loop(self):
        # print("got to server loop")
        print(self.uri)
        async with serve(self.handler, "", 9005) as server:
            await server.serve_forever()

    def init_server(self):
        try:
            asyn.run(self.server_loop())
        except Exception as e: 
            print("--------- thread error ---------")
            print(str(e))


#-------------------- port 9002: message is packaged and sent to row64server -------------------
async def msg_loop():
    
    ins = Signal_IN("ws://localhost:9005?login=api")
    s64 = stream64("ws://localhost:9002?login=api") # signal OUT to server
    s64.set_output(command="UPSERT", db="Examples", table="Security")
    s64.set_columns(["Incident", "Longitude", "Latitude", "Count"])
    ramdb_path = os.path.join(s64.get_folder(), "include/Security.ramdb")
    s64.set_types_from_ramdb(ramdb_path)
    async for w in ws.connect(s64.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    for pos in ins.queue:
                        msg = s64.gen_msg([0, pos[0], pos[1], 100])
                        await w.send(msg)
                        await w.recv()
                    ins.queue = []
                except Exception as e:print("inner error: " + str(e))
        except Exception as e:
            print("outer error: " + str(e))
            await ws.close()
            continue # auto recovery & re-connect cycle

asyn.run(msg_loop())