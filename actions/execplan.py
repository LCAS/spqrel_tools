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


asrkey = "ASR_transcription"
lu4rkey = "CommandInterpretations"

def ASR_callback(data):
    global asr_value
    asr_value = data.strip()
    print "ASR callback: ",asr_value


def LU4R_callback(data):
    global lu4r_value    
    lu4r_value = data.strip()
    print "LU4R callback: ",lu4r_value



def LU4R_to_plan(lu4r):
    return "vsay_starting; waitfor_screentouched; vsay_farewell;"


# non-blocking function
def doExecPlan(memory_service, lu4r_value):

    print " *** DEBUG *** ASR_enable set to 0 !!!"
    memory_service.raiseEvent("ASR_enable","0")

    plan = LU4R_to_plan(lu4r_value)

    cmd = 'cd ../plans; echo "'+plan+'" > GPSR_task.plan'
    os.system(cmd)

    cmd = 'cd ../plans; pnpgen_translator inline GPSR_task.plan' # ER ???
    os.system(cmd)

    
    print " *** DEBUG *** ASR_enable value = ", memory_service.getData("ASR_enable")

    cmd = 'cd ../plans; ./run_plan.py --plan GPSR_task'
    os.system(cmd)

    print " *** DEBUG *** ASR_enable value = ", memory_service.getData("ASR_enable")




def actionThread_exec (params):
    global asr_value, lu4r_value

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

    # action init
    command_understood = False    
    max_repetitions = 3 # max number of requests of repetitions of the command
    repetitions = 0
    memory_service.raiseEvent("ASR_enable","1")
    # action init

    while (not command_understood and repetitions < max_repetitions and getattr(t, "do_run", True)):

        # wait for command
        print '   -- Waiting for command'
        asr_value=''
        lu4r_value=''
        while (getattr(t, "do_run", True) and asr_value=='' and lu4r_value==''): 
            time.sleep(0.5)    

        if (lu4r_value!=''):
            print '   -- Command received: ',asr_value,' -> ',lu4r_value

            if (lu4r_value=='NO FRAME(S) FOUND'):                
                repetitions = repetitions + 1
                if (repetitions < max_repetitions):
                    memory_service.raiseEvent('DialogueVequest',"say_SOFTFAILUREMANAGEMENT")
            else:
                command_understood = True                

    if (command_understood):
        # compose and start plan
        doExecPlan(memory_service, lu4r_value)  # non-blocking
        # wait for end of plan execution
        val = 0
        while (getattr(t, "do_run", True) and val==0): 
            time.sleep(2)
            try:
                actpl = memory_service.getData("PNP/ActivePlaces")
            except:
                actpl = ""
            #print "    [DEBUG] active places: ",actpl
            if ("goal" in actpl):
                val = 1
            
    else:
        memory_service.raiseEvent('DialogueVequest',"say_GIVEUP")


    print "Action "+actionName+" "+params+" terminated"
    # action end
    cmd = "cd ../plans; ./run_plan.py --plan stop"
    os.system(cmd)
    memory_service.raiseEvent("ASR_enable","0")
    # action end
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


def init(session):
    global sub1, sub2, idsub1, idsub2
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

    memory_service  = session.service("ALMemory")
    try:
        sub1 = memory_service.subscriber(asrkey)
        idsub1 = sub1.signal.connect(ASR_callback)
        sub2 = memory_service.subscriber(lu4rkey)
        idsub2 = sub2.signal.connect(LU4R_callback)
    except RuntimeError:
        print "Cannot subscribing to keys ",asrkey,lu4rkey



def quit():
    global sub1, sub2, idsub1, idsub2
    print actionName+" quit"
    actionThread_exec.do_run = False
    sub1.signal.disconnect(idsub1)
    sub2.signal.disconnect(idsub2)

    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


