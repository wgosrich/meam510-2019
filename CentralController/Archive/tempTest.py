#testAllieSend
import time
import struct 
import numpy as np

def get_fake_message():
    """Summary

    Returns:
        TYPE: Description
    """
    # For Gui Test
    measTime = time.time()
    infoByte = int(((int(1) << int(4))+ (int(0) << int(3)) + (int((measTime//30)%2)<<int(2)) +   ( int(1)<<int(1)) + int(1)))



    towerByte = (np.uint8((measTime % 200)/14) +
                 (np.uint8(((measTime/2-50)%200)/14)<<4))

    outputString = struct.pack('=BHH9B',
                               np.uint8(infoByte),
                               np.uint16(measTime%1000),
                               np.uint16((2*measTime)%1000),
                               np.uint8((2*measTime)%100),
                               np.uint8((3*measTime)%100),
                               np.uint8((4*measTime)%100),
                               np.uint8((5*measTime)%100),
                               np.uint8((5*measTime)%100),
                               np.uint8((6*measTime)%100),
                               np.uint8((7*measTime)%100),
                               np.uint8((8*measTime)%100),
                               np.uint8(towerByte))
    return outputString

