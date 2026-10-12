import asyncio as asyn
import websockets as ws
import os
import random
from row64tools.stream64 import stream64
import pandas as pd

async def single_msg():
    s64 = stream64("ws://localhost:9002?login=api&v=2")
    s64.set_output(command="UPSERT", db="Examples", table="CarSim" )
    s64.set_columns(["ID", "Lon", "Lat"])
    ramdb_path = os.path.join(s64.get_folder(), "include/CarSim.ramdb")
    s64.set_types_from_ramdb(ramdb_path)
    async with ws.connect(s64.url) as w:
        msg = s64.gen_msg([0,random.uniform(644,1225), random.uniform(-793,-333)])
        await w.send(msg)
        print((await w.recv()).decode('ascii')) # print debug feedback
asyn.run(single_msg())
