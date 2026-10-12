import asyncio as asyn
import websockets as ws
import random
from row64tools.stream64 import stream64

from include.robot import robot

import pandas as pd

# http://localhost/dash/examples/robot-factory

async def msg_loop():
    
    s641 = stream64("ws://localhost:9002?login=api")
    s641.set_output(command="CREATE", db="Stream", table="RobotMotion" )
    s641.set_columns(["route","perc",  "lon","lat"]) 
    s641.set_types( ["text",  "float",  "bigfloat","bigfloat"] )

    s642 = stream64("ws://localhost:9002?login=api")
    s642.set_output(command="CREATE", db="Stream", table="RobotTime" )
    s642.set_columns(["time"])
    s642.set_types( ["text"] )
    
    s643 = stream64("ws://localhost:9002?login=api")
    s643.set_output(command="CREATE", db="Stream", table="Shelves" )
    s643.set_columns(["shelve","status","clr"])
    s643.set_types( ["text",  "float", "int"] )


    hour = 5.5 # 5:30 AM

    bot = robot()
    # sdata = bot.get_data(hour)
    # print(sdata)
    # return
    reset = True # reset on init
    # uri = "ws://localhost:9002?login=api&v=2"     # 0 = returns bstream, 1 = 0 or 1 boolean return, 2 = verbose description
    async for w in ws.connect(s641.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    
                    # ----------------------- Robot Data -----------------------
                    sdata = bot.get_data(hour)
                    shelfdat = bot.shelf_proximity(sdata, reset)

                    # print((await w.recv()).decode('ascii')) # print debug feedback

                    msg = s641.gen_msg(sdata)
                    await w.send(msg)
                    await w.recv() # high-speed, no check of return message
                    
                    msg2 = s643.gen_msg(shelfdat)
                    await w.send(msg2)
                    await w.recv() 

                    ftime = s642.get_24h_timestr(hour)
                    msg2 = s642.gen_msg([ftime])
                    await w.send(msg2)
                    await w.recv()
                    await asyn.sleep( .04 ) # delay (in seconds) to manage update speed
                    
                    hour+=.0003
                    # if hour >= 24:hour = 0
                    if hour >= 5.67:hour = 5.5;reset = True
                    else:reset = False
                except Exception as e:
                    print( "Inner exception: ",e)
                    break
        except Exception as e:
            print( "outer exception",e)
            await ws.close();
            continue # auto recovery & re-connect cycle
           


asyn.run(msg_loop())
