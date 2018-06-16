import time


import action_base
from action_base import *

actionName = "taskstep"


def actionThread_exec(params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action " + actionName + " started with params " + params
    # action init

    memory_service.insertData("current_task_step", params.replace('_', ' '))
    memory_service.raiseEvent("current_task_step", params.replace('_', ' '))
    print "set current task step to: " + params

    # action init
    time.sleep(0.5)
    print "Action " + actionName + " " + params + " terminated"
    # action end

    # action end
    action_success(actionName, params)


def init(session):
    print actionName + " init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName + " quit"
    actionThread_exec.do_run = False


if __name__ == "__main__":

    app = action_base.initApp(actionName)
    init(app.session)
    app.run()
    quit()

