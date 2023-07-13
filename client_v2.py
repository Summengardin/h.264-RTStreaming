#!/usr/bin/env python3

import socket
import av
import cv2
import struct
import signal
import sys


def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)


def client():
    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8485))
    print(f"Connecting to server at ip: {client_socket.getsockname()[0]}, port: {client_socket.getsockname()[1]}")

    # Make a file-like object out of the connection
    connection = client_socket.makefile('rb')

    try:
        codec = av.CodecContext.create("h264", "r")

        while True:
            # Read the length of the data, letter by letter until we reach EOL
            data_length = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            data = connection.read(data_length)
            
            packets = codec.parse(data)
            
            for packet in packets:
                frames = codec.decode(packet)
                if frames:
                    frame = frames[0].to_ndarray(format='bgr24')
                    cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break
    finally:
        connection.close()
        client_socket.close()


if __name__ == '__main__':
    
    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)
    
    # Start client
    client()