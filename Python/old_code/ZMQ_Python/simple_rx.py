#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zmq
import numpy as np
import time
from datetime import datetime
import os
import pmt

SAVE_FILE = True

zmq_ports = [60000,60002,60004] # list all the connected ports (60004 has both data and symbols)
zmq_decode_pmt = [False, False, True] # list if the data ports which should be decoded using pmt
zmq_names = ['TX_Symbols', 'TX_Data', 'RX_Data', 'RX_Symbols']
# zmq_rx_type = [np.uint8,np.uint8, np.uint8, np.uint8] # list the data types for each zmq rx
zmq_rx_type = [np.uint8, "PMT", "PMT"] # list the data types for each zmq rx

contexts = []
sockets = []
for p in zmq_ports:
    contexts.append(zmq.Context())
    sockets.append(contexts[-1].socket(zmq.SUB))
    sockets[-1].connect(f"tcp://127.0.0.1:{p}") # connect, not bind, the PUB will bind, only 1 can bind
    sockets[-1].setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
    print(f'port subscribed:{p}')

print("Welcome!")

if SAVE_FILE == True:
    # get the current time and create a file for each subscriber
    date = datetime.now().strftime('+%y-%m-%d_%H_%M_%S')
    file_names = []
    for suffix in zmq_names:
        file_names.append(f"results/log_{date}/{suffix}_{date}.txt")

    #make dir if it doesn't exist
    os.makedirs(f"results/log_{date}") 

    print(file_names)

# take data and write to log file
def write_log(data, log_file):
    date_format = '+%y-%m-%d_%H_%M_%S.%f'
    # write data to log file
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now().strftime(date_format)}]") # write time
        f.write(' [')
        #f.write(data) # this method will shorten the data if it is too long
        # write data using np.savetxt
        np.savetxt(f, np.array([data]), fmt='%s', delimiter=' ', newline='') #string format
        f.write('] [')
        np.savetxt(f, np.array([data]), fmt='%02X', delimiter=' ', newline='') #hex format
        f.write(']\n')

def poll_socket(socket, type=np.float32, vector_limit=1):
    if socket.poll(10) != 0: # check if there is a message on the socket
        msg = socket.recv() # grab the message
        print("Buffer Length: ",len(msg)) # size of msg
        print()

        # check if the message is a pmt message
        if type == "PMT":
            msg = pmt.deserialize_str(msg)
            # print("PMT: ",msg)
            # print("PMT: ",pmt.to_python(msg))
            print()
            return msg, True # data, valid
        else:
            # make sure to use correct data type (complex64 or float32); '-1' means read all data in the buffer
            data = np.frombuffer(msg, dtype=type, count=-1) 
            print(data) # the vector length is 52 channels for 802.11a ofdm
        
            # check if data is a list (can happen with overflows?)
            if len(data) > vector_limit:
                data = data[0] #discard the value
                print('WARNING: DATA DISCARD, over the vector limit!')
            return data, True # data, valid
    else:
        return [0], False # no data, invalid
    
def decode_data(data):
    if check_if_empty(data) == True: # if the data is 'empty', then return 0
        return 0
    # group and decode the integer symbols (bits) back into bytes
    # this will help show the data in a more readable format
    # data is a list of integers (bpsk for now)
    data_bytes = []
    # group the data into bytes, if not a multiple of 8, then discard the last few bits and warn the user
    if len(data)%8 != 0:
        print("WARNING: DATA DISCARD, data length is not a multiple of 8!?")
        data = data[0:len(data)-len(data)%8]
    for ii in range(int(len(data)/8)):
        data_bytes.append(data[ii*8:(ii+1)*8])

    # decode the data into hex
    decoded_data = []
    for byte in data_bytes:
        decoded_data.append(hex(int(''.join(str(x) for x in byte),2)))

    return decoded_data

def check_if_empty(data):
    if len(data) == 1 and data[0] == 0:
        return True
    else:
        return False

while True:
    for ii,port in enumerate(sockets):
        # make sure the datatype is valid for the port!
        data,data_valid = poll_socket(socket=port, type=zmq_rx_type[ii], vector_limit=3696)

        if data_valid == True:
            if SAVE_FILE == True:
                # append the data to a file for post-processing
                # write_log(data=str(data).replace("\n",""),log_file=file_names[ii])
                write_log(data=data,log_file=file_names[ii]) # give raw data to log file

        # if zmq_decode[ii] == True: # decode the data further
        #     if SAVE_FILE == True:
        #         # append the data to a file for post-processing
        #         decoded_data = decode_data(data)
        #         write_log(data=decoded_data,log_file=file_names[ii])
        
        # convert the data to ascii for better interpretation


        else:
            time.sleep(0.1) # wait 100ms and try again