# similar to tx_logger.py but it only has one port where the data comes in as one PMT message
# it monitors one zmq socket for the rx data, parses it, and stores it in a list of FrameData objects

# the data is stored as an custom data type
# the ports are hard coded here for my sanity

import zmq
import pmt
import numpy as np
from datetime import datetime
from frameData import FrameData
from util import decode_PMT

default_port = 60004

class RX_Logger:
    def __init__(self, ip_addr, port, verbose):
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        rc = self.socket.connect(f"tcp://{ip_addr}:{port}") # connect, not bind, the PUB will bind, only 1 can bind
        self.socket.setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
        if self.verbose:
            last_endpoint = self.socket.getsockopt(zmq.LAST_ENDPOINT)
            print("=== RX_Logger ===")
            print(f"connection status: {rc}")
            print(f"last endpoint: {last_endpoint}")

        self.data = [] # list of FrameData objects

    #===================================================================================================

    def get_last_data(self) -> FrameData:
        '''return the last data object'''
        return self.data[-1]
    
    #===================================================================================================
    def poll(self):
        '''poll the zmq socket for new data, and store it in the data list'''
        if self.socket.poll(10) != 0:
            if self.verbose:
                print("new data @ RX Logger")
            rx_data = self.socket.recv()
            # decode the data
            additional_info, docode_data = decode_PMT(rx_data) # from util.py
            # create the data object
            frame_data = FrameData(additional_info['symbols'], docode_data, datetime.now())
            # store the data object
            self.data.append(frame_data)
            if self.verbose:
                print(f"RX: {frame_data}")

    #===================================================================================================
    def close(self):
        '''close all sockets'''
        self.socket.close()
