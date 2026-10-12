import asyncio as asyn
import websockets as ws
from row64tools.stream64 import stream64
import pandas as pd

# Pandas CREATE a new .ramdb file only
async def single_msg():
    s64 = stream64("ws://localhost:9002?login=api")
    df = pd.DataFrame( {"txt": ["a","b", "hello world"],"num": [1, 2, 3]} )
    async with ws.connect(s64.url) as w:
        msg = s64.msg_from_pandas(df, db="Temp", table="Pandas_Table1")
        await w.send(msg);await w.recv()
asyn.run(single_msg())
