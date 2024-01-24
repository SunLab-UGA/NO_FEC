# if main arg parse and change the channel parameters
# otherwise implement the channel parameters as a module

# there are multiple channel parameters, each needs its own zmq socket
# they are hard coded here for my sanity

import zmq
import pmt
import argparse

# channel parameters:
zmq_names = ['SNR', 'freq_offset', 'noise', 'encoding']
zmq_ports = [50000, 50001, 50002, 50003]
default_ip = '127.0.0.1' # localhost

class Channel_Parameters:
    def __init__(self, ip_addr, ports, param_names, verbose):
        self.contexts = []
        self.sockets = []
        self.names = param_names
        self.ports = ports
        self.ip_addr = ip_addr

        for p in zmq_ports:
            self.contexts.append(zmq.Context())
            self.sockets.append(self.contexts[-1].socket(zmq.PUSH))
            rc = self.sockets[-1].bind(f"tcp://{ip_addr}:{p}") # connect, not bind, the PUB will bind, only 1 can bind
            #sockets[-1].setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
            if verbose:
                last_endpoint = self.sockets[-1].getsockopt(zmq.LAST_ENDPOINT)
                print(f"connection status: {rc}")
                print(f"last endpoint: {last_endpoint}")

    def get_param_names(self):
        '''return the names of the parameters'''
        return self.names

    def send(self, line, param_name):
        '''send a new parameter to the zmq socket as a pmt message'''
        # find the index of the param name
        idx = self.names.index(param_name)
        # get the socket
        socket = self.sockets[idx]
        # create the message
        key = pmt.to_pmt('xxxx') # key is arbitrary
        line = pmt.to_pmt(line)
        msg = pmt.cons(key, line)
        msg = pmt.serialize_str(msg)
        # send the message
        socket.send(msg)

    def close(self):
        '''close all sockets'''
        for s in self.sockets:
            s.close()

if __name__ == "__main__":
    # gather args (file name, ip address, port, delay)
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', help='ip address of receiver', default=default_ip)
    
    parser.add_argument('SNR', help='SNR of channel', default=0)
    parser.add_argument('freq_offset', help='frequency offset of channel', default=0)
    parser.add_argument('noise', help='noise of channel', default=0)
    parser.add_argument('encoding', help='encoding of channel', default=0)

    parser.add_argument('-v', '--verbose', help='print verbose output', action='store_true') # true if flag present
    args = parser.parse_args()

    # set up transmitter
    cp = Channel_Parameters(args.ip_addr, zmq_ports, zmq_names, args.verbose)

    # send each value
    cp.send(args.SNR, 'SNR')
    cp.send(args.freq_offset, 'freq_offset')
    cp.send(args.noise, 'noise')
    cp.send(args.encoding, 'encoding')

    # close socket
    cp.close()     

    if args.verbose:
        print("Channel parameters sent")