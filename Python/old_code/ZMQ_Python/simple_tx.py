# this script connects to a ZMQ server and sends a message and then quits (for now)

import zmq
import pmt
import numpy as np
import time
from datetime import datetime
from itertools import product

# ASCII CAPITAL LETTER RANGE: 65(0x41) - 90(0x5A)
ASCII = [chr(i) for i in range(0x41, 0x5A+1)]
ascii_index = 0 # index for the ascii list



zmq_ports = [50010,50000,50001,50002,50003] # list all the ports a connnection should be read
zmq_names = ['MSG','SNR', 'freq_offset', 'noise', 'encoding']
# zmq_rx_type = [np.float32] # list the data types for each port this is a message

PACKETS_PER_TEST = 50
# RATE = 0.25 # rate of tx in GNU Radio (interval)
RATE = 0.5 # packets per second (delay = 1/RATE seconds)

verbose_connection = False
contexts = []
sockets = []
for p in zmq_ports:
    contexts.append(zmq.Context())
    sockets.append(contexts[-1].socket(zmq.PUSH))
    rc = sockets[-1].bind(f"tcp://127.0.0.1:{p}") # connect, not bind, the PUB will bind, only 1 can bind
    #sockets[-1].setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
    last_endpoint = sockets[-1].getsockopt(zmq.LAST_ENDPOINT)
    if verbose_connection:
        print(f"connection status: {rc}")
        print(f"last endpoint: {last_endpoint}")

print("ZMQ Connections Launched")

def send_value(socket, value): # gnuradio doesn't care about the key, just the value
    # create pmt message and send it
    key = pmt.to_pmt('xxxx')
    value = pmt.to_pmt(value)
    msg = pmt.cons(key, value)
    msg = pmt.serialize_str(msg)
    socket.send(msg)
    return

print("====== Starting Test ======")

# create a list of values to send
snr_values = np.arange(30, -15, -5.0) 
# freq_offset_values = np.linspace(-2e-6, 2e-6, len(snr_values)) # length of snr_values
# freq_offset_values = np.linspace(0, 2e-6, 20)
freq_offset_values = np.linspace(0, 2e-6, 10)
noise_values = np.linspace(0, 1, 10)
encoding_values = np.arange(0, 9, 1) # 0-8, not inclusive

# 

show_values = False
if show_values:
    print(f"snr_values: {snr_values}")
    print(f'snr_values shape: {snr_values.shape}')
    print(f"freq_offset_values: {freq_offset_values}")
    print(f'freq_offset_values shape: {freq_offset_values.shape}')
    print(f"noise_values: {noise_values}")
    print(f'noise_values shape: {noise_values.shape}')
    print(f"encoding_values: {encoding_values}")
    print(f'encoding_values shape: {encoding_values.shape}')

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
        sockets[0].send(msg) # default message socket
        #print("sent default message ")
    else:
        # create and send the custom message
        print('not implemented yet')
        pass

iter_len = len(snr_values)*len(freq_offset_values)*len(noise_values)
print(f"number of iterations: {iter_len}")
# estimate the time to complete
print(f"estimated time to complete: ~{iter_len*RATE*PACKETS_PER_TEST} seconds")

for i,(f,s,n) in enumerate(product(freq_offset_values, snr_values, noise_values)): # iterate through all values
    print(f'snr:{s:.2f}, freq_offset:{f*10e5:.2f}e-6, noise:{n:.2f} ({i}of{iter_len})', end='')
    print("", end='\r') # set to clear the line

    # send_value(sockets[1], s) # send snr
    # send_value(sockets[2], f) # send freq_offset
    # send_value(sockets[3], n) # send noise
    
    time.sleep(0.1) # settle time before sending message
    
    # send a message
    for q in range(PACKETS_PER_TEST):
        tx_message() # None = default message
        time.sleep(1/RATE) # wait an interval before sending the next message
    
print("====== Test Complete ======")