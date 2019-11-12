"""Summary

"""

from datetime import datetime, timedelta
import time
import numpy as np
import math
import struct
from threading import Lock as TLock
from RoBAParams import RoBAParams
from RoBAQueues import HitQueue, RobotEventsQueue
from RoBAClasses import Robot, MetaTeam, Tower, Nexus, RobotNotActiveError, RobotListEmptyError
from RoBAThreading import LogLoop
import pickle
import os
"""NOTES:
Allowing the arena and main system to do all checks for timers,
robot class only keeps the last time an ability was used
not whether it is ready again """

"""CLASS: ARENA
    Contains game rules and data structures"""

class Arena:

    """Game object, holds all the state information and update methods
    FIXME and TODO abound.

    Attributes:
        allTeams (TYPE): A list of all the teams from the CSV
        autonomousMode (bool): Is Autonomous Mode Active
        gameStartTime (TYPE): When the game started
        isGameOn (bool): Is the game currently active or paused or stopped
        isGameStarted (bool): Is the game started or are we in the initialization
        params (RoBAParams Instance): Configuration variables
        pausedAtTime (float): Time at Pause

        blueTeam (MetaTeam Instance): Away team Metateam, blue team
        redTeam (TYPE): Home team Metateam, red team

        nexuses (Nexus Instance): list of the active nexuses
        robots (TYPE): list of all robots (first half red, second half blue)
        teams (TYPE): list of playing teams,i.e. [redteam, blueteam]
        towers (TYPE): list of two active towers
    """


    def __init__(self, teamFilename, redTeam, blueTeam):
        """Initializing with csv file to read for team information, and which of
        those teams are playing

        Args:
            teamFilename (TYPE): Description
            redTeam (int): Team number 1-12
            blueTeam (int): Team number 1-12
        """


        self.params = RoBAParams()

        self.allTeams = self.load_team_csv(teamFilename)
        self.redTeam = self.allTeams[redTeam-1]
        self.blueTeam = self.allTeams[blueTeam-1]

        # Give the active teams hitqs
        self.redTeam.hitQ = HitQueue()
        self.blueTeam.hitQ = HitQueue()

        # Give the active teams hitqs
        self.redTeam.set_color('Red')
        self.blueTeam.set_color('Blue')

        self.teams = [self.redTeam, self.blueTeam]

        # Use this shallow copy of robots for syncing
        self.robots = self.redTeam.robots + self.blueTeam.robots
        self.nexuses = [self.redTeam.nexus, self.blueTeam.nexus]

        self.redTeam.nexus.ID = 80
        self.blueTeam.nexus.ID = 81

        self.redTeam.nexus.IP = self.params.ipSubnet + '80' # (Added - 12 Nov 2019 - Aslamah)
        self.blueTeam.nexus.IP = self.params.ipSubnet + '81' # (Added - 12 Nov 2019 - Aslamah)

        self.towers = [Tower(self.params.towerDPS, ID=98), Tower(self.params.towerDPS, ID=99)]

        self.autonomousMode = self.params.autonomousStartEnabled
        self.isGameOn = False
        self.isGameStarted = False

        self.lock = TLock()

        self.lastHeartbeat = time.time()
        self.hbDelay = 1
        #self.sync = 0 (Removed - 5 Nov 2019 - Aslamah)
        self.sync = 1 # (Adde - 11 Nov 2019 - Aslamah)
        #self.forceSync = 0 (Removed - 5 Nov 2019 - Aslamah)
        self.demandReset = 0

        self.gameStartTime = datetime.now()

        self.debugFolder = "./debuglogs/" + time.strftime("%Y-%m-%d %H.%M.%S")+ "mteams_%d_%d" % (self.redTeam.number, self.blueTeam.number) +"/"
        os.mkdir(self.debugFolder)
        self.reset()
        self.logL = LogLoop('arenaLog.txt')

    def load_team_csv(self, teamFilename):
        """Summary

        Args:
            teamFilename (TYPE): Description

        Returns:
            TYPE: Description
        """
        teams = []
        data = np.genfromtxt(teamFilename, delimiter=',',
                             names=True, dtype=None)
        #### Column Headers
        # MetaTeamNumber: 1-numTeams
        # MetaTeamName
        # RobotNumber: 1-4 (per team)
        # RobotID: Unique identifier
        # RobotName
        # Weight
        # DesCooldown

        numTeams = np.amax(data['MetaTeamNumber'])

        #Instantiate team list
        for i in range(numTeams):
            teams.append(MetaTeam(i+1))

        for rowIndex, metaTeamNum in enumerate(data['MetaTeamNumber']):
            teams[metaTeamNum-1].name = data['MetaTeamName'][rowIndex]
            teams[metaTeamNum-1].add_robot(
                Robot(data['RobotName'][rowIndex],
                      data['RobotID'][rowIndex],
                      data['RobotNumber'][rowIndex],
                      #self.params.robotMaxHealth, (Removed - 2 Nov 2019 - Aslamah)
                      data['Weight'][rowIndex])
                      #data['DesCooldown'][rowIndex]) (Removed - 2 Nov 2019 - Aslamah)
                      )
        return teams

    def heartbeat(self):
        """Summary
        """

        if (self.lastHeartbeat + self.hbDelay) < time.time() and self.isGameStarted:

            if self.isGameOn:
                print(datetime.now(), '...')
            else:
                print('*** paused')
            self.lastHeartbeat = time.time()


    def reset(self):
        """Summary
        """
        self.pausedAtTime = datetime(2000, 1, 1)
        self.redTeam.reset()
        self.blueTeam.reset()

    def go(self):
        """Summary
        """
        for rob in self.robots + self.nexuses + self.towers:
            rob.isActive = True

    def pause(self):
        """Summary
        """
        for rob in self.robots + self.nexuses + self.towers:
            rob.isActive = False

    def start_pause(self):

        if not self.isGameOn: # if the game was off start the timer. This will reset if you send the start command once the game ended.
            if not self.isGameStarted: # if it is the first time around set the startTime
                self.isGameStarted = True
                self.gameStartTime = datetime.now()
                self.reset() #resets health and timers

                print("LET THE GAME BEGIN!!!")
                print(self.gameStartTime)
                self.go()
            else:
                pauseDelta = (datetime.now() - self.pausedAtTime)# how long it was just paused for
                self.gameStartTime += pauseDelta

                for rob in (self.robots + self.nexuses + self.towers):
                    rob.resume_from_pause(pauseDelta)
                    self.go()

            self.isGameOn = True
            print("Game on")

        else:   # pause
            self.isGameOn = 0
            self.pausedAtTime = datetime.now() # record when it was paused

            # if someone is dead we need to add the time of the pause to their revive time.
            print("Pause")
            print(self.pausedAtTime)
            self.pause()

    #RESPAWN TIME FUNCTION
    def get_respawn_time(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.params.respawn_time_function(self)


    def isGameOver(self):
        """Summary

        Returns:
            TYPE: Description
        """
        check = (not (self.redTeam.nexus.health and self.blueTeam.nexus.health))
        if check:
            for rob in self.robots + self.nexuses + self.towers:
                rob.isActive = False
        return check


    def update(self):

        self.heartbeat()

        if self.isGameOn:

            currTime = datetime.now()
            respawnTime = self.get_respawn_time()

            if currTime - self.gameStartTime > timedelta(seconds=self.params.autonomousStartTime):
                self.autonomousMode = 0

            # (Removed - 11 Nov 2019 - Aslamah)
            # self.redTeam.hitQ.update(self.blueTeam.robots + [self.blueTeam.nexus], self)
            # self.blueTeam.hitQ.update(self.redTeam.robots + [self.redTeam.nexus], self)

            self.update_healths()

            # (Removed - 11 Nov 2019 - Aslamah)
            # for rob in self.robots:

                # if rob.health == 0:
                #     if (currTime - rob.lastDeathTime) >= timedelta(seconds=respawnTime):
                #         rob.health = self.params.robotMaxHealth
                #         rob.isActive = True
                # else:
                #     rob.isActive = True
                #
                # if (currTime - rob.lastHitTime) >= timedelta(seconds=rob.hitDelay):
                #     rob.isCooldownHit = False

                # (Removed - 11 Nov 2019 - Aslamah)
                # if (currTime - rob.lastHealTime) >= timedelta(seconds=rob.healDelay):
                #     rob.isCooldownHeal = False



            if(self.isGameOver()):
                print("GAME OVER!!!")
                self.isGameStarted = False
                self.isGameOn = False


    def update_healths(self):
        for rob in self.robots+self.nexuses:
            rob.update_health() #update based on new architecture (Added - 2 Nov 2019 - Aslamah)


    def rob_who_IP(self, IP):
        """Given IP address, find which robot is talking

        Args:
            IP (str): IP address

        Returns:
            Robot Instance: the robot you were asking for
        """
        # print("IP: {}".format(IP))
        for ind, team in enumerate(self.teams):
            for rob in team.robots:
                if IP == rob.IP:
                    return rob, ind
            if IP == team.nexus.IP:
                return team.nexus, ind
        for tower in self.towers:
            if IP == tower.IP:
                return tower, 2

        for rob in self.robots + self.nexuses + self.towers:
            print(rob.IP)
        raise KeyError("KeyError, IP Not Found: " + str(IP))

    def get_sync_state(self):
        """Get the sync state of the arena.

        Iterate over all the robots and return True if all are synced and false
        if any are false.

        Returns:
            bool: Is everyone synced
        """
        return all([rob.synced for rob in self.robots])

    def get_message(self):
        """Summary

        Returns:
            TYPE: Description

        Args:
            rob (TYPE): Description
        """
        #FIXME Debug code need these to come from the robots WHAT IS RESET

                    # (Added - 5 Nov 2019 - Aslamah)
                    #(np.uint8(self.sync << 3) +  (Removed - 5 Nov 2019 - Aslamah)
        infoByte =  (np.uint8(1) + \
                    np.uint8(self.autonomousMode << 2) +  \
                    np.uint8(self.demandReset << 1) +  \
                    np.uint8(self.isGameOn << 0))
        cooldownByte = 0
        # (Removed - 11 Nov 2019 - Aslamah)
        # for ind, rob in enumerate(self.robots):
        #     cooldownByte += (rob.isCooldownHit<<ind)



        towerByte = (np.uint8((self.towers[0].capturePercentage + 100)/14) +
                     (np.uint8((self.towers[1].capturePercentage + 100)/14)<<4))

        # (Added - 4 Nov 2019 - Walker)
        #create integer list of robot starting health
        startHealth = [0]*8
        for enum, rob in enumerate(self.redTeam.robots):
            startHealth[enum] = rob.fullHealth
        for enum, rob in enumerate(self.blueTeam.robots):
            startHealth[enum+4] = rob.fullHealth

        # (Added - 4 Nov 2019 - Walker)
        #create (currently empty) location list for broadcast
        location = [0]*8

        #create integer list of robots health
        health = [0]*8
        for enum, rob in enumerate(self.redTeam.robots):
            health[enum] = rob.health
        for enum, rob in enumerate(self.blueTeam.robots):
            health[enum+4] = rob.health
        """ (Removed - 4 Nov 2019 - Walker)
        outputString = struct.pack('=BBHH12B',
                                   np.uint8(128 + infoByte),
                                   np.uint8(cooldownByte),
                                   np.uint16(self.nexuses[0].health),
                                   np.uint16(self.nexuses[1].health),
                                   np.uint8(health[0]),
                                   np.uint8(health[1]),
                                   np.uint8(health[2]),
                                   np.uint8(health[3]),
                                   np.uint8(health[4]),
                                   np.uint8(health[5]),
                                   np.uint8(health[6]),
                                   np.uint8(health[7]),
                                   np.uint8(towerByte),
                                   np.uint8(self.redTeam.number),
                                   np.uint8(self.blueTeam.number),
                                   np.uint8(128 + 2))
        """
        #(Added - 4 Nov 2019 - Walker)
        outputString = struct.pack('=BHH20B',
            np.uint8(128 + infoByte),
            np.uint16(self.nexuses[0].health),
            np.uint16(self.nexuses[1].health),
            np.uint8(startHealth[0]),
            np.uint8(startHealth[1]),
            np.uint8(startHealth[2]),
            np.uint8(startHealth[3]),
            np.uint8(startHealth[4]),
            np.uint8(startHealth[5]),
            np.uint8(startHealth[6]),
            np.uint8(startHealth[7]),
            np.uint8(location[0]),
            np.uint8(location[1]),
            np.uint8(location[2]),
            np.uint8(location[3]),
            np.uint8(location[4]),
            np.uint8(location[5]),
            np.uint8(location[6]),
            np.uint8(location[7]),
            np.uint8(towerByte),
            np.uint8(self.redTeam.number),
            np.uint8(self.blueTeam.number),
            np.uint8(128 + 2)) # why does Diego terminate with 10000010?? seems like it should be 128+1

        return outputString


    # (Added - 11 Nov 2019 - Aslamah)
    def receive_tophat_message(self, data, ip):
        print(ip)
        print(data)
        rob, ind = self.rob_who_IP(ip)

        message = []
        for i in range(8):
            message.append(data >> i & 0b1)

        rob.isActive = False if (message[0]) else True
        rob.health = int(message[1] | message[2] << 1 | message[3] << 2 | message[4] << 3 | message[5] << 4)
        rob.xLocation = int(message[8] | message[9] << 1 | message[10] << 2 | message[11] << 3)
        rob.yLocation = int(message[12] | message[13] << 1 | message[14] << 2 | message[15] << 3)


    def get_fake_message(self):
        """Summary

        Returns:
            TYPE: Description
        """
        # For Gui Test
        measTime = time.time()
        infoByte = int(((int(1) << int(4))+ (int(0) << int(3)) + (int((measTime//30)%2)<<int(2)) +   ( int(0)<<int(1)) + int(1)))

        cooldownByte = 0

        towerByte = (np.uint8((measTime % 200)/14) +
                     (np.uint8(((measTime/2-50)%200)/14)<<4))

        outputString = struct.pack('=BBHH12B',
                                   np.uint8(infoByte),
                                   np.uint8(cooldownByte),
                                   np.uint16(measTime%1000),
                                   np.uint16((2*measTime)%1000),
                                   np.uint8((2*measTime)%100),
                                   np.uint8((3*measTime)%100),
                                   np.uint8((4*measTime)%100),
                                   np.uint8((5*measTime)%100),
                                   np.uint8((5*measTime)%100),
                                   np.uint8((6*measTime)%100),
                                   np.uint8((7*measTime)%100),
                                   np.uint8((8*measTime)%100),
                                   np.uint8(towerByte),
                                   np.uint8(255),
                                   np.uint8(255),
                                   np.uint8(128+ ((measTime//5%2)*(measTime//10%4)) ))

        return outputString

    def GUI_update(self):
        receivedState = struct.unpack('=BBHH9B', self.get_fake_message())
        for ind, rob in enumerate(self.robots):
            rob.health = receivedState[ind + 3]
        for ind, nex in enumerate(self.nexuses):
            nex.health = receivedState[ind + 1]

    def dump(self):
        """Summary

        Args:
            robList (TYPE): Description
            hitQueue (TYPE): Description
        """
        print("Saving the arena state to file...")
        filename = self.debugFolder + "mteams_%d_%d.pickle" % (self.redTeam.number, self.blueTeam.number)
        del(self.lock)
        del(self.logL)
        with open(filename, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
            print("file saved successfully")


        print("Red Team")
        print(self.redTeam.hitQ.get_full())
        print("Blue Team")
        print(self.blueTeam.hitQ.get_full())
        print("______________________")
        # (Removed - 11 Nov 2019 - Aslamah)
        # for rob in (self.redTeam.robots+[self.redTeam.nexus]+
        #             self.blueTeam.robots+[self.blueTeam.nexus]):
        for rob in ([self.redTeam.nexus]+[self.blueTeam.nexus]):
            print(rob.ID, " : ")
            print(rob.eventQ.get_full())
            print("Damage: ", rob.eventQ.get_damage())

    def get_event(self, event):
        """Summary

        Args:
            robMsgTuple (TYPE): Description

        Returns:
            TYPE: Description
        """
        return ["null", "gotHit", "hit", "heal"][event]

    # (Removed - 2 Nov 2019 - Aslamah)
    # def handle_event(self, robMsgTuple, ip):
    #     """Summary
    #
    #     Args:
    #         rob (TYPE): Description
    #         robMsgTuple (TYPE): Description
    #         hitQueue (TYPE): Description
    #     """
    #     ev = self.get_event(robMsgTuple[0]&0b11)
    #
    #     healFreq = (robMsgTuple[0]>>2)&0b11
    #     # towersIsCaptured = [(robMsgTuple[0]>>2)&0b11, (robMsgTuple[0]>>2)&0b11]
    #     timestamp = robMsgTuple[1]
    #     try:
    #         rob, teamInd = self.rob_who_IP(ip)
    #     except ValueError:
    #         print("Event Detected from non playing robot")
    #         raise ValueError("Non-Playing Robot Detected")
    #
    #     if not rob.isActive:
    #         self.logL.write("***********Robot/Tower %d is inactive \n" % rob.ID)
    #         raise RobotNotActiveError
    #
    #     if teamInd == 2:# Tower message
    #
    #         rob.captureState = 0
    #         rob.capturePercentage = (robMsgTuple[1] & 0b11111111) - 127
    #         teamInd = (robMsgTuple[0]>>4) & 0b1
    #         rob.captureTeam = None
    #         # timestamp = robMsgTuple[1]  - (robMsgTuple[1] & 0b11111111)
    #         if ev == "hit":
    #             rob.captureState = 1
    #
    #             rob.captureTeam = 'BLUE' if teamInd else 'RED'
    #             self.teams[teamInd].nexus.eventQ.add_hit(-1, byWhom=rob.ID,
    #                                                  damage=rob.hitDamage)
    #             self.logL.write("\n    Hit: %d from tower: %d against "%(self.teams[teamInd].nexus.eventQ.buff[self.teams[teamInd].nexus.eventQ.hitInd-1, 0], rob.ID)+self.teams[teamInd].color +  " Nexus")
    #         return 1
    #
    #
    #     if ev == "hit":
    #         if rob.isCooldownHit:
    #             self.logL.write("\t \t Robot %d is on cooldown hit" % rob.ID)
    #             raise RobotNotActiveError
    #         self.logL.write("\n    Hit: %d from robot: %d"%(timestamp, rob.ID))
    #         self.teams[teamInd].hitQ.add_hit(timestamp, rob.ID, rob.hitDamage)
    #
    #     elif ev == "gotHit":
    #         self.logL.write("\nWas Hit: %d from robot: %d"%(timestamp, rob.ID))
    #         rob.eventQ.add_hit(timestamp)
    #
    #     elif ev == "heal":
    #         if rob.isCooldownHeal:
    #             self.logL.write("\t \t Robot %d is on cooldown heal" % rob.ID)
    #             raise RobotNotActiveError
    #
    #         if self.params.healFreq == healFreq and not rob.healFail:
    #             self.logL.write("\n   Heal: %d from robot: %d with heal freq: %d"% (timestamp,rob.ID, healFreq))
    #             rob.eventQ.add_heal(timestamp)
    #         else:
    #             rob.healFail = True
    #     return 1


    # (Added - 2 Nov 2019 - Aslamah)
    def handle_event(self, robMsgTuple, ip):
        """Summary: receive events from Towers and nexuses
        """

        try:
            rob, teamInd = self.rob_who_IP(ip)
        except ValueError:
            print("Event Detected from non playing robot")
            raise ValueError("Non-Playing Robot Detected")

        if not rob.isActive:
            self.logL.write("***********Robot/Tower %d is inactive \n" % rob.ID)
            raise RobotNotActiveError

        if teamInd == 2:# Tower message

            rob.captureState = 1
            teamInd = (robMsgTuple[0]>>1) & 0b1
            rob.captureTeam = 'BLUE' if teamInd else 'RED'
            # redteam is 0, blueteam is 1, so whoever captured should damage the other
            self.teams[abs(teamInd-1)].nexus.eventQ.add_hit(rob.hitDamage) #(To check - 2 Nov 2019 - Aslamah)
            self.logL.write("\n    Hit: from " + rob.CaptureTeam + "Tower against other Nexus")

            return 1

        #event handling for nexus
        rob.eventQ.add_hit()

        return 1


    def handle_event_checking(self, robMsgTuple, ip):
        """Summary

        Args:
            rob (TYPE): Description
            robMsgTuple (TYPE): Description
            hitQueue (TYPE): Description
        """
        event = robMsgTuple[0]&0b11
        healFreq = (robMsgTuple[0]>>2)&0b11
        # towersIsCaptured = [(robMsgTuple[0]>>2)&0b11, (robMsgTuple[0]>>2)&0b11]
        timestamp = robMsgTuple[1]

        ev = self.get_event(event)

        if ev == "hit":

            self.logL.write("Hit: %d from robot: "%timestamp + ip)

        elif ev == "gotHit":
            self.logL.write("Was Hit: %d from robot:"%timestamp + ip)

        elif ev == "heal":
            self.logL.write("Heal: %d from robot: " %timestamp + ip +'with heal freq: %d'% healFreq)
        return 1


if __name__ == "__main__":
    testArena = Arena('teamsTest.csv', 1, 2)
