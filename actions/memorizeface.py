'''
Memorize face
==================

Wait for 1 face detection with minimum size

If in that moment there is not Peopledetection take the idperson from  ALMemory 'Actions/personhere/PersonID'

Update  'Actions/MemorizePeople/Person/IDNUMBER' 


PARAMS:

memorizeface_inprofile_Humans/Profile<1|2|3> Read memorykey 'Humans/Profile<1|2|3>

memorizeface_name_<nameuser>

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
#confidenceThreshold=0.4 #default =0.4
min_size={'w':0.10 ,'h':0.10}

actionName = "memorizeface"



global msface_naoqi_enabled

def onFaceDetection(facevalues):
    
    for faceInfo in facevalues:
        # First Field = Shape info.
        faceShapeInfo = faceInfo[0]
        # Second Field = Extra info .
        faceExtraInfo = faceInfo[1]
        
        #print 'eyeLeft',round(faceExtraInfo[3][0],2),'eyeRight',round(faceExtraInfo[4][0],2)
        pose={'alpha': round(faceShapeInfo[1],2), 'beta': round(faceShapeInfo[2],2), 'width':round(faceShapeInfo[3],2), 'height': round(faceShapeInfo[4],2)}
        face={ 'name': faceExtraInfo[2], 'pose': pose}
        
    return face
 

def onPeopleDetection(value):
    
    personid=values
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
        #print 'FaceCharacteristics error '
        pass
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
        #print 'Person info error '
        pass

    face['faceinfo']=facecharacteristics      
    posetopological={'current_node':'TODO','closest_node':'TODO'}
    lastlocation= {'world':poseinworld , 'topological':posetopological}
    
    user={'personid': personid ,'person_naoqiid': personid,'info': personinfo, 'lastlocation':lastlocation, 'face_naoqi': face,'face_ms_api': {}}
    
   
    return user
    
def updateMemorizePeople(currentuser):



    try:
        mem_list=memory_service.getData('Actions/MemorizePeople/PeopleList')
        people_list=json.loads(mem_list)
        
        for i in range(len(people_list)):
            
            if currentuser['person_naoqiid']==people_list[i]['person_naoqiid']:
    
                back_person=people_list[i]
                

                if json_person['info']['height'] is not '':
                    back_person['info']['height']=currentuser['info']['height']
                    
                if json_person['info']['posture'] is not '':
                    back_person['info']['posture']=currentuser['info']['posture']
                
                back_person['face_naoqi']['name']=currentuser['face_naoqi']['name']
            
                # Update only if confidence is higher 
                if currentuser['face_naoqi']['faceinfo']['age']['conf'] >back_person['face_naoqi']['faceinfo']['age']['conf']:
                    back_person['face_naoqi']['faceinfo']['age']=currentuser['face_naoqi']['faceinfo']['age']
    
                if currentuser['face_naoqi']['faceinfo']['gender']['conf'] >back_person['face_naoqi']['faceinfo']['gender']['conf']:
                    back_person['face_naoqi']['faceinfo']['gender']=currentuser['face_naoqi']['faceinfo']['gender']

        
            ## Write data in ALMemory
            people_list[i]=back_person
            str_person=json.dumps(people_list)
            memory_service.insertData('Actions/memorizepeople/Peoplelist', str_person) 
            

    except:
        people_list=[]
        
def actionThread_exec (params):

    global face_char_service
    
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    faces_service = getattr(t, "session", None).service("ALFaceDetection")
    faces_service.setRecognitionEnabled(True)
    face_char_service = getattr(t, "session", None).service("ALFaceCharacteristics")
    print "Action "+actionName+" started with params "+params
    
    ##memorizeface_inmemory_Profile<1> Read memorykey 'Humans/Profile<1|2|3>
    nameuser=''
    personhere=None
    if params:
        parse_params=params.split('_')
        if parse_params[0]=='inprofile':
            try:
                userprofile=json.loadsmemory_service.getData(str(parse_params[1]))
                nameuser=userprofile['Name']
                personhere=userprofile['PersonID']
            except:
                print 'Humans/'+str(parse_params[1])+' not found ' 
        elif parse_params[0]=='name':
            nameuser=str(parse_params[1])
            
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
        peoplevisible =  memory_service.getData("PeoplePerception/VisiblePeopleList")
        
        if facevalues:
            
            facesarray=facevalues[1][0:len(facevalues[1]) -1] 
            
            #### Only valid when detects 1 face
            if len(facesarray) is 1:
    
                face_naoqi=onFaceDetection(facesarray)
                                
                if float(face_naoqi['pose']['width'])>= float(min_size['w']) and float(face_naoqi['pose']['height'])>=min_size['h']: 
                    
                    print 'Learning face ',nameuser
                    learned=faces_service.learnFace(nameuser)
                    #learned=True
                    print 'Face learned =',learned
                    if learned is False:
                        print 'Trying to relearn face ',nameuser
                        learned=faces_service.reLearnFace(nameuser)
                        
                        print 'Face learned =',learned                    
                    face_naoqi['name']=nameuser
                    
                    
                    face_ms_api={}
                    
                    ## ADD FACE MICROSOFT API 
                    if msface_naoqi_enabled== 'true': 
                        #memory_service.inserData("Actions/FaceRecognition/Recognition",'')
                        memory_service.raiseEvent('Actions/FaceRecognition/Command','addface_'+nameuser)
                        
                        learned=False
                        new_recognition=''
                        while len(new_recognition) < 1:
    
                            new_recognition=memory_service.getData("Actions/FaceRecognition/Recognition")
    
                            time.sleep(0.3)
                        
                        if new_recognition is 'false':
                            
                            print 'MS FACE API: not person added '
                            
                            ## TRY AGAIN??
                            
                        else :
                            face_ms_api=json.loads(new_recognition)
                            learned=True

                    if learned is True:

                        person=None
                        personid=None
                        
                            
                        if personhere is not None:
                            
                            personid=personhere
                            
                        elif len(peoplevisible) is 1:
                            
                            personid=peoplevisible
                                                    
                        else:
                            
                            try:
                                personid=memory_service.gettData('Actions/personhere/PersonID')
                        
                            except:
                                print 'memory Actions/personhere/PersonID not available'
                        
                        
                        if personid is not None:
                            
                            person=onPeopleDetection(personid)
                            if person is not None:
                                person['face_ms_api']=face_ms_api
                                updateMemorizePeople(person)

                                
                            
                            
                            ## START MICROSOFT API 
                            if msface_naoqi_enabled== 'true': 
                                memory_service.raiseEvent('Actions/FaceRecognition/Command','camera_stop')
                                
                            print 'EXIT TRUE'
                            b_completed=True
                            
                            
                        else:
                            
                            print 'There is not PeopleDetected to assign the face'
                            
                            ###
                            ## FORGET THE FACE ???
                            ## OR SAY SOMETHING
#                    else:
#                        print 'EXIT FALSE'
#                        memory_service.raiseEvent("PNP_action_result_"+actionName,"fail");
        

        time.sleep(0.3)

    # action end

    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");
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
