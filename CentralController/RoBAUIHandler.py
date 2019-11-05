
from UIUtility import _Getch as getch
from RoBAThreading import LogLoop
from RoBAArena import Arena
import time
import datetime

keyInput = getch()

def handle_key(arena):
    k = keyInput()
    if k == b'Q' or k == b'\x03' or k == b'\x1b' or k == b'\x11':
        raise KeyboardInterrupt

    elif k == b' ':
        arena.start_pause()

    elif k == b'D':

        try:
            print("Who attacks? Red 1-4, Blue 5-8")
            k1 = keyInput()
            k1 = int(k1)
            if not 1 <= k1 <= 7:
                raise ValueError
        except:
            print('expected an integer between 1 and 8')
            return 0
        k1 -= 1

        if k1 < 4:
            robAtt = arena.redTeam.robots[k1]
            teamAtt = arena.redTeam
        elif k1 < 7:
            robAtt = arena.blueTeam.robots[k1-4]
            teamAtt = arena.blueTeam


        try:
            print("Who defends? Red 1-4, Blue 5-8, Nexuses 9-0")
            k2 = keyInput()
            k2 = int(k2)
            if not k2:
                k2 = 10
            if not 1 <= k2 <= 10:
                raise ValueError
        except:
            print('expected an integer between 0 and 9 and not on the same team')
            return 0

        k2 -= 1

        if k2 < 4:
            robDef = arena.redTeam.robots[k2]
        elif k2 < 8:
            robDef = arena.blueTeam.robots[k2-4]
        else:
            robDef = arena.nexuses[k2-8]

        if robAtt.isActive and robDef.isActive and not robAtt.isCooldownHit:

            robDef.eventQ.add_hit(-1)# byWhom=robAtt.ID, damage=robAtt.hitDamage)
            teamAtt.hitQ.add_hit(robDef.eventQ.buff[robDef.eventQ.hitInd-1, 0],
                                robAtt.ID, robAtt.hitDamage)
            print(robAtt.ID, " attacked ", robDef.ID)
        else:
            print("Robot Inactive")

    elif k == b'K':

        try:
            print("Kill who? Red 1-4, Blue 5-8, Nexuses 9-0")
            k1 = keyInput()
            k1 = int(k1)
            if not k1:
                k1 = 10
            if not 1 <= k1 <= 10:
                raise ValueError
        except:
            print('expected an integer between 0 and 9')
            return 0
        k1 -= 1

        if k1 < 4:
            rob = arena.redTeam.robots[k1]
        elif k1 < 8:
            rob = arena.blueTeam.robots[k1-4]
        else:
            rob = arena.nexuses[k1-8]

        if rob.isActive:
            #rob.eventQ.add_hit(-1, 6666, 1000) (Removed - 2 Nov 2019 - Aslamah)
            rob.eventQ.add_hit(1000) # a very large damage to kill (Added - 2 Nov 2019 - Aslamah)

    elif k == b'H':

        try:
            print("Heal who? Red 1-4, Blue 5-8")
            k1 = keyInput()
            k1 = int(k1)
            if not 1 <= k1 <= 8:
                raise ValueError
        except:
            print('expected an integer between 1 and 8')
            return 0
        rob = arena.robots[k1-1]
        if rob.isActive and not rob.isCooldownHeal:
            rob.eventQ.add_heal(-1)

    elif k == b'R':
        print("Sending reset")
        arena.demandReset = 1

    # (Removed - 5 Nov 2019 - Aslamah)
    # elif k == b'S':
    #     print("Forcing Sync")
    #     arena.forceSync = 1
    else:
        print("Unknown command input from USER: ", k)


class TextGUI(LogLoop):
    def __init__(self, arena):
        LogLoop.__init__(self, 'stateLog.txt')
        self.arena = arena
    def prot_loop_startup(self):
        """Summary
        """

        print('Log File Thread #%s started: ' % self.ident  + self.filename)
        try:
            self.fh = open(self.filename, 'w')
        except IOError:
            self.fh = open(self.filename, 'w+')
        self.fh.close()

    def prot_loop_run(self):
        """Summary
        """
        arena = self.arena
        time.sleep(1)
        while not self.fh.closed:
            time.sleep(.1)
        try:
            with open(self.filename, 'a') as self.fh:
                health = [0]*8
                coolHit = [0]*8
                coolHeal = [0]*8

                for enum, rob in enumerate(arena.redTeam.robots):
                    health[enum] = rob.health
                    coolHit[enum] = rob.isCooldownHit
                    coolHeal[enum] = rob.isCooldownHeal
                for enum, rob in enumerate(arena.blueTeam.robots):
                    health[enum+4] = rob.health
                    coolHit[enum+4] = rob.isCooldownHit
                    coolHeal[enum+4] = rob.isCooldownHeal


                output = f"""
                # Game Time: {datetime.datetime.now() - arena.gameStartTime}\n
                ##############################################\n
                # Game State\tAutonomous\tSync\tReset\n
                # {'X' if arena.isGameOn else ''}\t{'X' if arena.autonomousMode else ''}\t{'X' if arena.sync else ''}\t{'X' if arena.demandReset else ''}\r\n
                ##############################################\n
                #     \tHealth\tHit Cooldown\tHeal Cooldown\n
                # Red N:\t{arena.nexuses[0].health}\n
                # Red 1:\t{health[0]}\t{'X' if coolHit[0] else ' '}\t{'X' if coolHeal[0] else ' '}\n
                # Red 2:\t{health[1]}\t{'X' if coolHit[1] else ' '}\t{'X' if coolHeal[1] else ' '}\n
                # Red 3:\t{health[2]}\t{'X' if coolHit[2] else ' '}\t{'X' if coolHeal[2] else ' '}\n
                # Red 4:\t{health[3]}\t{'X' if coolHit[3] else ' '}\t{'X' if coolHeal[3] else ' '}\n
                # ********************************************\n
                # Blue N:\t{arena.nexuses[1].health}\n
                # Blue 1:\t{health[4]}\t{'X' if coolHit[4] else ' '}\t{'X' if coolHeal[4] else ' '}\n
                # Blue 2:\t{health[5]}\t{'X' if coolHit[5] else ' '}\t{'X' if coolHeal[5] else ' '}\n
                # Blue 3:\t{health[6]}\t{'X' if coolHit[6] else ' '}\t{'X' if coolHeal[6] else ' '}\n
                # Blue 4:\t{health[7]}\t{'X' if coolHit[7] else ' '}\t{'X' if coolHeal[7] else ' '}\n
                # ********************************************\n
                # High Tower:\t{arena.towers[0].captureTeam}\t{arena.towers[0].capturePercentage}\n
                # Low Tower:\t{arena.towers[1].captureTeam}\t{arena.towers[1].capturePercentage}\n\n\n"""

                self.fh.write(str(output))
        except PermissionError as e:
            print(e, " trying again")
    def prot_loop_shutdown(self):
        """Summary
        """
        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)



    def write(self, line):
        """Summary

        Args:
            line (TYPE): Description
        """
        raise NameError
