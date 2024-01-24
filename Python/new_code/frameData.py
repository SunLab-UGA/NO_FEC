# Purpose: data type container for the transmitted or recieved data


from datetime import datetime, timedelta
from typing import NamedTuple
import numpy as np
from constants import MAC_FRAME_FIELDS, FRAME_CONTROL_FIELDS, SEQUENCE_CONTROL_FIELDS



class FrameData(NamedTuple):
    '''data type container for the transmitted data'''
    symbols: np.array
    data: np.array
    time: datetime

    def __repr__(self):
        return f"TX_Data(symbols={self.symbols}, data={self.data}, time={self.time})"
    
    def __str__(self):
        return f"TX_Data(symbols={self.symbols}, data={self.data}, time={self.time})"
    
    def __sub__(self, other:'FrameData') -> timedelta: 
        '''subtract two FrameData objects, and return the difference in time'''
        # check if the other object is a FrameData object
        if not isinstance(other, FrameData):
            raise TypeError(f"unsupported operand type(s) for -: 'FrameData' and '{type(other)}'")
        
        return self.time - other.time # this will return a datetime.timedelta object
    
    def __eq__(self, other:'FrameData') -> bool:
        '''compare two FrameData objects, and return True if they are the same
        **INGORES TIME**'''
        # check if the other object is a FrameData object
        if not isinstance(other, FrameData):
            raise TypeError(f"unsupported operand type(s) for ==: 'FrameData' and '{type(other)}'")
        # check if the symbols are the same
        if self.symbols != other.symbols:
            return False
        # check if the data is the same
        if self.data != other.data:
            return False
        # if all of the above are the same, return true
        return True
    
    def BER(self, other:'FrameData') -> float:
        '''calculate the bit error rate between two FrameData objects'''
        # check if the other object is a FrameData object
        if not isinstance(other, FrameData):
            raise TypeError(f"unsupported operand type(s) for ==: 'FrameData' and '{type(other)}'")
        # check same length
        if len(self.data) != len(other.data):
            raise ValueError(f"unsupported operand, irregeular data lengths to compare")
        # calc the number of errors
        errors = np.sum(np.bitwise_xor(self.data, other.data))
        ber = errors / len(self.data)
        return ber
    
    def SER(self, other:'FrameData') -> float:
        '''calculate the symbol error rate between two FrameData objects'''
        # check if the other object is a FrameData object
        if not isinstance(other, FrameData):
            raise TypeError(f"unsupported operand type(s) for ==: 'FrameData' and '{type(other)}'")
        # check same length
        if len(self.symbols) != len(other.symbols):
            raise ValueError(f"unsupported operand, irregeular data lengths to compare")
        # calc the number of errors
        errors = np.sum(np.bitwise_xor(self.symbols, other.symbols))
        ser = errors / len(self.symbols)
        return ser
    
    def get_sequence_control(self) -> int:
        '''return the sequence number [sequence control field] of the frame
        this would assume the data is not corrupted'''
        # use the MAC_FRAME_FIELDS dictionary to get the sequence control field
        sequence_control = self.data[MAC_FRAME_FIELDS["SequenceControl"][0]:MAC_FRAME_FIELDS["SequenceControl"][1]]
        # get the bits
        sequence_control = np.packbits(sequence_control)
        # split the bits into the two fields, and convert to int
        sequence_number = int(sequence_control[SEQUENCE_CONTROL_FIELDS["SequenceNumber"][0]:SEQUENCE_CONTROL_FIELDS["SequenceNumber"][1]])
        fragment_number = int(sequence_control[SEQUENCE_CONTROL_FIELDS["FragmentNumber"][0]:SEQUENCE_CONTROL_FIELDS["FragmentNumber"][1]])
        return fragment_number, sequence_number
        

    
