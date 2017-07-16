#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# DOCUMENTATION
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alpeopleperception-api.html#PeoplePerception
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alfacedetection.html

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



##PARAMS
confidenceThreshold=0.4 #default =0.4
min_size={'w':0.10 ,'h':0.10}

def writeJson(path,data):
    
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    jsonData=json.dumps(data,indent=2 )

    fh = open(path+'userlearned.json',"w")
    fh.write(jsonData)
    fh.close()


def onFaceDetection(facevalues):
    
    for faceInfo in facevalues:
        # First Field = Shape info.
        faceShapeInfo = faceInfo[0]
        # Second Field = Extra info .
        faceExtraInfo = faceInfo[1]
        
        #print 'eyeLeft',round(faceExtraInfo[3][0],2),'eyeRight',round(faceExtraInfo[4][0],2)
        pose={'alpha': round(faceShapeInfo[1],2), 'beta': round(faceShapeInfo[2],2), 'width':round(faceShapeInfo[3],2), 'height': round(faceShapeInfo[4],2)}
        face={'faceid': faceExtraInfo[0], 'user': faceExtraInfo[2], 'confidence':round(faceExtraInfo[1],3), 'pose': pose}
        
    return face
    

def rhMonitorThread (memory_service):
    t = threading.currentThread()
    print "learnperson thread started"
    print "waiting for face"
    while getattr(t, "do_run", True):
        
        
        facevalues =  memory_service.getData("FaceDetected")        
        peoplevisible =  memory_service.getData("PeoplePerception/VisiblePeopleList")
        
        if facevalues:
            
            facesarray=facevalues[1][0:len(facevalues[1]) -1] 
            
            #### TODO: Now only valid when detects 1 face
            if len(facesarray) is 1:
    
                face=onFaceDetection(facesarray)
                
                print 'pose',face['pose']
                if float(face['pose']['width'])>= float(min_size['w']) and float(face['pose']['height'])>=min_size['h']: 
                    
                    #####
                    ##### ID ????
                    print 'Learning face ',face['faceid']
                    learned=faces_service.learnFace('user-'+str(face['faceid']))
                    print 'Face learned =',learned
                    face['user']='user-'+str(face['faceid'])
                    
                    
                    
                    if learned is True:
                        
                        person=None
                        poseinworld=None
                        
                        if len(peoplevisible) is 1:
                        
                            personid=peoplevisible[0]
                            print 'personid= ',personid
                            #try:
                            
        #                    lookingat =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/LookingAtRobotScore")
        #                    gazedirection =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/GazeDirection")
        #                    age =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AgeProperties")
        #                    gender =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/GenderProperties")
        #                    expression =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ExpressionProperties")
        #                    smile =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/SmileProperties")
        #                    print 'lookingat=',lookingat
        #                    print 'gazedirection=',gazedirection
        #                    print 'age=',age
        #                    print 'gender=',gender
        #                    print 'expression=',expression
        #                    print 'smile=',smile
        #                    
        
                            
                            angles =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AnglesYawPitch")
                            distance =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/Distance")
                            height =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/RealHeight")
                            shirtcolor =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColor")
                            shirtcolorHSV =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColorHSV")
                            PositionInRobotFrame =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/PositionInRobotFrame")
        #                    issitting=memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/IsSitting")
        #                    
        #
        #                    print 'issitting=',issitting
        
                            # Write data in json format
                            
                            personinfo={'height': round(height,2), 'shirtcolor': shirtcolor, 'shirtcolorHSV':shirtcolorHSV}
                            
                            w_px, w_py = point2world(memory_service,[PositionInRobotFrame[0],PositionInRobotFrame[1]])
                            poseinworld={'x':w_px,'y': w_py}
                            
                            
                            person={'personid': personid, 'info': personinfo}
                        
                        posetopological={'current_node':'TODO','closest_node':'TODO'}
                        lastlocation= {'world':poseinworld , 'topological':posetopological}
                        
                        user={'face': face,'person': person,'lastlocation':lastlocation}
                        
                        writeJson('./data/',user)
                        
                        
                        
                        print 'EXIT TRUE'
                        quit()
                        break
                        
                        set_condition(memory_service,'learnperson','true')
                        
                        
                        
                    elif learned is False:
        
                        print 'EXIT FALSE'
                        quit()
                        set_condition(memory_service,'learnperson','false')

        time.sleep(0.2)
    print "learnperson thread quit"



def init(session):
    global memory_service
    global monitorThread

    global faces_service
    print "Learn Person init"

    #Starting services
    memory_service  = session.service("ALMemory")
    
    faces_service = session.service("ALFaceDetection")
    faces_service.setRecognitionConfidenceThreshold(confidenceThreshold)
    faces_service.setRecognitionEnabled(True)
    learnedlist = faces_service.getLearnedFacesList()
    print 'learnedlist=',learnedlist
    
    people_service = session.service("ALPeoplePerception")

    

    print "Creating the thread"

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()



def quit():
    global monitorThread
    print "Learn person quit"
    monitorThread.do_run = False 



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
