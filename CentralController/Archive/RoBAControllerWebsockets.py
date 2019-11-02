#!/usr/bin/env python
#
# Keeps track of robot health for the league of legend final mechatronics project.
# Robots start with a certain amount of health
# When they die a death timer starts so they can come back in after it has expired.
# The death timer increases over the course of the match in minute increments
# They can only do a certain amount of damage with each hit then they have to wait a cooldown period
# Similarly, they can heal but can only heal so much then have a cool down period
# When the match finishes (a nexus is dead) all the robots die so they know to stop
# To start the match the system must receive a command starting with 'S'
#
#
# It is ugly.  Using functions is probably a good idea. I think asynchronous functions will be a good thing to use, but I think it would take a while and time is short. It gradually grew from something small to a big monstrous mess.  I would like to think I will clean it up eventually but realistically if you are reading this it is because someone asked you to fix it.  I am sorry.  It may be better to just start over, but you can try to salvage it.
#
#
#    Paul Stegall Dec. 3 2017
#
# runs a websocket server based on:
# https://github.com/Pithikos/python-websocket-server/blob/master/README.md
# this keeps track of robot health for LOL Bots
#
# https://wiki.python.org/moin/UdpCommunication -- Done
#
#
#TO RUN:
#  Update your hit damage and cooldown time, lines 54 to 77 , then
# 1: Open a terminal
# 2: Type: cd Desktop
# 3: Type: sudo python3 LoLController.py


from datetime import datetime, timedelta
import socket
from DataStructureTesting import Arena
#import asyncio
from websocket_server import WebsocketServer





# from playsound import playsound
deathSound = "C:\Windows\media\Ring01.wav"
gameOverSound = "C:\Windows\media\Ring02.wav"
hostIP='192.168.2.100'; # this is the IP of your server (computer running this code).  Probably want a static IP.

UDP_IP1 = "10.0.0.3"; # ip addresses to send UDP packets to.  I port forward these to something on a different router that can then broadcast because I can't broadcast on the routers I have.
UDP_IP2 = "10.0.0.4";
UDP_PORT = 2808;  # port to send the UDP packets to.
 
udp = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP

game  = Arena('teamsTest.csv',1,2)

# times to keep track of these will be overwritten once the game starts
UDPLastSentTime = datetime.now();


def new_client(client, server):
    server.send_message(client,game.get_health_message())
    print('sent: ' + game.get_health_message() + '\n')
    
def client_left(client, server):
    print('We Lost one\n')
    
    
def on_message(client, server, message):
    print('received: ' + message + '\n')
    game.update(message)
    healthList = game.get_health_message()
    if game.isGameOn:
        server.send_message_to_all(healthList) # broadcast the healthList to anyone who will listen
        print('sent websocket: ' + healthList)
    
    udp.sendto(healthList.encode() , (UDP_IP1, UDP_PORT))
    udp.sendto(healthList.encode() , (UDP_IP2, UDP_PORT))
    print('sent udp: ' + healthList + '\n')
    

        


server = WebsocketServer(81, host=hostIP)  #this is the port and IP address you want the server to use.

server.set_fn_new_client(new_client) #when a new client joins in calls the function new_client
server.set_fn_message_received(on_message)#when a message is received it calls on_message
server.set_fn_client_left(client_left) #when a client leaves it calls client_left


server.run_forever()





