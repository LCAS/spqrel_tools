#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION

import qi
import argparse
import sys
import os
import time

from naoqi import ALProxy, ALBroker, ALModule

import conditions
from conditions import set_condition

def wave_callback(data):
    global memory_service
    print "Person has waved"
    set_condition(memory_service,'wavedetected','true')
    time.sleep(1)
    set_condition(memory_service,'wavedetected','false')


def init(session,app):
    global memory_service

    print "Waving detector init"

    #Starting services
    memory_service  = session.service("ALMemory")
    waving_service = session.service("ALWavingDetection")

    #PARAMETERS
    waving_service.setMinSize(0.1)

    try:
        wavingDetection = memory_service.subscriber("WavingDetection/Waving")
        idAnyDetection = wavingDetection.signal.connect(wave_callback)   
    except RuntimeError:
        print "Cannot find ALWavingDetection. Condition wavedetected not available"

    app.run()

def quit():
    print "Waving detector quit"


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
        app = qi.Application(["WaveDetected", "--qi-url=" + connection_url ])
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
