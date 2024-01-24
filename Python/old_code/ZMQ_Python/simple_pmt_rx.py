import zmq
import numpy as np
import time
from datetime import datetime
import os
import pmt


zmq_port = 60004
zmq_name = 'RX_Data'


context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(f"tcp://127.0.0.1:{zmq_port}")
socket.setsockopt(zmq.SUBSCRIBE, b'') 

print("Welcome!")

def poll_socket(socket):
    if socket.poll(10) != 0: # check if there is a message on the socket
        msg = socket.recv() # grab the message
        print("Buffer Length: ",len(msg)) # size of msg
        print()


        msg = pmt.deserialize_str(msg)
        print("MSG: ",msg)
        print("PMT: ",pmt.to_python(msg))

        print()
        # show the message types
        print(f"msg type: {type(msg)}")
        print(f"pmt type: {type(pmt.to_python(msg))}")

        # print the tuple length
        print(f"tuple length: {len(pmt.to_python(msg))}")
        
        # NOTE in general the last tuple will be bulk data, and the first will be additionally packed info
        # print the value of the last tuple
        print(f"last tuple value: {pmt.to_python(msg)[-1]}")
        # print the type of the value of last tuple
        print(f"last tuple value type: {type(pmt.to_python(msg)[-1])}") # this should be a numpy array (can make checks upon this fact)


        # get the len of the first tuple tuple
        print(f"first tuple length: {len(pmt.to_python(msg)[0])}")
        # get the type of the first tuple
        print(f"first tuple type: {type(pmt.to_python(msg)[0])}") # if there is additional info, this will be a dict (can make checks upon this fact)

        # assume the first tuple is a dict (for now)
        # print the keys of the dict
        print(f"first tuple keys: {pmt.to_python(msg)[0].keys()}")

while True:
    poll_socket(socket)
    time.sleep(0.1)
