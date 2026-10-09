import asyncio as asyn
import websockets as ws
import random
from row64tools.stream64 import stream64
import pandas as pd

# UPSERT random pos to demo: http://localhost/dash/examples/fleet
async def single_msg():
    s64 = stream64()
    s64.set_output(command="UPSERT VERBOSE", db="Examples", table="CarSim" )
    s64.set_columns(["ID", "Lon", "Lat"]) # partial UPSERT of a few columns
    s64.set_types( ["int", "float", "float"] )
    async with ws.connect("ws://localhost:9002?login=api") as w:
        msg = s64.gen_msg([0,random.uniform(644,1225), random.uniform(-793,-333)])
        await w.send(msg)
        print((await w.recv()).decode('ascii')) # print debug feedback
asyn.run(single_msg())