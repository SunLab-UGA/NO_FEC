import pmt
import numpy as np

def check_if_empty(data):
    if len(data) == 1 and data[0] == 0:
        return True
    else:
        return False
    
def decode_PMT(data) -> tuple:
    '''Decode the data tuple from a PMT message
        data should be a tuple of (dict, np.array)'''

    data = pmt.deserialize_str(data) # deserialize the data
    data = pmt.to_python(data) # convert the data to a python object

    # check if the data is 'empty', if so raise a warning and return 0
    if check_if_empty(data) == True:
        print("WARNING: empty data packet recieved!")
        return ([],[]) # return empty lists

    # check if the the data is a tuple
    if type(data) != tuple:
        print("ERROR: data is not a tuple!")
        return ([],[]) # return empty lists
    
    # check if the tuple has 2 items, and if the first item is a dict, and the second is a np.array
    if len(data) != 2 or type(data[0]) != dict or type(data[1]) != np.ndarray:
        print("ERROR: data tuple is not the correct format!")
        return ([],[]) # return empty lists

    additional_info = data[0] # dict
    data = data[1] # np.array

    return additional_info, data