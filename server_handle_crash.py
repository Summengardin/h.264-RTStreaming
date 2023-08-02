#!/usr/bin/env python3

import socket
import depthai as dai
import struct
import signal
import sys

def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)

def server():
    # Create pipeline
    pipeline = dai.Pipeline()

    camRgb = pipeline.create(dai.node.ColorCamera)
    
    camRgb.initialControl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.OFF)
    camRgb.initialControl.setAntiBandingMode(dai.CameraControl.AntiBandingMode.OFF)
    camRgb.initialControl.setAutoWhiteBalanceMode(dai.CameraControl.AutoWhiteBalanceMode.OFF)
    camRgb.initialControl.setAutoExposureLock(True)
    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setVideoSize(1280, 720)
    camRgb.setFps(20)


    videoEnc = pipeline.create(dai.node.VideoEncoder)
    videoEnc.setDefaultProfilePreset(camRgb.getFps(), dai.VideoEncoderProperties.Profile.H264_BASELINE)
    camRgb.video.link(videoEnc.input)

    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("h264")
    videoEnc.bitstream.link(xout.input)

    try:
        print("Connecting to camera...")
        with dai.Device(pipeline) as device:
            print("Camera connected\n")
            # Setup server socket
            print("Setting up server socket...")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # IPAddr = 'localhost'
            IPAddr = '10.19.127.11'  # Uncomment this line if you want to bind to a specific IP address
            server_socket.bind((IPAddr, 8485))
            server_socket.listen(1)  # Only allow one client to connect
            print(f"Socket setup at ip: {server_socket.getsockname()[0]}, port:  {server_socket.getsockname()[1]}\n")

            while True:
                print("Waiting for client to connect...")
                # Accept a single connection and make a file-like object out of it
                connection, client_address = server_socket.accept()
                print("Client connected:", client_address)

                try:
                    connection_file = connection.makefile('wb')

                    q = device.getOutputQueue(name="h264", maxSize=30, blocking=True)

                    while True:
                        data = q.get().getData()  # Blocking call, will wait until new data has arrived

                        # Write the length of the data and then the data itself
                        connection_file.write(struct.pack('<L', len(data)) + bytes(data))
                except ConnectionResetError:
                    # Handle connection reset by the remote host
                    print("ConnectionResetError: The remote host closed the connection.")
                finally:
                    connection_file.close()
                    connection.close()
    except socket.error as e:
        # Handle socket-related errors
        print(f"Socket error occurred: {e}")
    except RuntimeError as e:
        # Handle depthai Device-related errors
        print(f"Device error occurred: {e}")
    finally:
        try:
            server_socket.close()
        except NameError:
            pass

if __name__ == '__main__':
    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start the server
    server()
