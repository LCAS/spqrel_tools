import qi
import argparse
import sys
import time
import threading
import subprocess
import re

import action_base
from action_base import *

# Input: LU4R string
# Output: starting the corresponding plan

actionName = "execplan"

gpsrtaskname = "GPSRtask"

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


def clean_string(string):
    return string.replace('to ','').replace('the ','').replace('towards ','').replace('in ','').strip()


def get_filler(argument):
    argument_splitted = argument.split(':')
    filler = argument_splitted[1].replace('"', '')
    filler = clean_string(filler)
    return filler


def to_memory_key(filler, memory_service):
    try:
        memory_key = memory_service.getData("/location_mapping/" + filler.replace(" ", "+"))
    except:
        return ''
    return memory_key



def LU4R_to_plan(lu4r, asr_value, memory_service):

    text2lu4 = Test2lu4(pairs_say, reflections)
    #lu4r = lu4r + "#" + text2lu4.inputtext(asr_value)
    interpretations = lu4r.split("#")
    action = ''
    for interpretation in interpretations:
        to_say = ''
        if not interpretation:
            continue
        interpretation = interpretation.replace(")", "")
        splitted = interpretation.split('(')
        frame = splitted[0]
        if len(splitted) > 1:
            arguments_string = splitted[1]
            arguments = arguments_string.split(',')
            if frame == 'MOTION' or frame == 'ARRIVING':
                to_say = to_say + "I understood that I need to go. "
                for argument in arguments:
                    if 'goal' in argument:
                        filler = get_filler(argument)
                        location = to_memory_key(filler, memory_service)
                        if len(location) == 0:
                            to_say = to_say + "I'm sorry, I understood the word " + filler + ", but I failed to ground it. "
                if len(location) > 0:
                    to_say = to_say + "I understood that the location is " + filler + ". "
                    action = action + 'navigateto_' + location + ';'
                memory_service.raiseEvent("Veply", to_say)
            elif frame == 'COTHEME':
                to_say = to_say + "I understood that I need to follow. "
                for argument in arguments:
                    if 'cotheme' in argument:
                        filler = get_filler(argument)
                        if "me" in filler:
                            filler = "you"
                        to_say = to_say + "I understood that I need to follow " + filler + ". I will do it until I receive the stop command. "
                if 'you' in filler:
                    action = action + ' vsay_followyou; headpose_0_-20; followuntil_screentouched; '
                else:
                    to_say = to_say + "I don't know how to identify Maria. Please, go on! "
                memory_service.raiseEvent("Veply", to_say)
            elif frame == 'BRINGING' or frame == 'GIVING':
                theme_filler = ''
                theme_memory_key = ''
                goal_filler = ''
                goal_memory_key = ''
                to_say = to_say + "I understood that I need to bring. "
                for argument in arguments:
                    if 'theme' in argument:
                        theme_filler = get_filler(argument)
                        to_say = to_say + "I understood that the object is " + theme_filler + ". "
                        theme_memory_key = to_memory_key(theme_filler, memory_service)
                        if len(theme_memory_key) == 0:
                            to_say = to_say + "I'm sorry, I am not able to ground " + theme_filler + ". "
                    if ('beneficiary' in argument) or ('recipient' in argument):
                        filler = get_filler(argument)
                        if filler == 'me':
                            filler = 'you'
                        to_say = to_say + "I understood that I have to bring it to " + filler + ". "
                    if 'goal' in argument:
                        goal_filler = get_filler(argument)
                        goal_memory_key = to_memory_key(goal_filler, memory_service)
                        to_say = to_say + "I understood that the final position of the object will be " + goal_filler + ". "
                        if len(goal_memory_key) == 0:
                            to_say = to_say + "Sorry, I'm not allowed to bring the " + goal_filler + ". "
                    if 'source' in argument:
                        source_filler = get_filler(argument)
                        to_say = to_say + "I understood that the initial position of the object is " + source_filler + ". "
                if len(theme_memory_key) > 0:
                    action = action + ' navigateto_' + theme_memory_key + '; vsay_cannottake; wait_10; '
                else:
                    to_say = to_say + "I'm sorry, but I don't have the object " + theme_filler + " in my semantic map. "
                if len(goal_memory_key) > 0:
                    action = action + ' navigateto_' + goal_memory_key + ';'
                else:
                    to_say = to_say + "I'm sorry, but I don't have the goal of the action in my semantic map. "
                memory_service.raiseEvent("Veply", to_say)
            elif frame == 'TAKING' or frame == 'MANIPULATION':
                theme_filler = ''
                theme_memory_key = ''
                goal_filler = ''
                goal_memory_key = ''
                to_say = to_say + "I understood that I need to bring. "
                for argument in arguments:
                    if 'theme' in argument:
                        theme_filler = get_filler(argument)
                        to_say = to_say + "I understood that the object is " + theme_filler + ". "
                        theme_memory_key = to_memory_key(theme_filler, memory_service)
                        if len(theme_memory_key) == 0:
                            to_say = to_say + "I'm sorry, I am not able to ground " + theme_filler + ". "
                    if 'source' in argument:
                        source_filler = get_filler(argument)
                        to_say = to_say + "I understood that the initial position of the object is " + source_filler + ". "
                if len(theme_memory_key) > 0:
                    action = action + ' navigateto_' + theme_memory_key + '; vsay_cannottake; wait_10; '
                else:
                    to_say = to_say + "I'm sorry, but I don't have the object " + theme_filler + " in my semantic map. "
                memory_service.raiseEvent("Veply", to_say)
            elif frame == 'LOCATING':
                ground_filler = '';
                ground_memory_key = '';
                phenomenon_filler = ''
                phenomenon_memory_key = ''
                to_say = to_say + "I understood that I need to find. "
                for argument in arguments:
                    if ('ground' in argument) or ('entity' in argument):   # kitchen
                        ground_filler = get_filler(argument)
                        ground_memory_key = to_memory_key(ground_filler, memory_service)
                        to_say = to_say + "I understood the entity to find is in " + ground_filler + ". "
                    if 'phenomenon' in argument:
                        phenomenon_filler = get_filler(argument)
                        phenomenon_memory_key = to_memory_key(phenomenon_filler, memory_service)
                        to_say = to_say + "I understood that I have to look for " + phenomenon_filler + ". "
                if len(phenomenon_memory_key) > 0:
                    to_say = to_say + "I'm going to look for " + phenomenon_filler
                    action = action + ' navigateto_' + phenomenon_filler + "; wait_10; vsay_notfound; wait_10;"
                elif len(ground_memory_key) > 0:
                    to_say = to_say + "I'm going to look for " + ground_filler
                    action = action + ' navigateto_' + phenomenon_filler + "; wait_10; vsay_notfound; wait_10;"
                else:
                    to_say = to_say + "I'm sorry, I don't have neither " + phenomenon_filler + " nor " + ground_filler + " in my semantic map. "
                memory_service.raiseEvent("Veply", to_say)
        else:
            print "No arguments"
            if frame == 'MOTION' or frame == 'ARRIVING':
                to_say = to_say + "I understood that I need to go, but I don't know where. "
            elif frame == 'COTHEME':
                to_say = to_say + "I just understood that I need to follow someone. "
            elif frame == 'BRINGING' or frame == 'GIVING':
                to_say = to_say + "I understood that I need to bring, but I didn't get what. "
            elif frame == 'TAKING' or frame == 'MANIPULATION':
                to_say = to_say + "I understood that I need to take, but I don't know what. "
            elif frame == 'LOCATING':
                to_say = to_say + "I understood that I need to search, but I don't know what. "
            memory_service.raiseEvent("Veply", to_say)
    if len(action) == 0:
        return 'vsay_nextquestion; '
    else:
        return action


# non-blocking function
def doExecPlan(memory_service, lu4r_value, asr_value):

    #print " *** DEBUG *** ASR_enable set to 0 !!!"
    memory_service.raiseEvent("ASR_enable","0")

    plan = LU4R_to_plan(lu4r_value, asr_value, memory_service)
    os.chdir(os.environ["PLAN_DIR"])
    cmd = 'cd ../plans; echo "'+plan+'" > '+gpsrtaskname+'.plan'
    os.system(cmd)

    cmd = 'cd ../plans; pnpgen_translator inline '+gpsrtaskname+'.plan' # ER ???
    os.system(cmd)

    try:
        task = subprocess.check_output('cat ./'+gpsrtaskname+'.plan', shell=True, cwd=os.environ["PLAN_DIR"])
        memory_service.raiseEvent('/gpsr/plan', task)
    except Exception as e:
        print e

    #print " *** DEBUG *** ASR_enable value = ", memory_service.getData("ASR_enable")

    #cmd = 'cd ../plans; ./run_plan.py --plan '+gpsrtaskname
    #os.system(cmd)

    #print " *** DEBUG *** ASR_enable value = ", memory_service.getData("ASR_enable")


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
        doExecPlan(memory_service, lu4r_value, asr_value)  # non-blocking
        # wait for end of plan execution
        #val = 0
        #while (getattr(t, "do_run", True) and val==0): 
        #    time.sleep(2)
        #    try:
        #        actpl = memory_service.getData("PNP/ActivePlaces")
        #    except:
        #        actpl = ""
        #    #print "    [DEBUG] active places: ",actpl
        #    if ("goal" in actpl):
        #        val = 1
            
    else:
        memory_service.raiseEvent('DialogueVequest',"say_GIVEUP")


    # action end
    #cmd = "cd ../plans; ./run_plan.py --plan GPSR2"
    #os.system(cmd)
    memory_service.raiseEvent("ASR_enable","0")
    action_success(actionName,params)


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

pairs_say = (
  (r'(tell me|say) something about yourself',
  ( "SAY(message=\"peppino\") ")),
  (r'(tell me|say) the time',
  ( "SAY(message=\"time\") ")),
  (r'(tell me|say) what day is tomorrow',
  ( "SAY(message=\"tomorrow\") ")),
  (r'(tell me|say) what day is today',
  ( "SAY(message=\"day\") ")),
  (r'(tell me|say) your team name',
  ( "SAY(message=\"teamname\") ")),
  (r'(tell me|say) your country ',
  ( "SAY(message=\"teamcountry\") ")),
  (r'(tell me|say) your team affiliation',
  ( "SAY(message=\"teamaffiliation\") ")),
  (r'(tell me|say) (.*) day (.*) week',
  ( "SAY(message=\"weekday\") ")),
  (r'(tell me|say) (.*) day (.*) month',
  ( "SAY(message=\"monthday\") ")),
  (r'(tell me|say) (.*) joke',
  ( "SAY(message=\"joke\") ")),
  (r'(tell|say) (.*) joke to (.*) in (.*)',
  ( "SAY(message=\"joke\",beneficiary=\" %2 \",goal=\" %1 \") ")),
  (r'answer a question (.*)',
  ( "ANSWER(message=\"joke\") ")),
  (r'navigate (.*) ',
  ( "SAY(message=\"joke\") ")),
  (r'(tell me|say) how many (.*) there are (.*)',
  ( "BEING_LOCATED(located=\"%3\", theme=\"%2\") ")),
  (r'how many (.*) there are (.*)',
  ( "BEING_LOCATED(located=\"%2\", theme=\"%1\")")),
)

reflections = {
  "the "       : "",
  "in the "       : "",
  "to the "       : "",
  "at the "       : "",
  "on the "       : ""
}


class Test2lu4(object):
    def __init__(self, pairs, reflections={}):

        self._pairs = [(re.compile(x, re.IGNORECASE), y) for (x, y) in pairs_say]
        self._reflections = reflections
        self._regex = self._compile_reflections()

    def _compile_reflections(self):
        sorted_refl = sorted(self._reflections.keys(), key=len,
                             reverse=True)
        return re.compile(r"\b({0})\b".format("|".join(map(re.escape,
                                                           sorted_refl))), re.IGNORECASE)

    def _substitute(self, str):

        # Substitute words in the string, according to the specified reflections,

        return self._regex.sub(lambda mo:
                               self._reflections[mo.string[mo.start():mo.end()]],
                               str.lower())

    def _wildcards(self, response, match):
        pos = response.find('%')
        while pos >= 0:
            num = int(response[pos + 1:pos + 2])
            response = response[:pos] + \
                       self._substitute(match.group(num)) + \
                       response[pos + 2:]
            pos = response.find('%')
        return response

    def inputtext(self, txt):
        # check each pattern
        for (pattern, response) in self._pairs:
            # print 'pattern=',str(pattern)
            match = pattern.match(txt)

            if match:
                if len(response) > 1:
                    resp = response

                resp = self._wildcards(resp, match)  # process wildcards
                return resp
        return ''

if __name__ == "__main__":

    app = action_base.initApp(actionName)

        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


