"""Needs to be cleaned up for proper integration to the full system

Attributes:
    arena (TYPE): Description
    count (int): Description
    expectedPlayers (list): Description
    hitQ (TYPE): Description
    missingPlayers (bool): Description
    TCPServer (TYPE): Description
    UDPserver (TYPE): Description
"""

from RoBANetwork import get_host_name_IP
from RoBAArena import Arena
import RoBAThreading
from RoBAUIHandler import handle_key, TextGUI

import shutil


# arena = Arena('friendly2.csv', 1, 2)
arena = Arena('Teaminfo-downloadascsv.csv', 1, 2)
# arena = Arena('networkTest.csv', 1, 2)


count = 0

ipAddress = get_host_name_IP()[1]


try:
    # Create UDP State Update Loop Thread, which sends 4 times a second
    udpUpdateLoop = RoBAThreading.UDPBroadcastLoop(arena, port=5555, delay=0.25)
    tcpServerLoop = RoBAThreading.RoBATCPListener(ipAddress, arena, port=4444)
    #syncServerLoop = RoBAThreading.SyncServer(ipAddress, arena, port=3333, timeout=10) (Removed - 5 Nov 2019 - Aslamah)
    stateLog = TextGUI(arena)
    # udpUpdateLoop.listenOnly = 1
    # syncServerLoop.listenOnly = 1

    udpUpdateLoop.start()
    tcpServerLoop.start()
    #syncServerLoop.start() (Removed - 5 Nov 2019 - Aslamah)
    #syncServerLoop.logL.start() (Removed - 5 Nov 2019 - Aslamah)
    arena.logL.start()
    stateLog.start()


    print("Press game to start game: ")

    while True:
        handle_key(arena)

except KeyboardInterrupt:
    print("Ended by USER")
except Exception as err:
    print("Unexpected Exception in Main: ", err, err.args)
    raise

finally:
    udpUpdateLoop.shutdownFlag.set()
    tcpServerLoop.shutdownFlag.set()
    #syncServerLoop.shutdownFlag.set() # (Removed - 11 Nov 2019 - Aslamah)
    #syncServerLoop.logL.shutdownFlag.set() # (Removed - 11 Nov 2019 - Aslamah)
    arena.logL.shutdownFlag.set()
    stateLog.shutdownFlag.set()

    udpUpdateLoop.join()
    tcpServerLoop.join()
    # syncServerLoop.join() # (Removed - 11 Nov 2019 - Aslamah)
    # syncServerLoop.logL.join() # (Removed - 11 Nov 2019 - Aslamah)
    arena.logL.join()
    stateLog.join()

    try:
        shutil.copy2(arena.logL.filename, arena.debugFolder + arena.logL.filename)
        # shutil.copy2(syncServerLoop.logL.filename, arena.debugFolder + syncServerLoop.logL.filename) # (Removed - 11 Nov 2019 - Aslamah)
    except:
        print("Log copies failed, move manually!")

    arena.dump()

for rob in arena.robots:
    print("Robot ", rob.ID, ", IP: ", rob.IP)
