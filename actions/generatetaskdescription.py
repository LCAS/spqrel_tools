### register the utterance from the operator and interpret it with lu4r ###
import qi
import argparse
import sys
import time
import threading
import random
import re
import pprint as pp

import action_base
from action_base import *

actionName = "generatetaskdescription"

SEMANTIC_INFO_MEM = "/semantic_info"

tasks_definition = []
objects = []
names = []
locations = []
questions = []


def actionThread_exec (params):
    global response, lu4r_command
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action "+actionName+" started with params "+params

    task = eval(memory_service.getData("CurrentTaskInterpretation"))

    # current_task_i = len(tasks) - ttc
    # current_task = tasks[current_task_i]
    print "Confirming:",
    pp.pprint(task)

    print "command:", str(params)

    to_say = getToSay(task)

    print "Asking:", to_say

    #memory_service.insertData("tasks_to_confirm", ttc-1)

    memory_service.insertData("task_description", to_say)

    # time.sleep(2)

    action_success(actionName,params)

def clean_string(string):
    return string.replace('to ','').replace('the ','').replace('towards ','').replace('in ','').strip()

def to_memory_key(filler, memory_service):
    try:
        memory_key = memory_service.getData("/location_mapping/" + filler.replace(" ", "+"))
    except:
        return ''
    return memory_key

def load_gpsr_xmls(memory_service):
    global gpsr_tasks_definition, spr_tasks_definition, objects, names, locations, questions
    gpsr_tasks_definition = eval(memory_service.getData(SEMANTIC_INFO_MEM + "/gpsr_tasks_definition") )
    spr_tasks_definition = eval(memory_service.getData(SEMANTIC_INFO_MEM + "/spr_tasks_definition") )
    objects = eval(memory_service.getData(SEMANTIC_INFO_MEM + "/objects") )
    names = eval(memory_service.getData(SEMANTIC_INFO_MEM + "/names") )
    locations = eval(memory_service.getData(SEMANTIC_INFO_MEM + "/locations") )
    questions = eval(memory_service.getData(SEMANTIC_INFO_MEM + "/questions") )
    print "Semantic info loaded!"

def resolveMultipleSpotted(task):
    verb_index = task["index"]
    for attribute in task["requires"]:
        if "spotted" in attribute.keys():
            num_spotted = len(attribute["spotted"])
            lowest_index = 1000
            lowest_attribute = None
            # TODO gound it
            if num_spotted > 0:
                for spot in attribute["spotted"]:
                    if spot["index"] < lowest_index and spot["index"] > verb_index:
                        lowest_attribute = spot
                        lowest_index = spot["index"]
            if lowest_attribute is not None:
                attribute["spotted"] = lowest_attribute
            if type(attribute["spotted"]) == list:
                attribute["spotted"] = attribute["spotted"][0]
    return task

def describeTaking(task):
    to_say = ""
    verb = task["verb"]

    obj = None
    loc = None
    for attribute in task["requires"]:
        if "spotted" in attribute.keys():
            num_spotted = len(attribute["spotted"])
            if num_spotted > 0:
                if "object" in attribute.keys():
                    obj = attribute["spotted"]["text"]
                elif "location" in attribute.keys():
                    loc = attribute["spotted"]["text"]

    print "obj:", obj, "loc:", loc
    if obj is None and loc is None:
        to_say = "I understood that I need to " + verb + " something but I didn't got what."
    elif obj is not None and loc is not None:
        to_say = "I understood that I need to " + verb + " the " + obj + " from the " + loc + "."
    elif obj is not None:
        to_say = "I understood that I need to " + verb + " the " + obj
    elif loc is not None:
        to_say = "I understood that I need to " + verb + " something from the " + loc + "."

    return to_say

def describePlacing(task):
    verb = task["verb"]
    to_say = ""

    obj = None
    loc = None
    for attribute in task["requires"]:
        if "spotted" in attribute.keys():
            num_spotted = len(attribute["spotted"])
            if num_spotted > 0:
                if "object" in attribute.keys():
                    obj = attribute["spotted"]["text"]
                elif "location" in attribute.keys():
                    loc = attribute["spotted"]["text"]

    print "obj:", obj, "loc:", loc
    if obj is None and loc is None:
        to_say = "I understood that I need to " + verb + " something but I didn't got what."
    elif obj is not None and loc is not None:
        to_say = "I understood that I need to " + verb + " the " + obj + " on the " + loc
    elif obj is not None:
        to_say = "I understood that I need to " + verb + " the " + obj + ", but I am not sure where."
    elif loc is not None:
        to_say = "I understood that I need to " + verb + " something on the "+ loc + "."
    return to_say

def describeLocating(task):
    verb = task["verb"]
    to_say = ""

    obj = None
    loc = None
    name = None
    for attribute in task["requires"]:
        if "spotted" in attribute.keys():
            num_spotted = len(attribute["spotted"])
            if num_spotted > 0:
                if "object" in attribute.keys():
                    obj = attribute["spotted"]["text"]
                elif "location" in attribute.keys():
                    loc = attribute["spotted"]["text"]
                elif "name" in attribute.keys():
                    name = attribute["spotted"]["text"]

    print "obj:", obj, "loc:", loc
    if obj is None and name is None:
        to_say = "I understood that I need to " + verb + " something but I didn't got what."
    elif obj is not None and loc is not None:
        to_say = "I understood that I need to " + verb + " the " + obj + " in the " + loc
    elif obj is not None:
        to_say = "I understood that I need to " + verb + " the " + obj
    elif name is not None:
        to_say = "I understood that I need to " + verb + " " + name

    return to_say

def describeBringing(task):
    verb = task["verb"]
    to_say = ""

    return to_say

def describeMotion(task):
    verb = task["verb"]
    to_say = ""

    loc = None
    for attribute in task["requires"]:
        if "spotted" in attribute.keys():
            num_spotted = len(attribute["spotted"])
            if num_spotted > 0:
                if "location" in attribute.keys():
                    loc = attribute["spotted"]["text"]

    print "loc:", loc
    if loc is None:
        to_say = "I understood that I need to " + verb + " but I didn't got where."
    else:
        to_say = "I understood that I need to " + verb + " to " + loc

    return to_say

def describeTell(task):
    verb = task["verb"]
    to_say = ""

    wts = None
    for attribute in task["requires"]:
        if "spotted" in attribute.keys():
            num_spotted = len(attribute["spotted"])
            if num_spotted > 0:
                if "whattosay" in attribute.keys():
                    wts = attribute["spotted"]["text"]

    print "wts:", wts
    if wts is None:
        to_say = "I understood that I need to " + verb + " something, but not what."
    else:
        to_say = "I understood that I need to " + verb +" "+ wts + "!"

    return to_say

def describeAnswer(task):
    verb = task["verb"]
    to_say = ""

    to_say = "I understood that I need to " + verb + "a question!"

    return to_say


#def describeTaking(task):
#    verb = random.choice(task["possible_verbs"])



def getToSay(current_task):
    current_task = resolveMultipleSpotted(current_task)
    pp.pprint(current_task)
    to_say = ""
    if current_task["task"] == "taking":
        to_say = describeTaking(current_task)
    elif current_task["task"] == "locating":
        to_say = describeLocating(current_task)
    elif current_task["task"] == "bringing":
        to_say = describeBringing(current_task)
    elif current_task["task"] == "motion":
        to_say = describeMotion(current_task)
    elif current_task["task"] == "tell":
        to_say = describeTell(current_task)
    elif current_task["task"] == "placing":
        to_say = describePlacing(current_task)
    elif current_task["task"] == "answer":
        to_say = describeAnswer(current_task)

    return to_say

def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

    memory_service = session.service("ALMemory")

    load_gpsr_xmls(memory_service)

def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False



if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
