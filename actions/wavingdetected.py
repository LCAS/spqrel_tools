# DOCUMENTATION
# http://doc.aldebaran.com/2-5/naoqi/peopleperception/alengagementzones-api.html#alengagementzones-api

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

wavingdetected = 0
waving_person_id = 0

def waving_callback(data):
    print "\n"
    print " [ New Detection with Manuel Code ] "
    print "\n"


    #data = category ,confidence, xmin,ymin,xmax,ymax
    xmin = memory_service.getData("Actions/PeopleWaving/Person01/BBox/Xmin")
    xmax = memory_service.getData("Actions/PeopleWaving/Person01/BBox/Xmax")
    ymin = memory_service.getData("Actions/PeopleWaving/Person01/BBox/Ymin")
    ymax = memory_service.getData("Actions/PeopleWaving/Person01/BBox/Ymax")

    x_wave = (xmax - xmin) / 2
    y_wave = (ymax - ymin) / 4

    # compute the closest person identified to the waving coordinates
    plist = memory_service.getData("PeoplePerception/PeopleList")

    max_distance = 100000000

    for personid in plist:
        pmemkey_face   = "PeoplePerception/Person/"+str(personid)+"/FacialPartsProperties"
        data = memory_service.getData(pmemkey_face)

        # Upper mouth coordinates
        y_person_mouth = data[11][0][1]
        x_person_mouth = data[11][0][0]

        distance = sqrt((x_wave-x_person_mouth)^2 + (y_wave-y_person_mouth)^2)
        if distance < max_distance
            waving_person_id = personid
            max_distance = distance

    pmemkey_pos    = "PeoplePerception/Person/"+str(waving_person_id)+"/PositionInRobotFrame"
    data = memory_service.getData(pmemkey_pos)

    print "\n"
    print " [  PERSON WAVING  ]"
    print "       Person ID: ", waving_person_id
    print "       Perons X:  ", data[1]  #still dont know if this is the correct one
    print "       Person Y:  ", data[2]  #still dont know if this is the correct one
    print "\n"

    wavingdetected = 1


def rhMonitorThread (memory_service):
    global last_personid
    t = threading.currentThread()
    print "personhere thread started"

    while getattr(t, "do_run", True):
        plist = memory_service.getData("PeoplePerception/VisiblePeopleList")
        v = 'false'

        wavingDetection = memory_service.subscriber("Actions/PeopleWaving/NewDetection")
        idAnyDetection = zoneDetection.signal.connect(waving_callback)   

        if wavingdetected == 1
            memory_service.insertData('Actions/wavingdetected/wavingpersonid',str(waving_person_id))
            memory_service.insertData('Actions/wavingdetected/wavingpersonx',)
            memory_service.insertData('Actions/wavingdetected/wavingpersony',)
            v = 'true'

        set_condition(memory_service,'wavingdetected',v)
        
        time.sleep(0.5)

    print "personhere thread quit"



def init(session):
    global memory_service
    global monitorThread

    print "Waving detection init"

    #Starting services
    memory_service  = session.service("ALMemory")
    zones_service = session.service("ALEngagementZones")
    people_service = session.service("ALPeoplePerception")
    

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Waving detection quit"
    monitorThread.do_run = False 