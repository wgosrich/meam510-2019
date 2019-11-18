import socket
import time
import datetime
import struct
import numpy as np
from RoBAQueues import *
from RoBANetwork import *
from TEMPRoBAClasses import *

expectedPlayers = [1,2]
missingPlayers = True

arenaState = state()
hitQ = HitQueue()

count = 0
myHostName, myIPAddress = get_host_name_IP()
UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
UDPserver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDPserver.settimeout(1)
UDPserver.bind((myIPAddress, 3333))

TCPSyncServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPSyncServer.bind((myIPAddress, 4444))
TCPSyncServer.listen(20)
TCPSyncServer.settimeout(.5)


# TCPserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# TCPserver.bind((myIPAddress, 5555))
# TCPserver.listen(20)
# TCPserver.settimeout(.5)

while missingPlayers:
    missingPlayers = expectedPlayers.copy()
    robList = []
    numConnected = 0
    count = count + 1
    UDPserver.sendto(UDP_sync_msg( count ), ('<broadcast>', 3333))
    print(count, " message sent!")
    timeout = time.time() + 1

    while time.time() <= timeout:
        try:
            conn, addr = TCPSyncServer.accept()
        except:
            continue
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if not data:
                continue
            countCheck = data[0]
            robNumber = data[1]

            if (count==countCheck):
                try:
                    missingPlayers.remove(robNumber)
                    print("reply from ",robNumber)
                    numConnected = numConnected+1
                    # print(numConnected)
                    robList.append(TempRobot(robNumber,addr[0]))
                    if not missingPlayers:
                        break
                except ValueError:
                    print( "INTRUDER ALERT: ", robNumber, " does not belong")

TCPSyncServer.close()
TCPSyncServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPSyncServer.bind((myIPAddress, 4444))
TCPSyncServer.listen(20)
TCPSyncServer.settimeout(.5)

print("WE DID IT!!!")
print ("Current date and time: " , datetime.datetime.now())
arenaState.sync = 1
TCP_update_all(robList,arenaState)

print("HERE")

while True:
    try:
        try:
            conn, addr = TCPSyncServer.accept()
        except:
            continue
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if not data: continue
            # print(data)
            # print(data[0])
            # print(data[1])
            # print(data[2]<<(1*8))
            # print(data[3]<<(2*8))
            # print(data[4]<<(3*8))
            robotMessageTuple = (int(data[0]),
                        (np.uint32(data[1])+
                        np.uint32(data[2]<<(1*8))+
                        np.uint32(data[3]<<(2*8))+
                        np.uint32(data[4]<<(3*8)) ))
            # robotMessageTuple = struct.unpack_from('BL',data[0:8])
            ## WOULD UPDATE THE STATE VECTOR HERE
            print(robotMessageTuple)
        handle_event(    rob_who_IP(addr[0],robList),    robotMessageTuple ,hitQ       )
        hitQ.update(robList)
        TCP_update_all(robList,arenaState)
    except KeyboardInterrupt:
        dump(robList,hitQ)
        break



# connRobs = UDP_sync(numRob)


