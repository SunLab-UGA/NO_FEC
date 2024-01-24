# this is a module for logging what is transmitted into the channel
# it monitors two zmq sockets, one for the transmitted symbols and one for the transmitted data

# the data is stored as an custom data type
# the ports are hard coded here for my sanity


import zmq
import pmt
import numpy as np
from datetime import datetime
from frameData import FrameData
from util import decode_PMT

#===================================================================================================
zmq_ports = [60000,60002]
zmq_names = ['TX_Symbols', 'TX_Data']
zmq_types = [np.uint8, 'PMT'] # the type of data in the port, 'PMT' means it's a polymorphic message type
default_ip = '127.0.0.1' # localhost

#===================================================================================================
class TX_Logger:
    def __init__(self, ip_addr, ports, port_names, port_types, verbose):
        self.verbose = verbose
        self.context = []
        self.sockets = []
        self.names = port_names
        self.types = port_types
        self.ports = ports
        self.ip_addr = ip_addr


        self.data = [] # list of TX_Data objects

        for p in zmq_ports:
            self.context.append(zmq.Context())
            self.sockets.append(self.context[-1].socket(zmq.SUB))
            rc = self.sockets[-1].connect(f"tcp://{ip_addr}:{p}") # connect, not bind, the PUB will bind, only 1 can bind
            self.sockets[-1].setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
            if verbose:
                last_endpoint = self.sockets[-1].getsockopt(zmq.LAST_ENDPOINT)
                print("=== TX_Logger ===")
                print(f"connection status: {rc}")
                print(f"last endpoint: {last_endpoint}")

    #===================================================================================================
    def get_port_names(self):
        '''return the names of the parameters'''
        return self.names
 
    #===================================================================================================
    def get_last_data(self) -> FrameData:
        '''return the last data object'''
        return self.data[-1]

    #===================================================================================================
    def poll_ports(self, vector_limit=1000): # assumes both ports will have new data at the same time!
        '''Poll the ports for data store in a TX_Data object'''
        now = datetime.now() # get the current time
        for socket,type in zip(self.sockets, self.types):
            # check if there is a message on the socket
            if socket.poll(10) != 0:
                if self.verbose:
                    print("new data @ TX Logger")
                
                msg = socket.recv()

                if type == "PMT":
                    # decode the PMT message
                    additional_info, pmt_data = decode_PMT(msg) # from util.py
                else: # assume the message is a numpy type binary buffer
                    # make sure to use correct data type (complex64 or float32); '-1' means read all data in the buffer
                    _data = np.frombuffer(msg, dtype=type, count=-1) 
                    # check if data is a list (can happen with overflows?)
                    if len(_data) > vector_limit:
                        _data = _data[0] #discard the value
                        print('WARNING: DATA DISCARD, over the vector limit!')
            else:
                print(f"WARNING: missed data on {type} port!")
                return False
        if self.verbose:
            print("=== TX_Logger ===")
            print(f"PMT_DATA: {pmt_data}")
            print(f"ADDITIONAL_DATA: {additional_info}")
            print(f"DATA: {_data}")

        # build the TX_Data object
        tx_data = FrameData(symbols=_data, data=pmt_data, time=now)
        # append to the data list
        self.data.append(tx_data)
        return tx_data

    #===================================================================================================
    def close(self):
        '''close all sockets'''
        for s in self.sockets:
            s.close()