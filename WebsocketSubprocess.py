import asyncio
from websockets.server import serve
import time
from queue import Queue
import pathlib
import ssl
import json
def Process(tq):

    trq = Queue()

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    pem = pathlib.Path(__file__).with_name("cert.pem")
    key = pathlib.Path(__file__).with_name("key.pem")
    ssl_context.load_cert_chain(pem, keyfile=key)

    async def echo(websocket):
        print("here2")
        #tq.put([False, "*", trq])
        oldtable = {}
        async for message in websocket:
            decodedmessage = message.decode()
            if True:#decodedmessage == "get":
                rtablediff = json.loads(decodedmessage)
                for item in rtablediff:
                    tq.put([True, item, rtablediff[item]])

                tq.put([False, "*", trq])
                table = trq.get()

                stablediff = {}
                #if table == oldtable:
                #    print("nodiff")
                for item in table:
                    if item in oldtable:
                        if table[item] == oldtable[item]:
                            continue
                    if item in rtablediff:
                        if table[item] == rtablediff[item]:
                            continue
                    stablediff[item] = table[item]

                oldtable = table.copy()
                await websocket.send(json.dumps(stablediff))#str(str(pos[0]) + "," + str(pos[1]) + "," + str(pos[2]) + "," + str(rot)))
            else:
                toput = decodedmessage.split(",")
                if int(toput[2]) == 1:
                    if toput[1] == "true":
                        toput[1] = True
                    else:
                        toput[1] = False
                if int(toput[2]) == 3:
                    toput[1] = float(toput[1])
                tq.put([True, toput[0], toput[1]])

    async def main():
        async with serve(echo, "0.0.0.0", 8000):#, ssl=ssl_context):
            await asyncio.Future()  # run forever
    asyncio.run(main())
