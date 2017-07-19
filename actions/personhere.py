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

last_personid = 0

# function called when the signal "EngagementZones/PersonEnteredZone1" is triggered
def zone1_callback(data):
    global memory_service
    print "Person has entered Zone 1"
    set_condition(memory_service,'personhere','true')
    time.sleep(1)
    set_condition(memory_service,'personhere','false')


def rhMonitorThread (memory_service):
    global last_personid
    t = threading.currentThread()
    print "personhere thread started"
    personid = 0
    while getattr(t, "do_run", True):
        plist = memory_service.getData("PeoplePerception/PeopleList")
        
        personid = 0
        if (plist!=None and len(plist)>0):
            personid = plist[0]
        #print 'personhere:: personid ',personid    
        pmemkey_dist = "PeoplePerception/Person/"+str(personid)+"/Distance"
        pmemkey_angles = "PeoplePerception/Person/"+str(personid)+"/AnglesYawPitch"
        pmemkey_pos = "PeoplePerception/Person/"+str(personid)+"/PositionInTorsoFrame"

        v = 'false'
        try:
            pdist = memory_service.getData(pmemkey_dist)
            #print "personhere:: distance ",pdist
            if (personid>0 and pdist<1.5):
                v = 'true'
        except:
            v = 'false'

        set_condition(memory_service,'personhere',v)
        if (v=='true' and personid != last_personid):
            pangles = memory_service.getData(pmemkey_angles)
            ppos = memory_service.getData(pmemkey_pos)
            print 'personhere: ',str(personid),' dist: ', pdist, ' angle: ',pangles
            print 'personhere: ',str(personid),' Position (local): ',ppos
            memory_service.insertData('Actions/personhere/PersonAngleYaw',                    
                                      str(pangles[0]))
            memory_service.insertData('Actions/personhere/PersonAngleTurn',                    
                                      str((int)(pangles[0]/math.pi*180.0))+"_REL")
            memory_service.insertData('Actions/personhere/PersonID', personid)
            last_personid = personid


        time.sleep(0.5)
    print "personhere thread quit"



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

    # PARAMETERS
    zones_service.setFirstLimitDistance(1.5)
    zones_service.setSecondLimitDistance(2.5)
    zones_service.setLimitAngle(45)
    
    try:
        zoneDetection = memory_service.subscriber("EngagementZones/PersonEnteredZone1")
        idAnyDetection = zoneDetection.signal.connect(zone1_callback)   
    except RuntimeError:
        print "Cannot find ALEngagementZones service. Condition personhere not available"

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
