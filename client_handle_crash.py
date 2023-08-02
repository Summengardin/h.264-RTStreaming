#!/usr/bin/env python3

import socket
import av
import cv2
import struct
import signal
import sys
import time

def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)

def connect_to_server():
    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IPAddr = '10.19.127.11'
    port = 8485
    while True:
        try:
            client_socket.connect((IPAddr, port))
            print(f"Connecting to server at ip: {client_socket.getsockname()[0]}, port: {client_socket.getsockname()[1]}")
            return client_socket
        except ConnectionRefusedError:
            # Server actively refused the connection, attempt reconnection
            print("Connection refused by the server. Attempting to reconnect...")
            #client_socket.close()
            time.sleep(5)  # Wait for a few seconds before reconnecting

def client():
    client_socket = connect_to_server()
    # Make a file-like object out of the connection
    connection = client_socket.makefile('rb')

    try:
        codec = av.CodecContext.create("h264", "r")

        fpsCounter = 0
        startTime = time.time()
        fps = '-'

        while True:
            # Read the length of the data, letter by letter until we reach EOL
            data_length = connection.read(struct.calcsize('<L'))
            if not data_length:
                # Server closed the connection, attempt reconnection
                print("Server closed the connection. Attempting to reconnect...")
                client_socket.close()
                time.sleep(5)  # Wait for a few seconds before reconnecting
                client_socket = connect_to_server()
                connection = client_socket.makefile('rb')
                continue

            data_length = struct.unpack('<L', data_length)[0]
            data = connection.read(data_length)

            if not data:
                # Empty data received, handle the situation gracefully
                print("Received empty data.")
                break

            packets = codec.parse(data)

            for packet in packets:
                frames = codec.decode(packet)
                if frames:
                    frame = frames[0].to_ndarray(format='bgr24')

                    # Display FPS
                    fpsCounter += 1
                    elapsedTime = time.time() - startTime

                    update_rate = 1 #seconds
                    if elapsedTime >= update_rate:
                        fps = fpsCounter / (elapsedTime * (1/update_rate))
                        fps = f"{fps:.2f}"
                        fpsCounter = 0
                        startTime = time.time()

                    cv2.putText(frame, fps, (frame.shape[1]-100, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA)
                    cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break
    except socket.error as e:
        # Handle socket-related errors
        if e.errno == 10054:
            print("Connection forcibly closed by the remote host. Attempting to reconnect...")
            client_socket.close()
            cv2.destroyAllWindows()
            time.sleep(5)  # Wait for a few seconds before reconnecting
            client()
        else:
            print(f"Socket error occurred: {e}")
    except av.AVError as e:
        # Handle AV-related errors
        print(f"AVError occurred: {e}")
        cv2.destroyAllWindows()
    finally:
        connection.close()
        client_socket.close()

if __name__ == '__main__':
    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start client
    client()
