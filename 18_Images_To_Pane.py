import asyncio as asyn
import websockets as ws
from include.stream64 import stream64
from include.jetson import jetson
import os

# http://localhost/dash/stream/system-monitor
async def msg_loop():
    
    s64 = stream64("ws://localhost:9002?login=api&v=2")
    s64.set_output(command="CREATE", db="Stream", table="Jetson")
    s64.set_columns(["Time","GPU","Power","Temp_GPU","Temp_CPU","Temp_Soc0","Temp_Soc1"]) # replacement CREATE needs all columns
    s64.set_types(["datetime","float","float","float","float","float","float"])
    
    s64.debug_to_file = True

    s642 = stream64("ws://localhost:9002?login=api&v=2")
    
    mdata = [[],[],[],[],[],[],[]]
    dtime = s64.get_date64("10/15/2026 14:35","%m/%d/%Y %H:%M")
    perc = 0
    jet = jetson()
    flip = 0

    imgBuf = []
    for i in range(1,91):
        ipath =s642.get_folder() + "/include/Jetson/JN_0100"+str(i).zfill(2)+".jpg"
        if ( os.path.exists( ipath ) ) :
            with open(ipath, 'rb') as f:imgBuf.append(f.read())
        else:return

    count = 1
    icount = 0
    async for w in ws.connect(s64.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    imsg = s642.img_msg(imgBuf[icount],"stream","system-monitor","Image_Target.jpg")
                    if imsg is not None:
                        await w.send(imsg)
                        await w.recv()
                        await asyn.sleep( .05)

                    mdata = jet.get_data(mdata, dtime, perc, flip)
                    msg = s64.gen_msg(mdata)
                    await w.send(msg)
                    await w.recv() # high-speed, no check of return message
                    await asyn.sleep( .05 ) # delay (in seconds) to manage update speed
                    
                    dtime = dtime + 1000000000 # add 1 second in nanoseconds
                    if perc > 1: perc = 0;flip = not flip
                    else: perc += .01
                    icount += 1
                    count += 1
                    if icount > 89: icount = 0
                    
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle
asyn.run(msg_loop())
