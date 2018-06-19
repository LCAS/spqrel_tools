import qi
import re
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "asr"

response = None

asr_service = None

def onWordRecognized(msg):
    global response
    print "response=", msg
    response = msg[0]
    response = response.replace("<...> ", "").replace(" <...>", "")

def actionThread_exec (params):
    global response
    t = threading.currentThread()

    memory_service  = getattr(t, "mem_serv", None)

    #reset memory value
    memory_service.insertData("asrresponse", "")


    #establishing test vocabulary
    vocabulary = []
    if params == "drink":
        vocabulary = ["grape juice", "orange juice", "chocolate drink", "sprite", "coke"]
    elif params == "name":
        vocabulary = ["Alex", "Charlie", "Elizabeth", "Francis", "Jennifer", "Linda", "Mary", "Patricia", "Robin", "Skyler", "James", "John", "Michael", "Robert", "William"]
    elif params == "confirm":
        vocabulary = ["yes", "no"]

    asr_service.pause(True)
    asr_service.removeAllContext()
    try:
        asr_service.setVocabulary(vocabulary, True)
    except:
        print "error setting vocabulary"
    asr_service.pause(False)


    response = None
    #let it run
    while response is None:
        print "Waiting for an answer..."
        time.sleep(0.5)

    #save into memory
    memory_service.insertData("asrresponse", response)

    asr_service.pause(True)

    # action end
    action_success(actionName,params)

def init(session):
    global asr_service, asr_service_name, subWordRecognized, idSubWordRecognized
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

    #Starting services
    asr_service = session.service("ALSpeechRecognition")
    asr_service.setLanguage("English")

    memory_service = session.service("ALMemory")

    ## Start the speech recognition engine with user Test_ASR
    #asr_service_name = "Test_ASR" + str(time.time())
    #asr_service.subscribe(asr_service_name)


    #subscribe to event WordRecognized
    subWordRecognized = memory_service.subscriber("WordRecognized")
    idSubWordRecognized = subWordRecognized.signal.connect(onWordRecognized)

    asr_service.pause(True)

def quit():
    global subWordRecognized, idSubWordRecognized
    print actionName+" quit"
    #Disconnecting callbacks and subscribers
    subWordRecognized.signal.disconnect(idSubWordRecognized)

    #asr_service.unsubscribe(asr_service_name)

    asr_service.pause(True)

    actionThread_exec.do_run = False




if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
