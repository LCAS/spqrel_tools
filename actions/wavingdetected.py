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

waving_person_id = 0

def waving_callback(data):
    global wavingdetected
    global wavingpersonid
    global wavingpersonx
    global wavingpersony

    #data = category ,confidence, xmin,ymin,xmax,ymax
    confidence = memory_service.getData("Actions/PeopleWaving/person01/WaveProbability")
    xmin = memory_service.getData("Actions/PeopleWaving/person01/BBox/Xmin")
    xmax = memory_service.getData("Actions/PeopleWaving/person01/BBox/Xmax")
    ymin = memory_service.getData("Actions/PeopleWaving/person01/BBox/Ymin")
    ymax = memory_service.getData("Actions/PeopleWaving/person01/BBox/Ymax")

    x_wave = (float(xmax) - float(xmin)) / 2
    y_wave = (float(ymax) - float(ymin)) / 4 + float(ymin)

    # compute the closest person identified to the waving coordinates
    plist = memory_service.getData("PeoplePerception/VisiblePeopleList")

    max_distance = 100000000
    closest_waving_person_id = 0


    print " [  WAVING DETECTED  ]"
    
    for personid in plist:
        
        pmemkey_isface   = "PeoplePerception/Person/"+str(personid)+"/IsFaceDetected"
        data = memory_service.getData(pmemkey_isface)

        if data == 0:
            print "       Person ID: ",personid , "- NO Face detected "       

        else:
            pmemkey_face   = "PeoplePerception/Person/"+str(personid)+"/FacialPartsProperties"
            data = memory_service.getData(pmemkey_face)

            # Upper mouth coordinates
            y_person_mouth = data[11][0][1]
            x_person_mouth = data[11][0][0]

            distance = math.sqrt(math.pow(x_wave-x_person_mouth,2) + math.pow(y_wave-y_person_mouth,2))
            print "       Person ID: ",personid , "- Pixel Dist: ",distance, "- Confidence: ", confidence  

            if distance < max_distance:
                closest_waving_person_id = personid
                max_distance = distance

    if closest_waving_person_id == 0:
        print "\n"
        print "       [  NO PERSON ID WAVING fOUND ]"
        print "\n"
        wavingdetected = 0
    else:
        pmemkey_pos    = "PeoplePerception/Person/"+str(closest_waving_person_id)+"/PositionInRobotFrame"
        data = memory_service.getData(pmemkey_pos)

        print "       [  PERSON WAVING  ]"
        print "              Person ID: ", closest_waving_person_id
        print "              Person X:  ", data[1]  #still dont know if this is the correct one
        print "              Person Y:  ", data[2]  #still dont know if this is the correct one
        print "\n"

        wavingpersonid = closest_waving_person_id
        wavingpersonx = data[1]
        wavingpersony = data[2]
    
        wavingdetected = 1
 


def rhMonitorThread (memory_service):
    global wavingdetected
    global wavingpersonid
    global wavingpersonx
    global wavingpersony

    wavingdetected = 0

    t = threading.currentThread()
    print "personhere thread started"

    while getattr(t, "do_run", True):
        plist = memory_service.getData("PeoplePerception/VisiblePeopleList")
        v = 'false'

        wavingDetection = memory_service.subscriber("Actions/PeopleWaving/NewDetection")
        idAnyDetection = wavingDetection.signal.connect(waving_callback)   

        if wavingdetected == 1:
            memory_service.insertData('Actions/wavingdetected/wavingpersonid',str(wavingpersonid))
            memory_service.insertData('Actions/wavingdetected/wavingpersonx',str(wavingpersonx))
            memory_service.insertData('Actions/wavingdetected/wavingpersony',str(wavingpersony))
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