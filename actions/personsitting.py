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
from utils import point2world

from naoqi import ALProxy

import conditions
from conditions import set_condition


def rhMonitorThread (memory_service):
    t = threading.currentThread()
    print "personsitting thread started"
    
    while getattr(t, "do_run", True):
        plist = memory_service.getData("PeoplePerception/PeopleList")
        
        personid = 0
        IsSitting = 0
        v = 'false'
        try:
            if (plist!=None and len(plist)>0):
                for i in range (0,len(plist)):
                    personid = plist[i]
                    IsSitting = memory_service.getData("PeoplePerception/Person/"+str(personid)+"/IsSitting")
                    # Save person position
                    if (IsSitting == 1):
                        px,py,pz = memory_service.getData("PeoplePerception/Person/"+str(personid)+"/PositionInRobotFrame")
                        memory_service.setData("")
                        print "person sitting"
                        print "X: " + str(px) + "  Y: " + str(py)
                        w_px, w_py = point2world(memory_service,[px,py])
                        memory_service.insertData("personsitting/coordinates",[w_px,w_py])
                        memory_service.insertData("personsitting/id",personid)
                        v = 'true'
        except:
            v = 'false'
        set_condition(memory_service,'personsitting',v)
        #print 'personhere:: value ',v

        time.sleep(0.5)
    print "personsitting thread quit"



def init(session):
    global memory_service
    global monitorThread

    print "Person sitting init"

    #Starting services
    memory_service  = session.service("ALMemory")
    sitting_service = session.service("ALSittingPeopleDetection")

    # PARAMETERS
    sitting_service.setSittingThreshold(1.4)
    sitting_threshold = sitting_service.getSittingThreshold()
    print "sitting threshold: ",sitting_threshold

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Person sitting quit"
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
        app = qi.Application(["PersonSitting", "--qi-url=" + connection_url ])
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