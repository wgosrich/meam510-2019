"""Summary
"""
# Init file that contains all the options/parameters for the final game
# For now a place holder since I don't know how to actually run this

from datetime import datetime, timedelta
import numpy as np

HIGH = 1
LOW = 0
class RoBAParams:

    """Summary

    Attributes:
        autonomousStartEnabled (bool): Description
        healAmount (int): Description
        healDelay (int): Description
        healingEnabled (bool): Description
        maxDamage (int): Description
        nexusMaxHealth (int): Description
        nexusReflectedMulti (float): Description
        robotMaxHealth (int): Description
        towerDPS (int): Description
        towersEnabled (bool): Description

    """

    nexusMaxHealth = 900 # [HP]
    robotMaxHealth = 99 # [HP]
    healAmount = 20 # [HP]
    healDelay = 5 # [secs]
    towerDPS = 4  # [DPS]
    reflectedNexusMulti = .5 # []
    maxDamage = 25 # Max allowable damage per hit
    healFreq = HIGH
    healingEnabled = True # Enable the healing lights and healing capability
    towersEnabled = True # Enable tower capture
    autonomousStartEnabled = True # Enable autonomous mode at the start of the game
    autonomousStartTime = 30
    minDPS = 1
    towerHitRate = 1 #Hz


    def respawn_time_function(self, arena):
        """Summary

        Returns:
            TYPE: Description
        """
        return np.floor((datetime.now()-arena.gameStartTime).seconds/60) * 10 + 20
    def robot_dps(self, weight):
        return max((12 - 2 * weight), self.minDPS)