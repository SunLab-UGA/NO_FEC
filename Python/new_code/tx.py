# if main to transmit a file line by line (via zmq socket, via gnuradio_companion)
# otherwise can be used as a module to transmit a file line by line

import zmq
import pmt
import time
import argparse


class Transmitter:
    def __init__(self, ip_addr, port, verbose):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        rc = self.socket.bind(f"tcp://{ip_addr}:{port}")

        if verbose:
            print(f"connection status: {rc}")
            print(f"Sending file to {ip_addr}:{port}")

    def send(self, line):
        '''send a line to the zmq socket as a pmt message'''
        # key = pmt.to_pmt('xxxx') # key is arbitrary
        # line = pmt.to_pmt(line)
        # msg = pmt.cons(key, line)
        # msg = pmt.serialize_str(msg)
        # self.socket.send(msg)

        msg = pmt.to_pmt(line)
        msg = pmt.serialize_str(msg)
        self.socket.send(msg) # default message socket

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    # gather args (file name, ip address, port, delay)
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', help='file name to transmit')
    parser.add_argument('ip_addr', help='ip address of receiver')
    parser.add_argument('port', help='port of receiver')
    parser.add_argument('delay', help='delay between lines (in seconds)', default=0)
    parser.add_argument('eof', help='send "eof" to show end of file as a message', default=False)
    parser.add_argument('-v', '--verbose', help='print verbose output', action='store_true') # true if flag present
    args = parser.parse_args()

    # open file
    f = open(args.file_name, 'r')
    lines = f.readlines()
    f.close()

    # set up transmitter
    tx = Transmitter(args.ip_addr, args.port, args.verbose)

    # send each line
    for line in lines:
        tx.send(line)
        time.sleep(float(args.delay))

    # send eof message if specified
    if args.eof == 'True':
        tx.send("eof")

    # close socket
    tx.close()     

    if args.verbose:
        print("File sent")



