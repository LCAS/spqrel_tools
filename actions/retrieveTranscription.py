### register the utterance from the operator and interpret it with lu4r ###
import qi
import re
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "retrieveTranscription"

asrkey = "ASR_transcription"

asr_value = ""

def ASR_callback(data):
    global asr_value
    asr_value = data.strip()
    print "__ASR callback: ",asr_value

def actionThread_exec (params):
    global asr_value
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    sub1 = memory_service.subscriber(asrkey)
    idsub1 = sub1.signal.connect(ASR_callback)

    #tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

    asr_value = ""
    memory_service.insertData("transcription_retrieved", "")

    while (getattr(t, "do_run", True) and asr_value == ""):
        print "Waiting for transcription", asr_value
        time.sleep(0.5)


    memory_service.insertData("transcription_retrieved", asr_value)

    # action end
    action_success(actionName,params)


    sub1.signal.disconnect(idsub1)


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
