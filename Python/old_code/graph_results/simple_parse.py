# open the files in results folder, load into numpy arrays, align the time stamps
# note dropped frames. (count) remove them from the data.
# check each tx/rx pair for data integrity

import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# get the current working directory
cwd = os.getcwd()
print(f"cwd: {cwd}")

# get the results directory up one level, then add the results folder
# results_dir = os.path.join(os.path.dirname(cwd), 'results')

# get the results directory
results_dir = os.path.join(cwd, 'results')

# get the newest directory in the results folder
newest_dir = max([os.path.join(results_dir, d) for d in os.listdir(results_dir)], key=os.path.getmtime)
print(f"newest_dir: {newest_dir}")

def parse_line(line, type=np.uint8):
    '''parse a line with the format [time] [data]'''
    # split the line into a list
    line = line.split('] [')
    # remove the brackets from the first and last element
    line[0] = line[0][1:]
    line[-1] = line[-1][:-1]
    # convert the time to a datetime object
    line[0] = datetime.strptime(line[0], '+%y-%m-%d_%H_%M_%S.%f')
    # convert the data to a numpy array
    line[1] = np.fromstring(line[1], dtype=type, sep=' ')
    return line[0], line[1] # time, data

# start with loading the file with prefix 'RX_Data'
rx_data_file = [f for f in os.listdir(newest_dir) if f.startswith('RX_Data')][0]
# load the file 
with open(os.path.join(newest_dir, rx_data_file), 'r') as f:
    rx_data = f.readlines()
# parse the data into lists
rx_data = [parse_line(line) for line in rx_data]
# destack the data
rx_data_time, rx_data = zip(*rx_data)

# print the len of the data
print(f"rx_data len: {len(rx_data)}")
print(f"rx_data_time: {(rx_data_time)}")
print(f"rx_data: {rx_data}")


