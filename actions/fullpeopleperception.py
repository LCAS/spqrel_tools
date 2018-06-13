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



def rhMonitorThread (memory_service):
    t = threading.currentThread()
    print "fullpeopleperception thread started"

    while getattr(t, "do_run", True):
        
        plist = memory_service.getData("PeoplePerception/PeopleList")

        for personid in plist:
            pmemkey_dist   = "PeoplePerception/Person/"+str(personid)+"/Distance"
            pmemkey_angles = "PeoplePerception/Person/"+str(personid)+"/AnglesYawPitch"
            pmemkey_pos    = "PeoplePerception/Person/"+str(personid)+"/PositionInRobotFrame"
            pmemkey_sit    = "PeoplePerception/Person/"+str(personid)+"/IsSitting"
            pmemkey_wave   = "PeoplePerception/Person/"+str(personid)+"/IsWaving"
            pmemkey_height = "PeoplePerception/Person/"+str(personid)+"/RealHeight"
            pmemkey_shirt  = "PeoplePerception/Person/"+str(personid)+"/ShirtColor"
            pmemkey_face   = "PeoplePerception/Person/"+str(personid)+"/FacialPartsProperties"

            key_list = [pmemkey_dist, pmemkey_angles, pmemkey_pos, pmemkey_sit,
                        pmemkey_wave, pmemkey_height, pmemkey_shirt, pmemkey_face]
            
            data_list = memory_service.getListData(key_list)

            print "\n"
            print "[Person: ", personid, "]"
            #print "[Distance: ", data_list[0], "]"
            #print "[AnglesYawPitch: ", data_list[1], "]"
            #print "[PositionInRobotFrame: ", data_list[2], "]"
            #print "[IsSitting: ", data_list[3], "]"
            #print "[IsWaving: ", data_list[4], "]"
            #print "[RealHeight: ", data_list[5], "]"
            #print "[ShirtColor: ", data_list[6], "]"
            print  "[Mouth Coord (x,y): ", data_list[7][11][0][0], data_list[7][11][0][1] ,"]"
            #print "\n"


                    
        time.sleep(0.5)
        
    print "fullpeopleperception thread quit"



def init(session):
    global memory_service
    global monitorThread

    print "full perception init"

    #Starting services
    memory_service  = session.service("ALMemory")
    zones_service = session.service("ALEngagementZones")
    people_service = session.service("ALPeoplePerception")
    people_service.resetPopulation()
    people_service.setMovementDetectionEnabled(True)
    print "movement detection enabled: ", people_service.isMovementDetectionEnabled()
    waving_service = session.service("ALWavingDetection")
    sitting_service = session.service("ALSittingPeopleDetection")
    movement_service = session.service("ALMovementDetection")

    # PARAMETERS
    zones_service.setFirstLimitDistance(1.5)
    zones_service.setSecondLimitDistance(2.5)
    zones_service.setLimitAngle(45)

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Person here quit"
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
