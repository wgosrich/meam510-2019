OUT OF DATE MAKE NEW READ ME

TO run the server you need to run LoLController.py using python3, on a computer with the IP 10.0.0.2 because that is where every other node is looking. Before hand you need to change the hit delay (cool down), and hit damage for each robot.

This should be updated so you can enter it in for each team once and just indicate which team is which color.

Currently things only happen on events.  Using asyncio would allow some processes to run in parallel but I have not had time to look into this.  This would simplify how things work overall as some things (most) where made to work when events happen from the judges.

The data format is currently a set of chars.  The data length can be reduced to 2 bits for the data type (start/pause, red hit, blue hit, healing), and 3 bits for the who performed the action and 3 bits for who the action was performed on. 10 010 000 MSB (hit 1 or pause/heal 0), (red 1 / blue 0 or pause 1 / heal 0).

Similarly the health message is chars and could be changed to bytes, one for each bot.  This is more health than is needed but simplifies the parsing.

These are suggestions and you don't need to follow these changes if you see a better way, and there are certainly other improvements to make.