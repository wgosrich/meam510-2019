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
        healAmount (int): Description (Removed - 2 Nov 2019 - Aslamah)
        healDelay (int): Description (Removed - 2 Nov 2019 - Aslamah)
        healingEnabled (bool): Description (Removed - 2 Nov 2019 - Aslamah)
        maxDamage (int): Description
        nexusMaxHealth (int): Description
        nexusReflectedMulti (float): Description (Removed - 2 Nov 2019 - Aslamah)
        robotMaxHealth (int): Description (Removed - 2 Nov 2019 - Aslamah)
        towerDPS (int): Description
        towersEnabled (bool): Description

    """

    nexusMaxHealth = 48 # [HP]
    #robotMaxHealth = 99 # [HP] (Removed - 2 Nov 2019 - Aslamah)
    robotMinStartHealth = 2 # [HP] (Added - 2 Nov 2019 - Aslamah)
    #healAmount = 20 # [HP] (Removed - 2 Nov 2019 - Aslamah)
    #healDelay = 5 # [secs] (Removed - 2 Nov 2019 - Aslamah)
    towerDPS = 0.5  # [DPS] (Added - 2 Nov 2019 - Aslamah)
    #reflectedNexusMulti = .5 # [] (Removed - 2 Nov 2019 - Aslamah)
    maxDamage = 25 # Max allowable damage per hit
    #healFreq = HIGH (Removed - 2 Nov 2019 - Aslamah)
    #healingEnabled = True # Enable the healing lights and healing capability (Removed - 2 Nov 2019 - Aslamah)
    towersEnabled = True # Enable tower capture
    autonomousStartEnabled = True # Enable autonomous mode at the start of the game
    autonomousStartTime = 60
    minDPS = 1
    towerHitRate = 1 #Hz
    ipSubnet = '192.168.1.' # (Added - 12 Nov 2019 - Aslamah)
    ipOffset = 100 # (Added - 12 Nov 2019 - Aslamah)
    broadcastType = '1S' # AS-all subnets, 1S-1.subnet
    ipGUI = "192.168.1.3"


    def respawn_time_function(self, arena):
        """Summary

        Returns:
            TYPE: Description
        """
        return np.floor((datetime.now()-arena.gameStartTime).seconds/60) * 10 + 20
        # return 15 # (Added - 4 Nov 2019 - Walker)
    def robot_dps(self, weight):
        return max((12 - 2 * weight), self.minDPS)

    # (Added - 2 Nov 2019 - Aslamah)
    def robot_start_health(self, weight):
        """Summary: minimum weight is 500g or 0.5kg, which will have maximum health of 20

        Returns:
            int : starting health based on weight
        """
        # weight should be in kg
        return max(20/(weight + 0.5), self.robotMinStartHealth)
