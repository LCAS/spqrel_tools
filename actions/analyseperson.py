#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
# http://doc.aldebaran.com/2-5/naoqi/peopleperception/alengagementzones-api.html#alengagementzones-api

import qi
import argparse
import sys
import time
import threading
import json

import action_base

import os

actionName = "analyseperson"


person_analysis_outcome_received = False


def _on_result(data):
    global person_analysis_outcome_received
    print 'received result'
    person_analysis_outcome_received = True
    pass


def actionThread_exec(params):
    global person_analysis_outcome_received
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action " + actionName + " started with params " + params

    _sub = memory_service.subscriber('/ros/detect_people/fusion')
    _sub.signal.connect(_on_result)

    while getattr(t, "do_run", True) and not person_analysis_outcome_received:
        print "Action " + actionName + " running params " + params
        try:
            memory_service.raiseEvent('trigger_person_analysis', 'none')
            break
        except Exception as e:
            print 'EXCEPTION: %s' % str(e)
            break
    # action exec
    time.sleep(0.1)

    # action end
    action_success(actionName,params)


def init(session):
    print actionName + " init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName + " quit"
    actionThread_exec.do_run = False


if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    # Program stays at this point until we stop it
    app.run()

    quit()


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

    # Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ", connection_url
        app = qi.Application(["PersonHere", "--qi-url=" + connection_url])
    except RuntimeError:
        print (
            "Can't connect to Naoqi at ip \"" + pip + "\" on port " +
            str(pport) + ".\n"
            "Please check your script arguments. Run with -h option for help."
        )
        sys.exit(1)

    app.start()
    session = app.session
    init(session)

    app.run()


if __name__ == "__main__":
    main()
