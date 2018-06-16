#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION


import qi
import argparse
import sys
import os
import time
import threading
import math

from naoqi import ALProxy

import conditions
from conditions import set_condition

import requests
import json



'''
action iotget_sensor
Stores into a memory position the status of the sensor.
In openhab sensor names use the structure room_type_magnitude, so here are provided using slashes.
E.g.
    iotget_Kitchen-Multi-Presence -> sensor is resolved as Kitchen_Multi_Presence


'''




actionName = "iotget"
mem_key0 = "Actions/iotstatus"


baseURL = 'https://openhab.ngrok.lcas.group'
port = 4433

memory_service =None


def getStatus(itemName,baseURL,port):
    url = baseURL + ':' + str(port)+ '/rest/items/' + itemName + '/state'

    resp = requests.get(url)

    if(resp.ok):
        ans = resp.content
        #jresp = json.loads(resp.content)
        #print("Status of sensor {0} is {1}".format(itemName,jresp))
    else:
        resp.raise_for_status()
        return
    return ans

def setStatus(itemName,baseURL,port,newVal):    
    set_url = baseURL + ':' + str(port)+ '/rest/items/' + itemName 
    headers = {'Content-Type': 'text/plain'}
    resp = requests.post(set_url, headers=headers,data = newVal)
    if(not resp.ok):        
        resp.raise_for_status()
    return resp.ok

def parseSensor(params):
    return params.replace('-','_')


def actionThread_exec (params):
    global memory_service
    global baseURL
    global port

    itemName = parseSensor(params)    

    # action init
    count = 1

    # action exec
    while (getattr(t, "do_run", True) and count > 0): 
        val=getStatus(itemName,baseURL,port)
        print("Status of sensor {0} is [{1}]".format(itemName,val))    

        mem_key = mem_key0 + '/'+ itemName + "/value"
        memory_service.insertData(mem_key, str(val))

        count -= 1

    # action end
    action_success(actionName,params)



def init(session):
    global memory_service

    #Starting services
    memory_service  = session.service("ALMemory")

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


