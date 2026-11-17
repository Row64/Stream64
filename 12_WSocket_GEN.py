import asyncio as asyn
import websockets as ws
import random
from include.motion import motion


async def publish_loop():
    uri = "ws://localhost:9005"
    count = 0
    mgen = motion(-97.29451, 39.908065, 9.4 )
    async for w in ws.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=None):
        async def waitRecv():await w.recv()
        try:
            while True:
                try:
                    # msg = "hello" + str(count)
                    msg = mgen.get_pos()
                    await w.send(msg)
                    try:
                        await asyn.wait_for( waitRecv(), timeout=0.1 )
                    except TimeoutError:
                        pass
                    await asyn.sleep( .03 )
                    count += 1
                except Exception as e:
                    print("inner error: " + str(e))
                    break                
        except Exception as e:
            print("outer error: " + str(e))
            await w.close()
            continue
asyn.run(publish_loop())