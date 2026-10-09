import asyncio as asyn
import websockets as ws
import random
from row64tools.stream64 import stream64
import row64tools.stream64 as st64

import pandas as pd

# CREATE flight pos: http://localhost/dash/examples/flights
async def msg_loop():
    s64 = stream64()
    s64.set_output(command="CREATE", db="Examples", table="Flights" )
    s64.set_columns(["flight id","origin","dest","dept","dur","lon","lat","night"]) 
    s64.set_types( ["int","text","text","float","float","bigfloat","bigfloat","int"] )

    s642 = stream64()
    s642.set_output(command="CREATE", db="Examples", table="FlightTime" )
    s642.set_columns(["time"])
    s642.set_types( ["text"] )

    hour = 0
    uri = "ws://localhost:9002?login=api"
    async for w in ws.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    flights = s64.gen_flight_data(hour)
                    msg = s64.gen_msg(flights)
                    await w.send(msg);
                    await w.recv() # high-speed, no check of return message
                    # print((await w.recv()).decode('ascii')) # print debug feedback
                    await asyn.sleep( .03 ) # delay (in seconds) to manage update speed
                    
                    ftime = s64.get_flight_time(hour)
                    msg2 = s642.gen_msg([ftime])
                    await w.send(msg2);
                    await w.recv()
                    hour+=.01
                    if hour >= 24:hour = 0

                except Exception as e:
                    print( "Inner exception: ",e)
                    break
        except Exception as e:
            print( "outer exception",e)
            await ws.close();
            continue # auto recovery & re-connect cycle

asyn.run(msg_loop())
