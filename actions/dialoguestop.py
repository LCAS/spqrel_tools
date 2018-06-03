import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "dialoguestop"

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    
    print "Action "+actionName+" "+params+" started"
    # action init
    memory_service.raiseEvent('DialogueVequest',params+'_stop')
    # action init
    
    time.sleep(1.0)

    # action end
    action_success(actionName,params)


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


