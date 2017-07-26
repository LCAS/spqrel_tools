#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
# http://doc.aldebaran.com/2-5/naoqi/peopleperception/alengagementzones-api.html#alengagementzones-api

import qi
import argparse
import sys
import os
import time
import threading
import math

from naoqi import ALProxy

import conditions
from conditions import set_condition

def rhMonitorThread (memory_service,motion_service):

    t = threading.currentThread()
    print "sound detected thread started"


    while getattr(t, "do_run", True):
        v = 'false'
        #print "testing sound"
        try:
            sound_value = memory_service.getData("ALSoundLocalization/SoundLocated")
            if len(sound_value)>1:
                #print "confidence: ", sound_value[1][2]
                confidence = sound_value[1][2]
                if (confidence > 0.3):
                    print "sound detected!!!!!!!"
                    v = 'true'
                    sound_azimuth = sound_value[1][0]
                    head_yaw = sound_value[2][5]
                    turn = sound_azimuth + head_yaw
                    #motion_service.moveTo(0, 0, turn)

        except:
        #    print "exception in sound"
            v = 'false'

        set_condition(memory_service,'sounddetected',v)

        time.sleep(0.5)
    print "sounddetected thread quit"

def init(session):
    global memory_service
    global monitorThread

    print "Sound detected init"
    try:
        #Starting services
        memory_service  = session.service("ALMemory")
        sound_service = session.service("ALSoundLocalization")
        motion_service = session.service("ALMotion")
    except:
        pass

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,motion_service))
    monitorThread.start()


def quit():
    global monitorThread
    print "Sound detected quit"
    monitorThread.do_run = False 



def main():
    global memory_service
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ",    connection_url
        app = qi.Application(["PersonHere", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    init(session)

    app.run()    


if __name__ == "__main__":
    main()