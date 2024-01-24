#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zmq
import numpy as np
import time
from datetime import datetime
import os
import pmt

# if a log file should be saved
SAVE_FILE = False
HEX_FORMAT = False # also save the data in hex format

zmq_ports = [60000,60002,60004] # list all the connected ports (60004 has both data and symbols)
zmq_names = ['TX_Symbols', 'TX_Data', 'RX_Data_RX_Symbols']
zmq_rx_type = [np.uint8, "PMT", "PMT"] # list the data types for each zmq rx

log_file_names = ['TX_Symbols', 'TX_Data', 'RX_Data', 'RX_Symbols']

# general pmt format is tuple=>(dict, np.array), where the dict is additional info, and the np.array is the data
# the dict is optional, and the np.array can be any data type (int, float, complex, etc.)
# the dict can be used to store additional info, such as the sample rate, frequency, etc.

# for now we hard code the items we'd like to store in a log file (based on the zmq_names)

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
    for suffix in log_file_names:
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

        # check if the data is already a np.array, if not convert it
        if type(data) != np.ndarray:
            data = np.array([data])
        # write data using np.savetxt
        # print(f'data shape: {data.shape}')
        # print(f'data type: {data.dtype}')
        # print(f'data: {data}')

        np.savetxt(f, data, fmt='%s', delimiter=' ', newline=' ') #string format
        if HEX_FORMAT == True:
            f.write('] [')
            np.savetxt(f, data, fmt='%02X', delimiter=' ', newline=' ') #hex format
        f.write(']\n')

def poll_socket(socket, type=np.float32, vector_limit=1):
    if socket.poll(10) != 0: # check if there is a message on the socket
        msg = socket.recv() # grab the message
        print("Buffer Length: ",len(msg)) # size of msg
        print()

        # check if the message is a pmt message
        if type == "PMT":
            msg = pmt.deserialize_str(msg) # deserialize the message
            msg = pmt.to_python(msg) # convert the message to a python object
            return msg, True # data, valid
        else: # assume the message is a numpy type binary buffer
            # make sure to use correct data type (complex64 or float32); '-1' means read all data in the buffer
            data = np.frombuffer(msg, dtype=type, count=-1) 
        
            # check if data is a list (can happen with overflows?)
            if len(data) > vector_limit:
                data = data[0] #discard the value
                print('WARNING: DATA DISCARD, over the vector limit!')
            return data, True # data, valid
    else:
        return [0], False # no data, invalid
    
def decode_data(data):
    '''This function will decode the data into hex format'''
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

def decode_PMT(data):
    '''Decode the data tuple from the port as a PMT message
    data should be a tuple of (dict, np.array)'''

    # check if the data is 'empty', if so return 0
    if check_if_empty(data) == True:
        return 0
    
    # check if the the data is a tuple
    if type(data) != tuple:
        print("ERROR: data is not a tuple!")
        return 0
    
    # check if the tuple has 2 items, and if the first item is a dict, and the second is a np.array
    if len(data) != 2 or type(data[0]) != dict or type(data[1]) != np.ndarray:
        print("ERROR: data tuple is not the correct format!")
        return 0

    additional_info = data[0] # dict
    data = data[1] # np.array

    return additional_info, data


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
            # check the name of the port for how to decode the data for logging
            if zmq_names[ii] == 'RX_Data_RX_Symbols':
                # decode the data
                additional_info, data = decode_PMT(data)
                # get the symbols from the additional info
                symbols = additional_info['symbols']
                
                # write appropriate data to log files
                if SAVE_FILE == True:
                    # append the data to a file for post-processing
                    write_log(data=data,log_file=file_names[2]) # data log
                    write_log(data=symbols,log_file=file_names[3]) # symbol log
            if zmq_names[ii] == 'TX_Data':
                # decode the data
                additional_info, data = decode_PMT(data)
                
                # write appropriate data to log files
                if SAVE_FILE == True:
                    # append the data to a file for post-processing
                    write_log(data=data,log_file=file_names[1])

            if zmq_names[ii] == 'TX_Symbols':

                # write appropriate data to log files
                if SAVE_FILE == True:
                    # append the data to a file for post-processing
                    write_log(data=data,log_file=file_names[0])


        else:
            time.sleep(0.1) # wait 100ms and try again