import socket
import time

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(0.2)
server.bind(("192.168.1.5", 202))
count = 0
message = b"yo"
while True:
    server.sendto(message, ('<broadcast>', 3333))
    print("message sent!")
    time.sleep(1)