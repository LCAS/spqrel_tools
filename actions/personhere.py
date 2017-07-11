#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
# http://doc.aldebaran.com/2-5/naoqi/peopleperception/alengagementzones-api.html#alengagementzones-api

import qi
import argparse
import sys
import os
import time

from naoqi import ALProxy

import conditions
from conditions import set_condition

# function called when the signal "EngagementZones/PersonEnteredZone1" is triggered
def zone1_callback(data):
    global memory_service
    print "Person has entered Zone 1"
    set_condition(memory_service,'personhere','true')
    time.sleep(1)
    set_condition(memory_service,'personhere','false')


def init(session):
    global memory_service
    
    print "Person here init"

    #Starting services
    memory_service  = session.service("ALMemory")
    zones_service = session.service("ALEngagementZones")

    # PARAMETERS
    zones_service.setFirstLimitDistance(1.5)
    zones_service.setSecondLimitDistance(2.5)
    zones_service.setLimitAngle(45)
    
    try:
        zoneDetection = memory_service.subscriber("EngagementZones/PersonEnteredZone1")
        idAnyDetection = zoneDetection.signal.connect(zone1_callback)   
    except RuntimeError:
        print "Cannot find ALEngagementZones service. Condition personhere not available"


def quit():
    print "Person here quit"


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