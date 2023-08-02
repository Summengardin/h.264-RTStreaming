#!/usr/bin/env python3

import socket
import struct
import cv2
import signal
import sys
import numpy as np

def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)

def client():
    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IPAddr = '10.19.127.11'
    client_socket.connect((IPAddr, 8485))
    print(f"Connecting to server at ip: {client_socket.getsockname()[0]}, port: {client_socket.getsockname()[1]}")

    try:
        while True:
            # Read the length of the data, letter by letter until we reach EOL
            data_length = struct.unpack('<L', client_socket.recv(struct.calcsize('<L')))[0]
            data = client_socket.recv(data_length)

            # Convert the data back to an image frame
            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            #frame = cv2.imdecode(data, cv2.IMREAD_COLOR)


            cv2.imshow('frame', frame)


            if cv2.waitKey(1) == ord('q'):
                break

    except socket.error as e:
        # Handle socket-related errors
        print(f"Socket error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start the client
    client()
