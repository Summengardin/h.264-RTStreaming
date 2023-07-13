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
    camRgb.initialControl.AutoFocusMode(dai.CameraControl.AutoFocusMode.OFF)
    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.initialControl.setAutoExposureLock(True)


    videoEnc = pipeline.create(dai.node.VideoEncoder)
    videoEnc.setDefaultProfilePreset(camRgb.getFps(), dai.VideoEncoderProperties.Profile.H264_HIGH)
    camRgb.video.link(videoEnc.input)

    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("h264")
    videoEnc.bitstream.link(xout.input)


    # Setup server socket
    print("Setting up server socket...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8485))
    server_socket.listen(0)
    print(f"Socket setup at ip: {server_socket.getsockname()[0]}, port:  {server_socket.getsockname()[1]}\n")

    print("Waiting for client to connect...")
    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('wb')
    print("Client connected. Starting camera\n")

    try:
        with dai.Device(pipeline) as device:
            q = device.getOutputQueue(name="h264", maxSize=30, blocking=True)

            while True:
                data = q.get().getData()  # Blocking call, will wait until new data has arrived
                # write the length of the data and then the data itself
                connection.write(struct.pack('<L', len(data)) + bytes(data))
    finally:
        connection.close()
        server_socket.close()


if __name__ == '__main__':

    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start the server
    server()