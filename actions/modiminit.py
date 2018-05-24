import qi
import argparse
import sys
import time
import threading
import json

import action_base
from action_base import *

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print "Please set MODIM_HOME environment variable to MODIM folder."
    print e
    sys.exit(1)

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print "Please set MODIM_HOME environment variable to MODIM folder."
    print e
    sys.exit(1)
    
import ws_client
from ws_client import *

actionName = "modiminit"

#pepper_ip = '192.168.1.134' # ethernet
pepper_ip = '127.0.0.1'
pepper_port = 9101

def demopath(params):
    demo_path = os.getenv('DEMO_PATH')
    if demo_path == None:
        demo_path = os.getcwd()
        print "DEMO_PATH not set. Using " + demo_path + "."
        
    if (params=='cocktailparty'):
        return os.path.join(demo_path, "cocktail_party")

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params

    # action init
    count = 1
    setServerAddr(pepper_ip, pepper_port)
    # action init
    while (getattr(t, "do_run", True) and count>0): 
        print "Action "+actionName+" "+params+" exec..."
        # action exec
        print ("WS client:: sending data ...")
        data_str = "im.setProfile(['*', '*', 'en', '*'])"+"\n"
        data_str += "im.setPath('"+ demopath(params) +"')"+"\n###ooo###\n\n"
        csend(data_str)
        print ("WS client:: data sent")
        
        count = count - 1
        # action exec
        time.sleep(0.1)

    # action end
    print "Action "+actionName+" "+params+" terminated"
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


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


