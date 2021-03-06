### register the utterance from the operator and interpret it with lu4r ###
import qi
import re
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "understandcommand"

intkey = "CommandInterpretation"

interpretations = None


def interpretations_callback(data):
    global interpretations
    interpretations = data #.strip()
    print "Interpretations: ", eval(interpretations)

def actionThread_exec (params):
    global interpretations
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    sub2 = memory_service.subscriber(intkey)
    idsub2 = sub2.signal.connect(interpretations_callback)


    #tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

   # memory_service.insertData("GoogleTranscription", "What's the longest street in the world?")

    memory_service.raiseEvent("UnderstandCommand", (str(params)))

    memory_service.insertData("CommandInterpretation", [])

    interpretations = None

    while (getattr(t, "do_run", True) and interpretations is None):
        print "Waiting for interpretation..."
        time.sleep(0.5)

    if interpretations is not None and len(interpretations) > 0:
        memory_service.insertData("command_understood", 1)
        memory_service.insertData("CommandInterpretation", interpretations)


    # action end
    action_success(actionName,params)

    sub2.signal.disconnect(idsub2)


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
