#! /usr/bin/env python
# -*- encoding: UTF-8 -*-


import argparse
import sys
import os

from naoqi import ALProxy

PEPPER_IP='127.0.0.1'
PEPPER_PORT=9559

def start_behaviors():

    print "==================================="
    print "   Starting background behaviors   "
    print "==================================="

#    movementdetection = ALProxy( "ALMovementDetection" )
#    wavingdetection   = ALProxy( "ALWavingDetection" )
#    zonesdetection = ALProxy("ALEngagementZones")
#    sittingdetection = ALProxy("ALSittingPeopleDetection")

    facedetectionProxy = ALProxy("ALFaceDetection",os.getenv('PEPPER_IP'),9559)
    facecharacteristicsProxy = ALProxy("ALFaceCharacteristics",os.getenv('PEPPER_IP'),9559)
    peopledetectionProxy = ALProxy("ALPeoplePerception",os.getenv('PEPPER_IP'),9559)
    peoplesittingProxy = ALProxy("ALSittingPeopleDetection",os.getenv('PEPPER_IP'),9559)
    soundlocalizationProxy = ALProxy("ALSoundLocalization",os.getenv("PEPPER_IP"),9559)
    motionProxy = ALProxy("ALMotion",os.getenv("PEPPER_IP"),9559)


    facedetectionProxy.subscribe("Face_Behavior", 500, 0.0)
    facecharacteristicsProxy.subscribe("Char_Behavior", 500, 0.0)
    peopledetectionProxy.subscribe("People_Behavior", 500, 0.0)
    peoplesittingProxy.subscribe("Sitting_Behavior", 500, 0.0)
    soundlocalizationProxy.subscribe("Sound_Behavior", 500, 0.0)
    motionProxy.subscribe("Motion_Behavior", 500, 0.0)




def quit_behaviors():

    print "==================================="
    print "   Quitting background behaviors   "
    print "==================================="

    facedetectionProxy = ALProxy("ALFaceDetection",PEPPER_IP,PEPPER_PORT)
    facecharacteristicsProxy = ALProxy("ALFaceCharacteristics",PEPPER_IP,PEPPER_PORT)    
    peopledetectionProxy = ALProxy("ALPeoplePerception",PEPPER_IP,PEPPER_PORT)
    peoplesittingProxy = ALProxy("ALSittingPeopleDetection",PEPPER_IP,PEPPER_PORT)
    soundlocalizationProxy = ALProxy("ALSoundLocalization",PEPPER_IP,PEPPER_PORT)
    motionProxy = ALProxy("ALMotion",PEPPER_IP,PEPPER_PORT)

    
    
    facedetectionProxy.unsubscribe("Face_Behavior")
    facecharacteristicsProxy.unsubscribe("Char_Behavior")    
    peopledetectionProxy.unsubscribe("People_Behavior")
    peoplesittingProxy.unsubscribe("Sitting_Behavior")
    soundlocalizationProxy.unsubscribe("Sound_Behavior")
    motionProxy.unsubscribe("Motion_Behavior")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=os.getenv('PEPPER_IP'),
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--enabled", type=int, default=1,
                        help="Behaviors are enabled (0/1)")

    args = parser.parse_args()

    #session = qi.Session()
    #try:
    #    session.connect("tcp://" + args.ip + ":" + str(args.port))

    #except RuntimeError:
    #    print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
    #           "Please check your script arguments. Run with -h option for help.")
    #    sys.exit(1)

    if (args.enabled==1):
        start_behaviors()
    else:
        quit_behaviors()



