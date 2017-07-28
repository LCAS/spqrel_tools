#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
# http://doc.aldebaran.com/2-5/naoqi/peopleperception/alengagementzones-api.html#alengagementzones-api

import qi
import argparse
import sys
import time
import threading

import action_base

import os
from utils import point2world


from math import fabs


def find_center_person(plist, memory_service):
    min_y = 1e8
    p_id = None
    try:
        for p in plist:
            positionInRobotFrame = memory_service.getData(
                "PeoplePerception/Person/" + str(p) +
                "/PositionInRobotFrame"
            )
            if fabs(positionInRobotFrame[1]) < min_y:
                min_y = fabs(positionInRobotFrame[1])
                px = positionInRobotFrame[0]
                py = positionInRobotFrame[1]

                p_id = p
        if p_id is not None:
            w_px, w_py = point2world(
                memory_service,
                [px - 1.5, py]
            )
            return p_id, w_px, w_py
        else:
            return -1, 0, 0

    except Exception as e:
        print '*** FAILED TO FIND CENTER PERSON: %s' % str(e)
        return -1, 0, 0


actionName = "storecentralperson"


def actionThread_exec(params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action " + actionName + " started with params " + params

    t = threading.currentThread()
    while getattr(t, "do_run", True):
        plist = memory_service.getData("PeoplePerception/VisiblePeopleList")
        try:
            if (len(plist) > 0):
                p_id, p_x, p_y = find_center_person(plist, memory_service)
                if p_id > 0:
                    memory_service.insertData("center_person/id", str(p_id))
                    memory_service.insertData("center_person/pose", [p_x, p_y])
            break
        except Exception as e:
            print 'EXCEPTION: %s' % str(e)
            break
    # action exec
    time.sleep(0.1)

    print "Action " + actionName + " " + params + " terminated"
    # action end

    # action end
    memory_service.raiseEvent("PNP_action_result_" + actionName, "success")


def init(session):
    print actionName + " init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName + " quit"
    actionThread_exec.do_run = False


if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
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

    #Starting application
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
