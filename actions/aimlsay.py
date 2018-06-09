### generate the sentence using AIML and pronounce it ###
import qi
import re
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "aimlsay"

response = None


def response_cb(msg):
    global response
    #print "RESPONSE received", msg
    regex = re.compile("(\[.*?\])")
    commands = re.findall(regex, msg)
    for command in commands:
        msg = msg.replace(command, "")
    response = msg

def actionThread_exec (params):
    global response
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    #tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

    acb = memory_service.subscriber("DialogueVesponse")
    acb.signal.connect(response_cb)
    print "Subscriber connected!"

    # action init
    memory_service.raiseEvent('ParseAIMLRequest', params)
    print "  -- aimlsay: "+params

    # wait for the response to arrive
    while (getattr(t, "do_run", True) and response is None):
        print "Wait, AIML is parsing sentence "
        # action exec
        time.sleep(0.5)

    # pronuonce the response
    memory_service.raiseEvent("Veply", response)

    val = 0
    # wait for tts done
    print "wait"
    while (getattr(t, "do_run", True) and val == 0):
        print "Wait text pronounced"
        val = memory_service.getData("ALTextToSpeech/TextDone")
        time.sleep(0.5)

    response = None
    # action end
    action_success(actionName,params)


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False



if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
