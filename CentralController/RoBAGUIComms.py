"""Summary

Attributes:
    params (TYPE): Description
"""

from datetime import datetime, timedelta
import socket
import numpy as np
import threading
from RoBAClasses import Robot, Tower, Nexus, MetaTeam
from RoBAParams import RoBAParams
from RoBAQueues import HitQueue, RobotEventsQueue
"""NOTES:
Allowing the arena and main system to do all checks for timers,
robot class only keeps the last time an ability was used
not whether it is ready again """

"""CLASS: ARENA
    Contains game rules and data structures"""
params = RoBAParams()


def get_state_TCP(arena, port=6666):
    """

    Args:
        arena (TYPE): Description
        port (int, optional): Description
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(b'r')
        data = s.recv(1024)
        if not data:
            return False
        arena.parse_data(data)
    return True

