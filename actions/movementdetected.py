#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION

import qi
import argparse
import sys
import os
import time
import threading

from naoqi import ALProxy

import conditions
from conditions import set_condition


def rhMonitorThread (memory_service):
    t = threading.currentThread()
    times = []

    # PARAMETERS
    n_times = 12 #lenght of the array
    waving_delta = 5 #in seconds

    i = 0
    for i in range(0, n_times):
        times.append(0)
    #print "Movement detection started"
    
    while getattr(t, "do_run", True):
        data = memory_service.getData("MovementDetection/MovementInfo")
        if (len(data) != 0):
            t = int(data[0][0])
            #print t
            for i in range(0, n_times-1):
                times[i] = times[i+1]
            times[n_times-1] = t
            delta_t = times[n_times-1] - times[0]
            #print "delta: ", delta_t
        v = 'false'
        try:
            if (delta_t < waving_delta):
                print "waving!"
                v = 'true'
                for i in range(0, n_times):
                    times.append(0)
        except:
            v = 'false'
        set_condition(memory_service,'movementdetected',v)
        # print 'personhere = ',v

        time.sleep(0.2)
    print "personhere thread quit"



def init(session):
    global memory_service
    global monitorThread

    print "Movement detection init"

    #Starting services
    memory_service  = session.service("ALMemory")
    movement_service = session.service("ALMovementDetection")

    # PARAMETERS
    movement_service.setDepthSensitivity(0.1)

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Movement detection quit"
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
