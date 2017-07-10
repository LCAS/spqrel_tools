import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "dialogue"

dialogue_response = False

def response_cb(value):
    global dialogue_response
    print value
    dialogue_response = True


def actionThread_exec (params):
    global dialogue_response
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    
    acb = memory_service.subscriber("DialogueVesponse")
    acb.signal.connect(response_cb)


    print "Action "+actionName+" "+params+" started"
    # action init	
    print "  -- Dialogue: "+params
    memory_service.raiseEvent('DialogueVequest',params+'_start')
    memory_service.raiseEvent('ASRPause',0)
    dialogue_response = False
    # action init
    while (getattr(t, "do_run", True) and not dialogue_response): 
        print "Action "+actionName+" "+params+" exec..."
        # action exec	
        # action exec
        time.sleep(0.5)

    print "Action "+actionName+" "+params+" terminated"
    # action end
    memory_service.raiseEvent('DialogueVequest',params+'_stop')
    memory_service.raiseEvent('ASRPause',1)
    # action end

    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)
    session.service("ALMemory").declareEvent('DialogueVequest')


def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


