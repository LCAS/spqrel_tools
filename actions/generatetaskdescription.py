### register the utterance from the operator and interpret it with lu4r ###
import qi
import argparse
import sys
import time
import threading
import re

import action_base
from action_base import *

actionName = "generatetaskdescription"


def actionThread_exec (params):
    global response, lu4r_command
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action "+actionName+" started with params "+params

    tasks = eval(memory_service.getData("interpreted_tasks"))
    ttc = memory_service.getData("tasks_to_confirm")
    asr_string = memory_service.getData("command_sentence")

    current_task_i = len(tasks) - ttc
    current_task = tasks[current_task_i]
    print "Confirming:", str(current_task)

    to_say = getToSay(current_task, memory_service)

    print "Asking:", to_say

    memory_service.insertData("tasks_to_confirm", ttc-1)

    memory_service.insertData("task_description", to_say)

    action_success(actionName,params)

def clean_string(string):
    return string.replace('to ','').replace('the ','').replace('towards ','').replace('in ','').strip()

def to_memory_key(filler, memory_service):
    try:
        memory_key = memory_service.getData("/location_mapping/" + filler.replace(" ", "+"))
    except:
        return ''
    return memory_key

def getToSay(current_task, memory_service):
    action = ""
    to_say = ""
    dirty_frame = current_task.keys()[0]
    if "-" in dirty_frame:
        frame = dirty_frame.split("-")[1]
    else: frame = dirty_frame
    args = {}
    for arg in current_task[dirty_frame]:
        mods = ""
        for k in arg.keys():
            # put the mods togheter with the argvalue
            if k == "mods":
                mods = " ".join(arg["mods"]) + " "
            else:
                argk = k
                argv = arg[k]
        args.update({argk: mods + argv})
    if len(args) > 0:
        if frame == 'motion' or frame == 'arriving':
            to_say = to_say + "I understood that I need to go. "
            for arg in args:
                if 'goal' in arg:
                    filler = args[arg]
                    location = to_memory_key(filler, memory_service)
                    if len(location) == 0:
                        to_say = to_say + "I'm sorry, I understood the word " + filler + ", but I failed to ground it. "
            if len(location) > 0:
                to_say = to_say + "I understood that the location is " + filler + ". "
                action = action + 'navigateto_' + location + ';'
            #memory_service.raiseEvent("Veply", to_say)
        elif frame == 'cotheme':
            to_say = to_say + "I understood that I need to follow. "
            for arg in args:
                if 'cotheme' in arg:
                    filler = args[arg]
                    if "me" in filler:
                        filler = "you"
                    to_say = to_say + "I understood that I need to follow " + filler + ". I will do it until I receive the stop command. "
            if 'you' in filler:
                action = action + ' vsay_followyou; headpose_0_-20; followuntil_screentouched; '
            else:
                to_say = to_say + "I don't know how to identify Maria. Please, go on! "
            #memory_service.raiseEvent("Veply", to_say)
        elif frame == 'bringing' or frame == 'giving':
            theme_filler = ''
            theme_memory_key = ''
            goal_filler = ''
            goal_memory_key = ''
            to_say = to_say + "I understood that I need to bring. "
            for arg in args:
                if 'theme' in arg:
                    theme_filler = args[arg]
                    to_say = to_say + "I understood that the object is " + theme_filler + ". "
                    theme_memory_key = to_memory_key(theme_filler, memory_service)
                    if len(theme_memory_key) == 0:
                        to_say = to_say + "I'm sorry, I am not able to ground " + theme_filler + ". "
                if ('beneficiary' in arg) or ('recipient' in arg):
                    filler = args[arg]
                    if filler == 'me':
                        filler = 'you'
                    to_say = to_say + "I understood that I have to bring it to " + filler + ". "
                if 'goal' in arg:
                    goal_filler = args[arg]
                    goal_memory_key = to_memory_key(goal_filler, memory_service)
                    to_say = to_say + "I understood that the final position of the object will be " + goal_filler + ". "
                    if len(goal_memory_key) == 0:
                        to_say = to_say + "Sorry, I'm not allowed to bring the " + goal_filler + ". "
                if 'source' in arg:
                    source_filler = args[arg]
                    to_say = to_say + "I understood that the initial position of the object is " + source_filler + ". "
            if len(theme_memory_key) > 0:
                action = action + ' navigateto_' + theme_memory_key + '; vsay_cannottake; wait_10; '
            else:
                to_say = to_say + "I'm sorry, but I don't have the object " + theme_filler + " in my semantic map. "
            if len(goal_memory_key) > 0:
                action = action + ' navigateto_' + goal_memory_key + ';'
            else:
                to_say = to_say + "I'm sorry, but I don't have the goal of the action in my semantic map. "
            #memory_service.raiseEvent("Veply", to_say)
        elif frame == 'taking' or frame == 'manipulation':
            theme_filler = ''
            theme_memory_key = ''
            goal_filler = ''
            goal_memory_key = ''
            to_say = to_say + "I understood that I need to bring. "
            for arg in args:
                if 'theme' in arg:
                    theme_filler = args[arg]
                    to_say = to_say + "I understood that the object is " + theme_filler + ". "
                    theme_memory_key = to_memory_key(theme_filler, memory_service)
                    if len(theme_memory_key) == 0:
                        to_say = to_say + "I'm sorry, I am not able to ground " + theme_filler + ". "
                if 'source' in arg:
                    source_filler = args[arg]
                    to_say = to_say + "I understood that the initial position of the object is " + source_filler + ". "
            if len(theme_memory_key) > 0:
                action = action + ' navigateto_' + theme_memory_key + '; vsay_cannottake; wait_10; '
            else:
                to_say = to_say + "I'm sorry, but I don't have the object " + theme_filler + " in my semantic map. "
            #memory_service.raiseEvent("Veply", to_say)
        elif frame == 'locating':
            ground_filler = ''
            ground_memory_key = ''
            phenomenon_filler = ''
            phenomenon_memory_key = ''
            #to_say = to_say + "I understood that I need to find. "
            for arg in args:
                if ('ground' in arg) or ('entity' in arg):   # kitchen
                    ground_filler = args[arg]
                    ground_memory_key = to_memory_key(ground_filler, memory_service)
                    to_say = to_say + "I understood the entity to find is in " + ground_filler + ". "
                if 'phenomenon' in arg:
                    phenomenon_filler = args[arg]
                    phenomenon_memory_key = to_memory_key(phenomenon_filler, memory_service)
                    to_say = to_say + "I understood that I have to look for " + phenomenon_filler + ". "
            if len(phenomenon_memory_key) > 0:
                to_say = to_say + "I'm going to look for " + phenomenon_filler
                action = action + ' navigateto_' + phenomenon_filler + "; wait_10; vsay_notfound; wait_10;"
            elif len(ground_memory_key) > 0:
                to_say = to_say + "I'm going to look for " + ground_filler
                action = action + ' navigateto_' + phenomenon_filler + "; wait_10; vsay_notfound; wait_10;"
            else:
                tmp_filler = ""
                if phenomenon_filler != "" and ground_filler != "":
                    tmp_filler = "neither " + phenomenon_filler + " nor " + ground_filler
                elif phenomenon_filler != "":
                    tmp_filler = phenomenon_filler
                elif ground_filler != "":
                    tmp_filler = ground_filler
                if tmp_filler == "":
                    to_say = to_say + "I'm sorry, I did not understand what I have to find."
                else:
                    to_say = to_say + "I'm sorry, I don't have " + tmp_filler + " in my semantic map. "

            #memory_service.raiseEvent("Veply", to_say)
    else:
        print "No args"
        if frame == 'motion' or frame == 'arriving':
            to_say = to_say + "I understood that I need to go, but I don't know where. "
        elif frame == 'cotheme':
            to_say = to_say + "I just understood that I need to follow someone. "
        elif frame == 'bringing' or frame == 'giving':
            to_say = to_say + "I understood that I need to bring, but I didn't get what. "
        elif frame == 'taking' or frame == 'manipulation':
            to_say = to_say + "I understood that I need to take, but I don't know what. "
        elif frame == 'locating':
            to_say = to_say + "I understood that I need to search, but I don't know what. "
        #memory_service.raiseEvent("Veply", to_say)
        print "action:", action

    return to_say

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
