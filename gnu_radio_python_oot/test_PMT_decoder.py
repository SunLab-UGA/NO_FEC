#!/usr/bin/env python

from gnuradio import gr
import pmt

class MyPMTFilterBlock(gr.sync_block):
    def __init__(self, key):
        gr.sync_block.__init__(self,
            name="My PMT Filter",
            in_sig=None,
            out_sig=[],
        )
        self.key = key

    def work(self, input_items, output_items):
        # Iterate through the incoming PMT messages
        for item in input_items[0]:
            if pmt.is_dict(item):
                # Check if the PMT message is a dictionary
                value = pmt.dict_ref(item, self.key)
                # Extract the value associated with the specified key
                if value is not None:
                    # If the key exists, output it as a new message
                    self.message_port_pub(pmt.intern("output"), value)
        return len(input_items[0])

