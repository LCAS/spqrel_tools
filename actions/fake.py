import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "fake"


def actionThread_exec(params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "FAKING action " + params
    # action init
    dt = 0.25
    count = 1.0 / dt
    # action init
    while (getattr(t, "do_run", True) and count > 0):
        # print "Action "+actionName+" "+params+" exec..."
        # action exec
        count = count - 1
        # action exec
        time.sleep(dt)
    print "FAKING " + params + " terminated"
    # action end
    count = 0
    # action end
    memory_service.raiseEvent("PNP_action_result_" + actionName, "success");


def init(session):
    print actionName + " init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName + " quit"
    actionThread_exec.do_run = False


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()

