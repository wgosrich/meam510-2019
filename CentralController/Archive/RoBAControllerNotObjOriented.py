#!/usr/bin/env python
#
# Keeps track of robot health for the league of legend final mechatronics project.
# Robots start with a certain amount of health
# When they die a death timer starts so they can come back in after it has expired.
# The death timer increases over the course of the match in minute increments
# They can only do a certain amount of damage with each hit then they have to wait a cooldown period
# Similarly, they can heal but can only heal so much then have a cool down period
# When the match finishes (a nexus is dead) all the robots die so they know to stop
# To start the match the system must receive a command starting with 'S'
#
#
# It is ugly.  Using functions is probably a good idea. I think asynchronous functions will be a good thing to use, but I think it would take a while and time is short. It gradually grew from something small to a big monstrous mess.  I would like to think I will clean it up eventually but realistically if you are reading this it is because someone asked you to fix it.  I am sorry.  It may be better to just start over, but you can try to salvage it.
#
#
#	Paul Stegall Dec. 3 2017
#
# runs a websocket server based on:
# https://github.com/Pithikos/python-websocket-server/blob/master/README.md
# this keeps track of robot health for LOL Bots
#
# https://wiki.python.org/moin/UdpCommunication -- Done
#
#
#TO RUN:
#  Update your hit damage and cooldown time, lines 54 to 77 , then
# 1: Open a terminal
# 2: Type: cd Desktop
# 3: Type: sudo python3 LoLController.py


from datetime import datetime, timedelta
import socket

import asyncio
from websocket_server import WebsocketServer





# from playsound import playsound
deathSound = "C:\Windows\media\Ring01.wav"
gameOverSound = "C:\Windows\media\Ring02.wav"
hostIP='192.168.2.100'; # this is the IP of your server (computer running this code).  Probably want a static IP.

UDP_IP1 = "10.0.0.3"; # ip addresses to send UDP packets to.  I port forward these to something on a different router that can then broadcast because I can't broadcast on the routers I have.
UDP_IP2 = "10.0.0.4";
UDP_PORT = 2808;  # port to send the UDP packets to.
 
udp = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP

gameOn=0; #keep track if the game is running
					  
#===========================================================
# setup the individual player charicteristics

#hitDamage = 5;    # damage one hit generates
#player specific damage
R1HitDamage = 25;
R2HitDamage = 25;
R3HitDamage = 25;
R4HitDamage = 25;
R5HitDamage = 4; # turret

B1HitDamage = 19.8;
B2HitDamage = 25;
B3HitDamage = 8.5;
B4HitDamage = 9.4;
B5HitDamage = 4; # turret

# in seconds
R1HitDelay = 3;
R2HitDelay = 2.6;
R3HitDelay = 2.7;
R4HitDelay = 2.6;
R5HitDelay = 0; # turret

B1HitDelay = 2;
B2HitDelay = 3;
B3HitDelay = 1;
B4HitDelay = 1;
B5HitDelay = 0; # turret
#===========================================================

# keep track of the last time they hit for cooldowns.
R1LastHitTime = datetime.now();
R2LastHitTime = datetime.now();
R3LastHitTime = datetime.now();
R4LastHitTime = datetime.now();
R5LastHitTime = datetime.now();

B1LastHitTime = datetime.now();
B2LastHitTime = datetime.now();
B3LastHitTime = datetime.now();
B4LastHitTime = datetime.now();
B5LastHitTime = datetime.now();

R1LastHealTime = datetime.now();
R2LastHealTime = datetime.now();
R3LastHealTime = datetime.now();
R4LastHealTime = datetime.now();
R5LastHealTime = datetime.now();

B1LastHealTime = datetime.now();
B2LastHealTime = datetime.now();
B3LastHealTime = datetime.now();
B4LastHealTime = datetime.now();
B5LastHealTime = datetime.now();

# times to keep track of these will be overwritten once the game starts
initializationTime = datetime(2000,1,1) # start the time somewhere it will never be again to check if it is the first time through.
gameStartTime = initializationTime
UDPLastSentTime = datetime.now();
#print(B4LastHitTime);

maxHealthP= 99;   # max health of the robot limited to 2 digits because of the way health list is defined
maxHealthN= 990;   # max health of the robot limited to 3 digits because of the way health list is defined
healRate  = 20;    # amount of healing per healDelay.
healDelay = 5;	# I added this as a way of slowing down the healing.

pauseTimeTotal = timedelta(seconds = 0) # keep track of how long the game has been paused.  This can then be used to subtracted from the death timer.
pausedAtTime = datetime.now()  #time the game was paused at.  This will be overwritten
pauseDelta = timedelta(seconds = 0); # keeps track of how long the last pause was.
deathTimer = 10;  # initial death timer time
reflectedDamagePercent = .5;

# track if they were dead when it paused so it can be added to their revive time.
R1DeadAtPause = 0;
R2DeadAtPause = 0;
R3DeadAtPause = 0;
R4DeadAtPause = 0;
B1DeadAtPause = 0;
B2DeadAtPause = 0;
B3DeadAtPause = 0;
B4DeadAtPause = 0;

# time things should be revived. Will be overwritten when they die.
R1ReviveTime = datetime.now();
R2ReviveTime = datetime.now();
R3ReviveTime = datetime.now();
R4ReviveTime = datetime.now();
R5ReviveTime = datetime.now();

B1ReviveTime = datetime.now();
B2ReviveTime = datetime.now();
B3ReviveTime = datetime.now();
B4ReviveTime = datetime.now();
B5ReviveTime = datetime.now();

# initialize the health
healthRNexus  = maxHealthN;
healthR1      = maxHealthP;
healthR2      = maxHealthP;
healthR3      = maxHealthP;
healthR4      = maxHealthP;
healthR5      = maxHealthP; # turret

healthBNexus  = maxHealthN;
healthB1      = maxHealthP;
healthB2      = maxHealthP;
healthB3      = maxHealthP;
healthB4      = maxHealthP;
healthB5      = maxHealthP; # turret

healthList = "%03d%02d%02d%02d%02d%03d%02d%02d%02d%02d" % (healthRNexus,healthR1,healthR2,healthR3,healthR4, healthBNexus,healthB1,healthB2,healthB3,healthB4);




def new_client(client, server):
	server.send_message(client,healthList)
	print('sent: ' + healthList + '\n')
	
def client_left(client, server):
	print('We Lost one\n')
	
	
def on_message(client, server, message):
		
	global healthList, healthRNexus, healthR1, healthR2, healthR3, healthR4, healthBNexus, healthB1, healthB2, healthB3, healthB4,  maxHealthP, maxHealthN, healRate, R1HitDelay, R2HitDelay, R3HitDelay, R4HitDelay, B1HitDelay, B2HitDelay, B3HitDelay, B4HitDelay, R1LastHitTime, R2LastHitTime, R3LastHitTime, R4LastHitTime, R5LastHitTime, B1LastHitTime, B2LastHitTime, B3LastHitTime, B4LastHitTime, B5LastHitTime, gameOn, R1LastHealTime, R2LastHealTime, R3LastHealTime, R4LastHealTime, B1LastHealTime, B2LastHealTime, B3LastHealTime, B4LastHealTime, gameStartTime, deathTimer, R1ReviveTime, R2ReviveTime, R3ReviveTime, R4ReviveTime, B1ReviveTime, B2ReviveTime, B3ReviveTime, B4ReviveTime, reflectedDamagePercent, initializationTime, pauseTimeTotal, pausedAtTime, pauseDelta, R1DeadAtPause,R2DeadAtPause, R3DeadAtPause, R4DeadAtPause, B1DeadAtPause, B2DeadAtPause, B3DeadAtPause, B4DeadAtPause, deathSound, gameOverSound # if we want to change these in a function we need to say that we want the global version (also this is a mess)
	
	print('received: ' + message + '\n')
	
	if initializationTime != gameStartTime: # only check this after the game starts.
		# increase the death timer 10 seconds every minute.
		if ((datetime.now() - gameStartTime) >= (timedelta(minutes=5)+ pauseTimeTotal )):
			deathTimer = 60;
		elif ((datetime.now() - gameStartTime) >= (timedelta(minutes=4)+ pauseTimeTotal )):
			deathTimer = 50;
		elif ((datetime.now() - gameStartTime) >= (timedelta(minutes=3)+ pauseTimeTotal )):
			deathTimer = 40;
		elif ((datetime.now() - gameStartTime) >= (timedelta(minutes=2)+ pauseTimeTotal )):
			deathTimer = 30;
		elif ((datetime.now() - gameStartTime) >= (timedelta(minutes=1)+ pauseTimeTotal )):
			deathTimer = 20;
	
	# if the player is still dead after their revive time, bring them back
	if gameOn : # only revive while the game is on.
		if ((R1ReviveTime + (R1DeadAtPause * pauseDelta) <= datetime.now())  & (healthR1 == 0)):
			healthR1=maxHealthP;
			R1DeadAtPause = 0; # reset the dead at pause.
		if ((R2ReviveTime + (R2DeadAtPause * pauseDelta) <= datetime.now())  & (healthR2 == 0)):
			healthR2=maxHealthP;
			R2DeadAtPause = 0; # reset the dead at pause.
		if ((R3ReviveTime + (R3DeadAtPause * pauseDelta) <= datetime.now())  & (healthR3 == 0)):
			healthR3=maxHealthP;
			R3DeadAtPause = 0; # reset the dead at pause.
		if ((R4ReviveTime + (R4DeadAtPause * pauseDelta) <= datetime.now())  & (healthR4 == 0)):
			healthR4=maxHealthP;
			R4DeadAtPause = 0; # reset the dead at pause.
		
		if ((B1ReviveTime + (B1DeadAtPause * pauseDelta) <= datetime.now())  & (healthB1 == 0)):
			healthB1=maxHealthP;
			B1DeadAtPause = 0; # reset the dead at pause.
		if ((B2ReviveTime + (B2DeadAtPause * pauseDelta) <= datetime.now())  & (healthB2 == 0)):
			healthB2=maxHealthP;
			B2DeadAtPause = 0; # reset the dead at pause.
		if ((B3ReviveTime + (B3DeadAtPause * pauseDelta) <= datetime.now())  & (healthB3 == 0)):
			healthB3=maxHealthP;
			B3DeadAtPause = 0; # reset the dead at pause.
		if ((B4ReviveTime + (B4DeadAtPause * pauseDelta) <= datetime.now())  & (healthB4 == 0)):
			healthB4=maxHealthP;
			B4DeadAtPause = 0; # reset the dead at pause.
	
	# track what their health was so we can calculate if they died or are just dead.
	oldHealthR1      = healthR1;
	oldHealthR2      = healthR2;
	oldHealthR3      = healthR3;
	oldHealthR4      = healthR4;

	oldHealthB1      = healthB1;
	oldHealthB2      = healthB2;
	oldHealthB3      = healthB3;
	oldHealthB4      = healthB4;
	
	
	if message[0] == 'S':# start match
		if 0==gameOn: # if the game was off start the timer. This will reset if you send the start command once the game ended.
			gameOn = 1;
			pauseDelta = (datetime.now() - pausedAtTime); # how long it was just paused for
			pauseTimeTotal = pauseTimeTotal + pauseDelta;
			print("Game on");
			
						
			if initializationTime == gameStartTime: # if it is the first time around set the startTime
				gameStartTime = datetime.now()
				print("LET THE GAME BEGIN!!!");
				print(gameStartTime);
				pauseTimeTotal = timedelta(seconds = 0) # reset the pauseTimeTotal if it is the first time through
			
		else:	# pause
			gameOn = 0
			pausedAtTime = datetime.now() # record when it was paused
			# if someone is dead we need to add the time of the pause to their revive time.
			R1DeadAtPause = (0 == healthR1);
			R2DeadAtPause = (0 == healthR2);
			R3DeadAtPause = (0 == healthR3);
			R4DeadAtPause = (0 == healthR4);
			B1DeadAtPause = (0 == healthB1);
			B2DeadAtPause = (0 == healthB2);
			B3DeadAtPause = (0 == healthB3);
			B4DeadAtPause = (0 == healthB4);
			
			print("Pause");
		
		print("The game has been paused for: ", pauseTimeTotal)		
		print("The total game time is: ", datetime.now() - gameStartTime - pauseTimeTotal);
		print("The death timer is: ", deathTimer)
		
	if (gameOn): 
		
	
		if message[0] == 'R':
			#RED Player hit BLUE player
			# #fixed damage
			# healthBNexus  = healthBNexus - int(message[2]) * hitDamage;  
			# healthB1      = healthB1 - int(message[3]) * hitDamage;
			# healthB2      = healthB2 - int(message[4]) * hitDamage;
			# healthB3      = healthB3 - int(message[5]) * hitDamage;
			# healthB4      = healthB4 - int(message[6]) * hitDamage;
			
			# not the most efficient but with the time checks it seemed like the most straight forward
			# if it is the right user and that user has not hit for the cooldown period, they can hit again.  As long as they are not dead.
			if ((message[1]=='1') and ((datetime.now()-R1LastHitTime)>=timedelta(seconds=R1HitDelay)) and (healthR1>0)):
				# remove damage
				healthBNexus  = healthBNexus - int(message[2]) * R1HitDamage;
				healthR1	  = healthR1 - int(message[2]) * R1HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthB1      = healthB1 - int(message[3]) * R1HitDamage;
				healthB2      = healthB2 - int(message[4]) * R1HitDamage;
				healthB3      = healthB3 - int(message[5]) * R1HitDamage;
				healthB4      = healthB4 - int(message[6]) * R1HitDamage;
				
				R1LastHitTime = datetime.now(); #Reset Time
				print("Red1 Made A Hit!!!");
				
			elif ((message[1]=='2') and ((datetime.now()-R2LastHitTime)>=timedelta(seconds=R2HitDelay)) and (healthR2>0)):
				# remove damage
				healthBNexus  = healthBNexus - int(message[2]) * R2HitDamage;
				healthR2	  = healthR2 - int(message[2]) * R2HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthB1      = healthB1 - int(message[3]) * R2HitDamage;
				healthB2      = healthB2 - int(message[4]) * R2HitDamage;
				healthB3      = healthB3 - int(message[5]) * R2HitDamage;
				healthB4      = healthB4 - int(message[6]) * R2HitDamage;
				
				R2LastHitTime = datetime.now(); #Reset Time
				print("Red2 Made A Hit!!!");
				
			elif ((message[1]=='3') and ((datetime.now()-R3LastHitTime)>=timedelta(seconds=R3HitDelay)) and (healthR3>0)):
				# remove damage
				healthBNexus  = healthBNexus - int(message[2]) * R3HitDamage;
				healthR3	  = healthR3 - int(message[2]) * R3HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthB1      = healthB1 - int(message[3]) * R3HitDamage;
				healthB2      = healthB2 - int(message[4]) * R3HitDamage;
				healthB3      = healthB3 - int(message[5]) * R3HitDamage;
				healthB4      = healthB4 - int(message[6]) * R3HitDamage;
				
				R3LastHitTime = datetime.now(); #Reset Time
				print("Red3 Made A Hit!!!");
				
			elif ((message[1]=='4') and ((datetime.now()-R4LastHitTime)>=timedelta(seconds=R4HitDelay)) and (healthR4>0)):
				# remove damage
				healthBNexus  = healthBNexus - int(message[2]) * R4HitDamage;
				healthR4	  = healthR4 - int(message[2]) * R4HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthB1      = healthB1 - int(message[3]) * R4HitDamage;
				healthB2      = healthB2 - int(message[4]) * R4HitDamage;
				healthB3      = healthB3 - int(message[5]) * R4HitDamage;
				healthB4      = healthB4 - int(message[6]) * R4HitDamage;
				
				R4LastHitTime = datetime.now(); #Reset Time
				print("Red4 Made A Hit!!!");
			
			#this is the turret
			elif ((message[1]=='5') and ((datetime.now()-R5LastHitTime)>=timedelta(seconds=R5HitDelay)) and (healthR5>0)):
				# remove damage 
				healthBNexus  = healthBNexus - int(message[2]) * R5HitDamage;
				healthB1      = healthB1 - int(message[3]) * R5HitDamage;
				healthB2      = healthB2 - int(message[4]) * R5HitDamage;
				healthB3      = healthB3 - int(message[5]) * R5HitDamage;
				healthB4      = healthB4 - int(message[6]) * R5HitDamage;
				
				R5LastHitTime = datetime.now(); #Reset Time
				print("Red Turret Made A Hit!!!");
			
			
		elif message[0] == 'B':	
			#BLUE Player hit RED player
			# #fixed damage
			# healthRNexus  = healthRNexus - int(message[2]) * hitDamage;
			# healthR1      = healthR1 - int(message[3]) * hitDamage;
			# healthR2      = healthR2 - int(message[4]) * hitDamage;
			# healthR3      = healthR3 - int(message[5]) * hitDamage;
			# healthR4      = healthR4 - int(message[6]) * hitDamage;
			
			
			
			# not the most efficient but with the time checks it seemed like the most straight forward
			# if it is the right user and that user has not hit for the cooldown period, they can hit again. As long as they are not dead.
			if ((message[1]=='1') and ((datetime.now()-B1LastHitTime)>=timedelta(seconds=B1HitDelay)) and (healthB1>0)):
				# remove damage
				healthRNexus  = healthRNexus - int(message[2]) * B1HitDamage;
				healthB1	  = healthB1 - int(message[2]) * B1HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthR1      = healthR1 - int(message[3]) * B1HitDamage;
				healthR2      = healthR2 - int(message[4]) * B1HitDamage;
				healthR3      = healthR3 - int(message[5]) * B1HitDamage;
				healthR4      = healthR4 - int(message[6]) * B1HitDamage;
				
				B1LastHitTime = datetime.now(); #Reset Time
				print("Blue1 Made A Hit!!!");
				
			elif ((message[1]=='2') and ((datetime.now()-B2LastHitTime)>=timedelta(seconds=B2HitDelay)) and (healthB2>0)):
				# remove damage
				healthRNexus  = healthRNexus - int(message[2]) * B2HitDamage;
				healthB2	  = healthB2 - int(message[2]) * B2HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthR1      = healthR1 - int(message[3]) * B2HitDamage;
				healthR2      = healthR2 - int(message[4]) * B2HitDamage;
				healthR3      = healthR3 - int(message[5]) * B2HitDamage;
				healthR4      = healthR4 - int(message[6]) * B2HitDamage;
				
				B2LastHitTime = datetime.now(); #Reset Time
				print("Blue2 Made A Hit!!!");
				
			elif ((message[1]=='3') and ((datetime.now()-B3LastHitTime)>=timedelta(seconds=B3HitDelay)) and (healthB3>0)):
				# remove damage
				healthRNexus  = healthRNexus - int(message[2]) * B3HitDamage;
				healthB3	  = healthB3 - int(message[2]) * B3HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthR1      = healthR1 - int(message[3]) * R3HitDamage;
				healthR2      = healthR2 - int(message[4]) * B3HitDamage;
				healthR3      = healthR3 - int(message[5]) * B3HitDamage;
				healthR4      = healthR4 - int(message[6]) * B3HitDamage;
				
				B3LastHitTime = datetime.now(); #Reset Time
				print("Blue3 Made A Hit!!!");
				
			elif ((message[1]=='4') and ((datetime.now()-B4LastHitTime)>=timedelta(seconds=B4HitDelay)) and (healthB4>0)):
				# remove damage
				healthRNexus  = healthRNexus - int(message[2]) * B4HitDamage;
				healthB4	  = healthB4 - int(message[2]) * B4HitDamage * reflectedDamagePercent; # when you hit the nexus a portion of that damage comes back to you 
				healthR1      = healthR1 - int(message[3]) * B4HitDamage;
				healthR2      = healthR2 - int(message[4]) * B4HitDamage;
				healthR3      = healthR3 - int(message[5]) * B4HitDamage;
				healthR4      = healthR4 - int(message[6]) * B4HitDamage;
				
				B4LastHitTime = datetime.now(); #Reset Time
				print("Blue4 Made A Hit!!!");
			
			elif ((message[1]=='5') and ((datetime.now()-B5LastHitTime)>=timedelta(seconds=B5HitDelay)) and (healthB5>0)):
				# remove damage
				healthRNexus  = healthRNexus - int(message[2]) * B5HitDamage;
				healthR1      = healthR1 - int(message[3]) * B5HitDamage;
				healthR2      = healthR2 - int(message[4]) * B5HitDamage;
				healthR3      = healthR3 - int(message[5]) * B5HitDamage;
				healthR4      = healthR4 - int(message[6]) * B5HitDamage;
				
				B5LastHitTime = datetime.now(); #Reset Time
				print("Blue Turret Made A Hit!!!");
						
		
		elif message[0] == 'H':
			#Player healed updated after the delay from the last time they healed)
			if message[1] == 'R':
				if ((message[2]=='1') and ((datetime.now()-R1LastHealTime)>=timedelta(seconds=healDelay)) and (healthR1>0)):
					healthR1 = healthR1 + healRate;
					print("healthR1 Updated");
					R1LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthR1 > maxHealthP :
						healthR1 = maxHealthP;

				elif ((message[2]=='2') and ((datetime.now()-R2LastHealTime)>=timedelta(seconds=healDelay)) and (healthR2>0)):
					healthR2 = healthR2 + healRate;
					print("healthR2 Updated");
					R2LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthR2 > maxHealthP:
						healthR2 = maxHealthP;

				elif ((message[2]=='3') and ((datetime.now()-R3LastHealTime)>=timedelta(seconds=healDelay)) and (healthR3>0)):
					healthR3 = healthR3 + healRate;
					print("healthR3 Updated");
					R3LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthR3 > maxHealthP:
						healthR3 = maxHealthP;

				elif ((message[2]=='4') and ((datetime.now()-R4LastHealTime)>=timedelta(seconds=healDelay)) and (healthR4>0)):
					healthR4 = healthR4 + healRate;
					print("healthR4 Updated");
					R4LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthR4 > maxHealthP :
						healthR4 = maxHealthP;
			
			
			elif message[1] == 'B':
				if ((message[2]=='1') and ((datetime.now()-B1LastHealTime)>=timedelta(seconds=healDelay)) and (healthB1>0)):
					healthB1 = healthB1 + healRate;
					print("healthB1 Updated");
					B1LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthB1 > maxHealthP :
						healthB1 = maxHealthP;
				
				elif ((message[2]=='2') and ((datetime.now()-B2LastHealTime)>=timedelta(seconds=healDelay)) and (healthB2>0)):
					healthB2 = healthB2 + healRate;
					print("healthB2 Updated");
					B2LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthB2 > maxHealthP:
						healthB2 = maxHealthP;

				elif ((message[2]=='3') and ((datetime.now()-B3LastHealTime)>=timedelta(seconds=healDelay)) and (healthB3>0)):
					healthB3 = healthB3 + healRate;
					print("healthB3 Updated");
					B3LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthB3 > maxHealthP :
						healthB3 = maxHealthP;
				
				elif ((message[2]=='4') and ((datetime.now()-B4LastHealTime)>=timedelta(seconds=healDelay)) and (healthB4>0)):
					healthB1 = healthB1 + healRate;
					print("healthB4 Updated");
					B4LastHealTime = datetime.now(); #Reset Time
					#prevent it from going above max
					if healthB4 > maxHealthP :
						healthB4 = maxHealthP;
	
		#prevent it from going below 0
		if healthBNexus < 0:
			healthBNexus = 0;
		if healthB1 <= 0:
			healthB1 = 0;
			if healthB1 < oldHealthB1: # if they just died start their timer.
				B1ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		if healthB2 <= 0:
			healthB2 = 0;
			if healthB2 < oldHealthB2: # if they just died start their timer.
				B2ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		if healthB3 <= 0:
			healthB3 = 0;
			if healthB3 < oldHealthB3: # if they just died start their timer.
				B3ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		if healthB4 <= 0:
			healthB4 = 0;
			if healthB4 < oldHealthB4: # if they just died start their timer.
				B4ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		
		#prevent it from going below 0
		if healthRNexus < 0:
			healthRNexus = 0;
		if healthR1 <= 0:
			healthR1 = 0;
			if healthR1 < oldHealthR1: # if they just died start their timer.
				R1ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		if healthR2 <= 0:
			healthR2 = 0;
			if healthR2 < oldHealthR2: # if they just died start their timer.
				R2ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		if healthR3 <= 0:
			healthR3 = 0;
			if healthR3 < oldHealthR3: # if they just died start their timer.
				R3ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		if healthR4 <= 0:
			healthR4 = 0;
			if healthR4 < oldHealthR4: # if they just died start their timer.
				R4ReviveTime = datetime.now() + timedelta(seconds=deathTimer);
				#playsound(deathSound)
		
		if ((healthRNexus == 0) | (healthBNexus == 0)): # game over, Kill everyone and stop the game
			healthR1      = 0;
			healthR2      = 0;
			healthR3      = 0;
			healthR4      = 0;
			healthB1      = 0;
			healthB2      = 0;
			healthB3      = 0;
			healthB4      = 0;
			print("GAME OVER!!!");
			gameOn=0;
			
			#playsound(gameOverSound)
			
		healthList = self.get_health_message()
		
		server.send_message_to_all(healthList) # broadcast the healthList to anyone who will listen
		print('sent websocket: ' + healthList)
		udp.sendto(healthList.encode() , (UDP_IP1, UDP_PORT))
		udp.sendto(healthList.encode() , (UDP_IP2, UDP_PORT))
		print('sent udp: ' + healthList + '\n')
	
	else : #the game is off, stop all the bots.
		healthListZero = self.get_health_message()
		udp.sendto(healthListZero.encode() , (UDP_IP1, UDP_PORT))
		udp.sendto(healthListZero.encode() , (UDP_IP2, UDP_PORT))
		print('sent udp: ' + healthListZero + '\n')
		


server = WebsocketServer(81, host=hostIP)  #this is the port and IP address you want the server to use.

server.set_fn_new_client(new_client) #when a new client joins in calls the function new_client
server.set_fn_message_received(on_message)#when a message is received it calls on_message
server.set_fn_client_left(client_left) #when a client leaves it calls client_left


server.run_forever()





