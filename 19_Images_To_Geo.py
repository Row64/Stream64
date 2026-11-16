import asyncio as asyn
import websockets as ws
from include.stream64 import stream64
import os

# http://localhost/dash/stream/interstate
async def msg_loop():
    s64 = stream64("ws://localhost:9002?login=api")
    imgBuf = []
    for i in range(0,11):
        ipath =s64.get_folder() + "/include/Interstate/Interstate_"+str(i).zfill(2)+".png"
        if ( os.path.exists( ipath ) ):
            with open(ipath, 'rb') as f:imgBuf.append(f.read())
        else:return
    count = 0
    async for w in ws.connect(s64.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            pass
            while True:
                try:
                    imsg = s64.geo_img_msg(imgBuf[count],"stream","interstate","Geo2D2","Interstate_10.png")
                    if imsg is not None:
                        await w.send(imsg);await w.recv()
                        await asyn.sleep(.5)
                    count += 1
                    if count > 10: count = 0
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle
asyn.run(msg_loop())
