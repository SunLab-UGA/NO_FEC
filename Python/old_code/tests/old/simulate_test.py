# this is the main file for the ZMQ_Python project
# it will call other python files to run the tests

# each proceess is meant to be self-contained, and will run until it is stopped

import subprocess
import time
import threading
import signal

# globals
script_subdir = "ZMQ_Python"
scripts = ["simple_pmt_rx.py"]  # List of scripts to run
processes = [] # List of processes to monitor

def run_script(script_name):
    """Run a script as a subprocess and monitor its status."""
    process = subprocess.Popen(["python", script_name])
    return process

def monitor_process(process, script_name):
    """Monitor the process for completion or errors."""
    while True:
        if process.poll() is not None:
            print(f"Process for {script_name} has stopped.")
            break
        # Here you can add logic to check the script's log file for errors
        # For example, read the last line of the log file and check for error keywords
        # ...
        time.sleep(1)  # Check periodically, adjust the sleep time as needed

def signal_handler(sig, frame):
    """Handle the signal to stop the script."""
    print("Stopping processes...")
    for p in processes:
        p.terminate()
    print("Processes stopped.")
    exit(0)

def main():
    print("Welcome!")

    for script in scripts:
        processes.append(run_script(script_subdir+"/"+script))
        print(f"Started process for {script}")
        # Start a thread to monitor each process
        threading.Thread(target=monitor_process, args=(processes[-1], script), daemon=True).start()
        # print the pid of the process
        print(f"Process started with PID: {processes[-1].pid}")

    while True: # non-blocking loop
        
        # Do other things here
        time.sleep(1)

if __name__ == "__main__":
    # signal handler
    signal.signal(signal.SIGINT, signal_handler) # ctrl+c
    signal.signal(signal.SIGTERM, signal_handler) # kill pid

    main()
