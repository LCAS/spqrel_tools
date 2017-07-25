import qi
import argparse
import sys
import time
import threading
import json

import action_base
from action_base import *

actionName = "dialogue"

dialogue_response = False

def response_cb(value):
    global dialogue_response
    print value
    dialogue_response = True


def actionThread_exec (params):
    global dialogue_response, orderID
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    
    acb = memory_service.subscriber("DialogueVesponse")
    acb.signal.connect(response_cb)


    print "Action "+actionName+" "+params+" started"
    # action init	
    print "  -- Dialogue: "+params
    memory_service.raiseEvent('DialogueVequest',params+'_start')
    
    dialogue_response = False
    # action init
    while (getattr(t, "do_run", True) and not dialogue_response): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec	
        # action exec
        time.sleep(0.5)

    print "Action "+actionName+" "+params+" terminated"
    # action end
    memory_service.raiseEvent('DialogueVequest',params+'_stop')
    
    if (params=='takeorder' and dialogue_response):
        pinfo = memory_service.getData('DialogueVesponse')
        try:
            json.loads(pinfo)
            orderID = orderID+1
            memkey = "Humans/Profile"+str(orderID)
            memory_service.insertData(memkey, pinfo)
        except:
            print "Not a valid JSON file"

    # TODO acb. disconnect...
    # action end

    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


def init(session):
    global orderID
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)
    session.service("ALMemory").declareEvent('DialogueVequest')
    orderID = 0


def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


