"""
RoBA Network helper tools and functions
"""

import socket
import time
import datetime
import struct
import numpy as np
from RoBAQueues import *
from RoBAParams import RoBAParams

params = RoBAParams()

################################################################################
def get_host_name_IP():
    """Returns the host name and IP Address

    Returns the host name and IP Address of the host and prints the results
    to terminal for convenience.

    Returns:
        STR (0): Host_name, if it fails returns 0
        STR (0): IP Address, if it fails returns 0
    """
    try:
        # hostName = socket.gethostname()
        # hostIP = socket.gethostbyname(hostName)
        hostName = "central"
        hostIP = params.ipSubnet + '2'
        print("Hostname :  ", hostName)
        print("IP : ", hostIP)
        return hostName, hostIP

    except:
        print("Unable to get Hostname and IP")
        return 0, 0

################################################################################
# def TCP_update_all(arena,fakeState):
#     """Gets arena state and sends an update to all robots in game.

#     TODO: this function would eventually take an arena and not a
#     robot list since the arena will include the teams within it.

#     Args:
#         robList (Robot Class, List): List of robots that should be sent updates
#         arena (Arena Class): Class containing all the game information

#     Returns:
#         INT: Number of successful messages sent
#     """

#     successes = 0
#     for rob in arena.robots:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((rob.IP, 5555))
#             s.sendall(fakeState.get_message())
#             successes += 1
#     return successes


# ################################################################################
# def UDP_sync_msg(num):
#     """Produces single byte sync counter

#     Args:
#         num (int): Counter value

#     Returns:
#         bytes: bytes list for easy sending
#     """
#     return struct.pack('B', num%256)

# ################################################################################

# def UDP_broadcast_sync(arena, port=3333):
#     """Sync all the robots in the arena.

#     Attempts to sync all the robots it expects to be in the arena. This list is
#     initialized elsewhere.
#     TODO: Gives errors if it takes too long.
#     TODO: Allows for partial syncing: game shouldn't die if one robot is gone.
#     TODO: ARDUINO SIDE: UDP SHOULD TURN ROBOT TO SYNCING MODE
#     TODO: Make ARDUINO SIDE TCP PORTS separate ports

#     Args:
#         arena (arena Class Instance): Contains all the game information
#         port (int, optional): port to broadcast to

#     Returns:
#         bool: success equals true, false equals false

#     """

#     # Get the current host and IP address
#     ipAddress = get_host_name_IP()[1]

#     # Create UDPserver for syncing
#     udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#     udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#     udpServer.settimeout(1)
#     udpServer.bind((ipAddress, port))

#     tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcpServer.bind((ipAddress, port))
#     tcpServer.listen(20)
#     tcpServer.settimeout(.5)

#     # Get list of expected robots IDs
#     robots = arena.robots
#     expectedIDs = []
#     for rob in robots:
#         expectedIDs.append(rob.ID)
#     print(expectedIDs)

#     # Initialize missingPlayers to bootstrap While loop
#     missingIDs = True

#     # Initialize sync byte
#     syncCounter = 0

#     while missingIDs:

#         # Make a list of all the missing players
#         missingIDs = expectedIDs.copy()


#         # Broadcast the sync byte to the port
#         udpServer.sendto(UDP_sync_msg(syncCounter), ('<broadcast>', port))

#         print(syncCounter, " message sent!")
#         timeout = time.time() + 1

#         while time.time() <= timeout:
#             try:
#                 conn, addr = tcpServer.accept()
#             except:
#                 continue
#             with conn:
#                 print('Connected by', addr)
#                 data = conn.recv(1024)
#                 if not data:
#                     continue
#                 countCheck = data[0]
#                 robNumber = data[1]

#                 if syncCounter == countCheck:
#                     print("reply from ", robNumber)
#                     try:
#                         ind = expectedIDs.index(robNumber)
#                         missingIDs.remove(robNumber)
#                         robots[ind].IP = addr[0]

#                         if not missingIDs:
#                             break
#                     except ValueError:
#                         print("INTRUDER ALERT: ", robNumber, " does not belong")

#     udpServer.close()
#     tcpServer.close()
#     return True


# def TCP_hit_receiver_server(arena, port=4444):

#     ipAddress = get_host_name_IP()[1]
#     tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcpServer.bind((ipAddress, 4444))
#     tcpServer.listen(20)
#     tcpServer.settimeout(.5)

#     try:
#         while True:
#             try:
#                 conn, addr = tcpServer.accept()
#             except IOError:
#                 continue
#             except KeyboardInterrupt:
#                 raise
#             except Exception as err:
#                 print("Unexpected Exception: ", err, err.args)
#                 continue

#             with conn:
#                 print('Connected by', addr[0])
#                 data = conn.recv(1024)
#                 if not data:
#                     continue

#                 robotMessageTuple = (int(data[0]),
#                                      (np.uint32(data[1]) +
#                                       np.uint32(data[2]<<(1*8)) +
#                                       np.uint32(data[3]<<(2*8)) +
#                                       np.uint32(data[4]<<(3*8))))

#                 print(robotMessageTuple)

#             TEMP.handle_event_clean(arena, robotMessageTuple, addr[0])
#     except:
#         pass
