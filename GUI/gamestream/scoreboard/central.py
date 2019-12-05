import socket

class UDPBroadcastReceiver:
    def __init__(self):
        self.UDP_IP = "0.0.0.0"
        self.UDP_PORT = 5555
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.sock.setblocking(0)

class Params:
    def __init__(self):
        self.maxNexusHealth = 48;
        self.maxRobotHealth = 20;
