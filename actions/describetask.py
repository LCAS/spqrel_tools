### register the utterance from the operator and interpret it with lu4r ###
import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "describetask"

def actionThread_exec (params):
    global response, lu4r_command
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    description = memory_service.getData("task_description")

    # pronuonce the description
    memory_service.raiseEvent("Veply", description)

    val = 0
    # wait for tts done
    print "wait"
    while (getattr(t, "do_run", True) and val == 0):
        print "Wait text pronounced"
        val = memory_service.getData("ALTextToSpeech/TextDone")
        time.sleep(0.5)

    # action end
    action_success(actionName,params)



def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

def quit():
    print actionName+" quit"


if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
