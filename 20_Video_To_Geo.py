import asyncio as asyn
import websockets as ws
from PIL import Image
from moviepy import *
from include.stream64 import stream64
import os
import io
import time

# http://localhost/dash/stream/tradeshow

def video_bytes(in_vfile, in_time, in_format) : # in_format: 'jpeg', 'jpg' or 'png'
    if in_format == "jpg":in_format = "jpeg"
    framearr = in_vfile.get_frame( in_time )
    framedata = Image.fromarray( framearr.astype('uint8') ).convert('RGB')
    framebytes = io.BytesIO()
    framedata.save( framebytes, format = in_format )
    return framebytes.getvalue()
    
async def msg_loop():
    s64 = stream64("ws://localhost:9002?login=api")
    vFile = VideoFileClip( s64.get_folder() + "/include/Architecture_Motion.mp4" )
    async for w in ws.connect(s64.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            start = time.time()
            while True:
                try:
                    t = time.time()-start
                    if t > vFile.duration:t=0;start=time.time()
                    vbytes = video_bytes(vFile, t,'jpg')
                    imsg = s64.geo_img_msg(vbytes,"stream","tradeshow","Geo2D2","camera_01.jpg")
                    if imsg is not None:
                        await w.send(imsg);await w.recv()
                        await asyn.sleep(.05)
                except:break
        except:await ws.close();continue # auto recovery & re-connect cycle
asyn.run(msg_loop())
