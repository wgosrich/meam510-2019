from tkinter import *

root = Tk() # create tkinter object
root.geometry("1500x800") # set window size
root.configure(background='black') # set background color
root.title("MEAM 510") # window title

canvas = Canvas()
canvas.config(bg = "black", highlightthickness=0)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Values to Read In
redTeamName = "DUMBLEDORE'S ARMY"
redMetaTeamNumber = 1
redNexusHealth = 882
red1Label = Label(root, text = "HARRY")
red2Label = Label(root, text = "HERMIONE")
red3Label = Label(root, text = "RON")
red4Label = Label(root, text = "GINNY")
red1Health = 800
red2Health = 555
red3Health = 444
red4Health = 333
red1healing = False
red2healing = True
red3healing = True
red4healing = False

blueTeamName = "SUPERHEROES'"
blueMetaTeamNumber = 2
blueNexusHealth = 222
blue1Label = Label(root, text = "WONDERWOMAN")
blue2Label = Label(root, text = "SUPERMAN")
blue3Label = Label(root, text = "BATMAN")
blue4Label = Label(root, text = "AQUAMAN")
blue1Health = 357
blue2Health = 893
blue3Health = 456
blue4Health = 290
blue1healing = True
blue2healing = False
blue3healing = True
blue4healing = False

# Percentage Calculation
redNexusHealthPercentage = redNexusHealth/999
red1HealthPercentage = red1Health/999
red2HealthPercentage = red2Health/999
red3HealthPercentage = red3Health/999
red4HealthPercentage = red4Health/999

blueNexusHealthPercentage = blueNexusHealth/999
blue1HealthPercentage = blue1Health/999
blue2HealthPercentage = blue2Health/999
blue3HealthPercentage = blue3Health/999
blue4HealthPercentage = blue4Health/999

# Variables
yNexusHealthBar = 5
heightHealthBarNexus = 50
widthHealthBarNexus = 600
xDistanceFromEdge = 30
middleGapNexus = screen_width-2*widthHealthBarNexus-2*xDistanceFromEdge
yTeamName = 115
yRobot1 = 175
yRobotGap = 100
widthHealthBarRobot = 250
heightHealthBarRobot = 40
yRobotGapHealthBar = 55
middleGapRobot = screen_width-2*widthHealthBarRobot-2*xDistanceFromEdge

# Title
title = Label(root, text="MECHATRONICS 2018 FINAL TOURNAMENT") # title
title.config(bg = 'black', fg = 'white', font=("Helvetica", 44)) # set text configurations
title.pack()

# Red Nexus Health Bar and Percentage
canvas.create_rectangle(xDistanceFromEdge, yNexusHealthBar, widthHealthBarNexus+xDistanceFromEdge,
                        yNexusHealthBar + heightHealthBarNexus, fill='gray', width = 0) # gray background
canvas.create_rectangle(xDistanceFromEdge, yNexusHealthBar,
                        (widthHealthBarNexus+xDistanceFromEdge)*redNexusHealthPercentage,
                        yNexusHealthBar + heightHealthBarNexus, fill='red', width = 0) # red health indicator

redNexusHealthPercentageLabel = Label(root, text = str(redNexusHealth))
redNexusHealthPercentageLabel.config(bg='gray', fg='black', font=("Helvetica", 30))
if redNexusHealthPercentage < .9:
    redNexusHealthPercentageLabel.place(x=widthHealthBarNexus+xDistanceFromEdge-60,
                                        y=yNexusHealthBar + heightHealthBarNexus+10)

# Blue Nexus Health Bar and Percentage
canvas.create_rectangle(xDistanceFromEdge+widthHealthBarNexus+middleGapNexus, yNexusHealthBar,
                        screen_width-xDistanceFromEdge, yNexusHealthBar + heightHealthBarNexus,
                        fill='gray', width = 0) # gray background
canvas.create_rectangle((xDistanceFromEdge+widthHealthBarNexus+middleGapNexus) +
                        ((1-blueNexusHealthPercentage)*widthHealthBarNexus),
                        yNexusHealthBar, screen_width-xDistanceFromEdge, yNexusHealthBar + heightHealthBarNexus,
                        fill='blue', width = 0) # red health indicator

blueNexusHealthLabel = Label(root, text = str(blueNexusHealth))
blueNexusHealthLabel.config(bg='gray', fg='black', font=("Helvetica", 30))
if blueNexusHealthPercentage < .9:
    blueNexusHealthLabel.place(x=xDistanceFromEdge+widthHealthBarNexus+middleGapNexus,
                               y=yNexusHealthBar + heightHealthBarNexus+10)

# Meta Team Names
redTeamNameLabel = Label(root, text = redTeamName+" NEXUS")
redTeamNameLabel.config(bg = 'black', fg = 'white', font=("Helvetica", 30))
redTeamNameLabel.place(x=50, y=yTeamName)

blueTeamNameLabel = Label(root, text = blueTeamName+" NEXUS")
blueTeamNameLabel.config(bg = 'black', fg = 'white', font=("Helvetica", 30))
blueTeamNameLabel.place(x=800, y=yTeamName)

# Robot Names Red
red1Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
red1Label.place(x=xDistanceFromEdge, y=yRobot1)

red2Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
red2Label.place(x=xDistanceFromEdge, y=yRobot1+yRobotGap)

red3Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
red3Label.place(x=xDistanceFromEdge, y=yRobot1+yRobotGap*2)

red4Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
red4Label.place(x=xDistanceFromEdge, y=yRobot1+yRobotGap*3)

# Robot Names Blue
blue1Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
blue1Label.place(x=1000, y=yRobot1)

blue2Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
blue2Label.place(x=1000, y=yRobot1+yRobotGap)

blue3Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
blue3Label.place(x=1000, y=yRobot1+yRobotGap*2)

blue4Label.config(bg = 'black', fg = 'white', font=("Helvetica", 25))
blue4Label.place(x=1000, y=yRobot1+yRobotGap*3)

# Robot Health Red

# Red 1 Health Bar
canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar,
        widthHealthBarRobot+xDistanceFromEdge, yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
            fill='gray', width = 0) # gray background
if red1healing == True:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar,
         widthHealthBarRobot*red1HealthPercentage+xDistanceFromEdge, yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
            fill='green', width = 0) # red health indicator
else:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar,
        widthHealthBarRobot*red1HealthPercentage+xDistanceFromEdge, yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
            fill='red', width = 0) # red health indicator

# Red 2 Health Bar
canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar + yRobotGap,
        widthHealthBarRobot+xDistanceFromEdge, 2*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
            fill='gray', width = 0) # gray background
if red2healing == True:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar + yRobotGap,
        widthHealthBarRobot*red2HealthPercentage+xDistanceFromEdge, 2*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
            fill='green', width = 0) # red health indicator
else:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + yRobotGap,
        widthHealthBarRobot * red2HealthPercentage + xDistanceFromEdge,
            2 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
            fill='red', width=0)  # red health indicator

# Red 3 Health Bar
canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar + 2*yRobotGap,
                        widthHealthBarRobot+xDistanceFromEdge, 3*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
                        fill='gray', width = 0) # gray background
if red3healing == True:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + 2 * yRobotGap,
                            widthHealthBarRobot * red3HealthPercentage + xDistanceFromEdge,
                            3 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot, fill='green',
                            width=0)  # red health indicator
else:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + 2 * yRobotGap,
                            widthHealthBarRobot * red3HealthPercentage + xDistanceFromEdge,
                            3 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot, fill='red',
                            width=0)  # red health indicator

# Red 4 Health Bar
canvas.create_rectangle(xDistanceFromEdge, yRobotGap+yRobotGapHealthBar + 3*yRobotGap,
                        widthHealthBarRobot+xDistanceFromEdge, 4*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
                        fill='gray', width = 0) # gray background
if red4healing == True:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + 3 * yRobotGap,
                            widthHealthBarRobot * red4HealthPercentage + xDistanceFromEdge,
                            4 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot, fill='green',
                            width=0)  # red health indicator
else:
    canvas.create_rectangle(xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + 3 * yRobotGap,
                            widthHealthBarRobot * red4HealthPercentage + xDistanceFromEdge,
                            4 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot, fill='red',
                            width=0)  # red health indicator

# Red 1 Health Percentage
red1HealthLabel = Label(root, text = str(red1Health))
red1HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if red1HealthPercentage < .8:
    red1HealthLabel.place(x=widthHealthBarRobot+xDistanceFromEdge-50,
                          y=yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Red 2 Health Percentage
red2HealthLabel = Label(root, text = str(red2Health))
red2HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if red2HealthPercentage < .8:
    red2HealthLabel.place(x=widthHealthBarRobot+xDistanceFromEdge-50,
                          y=2*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Red 3 Health Percentage
red3HealthLabel = Label(root, text = str(red3Health))
red3HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if red3HealthPercentage < .8:
    red3HealthLabel.place(x=widthHealthBarRobot+xDistanceFromEdge-50,
                          y=3*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Red 4 Health Percentage
red4HealthLabel = Label(root, text = str(red4Health))
red4HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if red4HealthPercentage < .8:
    red4HealthLabel.place(x=widthHealthBarRobot+xDistanceFromEdge-50,
                          y=4*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Robot Health Blue

# Blue 1 Health Bar
canvas.create_rectangle(xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                        yRobotGap+yRobotGapHealthBar, screen_width-xDistanceFromEdge,
                        yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
                        fill='gray', width = 0) # gray background
if blue1healing == True:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue1HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar,
                            screen_width - xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='green', width=0)  # red health indicator
else:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue1HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar,
                            screen_width - xDistanceFromEdge, yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='blue', width=0)  # red health indicator

# Blue 2 Health Bar
canvas.create_rectangle(xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                        yRobotGap+yRobotGapHealthBar + yRobotGap, screen_width-xDistanceFromEdge,
                        2*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
                        fill='gray', width = 0) # gray background
if blue2healing == True:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue2HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar + yRobotGap,
                            screen_width - xDistanceFromEdge, 2 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='green', width=0)  # red health indicator
else:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue2HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar + yRobotGap,
                            screen_width - xDistanceFromEdge, 2 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='blue', width=0)  # red health indicator

# Blue 3 Health Bar
canvas.create_rectangle(xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                        yRobotGap+yRobotGapHealthBar + 2*yRobotGap, screen_width-xDistanceFromEdge,
                        3*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
                        fill='gray', width = 0) # gray background
if blue3healing == True:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue3HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar + 2 * yRobotGap,
                            screen_width - xDistanceFromEdge, 3 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='green', width=0)  # red health indicator
else:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue3HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar + 2 * yRobotGap,
                            screen_width - xDistanceFromEdge, 3 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='blue', width=0)  # red health indicator

# Blue 4 Health Bar
canvas.create_rectangle(xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                        yRobotGap+yRobotGapHealthBar + 3*yRobotGap, screen_width-xDistanceFromEdge,
                        4*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot,
                        fill='gray', width = 0) # gray background
if blue4healing == True:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue4HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar + 3 * yRobotGap,
                            screen_width - xDistanceFromEdge, 4 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='green', width=0)  # red health indicator
else:
    canvas.create_rectangle((xDistanceFromEdge + widthHealthBarRobot + middleGapRobot) + (
                (1 - blue4HealthPercentage) * widthHealthBarRobot), yRobotGap + yRobotGapHealthBar + 3 * yRobotGap,
                            screen_width - xDistanceFromEdge, 4 * yRobotGap + yRobotGapHealthBar + heightHealthBarRobot,
                            fill='blue', width=0)

# Blue 1 Health Percentage
blue1HealthLabel = Label(root, text = str(blue1Health))
blue1HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if blue1HealthPercentage < .8:
    blue1HealthLabel.place(x=xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                           y=yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Blue 2 Health Percentage
blue2HealthLabel = Label(root, text = str(blue2Health))
blue2HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if blue2HealthPercentage < .8:
    blue2HealthLabel.place(x=xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                           y=2*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Blue 3 Health Percentage
blue3HealthLabel = Label(root, text = str(blue3Health))
blue3HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if blue3HealthPercentage < .8:
    blue3HealthLabel.place(x=xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                           y=3*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Blue 4 Health Percentage
blue4HealthLabel = Label(root, text = str(blue4Health))
blue4HealthLabel.config(bg='gray', fg='black', font=("Helvetica", 25))
if blue4HealthPercentage < .8:
    blue4HealthLabel.place(x=xDistanceFromEdge+widthHealthBarRobot+middleGapRobot,
                           y=4*yRobotGap+yRobotGapHealthBar+heightHealthBarRobot+18)

# Meta Team Number
redMetaTeamNumberLabel = Label(root, text = str(redMetaTeamNumber))
redMetaTeamNumberLabel.config(bg='black', fg='white', font=("Helvetica", 100))
redMetaTeamNumberLabel.place(x=125, y=575)

blueMetaTeamNumberLabel = Label(root, text = str(blueMetaTeamNumber))
blueMetaTeamNumberLabel.config(bg='black', fg='white', font=("Helvetica", 100))
blueMetaTeamNumberLabel.place(x=1100, y=575)


# Place Holder Game Livestream
canvas.create_rectangle(screen_width/2-350, 100, screen_width/2+350, 800, fill='white', width = 0) # gray background

canvas.pack(fill=BOTH, expand=1)
root.mainloop()