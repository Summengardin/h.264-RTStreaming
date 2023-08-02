#!/usr/bin/env python3

import socket
import cv2
import struct
import signal
import sys


def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)


def server():

    cap = cv2.VideoCapture(0)

    try:
        print("Connecting to camera...")

        print("Camera connected\n")
        # Setup server socket
        print("Setting up server socket...")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #IPAddr = 'localhost'
        IPAddr = '10.19.127.11'
        server_socket.bind((IPAddr, 8485))
        server_socket.listen(0)
        print(f"Socket setup at ip: {server_socket.getsockname()[0]}, port:  {server_socket.getsockname()[1]}\n")

        print("Waiting for client to connect...")
        # Accept a single connection and make a file-like object out of it
        connection = server_socket.accept()[0].makefile('wb')
        print("Client connected")

        while True:
            ret, frame = cap.read()

            if not ret:
                continue
            
            # Convert the frame to bytes (byte data)
            _, frame_data = cv2.imencode('.jpg', frame)

            
            # write the length of the data and then the data itself
            connection.write(struct.pack('<L', len(frame_data)) + bytes(frame_data))
    finally:
        connection.close()
        server_socket.close()


if __name__ == '__main__':

    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start the server
    server()