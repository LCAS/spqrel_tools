'''
Find Person
==================

* Input params
findperson_<by{name|color|gender|profile}>_<value>

* Output 

 'Actions/FindPerson/<PersonID>'

TODO
-----


'''



import qi
import argparse
import sys
import time
import threading
import json

import action_base
from action_base import *

import conditions
from conditions import set_condition


##PARAMS
confidenceThreshold=0.5

actionName = "findperson"



def onFaceDetection(facevalues):
    
    for faceInfo in facevalues:
        # First Field = Shape info.
        faceShapeInfo = faceInfo[0]
        # Second Field = Extra info .
        faceExtraInfo = faceInfo[1]
        nameuser=str(faceExtraInfo[2]).strip()
        
        #print 'eyeLeft',round(faceExtraInfo[3][0],2),'eyeRight',round(faceExtraInfo[4][0],2)
        pose={'alpha': round(faceShapeInfo[1],2), 'beta': round(faceShapeInfo[2],2), 'width':round(faceShapeInfo[3],2), 'height': round(faceShapeInfo[4],2), 'head_torso':{}}
        face={ 'name': nameuser, 'confidence':round(faceExtraInfo[1],3), 'pose': pose}
        
    return face
 

def onPeopleDetection(value):
   
    personid=value
    print 'personid= ',personid
    face={'name':'','faceinfo':{}}
    age={'val':0.0,'conf':0.0}
    gender={'val':0.0,'conf':0.0}
    smile={'val':0.0,'conf':0.0}
    
    try:
        
        #res_char=face_char_service.analyzeFaceCharacteristics(personid)
        #print 'res_char',res_char
        
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
        pass
#                    
    facecharacteristics={'age':age, 'gender':gender,'smile':smile, 'expression':{}}


    shirtcolor={'name': '', 'hsv':[]}
    personinfo={'height': 0.0, 'shirtcolor': {} }
    poseinworld={'x':0.0,'y': 0.0} 
    issitting=0
    try:
        
        
        res_char=face_char_service.analyzeFaceCharacteristics(personid)
    
#                angles =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AnglesYawPitch")
#                distance =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/Distance")
        height =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/RealHeight")
        shirtcolorName =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColor")
        shirtcolorHSV =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColorHSV")
        PositionInRobotFrame =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/PositionInRobotFrame")
        try:
            issitting=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsSitting") #0 is standing,1 sitting,2 is unknown.
        except:
            pass
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
        pass

    face['faceinfo']=facecharacteristics      
    posetopological={'current_node':'TODO','closest_node':'TODO'}
    lastlocation= {'world':poseinworld , 'topological':posetopological}
    
    user={'personid': personid ,'person_naoqiid': personid,'info': personinfo, 'lastlocation':lastlocation, 'face_naoqi': face,'face_ms_api': {}}
    
   
    return user
    

def byname(facevalues,peoplevisible):

    targetid=None
    
    if facevalues:
        facesarray=facevalues[1][0:len(facevalues[1]) -1] 
       
        for  f in facesarray:
            
            face_naoqi=onFaceDetection(facesarray)
            if int(face_naoqi['confidence'])>0.0:
                if face_naoqi['name']==targetvalue and int(face_naoqi['confidence'])>0.5:
                    
                    print 'typevalue found!!!'
                    cameraPose_InTorsoFrame=facevalues[2]
                    facePose_InTorsoFRame={'yaw':round(cameraPose_InTorsoFrame[5],3),'pitch':round(cameraPose_InTorsoFrame[4],3)}
                    face_naoqi['pose']['head_torso']=facePose_InTorsoFRame
                    
                    print 'typevalue found!!!'
                    
                    mindistance=320.0
                    idgoal=None
                    for personid in peoplevisible:
                        
                        person=onPeopleDetection(personid)
                        face_corrected_yaw=face_naoqi['pose']['alpha']+face_naoqi['pose']['head_torso']['yaw']
                        distance=abs(person['lastlocation']['pose']['yaw']-image_yaw)
                        if distance < mindistance:
                            mindistance=distance
                            idgoal=person['personid']
                            
                    if mindistance<= 0.1:
                        
                        targetid=idgoal
    
                        
                    else:
                        
                        print 'not correspondence mindistance=',mindistance
    return targetid
    
def actionThread_exec (params):

    global face_char_service
    
    t = threading.currentThread()
    #memory_service = mem_serv

    faces_service = session.service("ALFaceDetection")
    faces_service.setRecognitionEnabled(True)
    learnedlist = faces_service.getLearnedFacesList()
    print 'learnedlist=',learnedlist
    face_char_service = session.service("ALFaceCharacteristics")
    sitting_service = session.service("ALSittingPeopleDetection")
    print "Action  started with params "
    
    parse_params=params.split('_')
    targettype=parse_params[0]
    targetvalue=parse_params[1]
    print 'params::',targetnumber,',',targettype,',',targetvalue
    idgoal=None
    b_completed=False    
    
    if targettype=='profile':
        
        try:   
            mem_profile=memory_service.getData(str(parse_params[2]))
            json_profile=json.loads(mem_profile)
            targetvalue=json_profile['Name']
        except:
            print 'Memory ',str(parse_params[2]),'not found'
            b_completed=True
            
            
    ## START MICROSOFT API 
    global msface_naoqi_enabled
    msface_naoqi_enabled='false'
    try:
        msface_naoqi_enabled=memory_service.getData('Actions/FaceRecognition/Enabled')
        print 'msface_naoqi_enabled=',msface_naoqi_enabled
        if msface_naoqi_enabled== 'true':    
            memory_service.raiseEvent('Actions/FaceRecognition/Command','camera_start')
    except:
        print 'Data not found Actions/FaceRecognition/Enabled'
        
    # action init
    b_completed=False
    
    while (getattr(t, "do_run", True) and b_completed==False):
        
        
        facevalues =  memory_service.getData("FaceDetected")        
        peoplevisible =  memory_service.getData("PeoplePerception/PeopleList")
        
        
        
        if targettype=='name':
            
            idgoal=byname(facevalues,peoplevisible)
            
            if idgoal is not None:
                memory_service.insertData('Humans/TargetID',idgoal)
                b_completed=True

                            
        if targettype=='color':
            target_list=[]
            for personid in peoplevisible:
                            
                person=onPeopleDetection(personid)
                try:
                    
                    if person['info']['shirtcolor']['name']==targetvalue:
                        
                        memory_service.insertData('Humans/TargetID',idgoal)
                        b_completed=True
                except:
                    pass
                
#                if len(target_list)==targetnumber:
#                    str_target_list=json.dumps(target_list)
#                    
#                    memory_service.insertData('Humans/Target',str_target_list)
#                    
#                    result={'num'=}
#                    str_result=json.dumps(result)                           
#                    memory_service.insertData('Humans/Peoplesummary',str_result)
#                    b_completed=True 
                                                                   
        if targettype=='gender':
            
            for personid in peoplevisible:
                            
                person=onPeopleDetection(personid)
                print 'color person=',person['face_naoqi']['faceinfo']['gender']['val'],'targetvalue=',targetvalue
                if person['face_naoqi']['faceinfo']['gender']['val']== targetvalue and person['face_naoqi']['faceinfo']['gender']['conf']> 0.7:
                    idgoal=person['personid']
                    memory_service.insertData('Humans/TargetID',idgoal)
                    b_completed=True                        

        if targettype=='posture':
            
            for personid in peoplevisible:
                            
                person=onPeopleDetection(personid)
                print 'color person=',person['info']['posture'],'targetvalue=',targetvalue
                if person['info']['posture']== targetvalue :
                    idgoal=person['personid']
                    memory_service.insertData('Humans/TargetID',idgoal)
                    b_completed=True
                                                        

        if targettype=='profile':
            
            idgoal=byname(facevalues,peoplevisible)
            
            if idgoal is not None:
                b_completed=True
                        

        time.sleep(0.3)

    # action end

    print idgoal              
    print "Action "+actionName+" "+params+" terminated"




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
