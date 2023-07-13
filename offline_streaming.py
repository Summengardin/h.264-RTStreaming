#!/usr/bin/env python3

import depthai as dai
import av
import signal
import sys
import cv2


def sigint_handler(signal, frame):
    print("Caught KeyboardInterrupt, exiting.")
    sys.exit(0)


def main():
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



    codec = av.CodecContext.create("h264", "r")

    with dai.Device(pipeline) as device:
        q = device.getOutputQueue(name="h264", maxSize=30, blocking=True)

        while True:
            data = q.get().getData()  # Blocking call, will wait until new data has arrived
            # write the length of the data and then the data itself
            encoded_data = bytes(data)
            decoded_data = codec.parse(encoded_data)

            for packet in decoded_data:
                frames = codec.decode(packet)
                if frames:
                    frame = frames[0].to_ndarray(format='bgr24')
                    cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break

                




if __name__ == '__main__':

    # Set up signal handler to handle keyboard interrupts
    signal.signal(signal.SIGINT, sigint_handler)

    # Start the server
    main()