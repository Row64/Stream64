import asyncio as asyn
import websockets as ws
import random
from include.stream64 import stream64
from include.robot import robot

# http://localhost/dash/stream/robot-factory
async def msg_loop():
    
    s641 = stream64("ws://localhost:9002?login=api")
    s641.set_output(command="CREATE", db="Stream", table="RobotMotion" )
    s641.set_columns(["route","perc",  "lon","lat"]) 
    s641.set_types( ["text",  "float",  "bigfloat","bigfloat"] )

    s642 = stream64("ws://localhost:9002?login=api")
    s642.set_output(command="CREATE", db="Stream", table="RobotLog" )
    s642.set_columns(["log","time"])
    s642.set_types( ["text","text"] )

    s643 = stream64("ws://localhost:9002?login=api")
    s643.set_output(command="CREATE", db="Stream", table="Shelves" )
    s643.set_columns(["shelve","status","clr"])
    s643.set_types( ["text",  "float", "int"] )
    
    rlog = [[],[]];lastlog="";hour = 5.5 # 5:30 AM
    bot = robot()
    reset = True # reset on init
    async for w in ws.connect(s641.url, ping_interval=None, ping_timeout=None, close_timeout=None):
        try:
            while True:
                try:
                    sdata = bot.get_data(hour)
                    shelfdat = bot.shelf_proximity(sdata, reset, hour, rlog)

                    msg = s641.gen_msg(sdata)
                    await w.send(msg);await w.recv()
                    
                    msg2 = s643.gen_msg(shelfdat)
                    await w.send(msg2);await w.recv()
                    
                    if len(rlog[0]) > 0:
                        if rlog[0][-1] is not lastlog:
                            msg3 = s642.gen_msg(rlog)
                            await w.send(msg3);await w.recv()
                            lastlog = rlog[0][-1]
                    await asyn.sleep( .04 )
                    hour+=.0003
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
