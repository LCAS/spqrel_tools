# DOCUMENTATION
# http://doc.aldebaran.com/2-5/naoqi/peopleperception/alengagementzones-api.html#alengagementzones-api

import qi
import argparse
import sys
import os
import time
import threading
import math
import almath

from naoqi import ALProxy

import conditions
from conditions import set_condition

def rhMonitorThread (memory_service,motion_service):

    t = threading.currentThread()
    print "sound detected thread started"

    prev_time = 0
    while getattr(t, "do_run", True):
        v = 'false'
        #print "testing sound"
        
        sound_value = memory_service.getData("ALSoundLocalization/SoundLocated")
        #print "\n"
        #print "[time(sec), time(usec)]", sound_value[0]
        #print "[azimuth(rad), elevation(rad), confidence, energy]", sound_value[1]
        #print "[Head Position[6D]] in FRAME_TORSO", sound_value[2]
        #print "[Head Position[6D]] in FRAME_ROBOT", sound_value[3]
        #head_pose6d = almath.Position6D(sound_value[3][0],sound_value[3][1],sound_value[3][2],
        #                                sound_value[3][3],sound_value[3][4],sound_value[3][5])
        #print head_pose6d
        #head_transform = almath.transformFromPosition6D(head_pose6d)
        #print "[Head Transform] in FRAME_ROBOT"
        #print head_transform
        #print "\n"

        if len(sound_value)>1 and prev_time != sound_value[0][0]:
            prev_time = sound_value[0][0]
            #print "confidence: ", sound_value[1][2]
            confidence = sound_value[1][2]
            if (confidence > 0.2):
                v = 'true'
                sound_azimuth = sound_value[1][0]
                head_yaw = sound_value[3][5]
                turn_angle = sound_azimuth + head_yaw
                turn_angle = int(turn_angle / math.pi * 180)
                memory_service.insertData('AngleSound', str(turn_angle) + "_REL")
                print "[SoundDetected] time: ", sound_value[0][0], "azimuth(rad): ", sound_azimuth
                
        set_condition(memory_service,'sounddetected',v)
        if v:
            time.sleep(5) #if true we give time to process the condition

        time.sleep(0.25)

    print "sounddetected thread quit"

def init(session):
    global memory_service
    global monitorThread

    print "Sound detected init"
    try:
        #Starting services
        memory_service  = session.service("ALMemory")
        motion_service = session.service("ALMotion")
        sound_service = session.service("ALSoundLocalization")
    except:
        print "Error connecting to services"
        pass

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,motion_service,))
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

