# this is meant to run a full (local) simulation of the FEC/NoFEC tx/rx systems

# the tx will send a complament of messages with fixed sizes of payload of data (500 bits) a log file will be created
# the rx will attempt to receive the data and decode it and log the results
# A BER will be calculated from the tx and rx data logs (and compared to the theoretical BER)

# the channel will be a simple AWGN channel with a fixed tx power and noise power for each test

import zmq
import pmt
import numpy as np
import time
from datetime import datetime
from itertools import product
import os

print("Welcome!")
# TRANSMITTER #############################################################
# ASCII CAPITAL LETTER RANGE: 65(0x41) - 90(0x5A)
ASCII = [chr(i) for i in range(0x41, 0x5A+1)]
ascii_index = 0 # index for the ascii list

# TEST PARAMETERS ##############
# create a list of values to send
snr_values = np.arange(30, -15, -5.0) 
freq_offset_values = np.linspace(0, 2e-6, 10)
noise_values = np.linspace(0, 1, 10)
# encoding_values = np.arange(0, 9, 1) # 0-8, not inclusive

zmq_ports_tx = [50010,50000,50001,50002,50003] # list all the ports a connnection should be read
zmq_names = ['MSG','SNR', 'freq_offset', 'noise', 'encoding']
# zmq_rx_type = [np.float32] # list the data types for each port this is a message

PACKETS_PER_TEST = 50
RATE = 0.5 # packets per second (delay = 1/RATE seconds)

contexts_tx = []
sockets_tx = []
for p in zmq_ports_tx:
    contexts_tx.append(zmq.Context())
    sockets_tx.append(contexts_tx[-1].socket(zmq.PUSH))
    rc = sockets_tx[-1].bind(f"tcp://127.0.0.1:{p}")
    last_endpoint = sockets_tx[-1].getsockopt(zmq.LAST_ENDPOINT)

print("ZMQ TX Connections Launched")

def send_value(socket, value): # gnuradio doesn't care about the key, just the value
    # create pmt message and send it
    key = pmt.to_pmt('xxxx')
    value = pmt.to_pmt(value)
    msg = pmt.cons(key, value)
    msg = pmt.serialize_str(msg)
    socket.send(msg)
    return

def tx_message(msg=None):
    '''send a message to the default message socket'''
    global ascii_index
    if msg == None:
        # send a default message
        PDU_LENGTH = 64 # number of bytes in a PDU
        letter = ASCII[ascii_index] # get the next letter
        ascii_index = (ascii_index + 1) % len(ASCII) # increment the index and wrap around
        pdu = "".join(letter for i in range(PDU_LENGTH))
        # create pmt and send
        msg = pmt.to_pmt(pdu)
        msg = pmt.serialize_str(msg)
        sockets_tx[0].send(msg) # default message socket
        #print("sent default message ")
    else:
        # create and send the custom message
        print('ERROR: not implemented yet')
        pass

# RECEIVER #############################################################
zmq_ports = [60000,60002,60004]
zmq_names = ['TX_Symbols', 'TX_Data', 'RX_Data_RX_Symbols']
zmq_rx_type = [np.uint8, "PMT", "PMT"] # list the data types for each zmq rx
log_file_names = ['TX_Symbols', 'TX_Data', 'RX_Data', 'RX_Symbols']

contexts_rx = []
sockets_rx = []
for p in zmq_ports:
    contexts_rx.append(zmq.Context())
    sockets_rx.append(contexts_rx[-1].socket(zmq.SUB))
    sockets_rx[-1].connect(f"tcp://127.0.0.1:{p}") # connect, not bind, the PUB will bind, only 1 can bind
    sockets_rx[-1].setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
    print(f'port subscribed:{p}')

print("ZMQ RX Connections Launched")

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
        np.savetxt(f, data, fmt='%s', delimiter=' ', newline=' ') #string format
        f.write(']\n')


def poll_socket(socket, type=np.float32, vector_limit=1):
    if socket.poll(10) != 0: # check if there is a message on the socket
        msg = socket.recv() # grab the message

        # check if the message is a pmt message
        if type == "PMT":
            msg = pmt.deserialize_str(msg) # deserialize the message
            msg = pmt.to_python(msg) # convert the message to a python object
            return msg
        else: # assume the message is a numpy type binary buffer
            # make sure to use correct data type (complex64 or float32); '-1' means read all data in the buffer
            data = np.frombuffer(msg, dtype=type, count=-1) 
        
            # check if data is a list (can happen with overflows?)
            if len(data) > vector_limit:
                data = data[0] #discard the value
                print('WARNING: DATA DISCARD, over the vector limit!')
            return data
    else:
        print("WARNING: no data on socket!")
        return [0]
    
def check_if_empty(data):
    if len(data) == 1 and data[0] == 0:
        return True
    else:
        return False
    
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

# RECEIVER ############################################################# RECEIVER END

# TESTING #############################################################
print("====== Starting Test ======")

def write_test_info(file_name, test_info:dict):
    '''write the test info to the file'''
    with open(file_name, 'a') as f:
        for key, value in test_info.items():
            f.write(f"{key}: {value}\n")

def make_log_files():
    '''make the log files for each subscriber'''
    # get the current time and create a file for each subscriber
    date = datetime.now().strftime('+%y-%m-%d_%H_%M_%S')
    file_names = []
    for suffix in log_file_names:
        file_names.append(f"results/log_{date}/{suffix}_{date}.txt")
    params_file_name = f"results/log_{date}/params_{date}.txt"
    os.makedirs(f"results/log_{date}")
    return file_names, params_file_name

# main loop ##################################
iter_len = len(snr_values)*len(freq_offset_values)*len(noise_values)
for i,(snr, freq_offset, noise) in enumerate(product(snr_values, freq_offset_values, noise_values)):
    print(f'snr:{snr:.2f}, freq_offset:{freq_offset*10e5:.2f}e-6, noise:{noise:.2f} ({i}of{iter_len})')

    # send the test info to the tx
    send_value(sockets_tx[1], snr)
    send_value(sockets_tx[2], freq_offset)
    send_value(sockets_tx[3], noise)

    # create the log files
    file_names, params_file_name = make_log_files()

    # Prepare the test info
    test_params = {
        'PACKETS_PER_TEST': PACKETS_PER_TEST,
        'RATE': RATE,
        'snr': snr,
        'freq_offset': freq_offset,
        'noise': noise,
        # 'encoding_values': encoding_values,
    }
    # write the test info to the log file
    write_test_info(params_file_name, test_params)  


    # test loop ##################################
    for ii in range(PACKETS_PER_TEST):

        # send a message to the tx
        tx_message()

        # dwell for a bit for the tx/rx to process the message
        time.sleep(0.25)

        # poll the sockets for data
        data = []
        for socket, name, type in zip(sockets_rx, zmq_names, zmq_rx_type):
            data = poll_socket(socket, type=type, vector_limit=3696)
            if name == 'TX_Symbols':
                write_log(data=data, log_file=file_names[0])
            if name == 'TX_Data': # only take the data from the TX_Data port
                additional_info, data = decode_PMT(data)
                write_log(data=data, log_file=file_names[1])
            if name == 'RX_Data_RX_Symbols':
                additional_info, data = decode_PMT(data)
                symbols = additional_info['symbols'] # get the symbols from the additional info
                write_log(data=data, log_file=file_names[2])
                write_log(data=symbols, log_file=file_names[3])

    # end test loop ##################################

    # calculate the BER
    

    



