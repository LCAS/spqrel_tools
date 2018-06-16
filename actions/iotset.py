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
action iotset_sensor_value
Sets the value of the sensor.
In openhab sensor names use the structure room_type_magnitude, so here are provided using slashes.
E.g.
    iotset_TV-Plug-Switch_ON -> sensor is resolved as TV_Plug_Switch


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

def parseVal(val):
    if 'ON' in val.upper():
        newval = b'ON'   
    else:
        newval = b'OFF'   
    return newval


def actionThread_exec (params):
    global memory_service
    global baseURL
    global port

    items = '_'.split()
    itemName = parseSensor(item[0])
    val = parseVal(item[1])    

    # action init
    count = 1

    # action exec
    while (getattr(t, "do_run", True) and count > 0): 
        setStatus(itemName,baseURL,port,val)

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


