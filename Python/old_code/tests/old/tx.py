# this is a args based tx and log creator
# based upon simple_tx.py

import zmq
import pmt
import numpy as np
import time
from datetime import datetime
from itertools import product

# ASCII CAPITAL LETTER RANGE: 65(0x41) - 90(0x5A)
ASCII = [chr(i) for i in range(0x41, 0x5A+1)]
ascii_index = 0 # index for the ascii list

# grab the arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--msg", help="message to send", type=str, default="")
parser.add_argument("--snr", help="snr to send", type=float, default=30)
parser.add_argument("--freq_offset", help="frequency offset to send", type=float, default=0)
parser.add_argument("--noise", help="noise to send", type=float, default=0)
parser.add_argument("--encoding", help="encoding to send", type=int, default=0)
parser.add_argument("--rate", help="rate to send packets (Hz, fractions availible)", type=float, default=0.5)
parser.add_argument("--num_packets", help="number of packets to send", type=int, default=50)

args = parser.parse_args()
# print(args)


