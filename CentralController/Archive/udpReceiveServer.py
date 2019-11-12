import socket
import time
import sys

UDP_IP = "192.168.4.2" # communicating devices should be within the same subnet
UDP_PORT = 10000

sock = socket.socket(socket.AF_INET, # Internet
                  socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(0)
    print("successful")
except:
    print("failed")
    sock.close()
    sys.exit()
# sock.bind((UDP_IP, UDP_PORT))

while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print ("received message:", data)
    except socket.error:
        # print("no data")
        pass
    time.sleep(0.5)
