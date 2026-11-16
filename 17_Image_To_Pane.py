import asyncio as asyn
import websockets as ws
from include.stream64 import stream64
import pandas as pd

# http://localhost/dash/stream/system-monitor
async def single_msg():
    s64 = stream64("ws://localhost:9002?login=api")
    imgPath = s64.get_folder() + "/include/Image_Target.jpg"
    async with ws.connect(s64.url) as w:
        msg = s64.img_msg_from_path(imgPath,"stream","system-monitor")
        if msg is not None:
            await w.send(msg);await w.recv()
asyn.run(single_msg())
