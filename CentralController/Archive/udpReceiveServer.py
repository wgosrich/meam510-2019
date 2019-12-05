import socket
import time
import sys

# UDP_IP = "192.168.1.3" # communicating devices should be within the same subnet
UDP_IP = "0.0.0.0"
UDP_PORT = 5555

sock = socket.socket(socket.AF_INET, # Internet
                  socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# while True:
#     try:
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)
print("successful")
    #     break;
    # except:
    #     print("failed")
    #     time.sleep(0.01)
    #     pass
        # sock.close()
        # sys.exit()
# sock.bind((UDP_IP, UDP_PORT))

while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print ("received message:", data)
    except socket.error:
        # print("no data")
        pass
    time.sleep(0.001)
