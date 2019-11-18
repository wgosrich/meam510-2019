b = 0xFFFF
print(b)
message = []
for i in range(16):
    message.append(b >> i & 0b1)
print(message)

isActive = False if (message[0]) else True
health = int(message[1] | message[2] << 1 | message[3] << 2 | message[4] << 3 | message[5] << 4)
xLocation = int(message[8] | message[9] << 1 | message[10] << 2 | message[11] << 3)
yLocation = int(message[12] | message[13] << 1 | message[14] << 2 | message[15] << 3)

print(isActive)
print(health)
print(xLocation)
print(yLocation)
