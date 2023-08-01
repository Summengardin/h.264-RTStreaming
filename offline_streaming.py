#!/usr/bin/env python3

import depthai as dai
import av
import signal
import sys
import cv2
import time
import numpy as np


def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)


def main():
    # Create pipeline
    pipeline = dai.Pipeline()

    camRgb = pipeline.create(dai.node.ColorCamera)

    camRgb.initialControl.AutoFocusMode(dai.CameraControl.AutoFocusMode.OFF)
    camRgb.initialControl.AutoWhiteBalanceMode(dai.CameraControl.AutoWhiteBalanceMode.OFF)
    camRgb.initialControl.AntiBandingMode(dai.CameraControl.AntiBandingMode.OFF)
    camRgb.initialControl.setAutoExposureLock(True)

    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setVideoSize(480,320)
    camRgb.setPreviewSize(480,320)
    
    videoEnc = pipeline.create(dai.node.VideoEncoder)
    videoEnc.setDefaultProfilePreset(camRgb.getFps(), dai.VideoEncoderProperties.Profile.H264_HIGH)
    camRgb.video.link(videoEnc.input)
    
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("h264")
    videoEnc.bitstream.link(xout.input)

    # Preview
    xout_preview = pipeline.create(dai.node.XLinkOut)
    xout_preview.setStreamName("preview")
    camRgb.preview.link(xout_preview.input)


    codec = av.CodecContext.create("h264", "r")

    with dai.Device(pipeline) as device:
        q = device.getOutputQueue(name="h264", maxSize=30, blocking=True)
        q_preview = device.getOutputQueue(name="preview", maxSize=30, blocking=True)

        fpsCounter = 0
        startTime = time.time()
        fps = '-'

        while True:
            h264_data = q.get().getData()  # Blocking call, will wait until new data has arrived
            # write the length of the data and then the data itself
            encoded_data = bytes(h264_data)
            packets = codec.parse(encoded_data)

            preview_frame = q_preview.get().getCvFrame()

            cv2.imshow("preview", preview_frame)
            


            for packet in packets:
                frames = codec.decode(packet)
                if frames:
                    frame = frames[0].to_ndarray(format='bgr24')

                    # Display FPS
                    fpsCounter += 1
                    elapsedTime = time.time() - startTime

                    if elapsedTime >= 1.0:
                        fps = fpsCounter / elapsedTime
                        fps = f"{fps:.2f}"
                        fpsCounter = 0
                        startTime = time.time()

                    cv2.putText(frame, fps, (frame.shape[1]-100, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA)
                    
                    cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break

                




if __name__ == '__main__':

    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start the server
    main()