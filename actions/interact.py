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

import ws_client
from ws_client import *

actionName = "interact"

#pepper_ip = '192.168.1.134' # ethernet
pepper_ip = '127.0.0.1'
pepper_port = 9101

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params

    # action init
    count = 1
    #cconnect()
    #csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #csock.connect((server_ip,server_port))
    #print ("WS client:: connected to %s:%d" %(server_ip, server_port))
    # action init
    while (getattr(t, "do_run", True) and count>0): 
        print "Action "+actionName+" "+params+" exec..."
        # action exec
        #csend
        data_str = "im.execute('"+params+"')"+"\n###ooo###\n\n"

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

