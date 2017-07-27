#!/usr/bin/env python

import qi
import argparse
import sys
import os
import time

import action_base
from action_base import *

# For each new action, add the following:
# import actionname
# actionname.init(session) in init function
# actionname.quit() in quit function

import dooropen, obstaclehere, screentouched
import say, vsay, wait, waitfor, goto, turn, lookfor, dialogue, dialoguestart, dialoguestop, asrenable
import posture, personhere, headpose, followuntil, movementdetected, webpage, personbehind, persondetected, speechbtn
import execplan, saveposition, soundtrack, navigateto, memorizepeople, memorizeface, sounddetected, continuebtn, enter, recdata, assign, reccam, gotopos
import personlost, peoplesummary

def init(session):
    screentouched.init(session)
    dooropen.init(session)
    obstaclehere.init(session)
    say.init(session)
    vsay.init(session)
    wait.init(session)
    waitfor.init(session)
    goto.init(session)
    turn.init(session)
    headpose.init(session)
    lookfor.init(session)
    dialogue.init(session)
    dialoguestart.init(session)
    dialoguestop.init(session)
    asrenable.init(session)
    posture.init(session)
    personhere.init(session)
    movementdetected.init(session)
    followuntil.init(session)
    personbehind.init(session)
    persondetected.init(session)
    execplan.init(session)
    saveposition.init(session)
    soundtrack.init(session)
    speechbtn.init(session)
    navigateto.init(session)
    memorizepeople.init(session)
    #memorizeface.init(session)
    sounddetected.init(session)
    continuebtn.init(session)
    enter.init(session)
    recdata.init(session)
    assign.init(session)
    personlost.init(session)
    peoplesummary.init(session)
    reccam.init(session)
    gotopos.init(session)

def quit():
    screentouched.quit()
    dooropen.quit()
    obstaclehere.quit()
    say.quit()
    vsay.quit()
    wait.quit()
    waitfor.quit()
    goto.quit()
    turn.quit()
    headpose.quit()
    lookfor.quit()
    dialogue.quit()
    dialoguestart.quit()
    dialoguestop.quit()
    asrenable.quit()
    posture.quit()
    personhere.quit()
    movementdetected.quit()
    followuntil.quit()
    personbehind.quit()
    persondetected.quit()
    execplan.quit()
    saveposition.quit()
    soundtrack.quit()
    speechbtn.quit()
    navigateto.quit()
    memorizepeople.quit()
    #memorizeface.quit()
    sounddetected.quit()
    enter.quit()
    continuebtn.quit()
    recdata.quit()
    assign.quit()
    personlost.quit()
    peoplesummary.quit()
    reccam.quit()
    gotopos.quit()

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
        app = qi.Application(["StartActions", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    init(session)

    app.run()    

    quit()

    time.sleep(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

