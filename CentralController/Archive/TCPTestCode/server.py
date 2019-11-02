#!/usr/bin/python3           # This is server.py file
# import socket                                         

# # create a socket object
# serversocket = socket.socket(
# 	        socket.AF_INET, socket.SOCK_STREAM) 

# # get local machine name
# host = socket.gethostname()                           
# print(host)
# port = 201                                           

# # bind to the port
# serversocket.bind(('192.168.1.5', port))                                  

# # queue up to 5 requests
# serversocket.listen(5)                                           

# while True:
#    # establish a connection
#    clientsocket,addr = serversocket.accept()      

#    print("Got a connection from %s" % str(addr))
    
#    # msg = 'Thank you for connecting'+ "\r\n"
#    # clientsocket.send(msg.encode('ascii'))
#    clientsocket.close()

   # Echo server program
import socket

HOST = '192.168.1.5'                 # Symbolic name meaning all available interfaces
PORT = 201             # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    while True:
        conn, addr = s.accept()
        with conn:
	        print('Connected by', addr)
	        while True:
	            data = conn.recv(1024)
	            if not data: break
	            print('gotData')
	            timeRead = int.from_bytes(data, byteorder='little')
	            print(timeRead)
	            conn.sendall(b'Hello')