#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles Method"""

import qi
import argparse
import sys
import time
import almath
import os
import threading
from naoqi import ALProxy, ALBroker, ALModule

def wave_callback(value):
    print "wave detected"


def main(session):

    #waving = session.service("ALWavingDetection")
    memory_service = session.service("ALMemory")
#    module_service = session.service("ALModule")
    maxrange = waving.getMaxDistance()
    minrange = waving.getMinSize()
    waving.setMinSize(0.1)

    print 'Max Range=',maxrange
    print 'Min Size=',minrange

    waveDetection = memory_service.subscriber("WavingDetection/Waving")
    idAnyDetection = waveDetection.signal.connect(wave_callback)


    try:
        while True:

            time.sleep(0.1)
    except KeyboardInterrupt:
        print
        print "Waving Detector Ended"



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,help="Naoqi port number")
    parser.add_argument("--right_angle",type=int, default=-60,help="Right angle")
    parser.add_argument("--left_angle",type=int, default=60,help="Left angle")
    parser.add_argument("--speed",type=float, default=0.5,help="Fraction Max Speed [0-1]")
    parser.add_argument("--wait_time",type=float, default=6.0,help="Wait time in each movement")

    args = parser.parse_args()
    session = qi.Session()

    waving = ALProxy("ALWavingDetection", os.environ['PEPPER_IP'],9559)

    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)