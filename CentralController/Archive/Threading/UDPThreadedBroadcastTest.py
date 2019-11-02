import RoBAThreading
import RoBAArena
import time

if __name__ == '__main__':
    arenaState = RoBAArena.Arena('networkTest.csv', 1, 2)
    try:
        udpLoop = RoBAThreading.UDP_broadcast_loop(arenaState)
        udpLoop2 = RoBAThreading.UDP_broadcast_loop(arenaState, port=5556)
        udpLoop.start()
        udpLoop2.start()
        # Keep the main thread running, otherwise signals are ignored.
        while True:
            time.sleep(5)
            udpLoop2.holdFlag.set()
            print('hold flag set')
    finally:
        udpLoop.shutdownFlag.set()
        udpLoop2.shutdownFlag.set()
        udpLoop.join()
        udpLoop2.join()
