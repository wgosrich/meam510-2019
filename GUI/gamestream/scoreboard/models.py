from django.db import models

# Create your models here.
class MetaTeam(models.Model):
    number = models.IntegerField(default=0)
    name = models.CharField(max_length=200)

class Robot(models.Model):
    IP = models.IntegerField(default=100)
    name = models.CharField(max_length=200)
    number = models.IntegerField(default=0)
    metaTeamNumber = models.IntegerField(default=0)
    health = models.IntegerField(default=24);

class Arena(models.Model):
    redMetaTeamNumber = models.IntegerField(default=0)
    redNexusHealth = models.IntegerField(default=48)

    blueMetaTeamNumber = models.IntegerField(default=0)
    blueNexusHealth = models.IntegerField(default=48)

    towerStatus = models.IntegerField(default=0)

    status = models.IntegerField(default=0)
    autoMode = models.IntegerField(default=0)
    stage = models.CharField(max_length=200)
