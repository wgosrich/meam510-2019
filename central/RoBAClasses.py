"""Summary

Attributes:
    params (TYPE): Description
"""

from datetime import datetime, timedelta
import numpy as np
from RoBAParams import RoBAParams
# from RoBAQueues import HitQueue, RobotEventsQueue
# not including RoBAQueues for now

"""NOTES:
Allowing the arena and main system to do all checks for timers,
robot class only keeps the last time an ability was used
not whether it is ready again """

"""CLASS: ARENA
    Contains game rules and data structures"""

params = RoBAParams()

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class RobotNotActiveError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    pass
class RobotListEmptyError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    pass


class Robot:
    """Class that keeps all the robot state information and operations on said robots

    Attributes:
        eventQ (TYPE): Description
        fullHealth (TYPE): Description
        health (TYPE): Description
        hitDamage (TYPE): Description
        hitDelay (TYPE): Description
        ID (TYPE): Description
        IP (str): Description
        isActive (bool): Description
        lastDeathTime (TYPE): Description
        lastHealTime (TYPE): Description
        lastHitTime (TYPE): Description
        name (TYPE): Description
        weight (TYPE): Description
    """

    def __init__(self, name, ID, number, startHealth, weight, desHitDelay):
        """Summary

        Args:
            name (TYPE): Description
            ID (TYPE): Description
            startHealth (TYPE): Description
            weight (TYPE): Description
            desHitDelay (TYPE): Description
        """
        # Added name field for live stream and stats display
        self.name = name
        self.ID = ID

        self.IP = ''
        self.eventQ = RobotEventsQueue()

        print("Robot Init  ID: ", end=' ')
        print(self.ID)

        # Keeps track of the robots starting health and what is max or respawn health
        # Note that this is in the init and not outside of it so that health
        # can be added as a design characteristic for the students (if desired)
        self.fullHealth = startHealth

        # Resets all of the robots state to clean slate


        # Timing variables
        self.lastHitTime = datetime(2000, 1, 1)
        self.lastHealTime = datetime(2000, 1, 1)
        self.lastDeathTime = datetime(2000, 1, 1)
        # Robot base characteristics
        self.health = self.fullHealth
        self.isActive = False
        self.reset()

        # Const Stats
        self.weight = weight
        self.hitDelay = float(desHitDelay)
        self.healDelay = params.healDelay
        self.hitDamage = self.calc_DPS()*desHitDelay

        # Perform a check to limit max damage and adjust hitDelay accordingly.
        # i.e. if calculated damage > max damage lower hitDelay
        if self.hitDamage > params.maxDamage: #Max allowable damage per hit:
            self.hitDamage = params.maxDamage
            self.hitDelay = float(params.maxDamage/self.calc_DPS())

        self.isCooldownHit = False
        self.isCooldownHeal = False
        self.healFail = False
        self.color = ""
        self.number = number

    def reset(self):
        """Summary
        """
        # Timing variables
        self.lastHitTime = datetime(2000, 1, 1)
        self.lastHealTime = datetime(2000, 1, 1)
        self.lastDeathTime = datetime(2000, 1, 1)
        # Robot base characteristics
        self.health = self.fullHealth
        self.isActive = False

    def resume_from_pause(self, timePassed):
        """Summary

        Args:
            timePassed (TYPE): Description
        # """

        print("Robot %d Last Death Time: " % self.ID, self.lastDeathTime)
        # print("lastHealTime",self.lastHealTime)
        # print("lastHitTime",self.lastHitTime)

        self.lastDeathTime += timePassed
        self.lastHealTime += timePassed
        self.lastHitTime += timePassed

        print("Robot %d Last Death Time: " % self.ID, self.lastDeathTime)
        # print("lastHealTime",self.lastHealTime)
        # print("lastHitTime",self.lastHitTime)

    def pause(self):
        """Summary
        """
        self.isActive = False

    def calc_DPS(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return params.robot_dps(self.weight) # Current robot DPS formula

    # def take_damage(self, damage):
    #     """Summary

    #     Args:
    #         damage (TYPE): Description
    #     """
    #     if self.isActive:
    #         self.health = max(self.health-damage,0)
    #         if self.health == 0:
    #             print(self.name,"Died")
    #             self.lastDeathTime = datetime.now()
    #             self.isActive = False

    def update_health(self):
        damage = self.eventQ.get_damage()
        if self.isActive:
            self.health = max(self.fullHealth - damage, 0)
            if self.health == 0:
                print("(" + self.color + str(self.number) + ") " + self.name.decode(), ": Died Gruesomely")
                self.eventQ.add_reaper()
                self.lastDeathTime = datetime.now()
                self.isActive = False

    def hit(self):
        """Summary
        """
        #TODO FIXME DEBUG We need to re introduce the cool down
        self.lastHitTime = datetime.now()

    def heal(self, healAmount):
        """Summary

        Args:
            healAmount (TYPE): Description
        """
        self.health = min( self.health + healAmount, self.fullHealth)
        self.lastHealTime = datetime.now()
