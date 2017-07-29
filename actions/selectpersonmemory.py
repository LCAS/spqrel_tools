'''
Peoplesummary
==================



PARAMS:

peoplesummary_{partydescription|SPRgame}

* 'partydescription' update the 'Humans/Profile<number> 
* 'SPRgame' return number of males and females detected

* 'Number/sitting'
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
command='closest'

actionName = "selectpersonmemory"
        
def actionThread_exec (params):

    global face_char_service
    
    t = threading.currentThread()
    print "selectpersonmemory thread started"
    memory_service = getattr(t, "mem_serv", None)
    https://github.com/LCAS/spqrel_tools.git

    print "Action "+actionName+" started with params "+params
    
    if params!='':
        
        command=params

    b_completed=False
    people_list=[]
    while (getattr(t, "do_run", True) and b_completed==False):
        try:
            mem_list=memory_service.getData('Actions/MemorizePeople/PeopleList')
            people_list=json.loads(mem_list)

            print 'len',len(people_list)
            print people_list
            
        except: 
            print 'Actions/MemorizePeople/PeopleList memory key not found '   

   
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
            for numberprofile in range(1,4):https://github.com/LCAS/spqrel_tools.git
                
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
                    

        elif command=='SPRgame':

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
            
            result={'total_persons':num_total,'num_males':num_males,'num_females':num_females }
            str_result=json.dumps(result)    
            memory_service.insertData('Humans/Crowd',str_result)
            
            b_completed=True
                    
        elif command=='description':
            name=''
            age=0
            str_gender=''
            tshircolor=''
            personid=''
            
            try:
                personid=memory_service.getData('Actions/personhere/PersonID')
        
            except:
                print 'memory Actions/personhere/PersonID not available'
            
            try:
                listvisible =  memory_service.getData("PeoplePerception/VisiblePeopleList")
                personid=listvisible[0]
            except:
                print 'memory Actions/personhere/PersonID not available'                
            
            
            try:
                tshircolor =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/ShirtColor")
                propage =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/AgeProperties")
                propgender =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/GenderProperties")
                age=round(propage[1],2)
                if propgender[0] ==0.0:
                    str_gender='female'
                elif propgender[0] ==1.0:
                    str_gender='male'
                

                
            except:
                print 'FaceCharacteristics not found ' 
                
            result={'PersonID':personid,'Name':'','Age':age, 'Gender':str_gender,'TshirtColor':tshircolor.lower()}
            str_result=json.dumps(result)                           
            memory_service.insertData('Humans/Description',str_result)


        elif command=='male':
            
            targetvalue=command
            for person in people_list:
                            
                if person['face_naoqi']['faceinfo']['gender']['val']== targetvalue and person['face_naoqi']['faceinfo']['gender']['conf']> 0.7:
                    idgoal=person['personid']
                    gender=person['face_naoqi']['faceinfo']['gender']['val']
                    age=person['face_naoqi']['faceinfo']['age']['val']
                    tshircolor=person['info']['shirtcolor']['name']
                    memory_service.insertData('Humans/TargetID',idgoal)
                    result={'PersonID':idgoal,'Name':'','Age':age, 'Gender':str_gender,'TshirtColor':tshircolor}
                    str_result=json.dumps(result)                           
                    memory_service.insertData('Humans/Description',str_result)

        elif command=='closest':
            
            targetvalue=command
            mindistance=5.0
            person=people_list[0]
            idgoal=person['personid']
            gender=person['face_naoqi']['faceinfo']['gender']['val']
            age=person['face_naoqi']['faceinfo']['age']['val']
            tshircolor=person['info']['shirtcolor']['name']
            memory_service.insertData('Humans/TargetID',idgoal)
            result={'PersonID':idgoal,'Name':'','Age':age, 'Gender':str_gender,'TshirtColor':tshircolor}
            str_result=json.dumps(result)                           
            memory_service.insertData('Humans/Description',str_result)

               
        b_completed=True                   
                    

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
