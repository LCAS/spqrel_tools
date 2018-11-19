#! /usr/bin/env python
# -*- encoding: UTF-8 -*-


import argparse
import sys
import os
import qi

from naoqi import ALProxy

PEPPER_IP='127.0.0.1'
PEPPER_PORT=9559

behaviours = [
    ('ALFaceDetection', 'Face_Behavior'),
    ('ALFaceCharacteristics', 'Char_Behavior'),
    ('ALPeoplePerception', 'People_Behavior'),
    ('ALSittingPeopleDetection', 'Sitting_Behavior'),
    ('ALSoundLocalization', 'Sound_Behavior'),
    ('ALMotion', 'Motion_Behavior'),
    ('ALWavingDetection', 'Waving_Behavior'),
    ('ALSpeechRecognition', 'ASR_Behavior'),
    ('ALAudioRecorder', 'Recorder_Behavior'),
    ('ALAnimationPlayer', None)
]

bm_service = None
ba_service = None
sm_service = None

def start_behaviors(session,pip,pport):
    global bm_service, ba_service, sm_service

    print "==================================="
    print "   Starting background behaviors   "
    print "==================================="


    facedetectionProxy = ALProxy("ALFaceDetection",pip,pport)
    facecharacteristicsProxy = ALProxy("ALFaceCharacteristics",pip,pport)
    peopledetectionProxy = ALProxy("ALPeoplePerception",pip,pport)
    peoplesittingProxy = ALProxy("ALSittingPeopleDetection",pip,pport)
    soundlocalizationProxy = ALProxy("ALSoundLocalization",pip,pport)
    #motionProxy = ALProxy("ALMotion",pip,pport)
    wavingdetectionProxy = ALProxy("ALWavingDetection",pip,pport)
    animationProxy = ALProxy("ALAnimationPlayer",pip,pport)


    facedetectionProxy.subscribe("Face_Behavior", 500, 0.0)
    facecharacteristicsProxy.subscribe("Char_Behavior", 500, 0.0)
    peopledetectionProxy.subscribe("People_Behavior", 500, 0.0)
    peoplesittingProxy.subscribe("Sitting_Behavior", 500, 0.0)
    soundlocalizationProxy.subscribe("Sound_Behavior", 500, 0.0)
    wavingdetectionProxy.subscribe("Waving_Behavior",500,0.0)
    #motionProxy.subscribe("Motion_Behavior", 500, 0.0)


    bm_service = session.service("ALBackgroundMovement")
    ba_service = session.service("ALBasicAwareness")
    sm_service = session.service("ALSpeakingMovement")

    bm_service.setEnabled(True)
    ba_service.setEnabled(True)
    sm_service.setEnabled(True)



def quit_behaviors(session,pip,pport):
    global bm_service, ba_service, sm_service

    print "==================================="
    print "   Quitting background behaviors   "
    print "==================================="

    

    facedetectionProxy = ALProxy("ALFaceDetection",pip,pport)
    facecharacteristicsProxy = ALProxy("ALFaceCharacteristics",pip,pport)
    peopledetectionProxy = ALProxy("ALPeoplePerception",pip,pport)
    peoplesittingProxy = ALProxy("ALSittingPeopleDetection",pip,pport)
    soundlocalizationProxy = ALProxy("ALSoundLocalization",pip,pport)
    #motionProxy = ALProxy("ALMotion",pip,pport)
    wavingdetectionProxy = ALProxy("ALWavingDetection",pip,pport)
    animationProxy = ALProxy("ALAnimationPlayer",pip,pport)

    
    
    facedetectionProxy.unsubscribe("Face_Behavior")
    facecharacteristicsProxy.unsubscribe("Char_Behavior")    
    peopledetectionProxy.unsubscribe("People_Behavior")
    peoplesittingProxy.unsubscribe("Sitting_Behavior")
    soundlocalizationProxy.unsubscribe("Sound_Behavior")
    wavingdetectionProxy.unsubscribe("Waving_Behavior")
    #motionProxy.unsubscribe("Motion_Behavior")

    bm_service.setEnabled(False)
    ba_service.setEnabled(False)
    sm_service.setEnabled(False)


def stop_behavior(session, behaviorName):
    behman_service = session.service("ALBehaviorManager")
    behman_service.stopBehavior(behaviorName)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=os.getenv('PEPPER_IP'),
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--enabled", type=int, default=1,
                        help="Behaviors are enabled (0/1)")

    args = parser.parse_args()

    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))

    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    if (args.enabled==1):
        start_behaviors(session,args.ip,args.port)
    else:
        quit_behaviors(session,args.ip,args.port)



