"""Summary
"""
import numpy as np
from RoBAParams import RoBAParams
params = RoBAParams()

class HitQueue:

    """Wrapper for an numpy array which gives access and control to a hitqueue

        A HitQueue instance stores any detected weapon hits from a set of robots,
        most often a team of robots. It has a buffer for quick access as well as
        well as long term storage for later analytics.
        TODO: Need to add thresholds for success
        TODO: Perhaps thread saving the full list in the background (every 5 seconds?)


    Attributes:
        buff (ndarray): Holds the mutable part of the hit list.
            This should be large enough to avoid causing delays
        bufferOverlap (int): When the buffer empties, this is how many rows are
            left behind for continuity
        bufferSize (int): length (rows) of the buffer
        columns (int): Number of columns with info
        hitInd (int): Current index in the buffer, acts as static variable
        hitQueue (ndarray): Longterm storage for hitQueue
        thresh (int): allowable time in ms between hits to be called a feasible hit
        threshOffset (int): moves the center of the threshhold
    """

    columns = 4 #timestamp, robotID, damage, defenderID
    bufferSize = 2000#5000
    bufferOverlap = 200#1000

    def __init__(self, thresh=100, threshOffset=15):
        self.buff = np.full([self.bufferSize, self.columns], np.nan)
        self.hitQueue = np.array([], dtype=np.int64).reshape(0, self.columns) # init array as empty ROW of columns elements
        self.hitInd = 0
        self.thresh = thresh
        self.threshOffset = threshOffset #Positive implies buttons tend to be hit later

    def add_hit(self, timestamp, robID, robDam, assignTo=-1):
        """Adds hit to the queue, if the queue ends full, flushes the buffer

        Args:
            timestamp (int): uint32 native, time in milliseconds of hit
            robID (int): robID of robot doing damage
            robDam (TYPE): damage capability of offended robot
        """

        # Save the hit to the buffer
        self.buff[self.hitInd, :] = np.array([timestamp, robID, robDam, assignTo])

        # Resort the buffer
        self.buff[:] = self.buff[self.buff[:, 0].argsort(), :]

        # Increment location in buffer
        self.hitInd += 1

        # If the buffer is full, flush
        if self.hitInd >= self.bufferSize:
            # Start location in buffer at the end of the overlap
            self.hitInd = self.bufferOverlap

            # Flush/save the buffer into hitQueue
            self.hitQueue = np.concatenate([self.hitQueue,
                                            self.buff[0:-self.bufferOverlap, :]],
                                           axis=0)

            # Move the overlapping rows up in the buffer
            self.buff[:self.bufferOverlap, :] = self.buff[-self.bufferOverlap:, :]

            # Set the rest of the buffer to nan, "not a number"
            self.buff[self.bufferOverlap:, :] = np.nan

    def get_buff(self):
        """Outputs the buffer

        Returns:
            ndarray: Outputs filled in buffer array, without any nans
        """
        return self.buff[~np.isnan(self.buff[:, 1]), :]

    def get_full(self):
        """Outputs the full array (longterm and buffer)

        Returns:
            ndarray: Outputs concatenated filled in and buffer, without any nans
        """
        if self.hitQueue.shape[0]:
            fullList = np.concatenate([self.hitQueue,
                                       self.buff[self.bufferOverlap:, :]],
                                      axis=0)
        else:
            fullList = self.buff
        fullList = fullList[~np.isnan(fullList[:, 1]), :]
        return fullList

    def check_thresh(self, timeHit, timeWasHit):
        """Checks if two times are within the window defined by thresh and threshOffset

        Args:
            time1 (uint32): Timestamp of a hit
            time2 (uint32): Timestamp of wasHit

        Returns:
            bool: DescValid hit or not True or False
        """
        return abs((timeWasHit - self.threshOffset) - timeHit) < self.thresh

    def update(self, robList, arena):
        """Updates the hit and event queues of all the robots.

        TODO: Integrate the arena or team lists for update
        Checks to see the nearest hit within the threshold/threshOffset.

        Args:
            robList (Robot Class, List): Takes in a list of robots and updates
                their event queue based on hitQueue
        """

        # For each robot, pull out the robot event queue and update
        for i, rob in enumerate(robList):
            if not rob.isActive:
                continue
            rEQ = rob.eventQ

            # From the robot event buffers, pull all the unassigned "washits"
            # unassigned hits have hitterID = -1
            unassignedWasHitInds = np.where(rEQ.get_buff()[:, 1] == -1)[0]

            # Pull those for easy access
            unassignedWasHit = rEQ.get_buff()[unassignedWasHitInds, :]

            # For all the detected "washits"
            for j, wasHitTime in np.ndenumerate(unassignedWasHit[:, 0]):

                # Get the current indices of all the unused hits
                # The unused hits have defenderID = -1
                unusedInds = np.where(self.buff[:, 3] == -1)[0]
                if np.min(unusedInds.shape) == 0:
                    break

                # Get a copy of the array using only the unused indices
                unused = self.buff[unusedInds, : ]

                # Assuming the list is sorted find the furthest left location
                # where inserting hitTime would not affect the sort then save
                # that and the previous element (the elements closest to hitTime)                #
                inds = np.array([-1, 0]) + np.searchsorted(unused[:, 0], wasHitTime)

                # Clip the unwanted negative and greater than maximum inds
                inds = np.clip(inds, 0, unused.shape[0]-1)

                # From the to nearest inds which is the closest the time
                nearest = np.argmin(np.abs(unused[inds, 0]- wasHitTime))
                if self.check_thresh(unused[inds, 0][nearest], wasHitTime):

                    # Assign a robID (1) and a robDam (2) to the "wasHit"
                    timestamp = unused[inds[nearest], 0]
                    attackerID = unused[inds[nearest], 1]
                    attackerDamage = unused[inds[nearest], 2]

                    rEQ.buff[unassignedWasHitInds[j], 1] =  attackerID #id
                    rEQ.buff[unassignedWasHitInds[j], 2] =  attackerDamage #damage

                    # Assign robot to the defenderID
                    self.buff[unusedInds[inds[nearest]], 3] = robList[i].ID

                    try:
                        if rob.reflectedMulti:
                            for rob in arena.robots:
                                if rob.ID == attackerID:
                                    rob.eventQ.add_hit(timestamp, byWhom=rob.ID, damage=rob.reflectedMulti * attackerDamage )
                                    break
                    except:
                        pass







class RobotEventsQueue:

    """Summary

    Attributes:
        buff (TYPE): Description
        bufferOverlap (int): Description
        bufferSize (int): Description
        columns (int): Description
        healerID (int): Description
        hitInd (int): Description
        hitQueue (TYPE): Description
        reaperID (int): Description
    """
    def __init__(self):
        """Summary
        """
        self.bufferSize = 500 #5000
        self.bufferOverlap = 100 #1000
        self.reaperID = 1111
        self.healerID = 2222
        #self.columns = 3 # timestamp, hitterID, hitterDamage (Removed - 2 Nov 2019 - Aslamah)
        self.columns = 1 # hitterDamage = 1 (Added - 2 Nov 2019 - Aslamah)
        self.buff = np.full([self.bufferSize, self.columns], np.nan)
        # init array as empty ROW of columns elements
        self.hitQueue = np.array([], dtype=np.int64).reshape(0, self.columns)
        self.hitInd = 0

    # (Removed - 2 Nov 2019 - Aslamah)
    # def add_hit(self, timestamp, byWhom=-1, damage=0):
    #     """Summary
    #
    #     Args:
    #         timestamp (TYPE): Description
    #     """
    #     if timestamp == -1:
    #         if self.hitInd:
    #             timestamp = self.buff[self.hitInd-1, 0]
    #         else:
    #             timestamp = 0
    #     self.buff[self.hitInd, :] = np.array([timestamp, byWhom, damage])
    #     self.buff[:] = self.buff[self.buff[:, 0].argsort(), :]
    #     self.hitInd += 1
    #     if self.hitInd >= self.bufferSize:
    #         self.hitInd = self.bufferOverlap
    #         self.hitQueue = np.concatenate([self.hitQueue, self.buff[0:-self.bufferOverlap, :]],
    #                                        axis=0)
    #         self.buff[:self.bufferOverlap, :] = self.buff[-self.bufferOverlap:, :]
    #         self.buff[self.bufferOverlap:, :] = np.nan

    def add_hit(self, damage=1):
        """Summary

        Args:
            timestamp (TYPE): Description
        """
        self.buff[self.hitInd, :] = np.array([damage])
        self.hitInd += 1
        if self.hitInd >= self.bufferSize:
            self.hitInd = self.bufferOverlap
            self.hitQueue = np.concatenate([self.hitQueue, self.buff[0:-self.bufferOverlap, :]],
                                           axis=0)
            self.buff[:self.bufferOverlap, :] = self.buff[-self.bufferOverlap:, :]
            self.buff[self.bufferOverlap:, :] = np.nan

    def add_reaper(self):

        if self.hitInd:
            timestamp = self.buff[self.hitInd-1, 0]
        else:
            timestamp = 0

        self.buff[self.hitInd, :] = np.array([timestamp, self.reaperID, 0])
        self.hitInd += 1
        if self.hitInd >= self.bufferSize:
            self.hitInd = self.bufferOverlap
            self.hitQueue = np.concatenate([self.hitQueue, self.buff[0:-self.bufferOverlap, :]],
                                           axis=0)
            self.buff[:self.bufferOverlap, :] = self.buff[-self.bufferOverlap:, :]
            self.buff[self.bufferOverlap:, :] = np.nan

    def add_heal(self, timestamp):
        # if ((datetime.now()-healingRobot.lastHealTime)>=timedelta(seconds=self.params.healDelay)) and (healingRobot.isActive):
                    # healingRobot.heal(self.params.healAmount)

        if timestamp == -1:
            if self.hitInd:
                timestamp = self.buff[self.hitInd-1, 0]
            else:
                timestamp = 0

        damage = self.get_damage()

        healingAmount = min(params.healAmount, damage)
        self.buff[self.hitInd, :] = np.array([timestamp, self.healerID, -healingAmount])
        self.buff[:] = self.buff[self.buff[:, 0].argsort(), :]
        self.hitInd += 1
        if self.hitInd >= self.bufferSize:
            self.hitInd = self.bufferOverlap
            self.hitQueue = np.concatenate([self.hitQueue, self.buff[0:-self.bufferOverlap, :]],
                                           axis=0)
            self.buff[:self.bufferOverlap, :] = self.buff[-self.bufferOverlap:, :]
            self.buff[self.bufferOverlap:, :] = np.nan

    def get_damage(self):
        """Summary

        Returns:
            TYPE: Description
        """
        lastDeathInd = np.where(self.buff[:, 1] == self.reaperID)[0]
        # print ("last death ind ", lastDeathInd)
        if not lastDeathInd.any():
            lastDeathInd = np.where(self.hitQueue[:, 1] == self.reaperID)[0]
            if not lastDeathInd.any():
                # print("Damage no death")
                # print(self.hitQueue[:, 2])
                # print(self.buff[:, 2])
                if self.hitQueue.shape[1]:
                    damage = np.nansum(self.hitQueue[:-self.bufferOverlap, 2]) + np.nansum(self.buff[:, 2])
                else:
                    damage = np.nansum(self.buff[:, 2])
            else:
                damage = (np.nansum(self.hitQueue[max(lastDeathInd):-self.bufferOverlap, 2]) +
                          np.nansum(self.buff[:, 2]))
        else:
            damage = np.nansum(self.buff[max(lastDeathInd):, 2])
        return damage

    def get_buff(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.buff[~np.isnan(self.buff[:, 1]), :]

    def get_full(self):
        """Summary

        Returns:
            TYPE: Description
        """
        fullList = np.concatenate([self.hitQueue, self.buff[0:-self.bufferOverlap, :]], axis=0)
        fullList = fullList[~np.isnan(fullList[:, 1]), :]
        return fullList
