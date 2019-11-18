# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 11:15:48 2018

@author: J. Diego Caporale
"""

import RoBAArena #Arena class object holds all the information


#GUI INIT CODE 
arena = RoBAArena.Arena('teamsTest.csv',1,2)


# GUI LOOP
arena.GUI_update() # Will update all the robot healths and what not






