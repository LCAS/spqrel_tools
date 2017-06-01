#!/usr/bin/env python

# -*- encoding: UTF-8 -*-
#
# This example demonstrates how to use the ALVideoRecorder module to record a
# video file on the robot.
#
# Usage: python vision_videorecord.py "robot_ip"
#

import os
import sys
import argparse
import time
from naoqi import ALProxy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--camera", type=int, default=0,
                        help="Robot camera ID address. 0 by default")
                        
    args = parser.parse_args()
    IP = args.pip
    PORT = args.pport 

    videoRecorderProxy = ALProxy("ALVideoRecorder", IP, PORT)

    # This records a 320*240 MJPG video at 10 fps.
    # Note MJPG can't be recorded with a framerate lower than 3 fps.
    videoRecorderProxy.setResolution(1)
    videoRecorderProxy.setFrameRate(10)
    videoRecorderProxy.setVideoFormat("MJPG")
    videoRecorderProxy.startRecording("/home/nao/recordings/cameras", "myvideo")

    time.sleep(5)

    # Video file is saved on the robot in the
    # /home/nao/recordings/cameras/ folder.
    videoInfo = videoRecorderProxy.stopRecording()

    print "Video was saved on the robot: ", videoInfo[1]
    print "Num frames: ", videoInfo[0]