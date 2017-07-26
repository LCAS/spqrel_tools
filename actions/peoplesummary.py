'''
Peoplesummary
==================



PARAMS:

peoplesummary_{partydescription|SPRgame}

* 'partydescription' update the 'Humans/Profile<number> 
* 'SPRgame' return number of males and females detected

TODO:



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

actionName = "peoplesummary"
        
def actionThread_exec (params):

    global face_char_service
    
    t = threading.currentThread()
    print "peoplesummary thread started"
    memory_service = getattr(t, "mem_serv", None)
    

    print "Action "+actionName+" started with params "+params
    
    command=params

    b_completed=False
    
    while (getattr(t, "do_run", True) and b_completed==False):
        try:
            mem_list=memory_service.getData('Actions/MemorizePeople/Peoplelist')
            people_list=json.loads(mem_list)

            print 'len',len(people_list)
            print people_list
            
        except: 
            print 'Actions/Memorizepeople/Peoplelist memory key not found '   

   
        if command=='Partydescription':

    
            try:
                list_features=[]
                
                for p in people_list:
                    
                    print 'person_naoqiid: ',p['person_naoqiid']
                    valgender=''
                    if p['face_naoqi']['faceinfo']['gender']['conf']>0.8:
                        valgender=p['face_naoqi']['faceinfo']['gender']['val']
                        
                    print 'valgender=',valgender
                    valheight=''    
                    if p['info']['posture'] is not 'sitting': #not sitting
                        valheight=p['info']['height']
                    print 'valheight=',valheight
                    valaccessories=''    
                    if len(p['face_ms_api']) >1:
                        valaccessories=p['face_ms_api']['faceinfo']['glasses']
                    print 'valaccessories=',valaccessories
                    person= PersonFeatures(personid=p['person_naoqiid'],name=p['face_naoqi']['name'], gender=valgender, height=valheight, colortshirt=p['info']['shirtcolor']['name'],accessories=valaccessories)
                    list_features.append(person)
            except: 
                print 'people features error'     
                
            list_profiles=[]
            for numberprofile in range(1,4):
                
                try:
                    mem=memory_service.getData('Humans/Profile'+str(numberprofile))

                    json_mem=json.loads(mem)
                    print 'json_mem=',json_mem
                    for current_profile in list_features:
                        if current_profile.name==json_mem['Name']:

                    
                            json_mem['Gender']=current_profile.gender
                            json_mem['ColorTshirt']=current_profile.colortshirt
                            json_mem['Singularity']=''

                            str_profile=json.dumps(json_mem)
                           
                            memory_service.insertData('Humans/Profile'+str(numberprofile),str_profile)

                    
                    #singularity
#                    list_profiles.append(json_mem)
                    
                except: 
                    print 'Humans/Profile'+str(numberprofile)+' not found '  
                    

        if command=='Crowd':
            
            num_males=0
            num_females=0
            num_total=len(people_list)
            for p in people_list:
                
                if p['face_naoqi']['faceinfo']['gender']['val'] =='male':
                    num_males +=1
                elif p['face_naoqi']['faceinfo']['gender']['val'] =='female':
                    num_females +=1
            print '*****'
            print 'TOTAL PERSONS :', num_total
            print 'TOTAL MALES :', num_males
            print 'TOTAL FEMALES :', num_females
            
            result={'total':num_total,'num_males':num_males,'num_females':num_females }
            str_result=json.dumps(result)    
            memory_service.insertData('Humans/Peoplesummary',str_result)
                    
        if command=='Person':
            name=''
            age=''
            gender=''
            tshircolor=''
            result={'PersonID':personid,'Name':name,'Age':age, 'Gender': gender, 'TshirtColor':tshircolor}
            try:
                personid=memory_service.gettData('Actions/personhere/PersonID')
        
            except:
                print 'memory Actions/personhere/PersonID not available'
            
            try:
                mem_list=memory_service.getData('Actions/MemorizePeople/Peoplelist')
                people_list=json.loads(mem_list)
    
                print 'len',len(people_list)
                print people_list
                
                for currentuser in people_list:
                    if currentuser['person_naoqiid']==personid:
                        name=currentuser['face_naoqi']['name']
                        age=currentuser['face_naoqi']['faceinfo']['age']
                        gender=currentuser['face_naoqi']['faceinfo']['gender']
                        tshircolor=currentuser['infp']['shirtcolor']['name']
                        
                        result={'PersonID':personid,'Name':name,'Age':age, 'Gender': gender, 'TshirtColor':tshircolor}
                        
                        
                
            except: 
                print 'Actions/MemorizePeople/Peoplelist memory key not found '   
                
                try:
                    shirtcolorName =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColor")
                    propage =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AgeProperties")
                    propgender =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/GenderProperties")
                    if propgender[0] ==0.0:
                        str_gender='female'
                    elif propgender[0] ==1.0:
                        str_gender='male'
                    result={'PersonID':personid,'Name':'','Age':round(propage[1],2), 'Gender':str_gender,'TshirtColor':shirtcolorName}

                    
                except:
                    print 'FaceCharacteristics not found '  

            str_result=json.dumps(result)                           
            memory_service.insertData('Humans/Peoplesummary',str_result)
                      
        b_completed=False                   
                    

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
