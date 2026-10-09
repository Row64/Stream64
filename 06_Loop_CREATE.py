import asyncio as asyn
import websockets as ws
import random
from row64tools.stream64 import stream64
import pandas as pd

# Loop CREATE an entire table per update - demo: http://localhost/dash/examples/fleet
async def msg_loop():
    s64 = stream64()
    s64.set_output(command="CREATE VERBOSE", db="Examples", table="CarSim")
    s64.set_columns(["ID", "Lon", "Lat", "Clr", "Calm", "Speed"]) # replacement CREATE needs all columns
    s64.set_types(["int", "float", "float","int", "float", "float"])
    nbRows = 5000
    ids = list(range(0,nbRows))
    clrs = [0] * nbRows
    calm = speed = [.5] * nbRows
    uri = "ws://localhost:9002?login=api"
    async for w in ws.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    lons = [random.uniform(644,1225) for _ in range(nbRows)]
                    lats = [random.uniform(-793,-333) for _ in range(nbRows)]
                    msg = s64.gen_msg([ids, lons, lats, clrs, calm, speed])
                    await w.send(msg);await w.recv() # high-speed, no check of return message
                    await asyn.sleep( .05 ) # delay (in seconds) to manage update speed
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle
asyn.run(msg_loop())
