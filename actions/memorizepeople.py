#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alpeopleperception-api.html#PeoplePerception
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alfacedetection.html

'''
Memorize people
==================

Writes in ALMemory 'Actions/memorizepeople/PeopleList/' array with peoplelist 

Writes in 'Actions/memorizepeople/Person/IDNUMBER' for each person detected the json data

IDNUMBER for now is the same as the personid providede by PeopleDetected

TODO
-----
Topological position 
posetopological={'current_node':'TODO','closest_node':'TODO'}

How and when remove all this data???


''''



import qi
import argparse
import sys
import os
import time
import threading
import json

from naoqi import ALProxy

from utils import point2world
import conditions
from conditions import set_condition






global people_list


def update_data(currentuser):
    

    
    b_new=True
    
    
    # update some info for old detections
    
    for i in range(len(people_list)):
        
        if currentuser['person_naoqiid']==people_list[i]:
            
            mem_person=memory_service.getData('Actions/memorizepeople/'+people_list[i])
            json_person=json.loads(mem_person)
            b_new=False
            
            json_person['info']['height']=currentuser['info']['height']
            json_person['info']['posture']=currentuser['info']['posture']
            
            # Update only if confidence is higher 
            if currentuser['face_naoqi']['faceinfo']['age']['conf'] >json_person['face_naoqi']['faceinfo']['age']['conf']:
                json_person['face_naoqi']['faceinfo']['age']=currentuser['face_naoqi']['faceinfo']['age']

            if currentuser['face_naoqi']['faceinfo']['gender']['conf'] >json_person['face_naoqi']['faceinfo']['gender']['conf']:
                json_person['face_naoqi']['faceinfo']['gender']=currentuser['face_naoqi']['faceinfo']['gender']
                
            ## Write data in ALMemory
            str_person=json.dumps(json_person)
            memory_service.insertData('Actions/memorizepeople/Person/'+currentuser['personid'], str_person)
            
    ## ADD new person    
    if b_new is True:
        
        people_list.append(currentuser)
        
        ## Write data in ALMemory
        str_person=json.dumps(currentuser)
        memory_service.insertData('Actions/memorizepeople/Person/'+currentuser['personid'], currentuser)
        
    memory_service.insertData('Actions/memorizepeople/PeopleList/', people_list)

def rhMonitorThread (memory_service):
    t = threading.currentThread()
    print "memorizepeople thread started"

    global people_list
    people_list=[]
    
    while getattr(t, "do_run", True):
        
        
        people_list =  memory_service.getData("PeoplePerception/PeopleList")
                                
        person=None
        poseinworld=None
        
        for personid in people_list:
            
            print 'personid= ',personid
            face={'name':'','faceinfo':{}}
            age={'val':0.0,'conf':0.0}
            gender={'val':0.0,'conf':0.0}
            smile={'val':0.0,'conf':0.0}
            try:
                
                #try:
                res_char=face_char_service.analyzeFaceCharacteristics(personid)
                print 'res_char',res_char
                
                #lookingat =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/LookingAtRobotScore")
                #gazedirection =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/GazeDirection")
                propage =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AgeProperties")
                propgender =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/GenderProperties")
                propexpression =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ExpressionProperties")
                propsmile =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/SmileProperties")

                
                if propgender[0] ==0.0:
                    str_gender='female'
                elif propgender[0] ==1.0:
                    str_gender='male'
                age={'val':propage[0],'conf':round(propage[1],2)}
                gender={'val':str_gender,'conf':round(propgender[1],2)}
                smile={'val':round(propsmile[0],2),'conf':round(propsmile[1],2)}
                
                #propexpression  [neutral, happy, surprised, angry or sad].
                #expression={'neutral':round(propexpression[0],2),'happy':round(propexpression[1],2),'surprised':round(propexpression[2],2),'angry':round(propexpression[3],2),'sad':round(propexpression[4],2)}
                
            except:
                print 'FaceCharacteristics error '
#                    
            facecharacteristics={'age':age, 'gender':gender,'smile':smile, 'expression':{}}


            shirtcolor={'name': '', 'hsv':[]}
            personinfo={'height': 0.0, 'shirtcolor': {} }
            poseinworld={'x':0.0,'y': 0.0} 
            
            try:
#                angles =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AnglesYawPitch")
#                distance =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/Distance")
                height =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/RealHeight")
                shirtcolorName =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColor")
                shirtcolorHSV =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColorHSV")
                PositionInRobotFrame =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/PositionInRobotFrame")
                issitting=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsSitting") #0 is standing,1 sitting,2 is unknown.
#                    
#
                posture='unknow'
                if issitting==0:
                    posture='standing'
                elif issitting==1:
                    posture='sitting'
                # Write data in json format

                shirtcolor={'name': shirtcolorName, 'hsv':shirtcolorHSV}
                personinfo={'height': round(height,2), 'shirtcolor': shirtcolor,'posture':posture}
                face['faceinfo']=facecharacteristics
                
                w_px, w_py = point2world(memory_service,[PositionInRobotFrame[0],PositionInRobotFrame[1]])
                poseinworld={'x':w_px,'y': w_py}
                
                
                
                
            except:
                print 'Person info error '
        
            posetopological={'current_node':'TODO','closest_node':'TODO'}
            lastlocation= {'world':poseinworld , 'topological':posetopological}
            
            user={'personid': personid ,'person_naoqiid': personid,'info': personinfo, 'lastlocation':lastlocation, 'face_naoqi': {},'face_ms_api': {}}
            
            
            update_data(user)        
            
            
            
        
        
        
        time.sleep(0.5)
    print "Memorizepeople thread quit"



def init(session):
    global memory_service
    global monitorThread

    print "Memorizepeople init"

    #Starting services
    memory_service  = session.service("ALMemory")
        
#    people_service = session.service("ALPeoplePerception")
    face_char_service = session.service("ALFaceCharacteristics")
    sitting_service = session.service("ALSittingPeopleDetection")
    

    

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Memorizepeople quit"
    monitorThread.do_run = False 
    

    ###
    ##  End sessions????


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ",    connection_url
        app = qi.Application(["PersonHere", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    init(session)

    app.run()    


if __name__ == "__main__":
    main()