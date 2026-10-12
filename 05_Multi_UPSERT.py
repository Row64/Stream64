import asyncio as asyn
import websockets as ws
import random
from row64tools.stream64 import stream64
import pandas as pd

# UPSERT multi-row lists, with demo: http://localhost/dash/examples/fleet
async def single_msg():
    s64 = stream64("ws://localhost:9002?login=api&v=2")
    s64.set_output(command="UPSERT", db="Examples", table="CarSim" )
    s64.set_columns(["ID", "Lon", "Lat"]) # partial UPSERT of a few columns
    s64.set_types( ["int", "float", "float"] )
    ids = list(range(0,10))
    lons = [random.uniform(644,1225) for _ in range(10)]
    lats = [random.uniform(-793,-333) for _ in range(10)]
    async with ws.connect(s64.url) as w:
        msg = s64.gen_msg([ids,lons,lats])
        await w.send(msg)
        print((await w.recv()).decode('ascii')) # print debug feedback
asyn.run(single_msg())
