### register the utterance from the operator and interpret it with lu4r ###
import qi
import argparse
import sys
import time
import threading
import re

import action_base
from action_base import *

actionName = "extracttasks"


def actionThread_exec (params):
    global response, lu4r_command
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action "+actionName+" started with params "+params

    interpretation = ""

    # get the lu4r command
    interpretations = memory_service.getData("command_annotations")
    command_sentence = memory_service.getData("command_sentence")

    commands = {}
    to_say = ''
    #interpretation = interpretation.lower()
    #interpretation = interpretation.replace(")", "")
    #splitted = interpretation.split('(')
    #print splitted
    lu4r_interpretation = interpretations[0].lower()
    ws_interpretation = interpretations[1]

    int_dict = generateDict(lu4r_interpretation)
    print "LU4r DICTIONARY:", int_dict
    if "and" in int_dict.keys():
        int_dict = int_dict["and"]
    else:
        int_dict = [int_dict]

    memory_service.insertData("interpreted_tasks", str(int_dict))

    num_tasks = len(int_dict)
    memory_service.insertData("tasks_to_confirm", num_tasks)


    print int_dict
    print "Num tasks:", str(num_tasks)

    time.sleep(2)

    action_success(actionName,params)

def generateDict(inter, depth=1):
    frames_dict = {}

    start_fi = inter.find(" / ") + 3
    end_fi = inter.find("\n")
    frame, rest = inter[start_fi:end_fi], inter[end_fi:]

    if frame == "and":
        ops = rest.split("\n" + "\t"*depth + ":op")[1:]
        frame_ops_list = []
        for op in ops:
            frame_ops_list.append(generateDict(op, depth+1))

        frames_dict.update({frame: frame_ops_list})
    else:
        args = rest.split("\n" + "\t"*depth + ":")[1:]
        args_list = []
        for arg in args:
            end_ani = arg.find(" (")
            start_avi = arg.find(" / ") + 3
            arg_name, arg_value = arg[:end_ani], arg[start_avi:]
            if ":mod" in arg_value:
                splitted = arg_value.split("\t"*(depth+1) + ":mod")
                print splitted, arg_value
                arg_value = splitted[0][:splitted[0].find("\n")]
                mod_list = []
                for split in splitted[1:]:
                    start_mi, end_mi = split.find(" / ") + 3, split.find(")")
                    mod_list.append(split[start_mi:end_mi])
                args_list.append({arg_name: arg_value, "mods": mod_list})
            else:
                arg_value = arg_value[:arg_value.find(")")]
                args_list.append({arg_name : arg_value})

        frames_dict.update({frame: args_list})

    return frames_dict

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
