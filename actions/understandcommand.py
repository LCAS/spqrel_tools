### register the utterance from the operator and interpret it with lu4r ###
import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "understandcommand"

#asrkey = "ASR_transcription"
lu4rkey = "CommandInterpretations"

lu4r_command = ""

#def ASR_callback(data):
#    global asr_value
#    asr_value = data.strip()
#    print "ASR callback: ",asr_value


def LU4R_callback(data):
    global lu4r_command
    lu4r_command = data.strip()
    print "LU4R callback: ", lu4r_command

def actionThread_exec (params):
    global response, lu4r_command
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    #sub1 = memory_service.subscriber(asrkey)
    #idsub1 = sub1.signal.connect(ASR_callback)
    sub2 = memory_service.subscriber(lu4rkey)
    idsub2 = sub2.signal.connect(LU4R_callback)

    #tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

    memory_service.insertData("lu4r_command_understood", 0)

    lu4r_command = ""
    memory_service.raiseEvent("ASR_enable","1")

    while (getattr(t, "do_run", True) and lu4r_command == ""):
        print "Waiting lu4r interpretation"
        time.sleep(0.5)

    memory_service.raiseEvent("ASR_enable","0")

    if (lu4r_command != 'NO FRAME(S) FOUND'):
        memory_service.insertData("lu4r_command_understood", 1)
        memory_service.insertData("lu4r_command", lu4r_command)
        time.sleep(1)


    # action end
    action_success(actionName,params)


    #sub1.signal.disconnect(idsub1)
    sub2.signal.disconnect(idsub2)

def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

def quit():
    print actionName+" quit"
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    memory_service.raiseEvent("ASR_enable","0")
    actionThread_exec.do_run = False



if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
