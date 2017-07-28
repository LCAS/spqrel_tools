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

def rhMonitorThread (memory_service):
    global last_personid
    t = threading.currentThread()
    print "persondetected thread started"
    personid = 0
    while getattr(t, "do_run", True):
        plist = memory_service.getData("PeoplePerception/PeopleList")
        v = 'false'
        try:
            if (len(plist)>0):
                memory_service.insertData("persondetectedid",plist[0])
                v = 'true'
        except:
            v = 'false'

        set_condition(memory_service,'persondetected',v)

        time.sleep(0.5)
    print "persondetected thread quit"



def init(session):
    global memory_service
    global monitorThread

    print "Person here init"

    #Starting services
    memory_service  = session.service("ALMemory")
    zones_service = session.service("ALEngagementZones")
    people_service = session.service("ALPeoplePerception")
    people_service.resetPopulation()
    
    #waving_service = session.service("ALWavingDetection")
    #movement_service = session.service("ALMovementDetection")

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Person detected quit"
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
