#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alpeopleperception-api.html#PeoplePerception
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alfacedetection.html

'''
Memorize people
==================

Writes in ALMemory 'Actions/MemorizePeople/PeopleList/' json string with all features 

params== 'SPRgame'
'''



import qi
import argparse
import sys
import os
import time
import threading
import json
import math

from naoqi import ALProxy


import action_base
from action_base import *

from utils import point2world
import conditions
from conditions import set_condition


import headpose

actionName = "memorizepeople"

global people_list
global memory_service

Step_turn_angle= math.pi/5
Max_turn_angle= math.pi
global countdt
countdt = 0
global currentangle
currentangle=0
Timeoutangle=5

headYaw = [ 0.2, 0.0, -0.2, -0.2, 0.0, 0.2, 0.0 ]
headPitch = [ -0.3, -0.3, -0.3, 0.0, 0.0, 0.0 ,-0.1]
headtime = 0.6

def update_data(currentuser):
    b_new=True
    
    try:
        mem_list=memory_service.getData('Actions/MemorizePeople/PeopleList')
        people_list=json.loads(mem_list)
        
    except:

        people_list=[]
        
    if len(people_list)>1:
        
        
        # update some info for old detections
        
        for i in range(len(people_list)):
            
            if currentuser['person_naoqiid']==people_list[i]['person_naoqiid']:
                
                json_person=people_list[i]
                
    #            mem_person=memory_service.getData('Actions/MemorizePeople/'+people_list[i])
    #            json_person=json.loads(mem_person)
                b_new=False
                
                json_person['info']['height']=currentuser['info']['height']
                json_person['info']['posture']=currentuser['info']['posture']
                
                # Update only if confidence is higher 
                if currentuser['face_naoqi']['faceinfo']['age']['conf'] >json_person['face_naoqi']['faceinfo']['age']['conf']:
                    json_person['face_naoqi']['faceinfo']['age']=currentuser['face_naoqi']['faceinfo']['age']
    
                if currentuser['face_naoqi']['faceinfo']['gender']['conf'] >json_person['face_naoqi']['faceinfo']['gender']['conf']:
                    json_person['face_naoqi']['faceinfo']['gender']=currentuser['face_naoqi']['faceinfo']['gender']
                    
    #            ## Write data in ALMemory
    #            str_person=json.dumps(json_person)
    #            memory_service.insertData('Actions/MemorizePeople/Person/'+currentuser['personid'], str_person)
    
                people_list[i]=json_person
       
            
    ## ADD new person    
    if b_new is True:
        
        people_list.append(currentuser)

        
        
    str_person=json.dumps(people_list)
    memory_service.insertData('Actions/MemorizePeople/PeopleList', str_person) 
    





def actionThread_exec (params):

    #global face_char_service
    global memory_service
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    faces_service = getattr(t, "session", None).service("ALFaceDetection")
    faces_service.setRecognitionEnabled(True)
    motion_service  = getattr(t, "session", None).service("ALMotion")
    face_char_service = getattr(t, "session", None).service("ALFaceCharacteristics")
    print "Action "+actionName+" started with params "+params

    # DElete old list
    global people_list
    people_list=[]

    b_completed=False
    memory_service.insertData('Actions/MemorizePeople/PeopleList',people_list) 
    
    while (getattr(t, "do_run", True) and b_completed==False):
        
        motion_service
        naoqi_people_list =  memory_service.getData("PeoplePerception/PeopleList")
                                
        person=None
        poseinworld=None
#        print 'naoqi_people_list= ',naoqi_people_list
#        print '#################'
        for personid in naoqi_people_list:
            
            #print 'personid= ',personid
#            print '__________'
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

                print 'propgender',propgender
                
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
                pass
#                    
            facecharacteristics={'age':age, 'gender':gender,'smile':smile, 'expression':{}}


            shirtcolor={'name': '', 'hsv':[]}
            personinfo={'height': 0.0, 'shirtcolor': shirtcolor,'posture':'' }
            poseinworld={'x':0.0,'y': 0.0} 
            
            try:
#                angles =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AnglesYawPitch")
#                distance =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/Distance")
                height =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/RealHeight")
                shirtcolorName =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColor")
                shirtcolorHSV =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColorHSV")
                PositionInRobotFrame =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/PositionInRobotFrame")
                issitting=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsSitting") #0 is standing,1 sitting,2 is unknown.
                
                iswaving=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsWaving")
                iswavingcenter=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsWavingCenter")
                iswavingleft=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsWavingLeft")
                iswavingright=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsWavingRight")
                

                

#
                posture='unknow'
                if issitting==0:
                    posture='standing'
                elif issitting==1:
                    posture='sitting'
                    
                wavingmode='none'
                if iswavingcenter==1:
                    wavingmode='center'
                if iswavingcenter==1:
                    iswavingleft='left'
                if iswavingcenter==1:
                    iswavingright='right'
                # Write data in json format

                shirtcolor={'name': shirtcolorName.lower(), 'hsv':shirtcolorHSV}
                personinfo={'height': round(height,2), 'shirtcolor': shirtcolor,'posture':posture,'waving': wavingmode}
                

                w_px, w_py = point2world(memory_service,[PositionInRobotFrame[0],PositionInRobotFrame[1]])
                poseinworld={'x':w_px,'y': w_py}
                
                
                
                
            except:
                print 'Person info error '
                pass


            try:
                current_node=memory_service.getData('TopologicalNav/CurrentNode')
                closest_node=memory_service.getData('TopologicalNav/ClosestNode')
                
            except:
                #print 'topological localization error '
                current_node=None
                closest_node=None
                
            face['faceinfo']=facecharacteristics
        
            posetopological={'current_node':current_node,'closest_node':closest_node}
            lastlocation= {'world':poseinworld , 'topological':posetopological}
            
            user={'personid': personid ,'person_naoqiid': personid,'info': personinfo, 'lastlocation':lastlocation, 'face_naoqi': face,'face_ms_api': {}}
            
            
            update_data(user)        
            


        if params== 'SPRgame':
            global countdt
            global currentangle
            
            if countdt>Timeoutangle:
                
#                motion_service.moveTo(0.0, 0.0, currentangle)
#                currentangle+=Step_turn_angle
                
                headpose.moveHead(motion_service, headYaw[currentangle], headPitch[currentangle], headtime)
                countdt = 0
                currentangle+=1
            else:
                countdt+=1

            if currentangle > len(headYaw)-1:
                print 'stop currentangle=',currentangle
                
                b_completed=True
                
        if params== 'Cocktailparty':
            
            global countdt
            global currentangle
            
            if countdt>Timeoutangle:
                
#                motion_service.moveTo(0.0, 0.0, currentangle)
#                currentangle+=Step_turn_angle
                
                headpose.moveHead(motion_service, headYaw[currentangle], headPitch[currentangle], headtime)
                countdt = 0
                currentangle+=1
            else:
                countdt+=1

            if currentangle > len(headYaw)-1:
                print 'stop currentangle=',currentangle
                
                b_completed=True
#            if currentangle > Max_turn_angle:
#                print 'stop currentangle=',currentangle
#                
#                b_completed=True

     
#            try:
#                mem_list=memory_service.getData('Actions/MemorizePeople/PeopleList')
#                people_list=json.loads(mem_list)
#                
#                b_completed=True
#                
#                for p in people_list:
#                    if p['face_naoqi']['faceinfo']['gender']['conf']<0.6:
#                        b_completed=False
#                        
#                if b_completed is True and len(people_list)>3:
#                    b_completed=True
#                        
#        
#            except:
#                pass
#            
            
                
            
        time.sleep(0.3)
        
    # action end
    action_success(actionName,params)






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
