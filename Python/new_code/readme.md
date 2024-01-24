# No-FEC Project
* These scripts are used in conjunction with gr_ieee802_11 gnuradio
* They record and present a BER with minimal changes to the main 802_11 library
    * the No-FEC has modifications to remove all forward errror correction

# Steps for Testing
* run gnuradio_companion and start the tx/rx scripts (later done)
* run the reciever script
* run the transmitter script (reads tx_file.txt, line by line, transmits each line, quits)
(TODO: integrate the process into one script)

- the file structure of saved data
    -{test index - date}
        - readme (contains a text structure of the pickle)
        - tx_data.pickle (data of all data transmitted)
        - rx_data.pickle (data of all data recieved)
        - {any post processing}

* this is meant to be seperable such that the tx and rx can be run on seperate (time syncronized) computers
