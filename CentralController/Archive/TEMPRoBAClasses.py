"""List of temporary functions and classes that should eventually be
added to the overall class structure
"""
import numpy as np
import struct
from RoBAQueues import *

class TempRobot:

    """Summary

    Attributes:
        EventQ (TYPE): Description
        ID (TYPE): Description
        IP (TYPE): Description
    """

    def __init__(self, number, IP):
        """Summary

        Args:
            number (TYPE): Description
            IP (TYPE): Description
        """
        self.ID = number
        self.IP = IP
        self.EventQ = RobotEventsQueue()

# def rob_who_IP(IP, robList):
#     """Summary

#     Args:
#         IP (TYPE): Description
#         robList (TYPE): Description

#     Returns:
#         TYPE: Description
#     """
#     for rob in robList:
#         if IP == rob.IP:
#             return rob

#     return -1


class state:

    """Summary

    Attributes:
        auto (int): Description
        cooldown (int): Description
        gameSt (int): Description
        nexus (list): Description
        reset (int): Description
        robots (list): Description
        sync (int): Description
        towers (list): Description
    """

    towers = [60, -30]
    robots = [10, 20, 30, 40, 50, 60, 70, 80]
    nexus = [500, 128]
    sync = 0
    cooldown = 0
    auto = 0
    reset = 0
    gameSt = 1
    def get_message(self):
        """Summary

        Returns:
            TYPE: Description
        """
        infoByte = (np.uint8(self.sync<<4) + \
                   np.uint8(self.cooldown<<3) + \
                   np.uint8(self.auto<<2) +  \
                   np.uint8(self.reset<<1) +  \
                   np.uint8(self.gameSt<<0))

        # print(self.sync<<4)
        # print(self.cooldown<<3)
        # print(self.auto<<2)
        # print(self.reset<<1)
        # print(self.gameSt<<0)


        towerByte = (np.uint8((self.towers[0]+100)/14) + (np.uint8((self.towers[1]+100)/14)<<4) )
        # print(infoByte)
        # print(towerByte)
        # print(type(np.uint8(towerByte)))
        outputString = struct.pack('BHHBBBBBBBBB',
                                   np.uint8(infoByte),
                                   np.uint16(self.nexus[0]),
                                   np.uint16(self.nexus[1]),
                                   np.uint8(self.robots[0]),
                                   np.uint8(self.robots[1]),
                                   np.uint8(self.robots[2]),
                                   np.uint8(self.robots[3]),
                                   np.uint8(self.robots[4]),
                                   np.uint8(self.robots[5]),
                                   np.uint8(self.robots[6]),
                                   np.uint8(self.robots[7]),
                                   np.uint8(towerByte))
        # print(outputString)
        return outputString

def handle_event(rob, robMsgTuple, hitQueue):
    """Summary

    Args:
        rob (TYPE): Description
        robMsgTuple (TYPE): Description
        hitQueue (TYPE): Description
    """
    ev = get_event(robMsgTuple)
    if   ev == "hit":
        print("Hit: ", robMsgTuple[1], " from robot: ", rob.ID)
        hitQueue.add_hit(robMsgTuple[1], rob.ID,rob.ID * 2)
    elif ev == "gotHit":
        print("WasHit: ", robMsgTuple[1], "from robot: ", rob.ID )
        rob.eventQ.add_hit(robMsgTuple[1])


def get_event(robMsgTuple):
    """Summary

    Args:
        robMsgTuple (TYPE): Description

    Returns:
        TYPE: Description
    """
    return ["null","gotHit","hit","heal"][robMsgTuple[0]]


def handle_event_clean(arena, robMsgTuple, ip):
    """Summary

    Args:
        rob (TYPE): Description
        robMsgTuple (TYPE): Description
        hitQueue (TYPE): Description
    """
    rob, teamInd = arena.rob_who_IP(ip)

    ev = get_event(robMsgTuple)

    if   ev == "hit":
        print("Hit: ", robMsgTuple[1], " from robot: ", rob.ID)
        arena.teams[teamInd].hitQueue.add_hit(robMsgTuple[1], rob.ID, rob.ID * 2)
    elif ev == "gotHit":
        print("WasHit: ", robMsgTuple[1], "from robot: ", rob.ID)
        rob.eventQ.add_hit(robMsgTuple[1])

