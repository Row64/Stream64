import asyncio as asyn
import websockets as ws
import random
from include.stream64 import stream64
from include.flights import flights

# CREATE flight pos: http://localhost/dash/examples/flights
async def msg_loop():
    s64 = stream64("ws://localhost:9002?login=api")
    s64.set_output(command="CREATE", db="Stream", table="Flights" )
    s64.set_columns(["flight id","origin","dest","dept","dur","lon","lat","night"]) 
    s64.set_types( ["int","text","text","float","float","bigfloat","bigfloat","int"] )
    
    s642 = stream64("ws://localhost:9002?login=api")
    s642.set_output(command="CREATE", db="Stream", table="FlightTime" )
    s642.set_columns(["time"])
    s642.set_types( ["text"] )

    fgen = flights()
    hour = 0
    
    async for w in ws.connect(s64.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    flightData = fgen.gen_flight_data(hour)
                    msg = s64.gen_msg(flightData)
                    await w.send(msg)
                    await w.recv() # high-speed, no check of return message
                    # print((await w.recv()).decode('ascii')) # print debug feedback
                    await asyn.sleep( .03 ) # delay (in seconds) to manage update speed
                    
                    ftime = fgen.get_flight_time(hour)
                    msg2 = s642.gen_msg([ftime])
                    await w.send(msg2)
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
