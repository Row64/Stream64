import asyncio as asyn
import websockets as ws
from row64tools.stream64 import stream64
import pandas as pd

# Use CREATE VERBOSE to get debug / diagnostic feedback from the server
async def single_msg():
    s64 = stream64("ws://localhost:9002?login=api&v=2")
    # Example typo, correct with db="Temp"
    s64.set_output(command="CREATE", db="Temp_TYPO", table="Test_Table" )
    s64.set_columns(["ID", "Lon", "Lat"])
    s64.set_types( ["int", "float", "float"] )
    async with ws.connect(s64.url) as w:
        msg = s64.gen_msg([71,-118.496475,34.024212])
        await w.send(msg)
        print((await w.recv()).decode('ascii')) # print debug feedback
asyn.run(single_msg())
