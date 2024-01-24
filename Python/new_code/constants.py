# a dictionary of the MAC Frame and [start,end] positions
MAC_FRAME_FIELDS = {"FrameControl": [0,2], # 2 bytes "octets"
                    "Duration": [2,4], # 2 bytes, Duration/ID
                    "Address1": [4,10], # 6 bytes, MAC address
                    "Address2": [10,16], # 6 bytes, MAC address
                    "Address3": [16,22], # 6 bytes, MAC address
                    "SequenceControl": [22,24], # 2 bytes
                    "Address4": [24,30], # 6 bytes, MAC address
                    "FCS": [-4,-1] # 4 bytes, Frame Check Sequence, CRC32, end of frame
                    }
FRAME_CONTROL_FIELDS = {"ProtocolVersion": [0,2], # 2 bits
                        "Type": [2,4], # 2 bits
                        "Subtype": [4,8], # 4 bits
                        "ToDS": [8,9], # 1 bit
                        "FromDS": [9,10], # 1 bit
                        "MoreFragments": [10,11], # 1 bit
                        "Retry": [11,12], # 1 bit
                        "PowerManagement": [12,13], # 1 bit
                        "MoreData": [13,14], # 1 bit
                        "ProtectedFrame": [14,15], # 1 bit, WEP encryption
                        "Order": [15,16] # 1 bit
                        }

SEQUENCE_CONTROL_FIELDS = {"FragmentNumber": [0,4], # 4 bits
                            "SequenceNumber": [4,16] # 12 bits
                            }