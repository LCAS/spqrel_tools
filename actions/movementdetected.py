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

times=[]
n_times = 15 #lenght of the array
waving_delta = 5 #in seconds


def movement_callback(value):
        #global memory_service
        
        time = int(value[0][0])
        for i in range(0, n_times-1):
            times[i] = times[i+1]
            times[n_times-1] = time
            delta_t = times[n_times-1] - times[0]
            if delta_t < waving_threshold:
                print "Continous Movement detected"
                set_condition(memory_service,'movementdetected','true')
                time.sleep(1)
                set_condition(memory_service,'movementdetected','false')


def init(session):
    global memory_service
    
    print "Movement detector init"

    #Starting services
    memory_service  = session.service("ALMemory")
    movement_service = session.service("ALMovementDetection")

    # PARAMETERS
    movement_service.setDepthSensitivity(0.1)
    
    try:
        movementDetection = memory_service.subscriber("MovementDetection/MovementDetected")
        idAnyDetection = movementDetection.signal.connect(movement_callback) 
    except RuntimeError:
        print "Cannot find ALMovementDetection service. Condition personhere not available"


def quit():
        print "Movement detector quit"


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
        app = qi.Application(["MovementDetected", "--qi-url=" + connection_url ])
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
