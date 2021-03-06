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


pepper_ip = ''
pepper_port = 9101

try:
    pepper_ip = os.getenv('PEPPER_IP')
except Exception as e:
    print "Please set PEPPER_IP environment variable."
    print e
    sys.exit(1)
    
import ws_client
from ws_client import *

import conditions
from conditions import *

actionName = "interactq"

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params

    modim_client = ModimWSClient()
    modim_client.setCmdServerAddr(pepper_ip, pepper_port)
    # action init
    count = 1
    # action init
    while (getattr(t, "do_run", True) and count>0):
        print "Action "+actionName+" "+params+" exec..."
        # action exec
	try:
            # set to false all the conditions in the action
            data_str = "im.listConditions('"+params+"')"
            rdata = modim_client.csend(data_str)

            ldata = eval(rdata) # rdata is the string representation of a list of strings
            # ldata is a list of conditions to set to false
            for cc in ldata:
                set_condition(memory_service, cc, 'false')
        #        print "Condition: ",cc,get_condition(memory_service, cc)
        except:
            print "listConditions failed"

        # now wait for the actual answer
        data_str = "im.ask('"+params+"')"
        #TODO make it interruptible !!!
        rdata = modim_client.csend(data_str)
        rdata = rdata.strip() # rdata is the answer of the ask action
            
        count = count - 1
        # action exec
        time.sleep(0.1)

    print "setting condition: %s true"%rdata
    set_condition(memory_service, rdata, 'true')
    # action end
    action_success(actionName,params)
    modim_client.cclose()


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
