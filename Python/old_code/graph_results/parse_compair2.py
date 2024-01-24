# open the files in results folder, load into numpy arrays, align the time stamps
# note dropped frames. (count) remove them from the data.
# check each tx/rx pair for data integrity

import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from datetime import timedelta

# silence the numpy deprecation warnings
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) # didn't work here...
warnings.filterwarnings("ignore") # not great but np is silly

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

# override the directory with a specific (hardcoded) directory
# newest_dir = os.path.join(results_dir, 'log_+23-12-20_20_39_07')

####################################################################################################
def bitwise_error_rate(tx_data, rx_data):
    '''calculate the BER between the tx and rx data'''
    # check if the data is the same length
    if len(tx_data) != len(rx_data):
        print("WARNING: Data is not the same length!?")
        return -1
    
    # calculate the BER
    errors = np.sum(np.bitwise_xor(tx_data, rx_data))
    ber = errors / len(tx_data) # errors / total bits

    return ber, len(tx_data), errors

def find_frame_pairs(tx, rx, max_delta=1.0):
    '''this function pairs the closest rx to tx times, the remaining tx times are dropped frames'''
    max_delta = timedelta(seconds=max_delta)  # Convert max_delta to timedelta object
    # loop through the tx times, find the closest positive rx time, if the delta is less than max_delta then pair them as valid tx/rx
    valid_tx_pairs = []
    tx_index = [] # track the tx index of the valid pairs
    delta_times = []
    search_tx = list(zip(tx[0],tx[1])) # copy the tx data, invert the indexing for element-wise access
    search_rx = list(zip(rx[0],rx[1])) # same for rx
    # automatically pair the first tx/rx because there is exessive delay at the start
    valid_tx_pairs.append([search_tx[0], search_rx[0]]) # [[tx_time, tx_data], [rx_time, rx_data]]
    # print(f'valid_tx_pairs: {valid_tx_pairs}')

    # remove the first tx/rx from the search lists
    search_tx = search_tx[1:]
    search_rx = search_rx[1:]

    # retrieve all remaining tx times
    search_tx_times = [_[0] for _ in search_tx]
    # loop through the tx times
    for ii, tx_time in enumerate(search_tx_times):
        # check if there are any rx times left
        if len(search_rx) == 0:
            break
        # check if the rx time is less than the tx time
        # print(f"time delta: {search_rx[0][0] - tx_time}")
        if search_rx[0][0] < tx_time:
            # remove the rx time from the list
            search_rx = search_rx[1:]
            print("ERROR: RX time is less than TX time!")
            continue
        # check if the rx time is greater than the tx time and less than the max_delta
        if search_rx[0][0] >= tx_time:
            if search_rx[0][0] - tx_time <= max_delta:
                # pair the tx/rx
                valid_tx_pairs.append([search_tx[ii], search_rx[0]]) # [[tx_time, tx_data], [rx_time, rx_data]]
                # track the tx index
                tx_index.append(ii)
                # track the time delta
                delta_times.append(search_rx[0][0] - tx_time)
                # remove the rx time from the search
                search_rx = search_rx[1:]
                # print("paired tx/rx")
                # print(valid_tx_pairs[-1])
            else:
                print(f"--Dropped frame at index {ii} with time delta of {search_rx[0][0] - tx_time} s")

    
    # return the valid tx pairs and delta times
    return valid_tx_pairs, tx_index, delta_times




def load_file(file_name, type=np.uint8):
    '''load a file into a list of lines'''
    with open(file_name, 'r') as f:
        data = f.readlines()
    # parse the data into lists
    data = [parse_line(line, type=type) for line in data]
    # destack the data
    data_time, data = zip(*data)
    return data_time, data

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
    # print(f"line[1]: {line[1]}")
    return [line[0], line[1]] # time, data

# start with loading the file with prefix 'RX_Data'
rx_data_file = [f for f in os.listdir(newest_dir) if f.startswith('RX_Data')][0]
print(f"rx_data_file: {rx_data_file}")
rx_data = load_file(os.path.join(newest_dir, rx_data_file), type=np.uint8)
print(f"rx_data len: {len(rx_data[0])}")

# load the file with prefix 'TX_Data'
tx_data_file = [f for f in os.listdir(newest_dir) if f.startswith('TX_Data')][0]
print(f"tx_data_file: {tx_data_file}")
tx_data = load_file(os.path.join(newest_dir, tx_data_file), type=np.uint8)
# print the len of the data
print(f"tx_data len: {len(tx_data[0])}")

# # print the first frame tx/rx
# print("first frame tx/rx data:")
# print(f"tx_data[1][1]: {tx_data[1][1]}")
# print(f"rx_data[1][1]: {rx_data[1][1]}")

# check if both data sets have the same length or if one is longer
if len(rx_data[0]) == len(tx_data[0]):
    print("Data sets are the same length (no dropped frames)")
elif len(rx_data[0]) > len(tx_data[0]):
    print(f"RX data is longer by {len(rx_data[0]) - len(tx_data[0])} frames!?")
    print("Exiting...")
    exit()
else:
    print(f"TX data is longer by {len(tx_data[0]) - len(rx_data[0])} frames")

# finding valid frames pairs
print()
max_time_delta = 2.25 # seconds
print(f"finding valid frames pairs with max_time_delta of {max_time_delta} s")
valid_tx_rx_pairs, valid_tx_index, delta_times = find_frame_pairs(tx_data, rx_data, max_delta=max_time_delta)
print()

print(f"num valid frames found: {len(valid_tx_rx_pairs)}")
# print delta times, convert to float
delta_times = [delta.total_seconds() for delta in delta_times]
# find the average delta time
avg_delta_time = np.mean(delta_times)
print(f"avg_delta_time: {avg_delta_time} s")

# check first/last valid tx/rx pairs
print("first/last valid tx/rx pairs:")
print(f"valid_tx_pairs[0]: {valid_tx_rx_pairs[0]}")
print(f"valid_tx_pairs[-1]: {valid_tx_rx_pairs[-1]}")

print()
####################################################################################################

# check the first few frames for equal length
print("Performing some sanity checks...")
if len(valid_tx_rx_pairs[0][0][1]) == len(valid_tx_rx_pairs[0][1][1]): # [frame][tx/rx][time/data]
    print("Data frame 0 tx/rx are the same length")

print()

####################################################################################################

print("Proceeding to calculate BER...")
full_bit_errs = 0
full_bit_tot = 0
frame_ber = []
for ii in range(len(valid_tx_rx_pairs)): # [frame][tx/rx][time/data]
    t = valid_tx_rx_pairs[ii][0][1] # tx data
    r = valid_tx_rx_pairs[ii][1][1] # rx data
    # calculate the BER
    ber, bit_tot, bit_err = bitwise_error_rate(t, r) 
    # add to the total
    full_bit_errs += bit_err
    full_bit_tot += bit_tot
    # add frame ber to list
    frame_ber.append(ber)

# calculate the full BER
full_ber = full_bit_errs / full_bit_tot

print(f"full_bit_errs: {full_bit_errs}")
print(f"full_bit_tot: {full_bit_tot}")
print()
print(f"**Bit Error Rate**: {full_ber}")
print()
# get the number of frames with a BER > 0
num_bad_frames = len([f for f in frame_ber if f > 0])
print(f"number of frames with errors: {num_bad_frames}")

# get the index of the frames with a BER > 0
bad_frame_indexes = [i for i,f in enumerate(frame_ber) if f > 0]
print(f"bad_frame_indexes: {bad_frame_indexes}")

# # print the first bad frame data tx/rx
# if len(bad_frame_indexes) > 0:
#     print(f"first bad frame:")
#     print(f"tx_data[{bad_frame_indexes[0]}]: {tx_data[bad_frame_indexes[0]]}")
#     print(f"rx_data[{bad_frame_indexes[0]}]: {rx_data[bad_frame_indexes[0]]}")

# print frame_ber
print("frame_ber: ")
print(frame_ber)
print('tx_index:')
print(valid_tx_index)
# print the index of dropped frames
dropped_frames = [i for i in range(len(tx_data[0])-1) if i not in valid_tx_index]
print(f"dropped_frames: {dropped_frames} of total {len(tx_data[0])} frames")


# plot the frame BER
plt.figure()
plt.plot(frame_ber)
plt.title(f"Bit Error Rate: {full_ber}")
plt.xlabel("Frame Number")
plt.ylabel("BER")
plt.grid()
plt.show()


