from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .models import *

import random


def home(request):
    return render(request, "home.html")

def update(request):
    maxNexusHealth = 48;
    maxRobotHealth = 20;

    arena = Arena.objects.all()

    redMetaTeam = MetaTeam.objects.filter(number=arena[0].redMetaTeamNumber)
    redRobots = Robot.objects.filter(metaTeamNumber=arena[0].redMetaTeamNumber)
    blueMetaTeam = MetaTeam.objects.filter(number=arena[0].blueMetaTeamNumber)
    blueRobots = Robot.objects.filter(metaTeamNumber=arena[0].blueMetaTeamNumber)

    if arena[0].towerStatus == 0:
        towerStatus = "Not captured"
    else:
        if arena[0].towerStatus == 1:
            towerStatus = "Captured by Blue team!"
        else:
            towerStatus = "Captured by Red team!"

    if arena[0].status == 0:
        arenaStatus = "Off"
    else:
        arenaStatus = "On"

    percent = random.uniform(0,100)
    data = {"arenaStatus": arenaStatus,
            "arenaStage": arena[0].stage,
            "towerStatus": towerStatus,
            "redMetaTeamName": redMetaTeam[0].name,
            "redNexusHealth": int(arena[0].redNexusHealth/maxNexusHealth)*100,
            "redRobot1Name": redRobots[0].name,
            "redRobot1Health": int(percent), #redRobots[0].health,
            "redRobot2Name": redRobots[1].name,
            "redRobot2Health": int(redRobots[1].health/maxRobotHealth)*100,
            "redRobot3Name": redRobots[2].name,
            "redRobot3Health": int(redRobots[2].health/maxRobotHealth)*100,
            "redRobot4Name": redRobots[3].name,
            "redRobot4Health": int(redRobots[3].health/maxRobotHealth)*100,
            "blueMetaTeamName": blueMetaTeam[0].name,
            "blueNexusHealth": int(arena[0].blueNexusHealth/maxNexusHealth)*100,
            "blueRobot1Name": blueRobots[0].name,
            "blueRobot1Health": int(blueRobots[0].health/maxRobotHealth)*100,
            "blueRobot2Name": blueRobots[1].name,
            "blueRobot2Health": int(blueRobots[1].health/maxRobotHealth)*100,
            "blueRobot3Name": blueRobots[2].name,
            "blueRobot3Health": int(blueRobots[2].health/maxRobotHealth)*100,
            "blueRobot4Name": blueRobots[3].name,
            "blueRobot4Health": int(blueRobots[3].health/maxRobotHealth)*100,
            }
    return JsonResponse(data)
