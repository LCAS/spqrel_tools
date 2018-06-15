import time
import threading

import action_base

#import headpose

headJointsNames = ["HeadYaw", "HeadPitch"]
headYaw = 0.0
headPitch = -0.2 # head up
actionName = "navigateto"


goal_reached = False
goal_failed = False


def navstatus_cb(value):
    # global tts_service
    global goal_reached
    global memory_service
    global goal_failed

    print "NAOqi Planner status: ", value
    # GoalReached, PathFound, PathNotFound, WaitingForGoal
    if value == 'Success':
        goal_reached = True
    elif value == 'Fail':
        goal_failed = True


def actionThread_exec(params):
    global goal_reached
    global memory_service
    # global tts_service
    global goal_failed

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")
    # tts_service = getattr(t, "session", None).service("ALTextToSpeech")

    print "Action " + actionName + " started with params " + params
    # tts_service.say("Going to location "+params)

    # action init
    target = params
    if target[0] == '^':
        target = memory_service.getData(target[1:])
    print "  -- Goto: " + str(target)
    mem_key_goal = "TopologicalNav/Goal"
    mem_key_status = "TopologicalNav/Status"

    acb = memory_service.subscriber(mem_key_status)
    acb.signal.connect(navstatus_cb)

    goal_reached = False
    goal_failed = False
    memory_service.raiseEvent(mem_key_goal, target)

    # action init
    while getattr(t, "do_run", True) and not goal_reached and not goal_failed:
        time.sleep(0.5)
    if not getattr(t, "do_run", True):
        # cancelled send empty goal to stop
        memory_service.raiseEvent(mem_key_goal, "")

    #headpose.moveHead(motion_service, headYaw, headPitch, headtime)
    print "Action " + actionName + " " + params + " terminated"
    # action end
    if goal_reached:
        action_base.action_success(actionName, params)
    else:
        action_base.action_failed(actionName, params)


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
