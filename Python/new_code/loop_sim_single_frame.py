# this is the main file for the loopback simulation

from tx import Transmitter
from rx_logger import RX_Logger
from tx_logger import TX_Logger
from channel_parameters import Channel_Parameters
from frameData import FrameData
from datetime import datetime
import numpy as np
import os
import subprocess
import time

print("=== Starting Loopback Simulation ===")

# run wifi_loopback.py to start the simulation as a subprocess
# gnuradio_process = subprocess.Popen(['python3', 'wifi_loopback.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# wait for the simulation to start
# print("waiting 2 seconds for simulation to start...")
# time.sleep(2)

#====================================================================================
localhost = '127.0.0.1'

# instantiate the objects
rxLog = RX_Logger(localhost, 60004, verbose=False)
txLog = TX_Logger(localhost, [60000,60002], ['TX_Symbols', 'TX_Data'], [np.uint8, 'PMT'], verbose=False)
channel = Channel_Parameters(localhost, [50000, 50001, 50002, 50003], ['SNR', 'freq_offset', 'noise', 'encoding'], False)
tx = Transmitter(localhost, 50010, False)

print("=== Connected ===")
#====================================================================================
channel_params = {'SNR':30, 'freq_offset':0, 'noise':0, 'encoding':0}
for c in channel_params:
    print(f"Sending {c} = {channel_params[c]}")
    channel.send(channel_params[c], c)
time.sleep(1)

#====================================================================================
# test sending a frame of data
for z in range(5):
    print("=== Sending Test Frame ===")
    tx.send('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

    time.sleep(0.5)
    print("=== Test Frame Sent ===")
#====================================================================================
print("=== Polling for Test Frame ===")
# simple poll until the data is received
while len(rxLog.data) == 0:
    rxLog.poll()
    time.sleep(0.1)
print("=== RX Test Frame Received ===")
while len(txLog.data) == 0:
    txLog.poll_ports()
    time.sleep(0.1)
print("=== TX Test Frame Received ===")

#====================================================================================
# show how many frames were tx and rx
print(f"TX frames: {len(txLog.data)}")
print(f"RX frames: {len(rxLog.data)}")

# get data from the loggers to print
tx_data = txLog.get_last_data()
rx_data = rxLog.get_last_data()

# print(f"TX data: {tx_data}")
# print the parts of tx_data
print(f"TX symbols: {tx_data.symbols}")
print(f"TX data: {tx_data.data}")
print(f"TX time: {tx_data.time}")
print()
# print(f"RX data: {rx_data}")
# print the parts of rx_data
print(f"RX symbols: {rx_data.symbols}")
print(f"RX data: {rx_data.data}")
print(f"RX time: {rx_data.time}")
print()

#print the length of the symbols and data (convert to bits from bytes)
print(f"TX symbols length: {len(tx_data.symbols)}")
print(f"TX data length: {len(tx_data.data)*8} bits")
print(f"RX symbols length: {len(rx_data.symbols)}")
print(f"RX data length: {len(rx_data.data)*8} bits")

# find the time difference between the two
time_diff = tx_data - rx_data # 
print(f"time difference: {time_diff}")

# calculate the BER (bit error rate)
ber = tx_data.BER(rx_data)
print(f"BER: {ber}")
# calculate the SER (symbol error rate)
ser = tx_data.SER(rx_data)
print(f"SER: {ser}")

#close the sockets
rxLog.close()
txLog.close()
channel.close()
tx.close()

print(f"mini-test complete!")