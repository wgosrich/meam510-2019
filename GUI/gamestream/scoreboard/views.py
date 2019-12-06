from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import numpy as np

from .models import *
import gamestream.urls
from .central import Params

import random
import socket

params = Params()

def home(request):
    return render(request, "home.html")

def update(request):
    arena = Arena.objects.all()

    try:
        incomingData, addr = gamestream.urls.udpReceiver.sock.recvfrom(1024) # buffer size is 1024 bytes
        print ("received message:", incomingData)

        arena.update(status = 1 & (incomingData[0] >> 0))
        arena.update(autoMode = 1 & (incomingData[0] >> 2))
        arena.update(redMetaTeamNumber = int(incomingData[22]))
        arena.update(blueMetaTeamNumber = int(incomingData[23]))
        arena.update(redNexusHealth = (incomingData[1] | incomingData[2] << 8))
        arena.update(blueNexusHealth = (incomingData[3] | (incomingData[4] << 8)))
        arena.update(towerStatus = 1 & (incomingData[21] >> 0))

        if arena[0].redMetaTeamNumber > 7:
            arena.update(redMetaTeamNumber = random.uniform(1,7))
        if arena[0].blueMetaTeamNumber > 7:
            arena.update(blueMetaTeamNumber = random.uniform(1,7))

        redMetaTeam = MetaTeam.objects.filter(number=arena[0].redMetaTeamNumber)
        redRobots = Robot.objects.filter(metaTeamNumber=arena[0].redMetaTeamNumber)
        blueMetaTeam = MetaTeam.objects.filter(number=arena[0].blueMetaTeamNumber)
        blueRobots = Robot.objects.filter(metaTeamNumber=arena[0].blueMetaTeamNumber)

        for i in range(4):
            redRobot = Robot.objects.filter(metaTeamNumber=arena[0].redMetaTeamNumber, number=(i+1))
            redRobot.update(health=incomingData[5+i])
            blueRobot = Robot.objects.filter(metaTeamNumber=arena[0].blueMetaTeamNumber, number=(i+1))
            blueRobot.update(health=incomingData[9+i])

    except:
        redMetaTeam = MetaTeam.objects.filter(number=arena[0].redMetaTeamNumber)
        redRobots = Robot.objects.filter(metaTeamNumber=arena[0].redMetaTeamNumber)
        blueMetaTeam = MetaTeam.objects.filter(number=arena[0].blueMetaTeamNumber)
        blueRobots = Robot.objects.filter(metaTeamNumber=arena[0].blueMetaTeamNumber)

        pass

    if arena[0].towerStatus == 0:
        towerStatus = "Unoccupied"
    else:
        towerStatus = "Captured!"

    redMetaTeam = MetaTeam.objects.filter(number=arena[0].redMetaTeamNumber)
    redRobots = Robot.objects.filter(metaTeamNumber=arena[0].redMetaTeamNumber)
    blueMetaTeam = MetaTeam.objects.filter(number=arena[0].blueMetaTeamNumber)
    blueRobots = Robot.objects.filter(metaTeamNumber=arena[0].blueMetaTeamNumber)

    if arena[0].status == 0:
        arenaStatus = "Off"
    else:
        arenaStatus = "On"

    percent = random.uniform(0,100)
    data = {"arenaStatus": arenaStatus,
            "autoMode": arena[0].autoMode,
            "arenaStage": arena[0].stage,
            "towerStatus": towerStatus,
            "redMetaTeamName": redMetaTeam[0].name,
            "redNexusHealth": int(arena[0].redNexusHealth*100/params.maxNexusHealth),
            "redRobot1Name": redRobots[0].name,
            "redRobot1Health": redRobots[0].health,
            "redRobot2Name": redRobots[1].name,
            "redRobot2Health": int(redRobots[1].health*100/params.maxRobotHealth),
            "redRobot3Name": redRobots[2].name,
            "redRobot3Health": int(redRobots[2].health*100/params.maxRobotHealth),
            "redRobot4Name": redRobots[3].name,
            "redRobot4Health": int(redRobots[3].health*100/params.maxRobotHealth),
            "blueMetaTeamName": blueMetaTeam[0].name,
            "blueNexusHealth": int(arena[0].blueNexusHealth*100/params.maxNexusHealth),
            "blueRobot1Name": blueRobots[0].name,
            "blueRobot1Health": int(blueRobots[0].health*100/params.maxRobotHealth),
            "blueRobot2Name": blueRobots[1].name,
            "blueRobot2Health": int(blueRobots[1].health*100/params.maxRobotHealth),
            "blueRobot3Name": blueRobots[2].name,
            "blueRobot3Health": int(blueRobots[2].health*100/params.maxRobotHealth),
            "blueRobot4Name": blueRobots[3].name,
            "blueRobot4Health": int(blueRobots[3].health*100/params.maxRobotHealth),
            }
    # print(data)
    return JsonResponse(data)
