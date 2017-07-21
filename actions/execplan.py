import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *

# Input: LU4R string
# Output: starting the corresponding plan

actionName = "execplan"

def LU4R_to_plan(lu4r):
    return "say_starting; waitfor_screentouched; say_hello;"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

    # action init
    
    print "  -- LU4R string: ",params
    plan = LU4R_to_plan(params)
    print "  -- Plan to exec: ",plan 

    cmd = 'cd ../plans; echo "'+plan+'" > GPSR_task.plan'
    os.system(cmd)

    cmd = 'cd ../plans; pnpgen_translator inline GPSR_task.plan' # ER ???
    os.system(cmd)

    cmd = 'cd ../plans; ./run_plan.py --plan GPSR_task'
    os.system(cmd)

    val = 0
    # action init
    
    while (getattr(t, "do_run", True) and val==0): 
        # print "Action "+actionName+" "+params+" exec..."
        # action exec 
        val = 1 # "goal" in "PNP_current_places"
        # action exec
        time.sleep(0.5)


    print "Action "+actionName+" "+params+" terminated"
    # action end
    cmd = "cd ../plans; ./run_plan.py --plan stop"
    os.system(cmd)
    # action end
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


