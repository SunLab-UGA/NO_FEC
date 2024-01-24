# creates a text file with a sequence of ascii characters the length of the PDU (64 bytes)

# array of ascii characters
ASCII = [chr(i) for i in range(0x41, 0x5A+1)] # ASCII CAPITAL LETTER RANGE: 65(0x41) - 90(0x5A)

PDU_LENGTH = 64 # number of bytes in a PDU

# create the file and write the ascii characters to it
with open('ascii.txt', 'w') as f:
    for a in ASCII:
        pdu = "".join(a for i in range(PDU_LENGTH))
        f.write(pdu) # write the ascii character PDU_LENGTH times
        f.write('\n')

print("ASCII file created")