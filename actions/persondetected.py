#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
#http://doc.aldebaran.com/2-4/naoqi/peopleperception/alpeopleperception-api.html#alpeopleperception-api

import qi
import argparse
import sys
import os
import time

from naoqi import ALProxy

import conditions
from conditions import set_condition

def person_callback(data):
    print "Person detected!"
    print "ID: ",data
    set_condition(memory_service,'persondetected','true')
    time.sleep(1)
    set_condition(memory_service,'persondetected','false')


def init(session,app):
    global memory_service
    
    print "Person detector init"

    #Starting services
    memory_service  = session.service("ALMemory")
    people_service = session.service("ALPeoplePerception")

    # PARAMETERS
    
    try:
        peopleDetection = memory_service.subscriber("PeoplePerception/JustArrived")
        idAnyDetection = peopleDetection.signal.connect(person_callback)   
    except RuntimeError:
        print "Cannot find ALPeoplePerception service. Condition personhere not available"


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
        app = qi.Application(["PersonDetected", "--qi-url=" + connection_url ])
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
