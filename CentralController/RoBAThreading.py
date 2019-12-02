"""Summary
"""
import time
from datetime import datetime
import threading
import socket
import numpy as np
from RoBANetwork import get_host_name_IP
from RoBAClasses import  RobotNotActiveError, RobotListEmptyError
import struct







class ProtectedLoop(threading.Thread):

    """This class provides events used for clean up and close of a thread.
    https://www.g-loaded.eu/2016/11/24/how-to-terminate-running-python-threads-using-signals/
    https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client

    Attributes:
        shutdownFlag (TYPE): Description

    Deleted Attributes:
        shutdown_flag (threasding.Event): If set the thread shutdown
    """
    shutdownFlag = threading.Event()
    def __init__(self):
        """Summary
        """
        threading.Thread.__init__(self)

        # The shutdownFlag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.holdFlag = threading.Event()

        # ... Other thread setup code here ...
    def prot_loop_startup(self):
        """Summary
        """
        print('Thread #%s started' % self.ident)

    def prot_loop_run(self):
        """Summary
        """

        time.sleep(1)
        print("running: %s" % self.ident)

    def prot_loop_shutdown(self):
        """Summary
        """
        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)

    def run(self):
        """Summary
        """
        self.prot_loop_startup()

        try:
            while not self.shutdownFlag.is_set():
                # ... Job code here ...

                if not self.holdFlag.is_set():
                    self.prot_loop_run()
                else:
                    time.sleep(.1)

        finally:
            self.prot_loop_shutdown()

class ThreadedTCPServer(ProtectedLoop):

    """Server Thread that listens for TCP communication

    Attributes:
        host (TYPE): Description
        port (TYPE): Description
        sock (TYPE): Description
    """

    def __init__(self, host, port):
        """Summary

        Args:
            host (TYPE): Description
            port (TYPE): Description
        """
        ProtectedLoop.__init__(self)
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def prot_loop_startup(self):
        """Summary
        """
        self.sock.listen(10)
        print('Thread #%s started: TCP Server' % self.ident)

    def prot_loop_run(self):
        """Summary
        """
        self.listen()
        time.sleep(.01)

    def prot_loop_shutdown(self):
        """Summary
        """
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        print("Closing the TCP Server on thread ", self.ident )

    def listen(self):
        """Summary

        Returns:
            TYPE: Description
        """
        try:
            conn, addr = self.sock.accept()
        except IOError:
            return 0
        except Exception as err:
            print("Unexpected Server Exception: ", err, err.args)
            return 0
        conn.settimeout(1)


        threading.Thread(target=self.listen_to_client, args=(conn, addr)).start()

    def listen_to_client(self, client, address):
        """Summary

        Args:
            client (TYPE): Description
            address (TYPE): Description

        Returns:
            TYPE: Description

        Raises:
            Exception: Description
        """
        size = 1024
        try:
            data = client.recv(size)
            if data:
                # Set the response to echo back the recieved data
                response = data
                client.send(response)
            else:
                raise Exception('Client disconnected')
        except:
            client.close()
            return False

class RoBATCPListener(ThreadedTCPServer):

    """Summary

    Attributes:
        host (TYPE): Description
        port (TYPE): Description
        sock (TYPE): Description
    """

    def __init__(self, host, arena, port=4444, timeout=5):
        """Summary

        Args:
            host (TYPE): Description
            port (TYPE): Description
        """
        ThreadedTCPServer.__init__(self, host, port)
        self.arena = arena
        self.timeout = timeout
        self.sock.settimeout(1)

    def listen(self):
        try:
            # print("listening here")
            conn, addr = self.sock.accept()
            self.arena.logL.write("\n***********Getting IO: " + addr[0] + "\n")
        except IOError:
            return 0
        except Exception as err:
            print("Unexpected Server Exception: ", err, err.args)
            return 0
        conn.settimeout(1)

        # NOTE: HERE IS THE DIFFERENCE ROBA

        listen_RoBA_client(conn, addr, self.arena, timeout=self.timeout).start()

class listen_RoBA_client(ProtectedLoop):

    """Summary

    Args:
        client (TYPE): Description
        address (TYPE): Description

    Returns:
        TYPE: Description

    Raises:
        Exception: Description

    No Longer Raises:
        error: Description
    """



    def __init__(self, cli, address, arena, timeout=5):
        ProtectedLoop.__init__(self)
        self.client = cli
        self.address = address
        self.arena = arena
        self.timeout = timeout
        self.lastRecvTime = time.time()

    def prot_loop_startup(self):
        """Summary
        """
        # print('Client Thread #%s started: TCP Server Loop' % self.ident)
        pass

    def prot_loop_run(self):
        """Summary

        """
        size = 1024
        try:
            data = self.client.recv(size)
            if data:
                self.lastRecvTime = time.time()
                # print(data)
                msg = 0
                for ind in range(1, len(data)):
                    msg += np.uint32(data[ind]<<((ind-1)*8))
                robotMessageTuple = (int(data[0]), msg)
                                     # (np.uint32(data[1]) +
                                     #  np.uint32(data[2]<<(1*8)) +
                                     #  np.uint32(data[3]<<(2*8)) +
                                     #  np.uint32(data[4]<<(3*8))))
                self.arena.logL.write("***********Robot Message Tuple" + str(robotMessageTuple)+'\n')
            else:
                raise Exception('Client disconnected')
        except Exception as err:
            raise err
            # print(err  "  was an unexpected error in client_handler")

        time.sleep(.1)
        try:
            with self.arena.lock:
                self.arena.handle_event(robotMessageTuple, self.address[0])

        except RobotNotActiveError:
            pass
        except Exception as e:
            print(e, e.args, "  was an unexpected error in client_handler")

    def prot_loop_shutdown(self):
        """Summary
        """
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except OSError:
            self.client.shutdown()
        self.client.close()
        # print("Closing the TCP Client on thread ", self.ident)

    def run(self):
        """Summary
        """
        self.prot_loop_startup()

        try:
            while (not self.shutdownFlag.is_set()) and (time.time() < self.lastRecvTime+self.timeout):
                # ... Job code here ...

                # time.sleep(.5)
                # print(self.lastRecvTime+self.timeout)
                # print(time.time())
                # print (time.time() < self.lastRecvTime+self.timeout)
                if not self.holdFlag.is_set():
                    self.prot_loop_run()
                else:
                    time.sleep(.1)
        except Exception as err:
            pass #print(err)
        finally:
            self.prot_loop_shutdown()

    def listen_to_client(self, client, address):
        #This method should not exist for this child of the parent
        raise NameError

class UDPBroadcastLoop(ProtectedLoop):
    def __init__(self, arena, port=5555, delay=1):

        ProtectedLoop.__init__(self)
        self.delay = delay

        self.port = port
        self.arena = arena

        # Get the current host and IP address
        self.ipAddress = get_host_name_IP()[1]

        # Create UDPserver for syncing
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udpServer.settimeout(1)
        self.udpServer.bind((self.ipAddress, port)) # (Removed - 11 Nov 2019 - Aslamah)
        #self.udpServer.bind(("", port)) # (Added - 11 Nov 2019 - Aslamah)

        self.listenOnly = 0
        self.lastSend = time.time()

    def prot_loop_startup(self):
        """Summary
        """
        print('Thread #%s started: UDP broadcast loop' % self.ident)

    def prot_loop_run(self):
        """Summary
        """

        # print("Update message sending: %s" % self.ident)

        # time.sleep(self.delay)
        # print('Thread #%s sending UDP broadcast' % self.ident)
        if time.time() > (self.lastSend + self.delay):
            self.lastSend = time.time()
            #DEBUG print(self.lastSend)
            with self.arena.lock:
                self.arena.update()
                if not self.listenOnly:
                    self.udpServer.sendto(self.arena.get_message(), ('<broadcast>', self.port))
                    # self.arena.logL.write(datetime.now().strftime("%H:%M:%S:%f")+"\n")
        else:
            time.sleep(.01)

    def prot_loop_shutdown(self):
        """Summary
        """
        # ... Clean shutdown code here ...
        self.udpServer.close()
        print('Thread #%s stopped: UDP broadcast loop' % self.ident)

# (Added - 11 Nov 2019 - Aslamah)
class UDPReceiverLoop(ProtectedLoop):
    def __init__(self, arena, port=10000, delay=0.001):
        ProtectedLoop.__init__(self)

        self.delay = delay
        self.port = port
        self.arena = arena
        self.lastRecvTime = time.time()

        # Get the current host and IP address
        self.ipAddress = get_host_name_IP()[1]
        self.bufferSize = 1024

        # Create UDPserver for syncing
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udpServer.bind((self.ipAddress, port))
        #Prevent the socket from blocking until it receives all the data it wants
        #Note: Instead of blocking, it will throw a socket.error exception if it
        #doesn't get any data
        self.udpServer.setblocking(0)

    def prot_loop_startup(self):
        """Summary
        """
        print('Thread #%s started: UDP receive loop' % self.ident)

    def prot_loop_run(self):
        """Summary
        """
        try:
            data, address = self.udpServer.recvfrom(self.bufferSize)
            with self.arena.lock:
                self.arena.receive_tophat_message(data, address[0])

        except socket.error:
            pass

        time.sleep(self.delay)

    def prot_loop_shutdown(self):
        """Summary
        """
        # ... Clean shutdown code here ...
        self.udpServer.close()
        print('Thread #%s stopped: UDP receiver loop' % self.ident)



class SyncServer(ThreadedTCPServer):
    def __init__(self, host, arena, port=3333, timeout=5, delay=1):
        """Summary

        Args:
            host (TYPE): Description
            port (TYPE): Description
        """

        ThreadedTCPServer.__init__(self, host, port)

        self.arena = arena
        self.timeout = timeout
        self.sock.settimeout(1)

        self.expectedIDs = []
        for rob in (self.arena.robots + self.arena.nexuses):
            self.expectedIDs.append(rob.ID)
        print(self.expectedIDs)
        self.missingIDs = self.expectedIDs.copy()
        self.noResponseCount = [0] * len(self.missingIDs)



        # Get the current host and IP address
        self.ip = get_host_name_IP()[1]

        # Create UDPserver for syncing
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udpServer.settimeout(1)
        self.udpServer.bind((self.ip, self.port))
        #Initialize sync byte
        self.syncCounter = 0
        self.holdSync = 0
        self.listenOnly = 0
        self.arena.forceSync = 0
        self.logL = LogLoop('syncLog.txt')

    def prot_loop_startup(self):
        """Summary
        """
        self.sock.listen(50)
        print('Thread #%s started: TCP Sync Server' % self.ident)


    def listen(self):

        try:
            # print("sync listening here")
            conn, addr = self.sock.accept()
            # print("Getting IO: ", addr)
        except IOError:
            return 0
        except Exception as err:
            print("Unexpected Server Exception: ", err, err.args)
            return 0
        conn.settimeout(1)

        # threading.Thread(target=self.listen_to_client, args=(conn, addr)).start()


        if self.holdSync:
            self.logL.write("Resync Requested: Restarting Sync Subsystem\n")
            self.arena.sync = 0
            self.holdSync = 0
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        else:
            with conn:
                self.logL.write('\t \t Connected by ' + addr[0] + "\n")
                try:
                    data = conn.recv(1024)
                except Exception as err:
                    data = 0
                    self.logL.write(str(data) + "\t")
                    self.logL.write(str(err)+"\n")
                if data:
                    robNumber = data[0]
                    try:
                        countCheck = data[1]
                    except IndexError:
                        countCheck = 255
                    # self.logL.write(countCheck)
                    # self.logL.write(robNumber)
                    self.logL.write("syncCounter: %d and countCheck: %d \n" %( (1 + self.syncCounter%200), countCheck ))
                    if (1 + self.syncCounter%200) == countCheck:
                        self.logL.write("Reply received from robot # %d \n"% robNumber)
                        try:
                            ind = self.expectedIDs.index(robNumber)
                            self.missingIDs.remove(robNumber)
                            (self.arena.robots + self.arena.nexuses)[ind].IP = addr[0]

                            if not self.missingIDs:
                                raise RobotListEmptyError
                        except ValueError:
                            self.logL.write("INTRUDER ALERT: %d does not belong \n" % robNumber)
                else:
                    self.logL.write("No data in Sync which is weird \n")

        # We expect two different use cases, we are sending sync messages out and listening or we are not and we are listening

    def run(self):
        """Summary
        """
        self.prot_loop_startup()
        try:
            while not self.shutdownFlag.is_set():
                try:    # ... Job code here ...
                    while not self.holdSync and not self.shutdownFlag.is_set():

                        self.missingIDs = self.expectedIDs.copy()

                        self.syncCounter = self.syncCounter + 1
                        if not self.listenOnly:
                            # Broadcast the sync byte to the port
                            self.udpServer.sendto(struct.pack('B', 1 + self.syncCounter%200), ('<broadcast>', self.port))
                            # self.udpServer.sendto(struct.pack('B', self.syncCounter%256), ('10.103.214.135', self.port))
                            # self.udpServer.sendto(struct.pack('B', self.syncCounter%256), ('192.168.1.107', self.port))


                            self.logL.write("%d message sent!" % self.syncCounter +'\n')

                        timeout = time.time() + self.timeout

                        while time.time() <= timeout:
                            self.listen()
                        if self.arena.forceSync == 1:
                            self.logL.write("*******Forcing Sync**********\n")
                            self.arena.forceSync = 0
                            raise RobotListEmptyError
                    self.listen()
                    time.sleep(.1)
                except RobotListEmptyError:
                    self.arena.sync = 1
                    self.holdSync = 1
                    self.logL.write("WE DID IT!!! "+ str(datetime.now())+ "\n")
        finally:
            self.prot_loop_shutdown()



class LogLoop(ProtectedLoop):

    def __init__(self, filename):
        """Summary

        Args:
            host (TYPE): Description
            port (TYPE): Description
        """
        ProtectedLoop.__init__(self)
        self.filename = filename
        self.lines = []
        self.fh = 0
    def prot_loop_startup(self):
        """Summary
        """

        print('Log File Thread #%s started: ' % self.ident  + self.filename)
        try:
            self.fh = open(self.filename, 'w')
        except IOError:
            self.fh = open(self.filename, 'w+')
        self.fh.close()


    def prot_loop_run(self):
        """Summary
        """
        time.sleep(1)
        while not self.fh.closed:
            time.sleep(.1)
        try:
            if self.lines:
                with open(self.filename, 'a') as self.fh:
                    for ind, line in enumerate(self.lines):
                        self.fh.write(str(self.lines.pop(0)))
        except PermissionError as e:
            print(e, " trying again")

    def prot_loop_shutdown(self):
        """Summary
        """
        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)



    def write(self, line):
        """Summary

        Args:
            line (TYPE): Description
        """
        self.lines.append(line)
