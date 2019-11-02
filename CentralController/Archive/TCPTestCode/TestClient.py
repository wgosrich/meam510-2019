#!/usr/bin/env python

import asyncio
import websockets

async def questionSend():
    async with websockets.connect('ws://10.0.0.2:81') as websocket:

        name = input("What's your name? ")
        await websocket.send(name)
        print("> {}".format(name))

        greeting = await websocket.recv()
        print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(questionSend())